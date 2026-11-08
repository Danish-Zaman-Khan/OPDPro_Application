#define AppName "OPDPro"
#define AppVersion "1.0.0"
#define AppPublisher "OPDPro"
#define AppExeName "OPDPro.exe"
#define SourcePath GetEnv("OPDPRO_SOURCE_DIR")

[Setup]
AppId={{1F970A33-FCA6-4F47-A783-8CA4A349F123}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\OPDPro
DefaultGroupName=OPDPro
PrivilegesRequired=lowest
OutputDir={#SourcePath}\dist
OutputBaseFilename=OPDPro-Setup
WizardStyle=modern
CloseApplications=yes
UninstallDisplayIcon={app}\OPDPro.exe
Compression=lzma2
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#SourcePath}\dist\OPDPro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\OPDPro"; Filename: "{app}\OPDPro.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\OPDPro"; Filename: "{app}\OPDPro.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\OPDPro.exe"; Description: "Open OPDPro"; WorkingDir: "{app}"; Flags: postinstall nowait skipifsilent
