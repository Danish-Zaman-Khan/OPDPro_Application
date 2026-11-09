# OPDPro: install and use on Windows

This folder is a Windows test release for one clinic on one computer. Install it only on a trusted Windows 10/11 computer. It is not a shared-network or internet server.

## What you need

- Windows 10 or 11, 64-bit.
- Internet for the first installation, so the installer can set up Python (if needed) and download OPDPro's components.
- Permission to run PowerShell scripts on your computer. The installer does not require administrator privileges.

## Install

1. Copy the complete `OPDPro-Test-Install` folder to the Windows computer, or share it as a ZIP and extract the ZIP first. Keep all files together.
2. Open the folder and double-click **Install-OPDPro.bat**.
3. If Windows asks for permission to run the installer, allow it. Leave the installer window open while setup completes.
4. The installer creates a private application environment and adds **OPDPro** shortcuts to the Desktop and Start menu. It opens OPDPro when installation finishes.
5. On first launch, select **Create clinic administrator** and set up the clinic's administrator account. Use a unique password of at least 12 characters.
6. When the clinic window says it is ready, select **Open OPDPro**. The app opens in your browser. Sign in with the administrator account and add staff accounts from **Admin tools**.

If Python setup fails, install Python 3.13 from <https://www.python.org/downloads/windows/> and run **Install-OPDPro.bat** again. If Windows blocks the installer, ask your computer administrator for help rather than changing security policies.

## Open, close, and keep clinic data

- After installation, open OPDPro from its Desktop or Start menu shortcut. The small **OPDPro Clinic** window starts the local app; choose **Open OPDPro** to use it in your browser.
- To close it, close the **OPDPro Clinic** window. The local server stops, but saved clinic information remains on the computer. Closing the browser alone does not stop the app.
- Open OPDPro again from its shortcut to continue. Records and uploaded reports are stored separately from the installed application under `%LOCALAPPDATA%\OPDPro`; restarting or reinstalling the application does not remove them.
- Use **Create backup** in the clinic window regularly. Store backups in a secure clinic-controlled location. Backup files contain sensitive patient data and are not encrypted by OPDPro.
- **Restore backup** replaces current clinic data. Choose it only when needed; OPDPro asks for confirmation and creates a safety backup first.

Do not delete `%LOCALAPPDATA%\OPDPro` if you want to keep clinic records. To move records to another computer, make a backup on the first computer and restore it on the second.

## Updates and removal

For an update, close OPDPro and run the new release's **Install-OPDPro.bat**. It updates the application separately from clinic data. Back up the clinic first.

To remove OPDPro, delete the Desktop/Start menu shortcuts and the application folder at `%LOCALAPPDATA%\Programs\OPDPro`. Keep `%LOCALAPPDATA%\OPDPro` to retain the clinic database and reports. Python may be shared with other applications, so the OPDPro installer does not uninstall it.

## Important limits

- This test release is for one clinic and one computer. It must not be exposed to a clinic LAN or the public internet.
- Do not enter real patient data until the clinic has reviewed privacy, access, backup, and regulatory requirements. OPDPro is not certified for regulatory compliance.
- Some interface styles and icons load from public CDNs and therefore need internet access.
- The package was assembled on macOS and has not been run through its Windows installer on a Windows computer. Have the receiving tester validate installation and backups with fictional data first.
