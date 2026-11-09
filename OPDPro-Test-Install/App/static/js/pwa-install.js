(() => {
  let installPrompt = null;
  const installButtons = [...document.querySelectorAll('[data-pwa-install]')];
  const helpDialog = document.getElementById('pwaInstallHelp');
  const helpText = helpDialog?.querySelector('[data-install-instructions]');
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const isAppleMobile = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const isAndroid = /android/i.test(navigator.userAgent);

  const setInstallVisible = visible => installButtons.forEach(button => {
    button.hidden = !visible;
  });

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js', { scope: '/' }).catch(() => {});
    });
  }

  if (isStandalone) return;
  if (isAppleMobile || isAndroid) setInstallVisible(true);

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    installPrompt = event;
    setInstallVisible(true);
  });

  window.addEventListener('appinstalled', () => {
    installPrompt = null;
    setInstallVisible(false);
  });

  installButtons.forEach(button => button.addEventListener('click', async () => {
    if (installPrompt) {
      const promptEvent = installPrompt;
      installPrompt = null;
      await promptEvent.prompt();
      const choice = await promptEvent.userChoice;
      if (choice.outcome === 'accepted') setInstallVisible(false);
      return;
    }

    if (helpText) {
      helpText.textContent = isAppleMobile
        ? 'Tap Share, then choose Add to Home Screen.'
        : 'Open your browser menu and choose Install app or Add to Home screen.';
    }
    if (helpDialog?.showModal) helpDialog.showModal();
    else helpDialog?.setAttribute('open', '');
  }));
})();
