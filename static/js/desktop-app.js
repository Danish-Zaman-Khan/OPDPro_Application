(() => {
  const status = document.querySelector('[data-desktop-status]');
  const toast = document.querySelector('[data-desktop-toast]');
  const setupDialog = document.querySelector('[data-desktop-setup]');
  const setupForm = document.querySelector('[data-desktop-setup-form]');
  const setupError = document.querySelector('[data-desktop-setup-error]');
  const setupButton = document.querySelector('[data-desktop-action="setup"]');
  let toastTimer;

  if (!status || !setupDialog || !setupForm) return;

  const showToast = (message, isError = false) => {
    toast.textContent = message;
    toast.classList.toggle('is-error', isError);
    toast.classList.add('is-visible');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 5000);
  };

  const setBusy = (busy, message) => {
    document.querySelectorAll('.desktop-action').forEach(button => {
      button.disabled = busy;
    });
    status.textContent = message;
  };

  const showSetup = () => {
    setupError.hidden = true;
    setupError.textContent = '';
    if (!setupDialog.open) setupDialog.showModal();
  };

  const initialize = async () => {
    if (!window.pywebview?.api) return;
    try {
      const state = await window.pywebview.api.get_status();
      if (!state.ready) throw new Error(state.error || 'The clinic service is not ready.');
      status.textContent = 'Clinic data stays on this computer';
      setupButton.hidden = state.has_admin;
      if (!state.has_admin) showSetup();
    } catch (error) {
      status.textContent = 'OPDPro needs attention';
      showToast(error.message || 'OPDPro could not initialize.', true);
    }
  };

  if (window.pywebview?.api) {
    initialize();
  } else {
    window.addEventListener('pywebviewready', initialize, { once: true });
  }

  setupButton.addEventListener('click', showSetup);
  setupForm.addEventListener('submit', async event => {
    event.preventDefault();
    const formData = new FormData(setupForm);
    const values = Object.fromEntries(formData.entries());
    const submit = setupForm.querySelector('button[type="submit"]');
    submit.disabled = true;
    setupError.hidden = true;
    try {
      const result = await window.pywebview.api.create_administrator(
        values.first_name,
        values.last_name,
        values.email,
        values.password,
        values.confirm_password,
      );
      if (!result.ok) {
        setupError.textContent = result.error;
        setupError.hidden = false;
        return;
      }
      setupDialog.close();
      setupForm.reset();
      status.textContent = 'Administrator created';
      showToast('Administrator created. Sign in to open your clinic.');
      window.location.assign('/');
    } catch (error) {
      setupError.textContent = error.message || 'Administrator account could not be created.';
      setupError.hidden = false;
    } finally {
      submit.disabled = false;
    }
  });

  document.querySelector('[data-desktop-action="backup"]').addEventListener('click', async () => {
    setBusy(true, 'Choose a secure backup location…');
    try {
      const result = await window.pywebview.api.create_backup();
      if (!result.cancelled) showToast(`Backup saved to ${result.path}`);
      status.textContent = 'Clinic data stays on this computer';
    } catch (error) {
      status.textContent = 'Clinic data stays on this computer';
      showToast(error.message || 'Backup could not be created.', true);
    } finally {
      setBusy(false, 'Clinic data stays on this computer');
    }
  });

  document.querySelector('[data-desktop-action="restore"]').addEventListener('click', async () => {
    try {
      const selected = await window.pywebview.api.select_restore_backup();
      if (selected.cancelled) return;
      const confirmed = window.confirm(
        'Restoring replaces current clinic records and uploaded reports. ' +
        'OPDPro will first save a safety backup in its local backups folder. Continue?',
      );
      if (!confirmed) return;
      setBusy(true, 'Creating a safety backup and restoring clinic data…');
      const result = await window.pywebview.api.restore_backup(selected.path);
      status.textContent = 'Clinic data restored';
      showToast(`Restore complete. Safety backup saved to ${result.safety_backup}`);
      window.setTimeout(() => window.location.reload(), 700);
    } catch (error) {
      status.textContent = 'Clinic data stays on this computer';
      showToast(error.message || 'Backup could not be restored.', true);
    } finally {
      setBusy(false, 'Clinic data stays on this computer');
    }
  });

  document.querySelector('[data-desktop-action="data"]').addEventListener('click', async () => {
    try {
      await window.pywebview.api.open_data_folder();
    } catch (error) {
      showToast(error.message || 'The clinic data folder could not be opened.', true);
    }
  });
})();
