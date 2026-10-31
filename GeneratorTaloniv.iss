
#define MyAppName "GeneratorTaloniv"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GeneratorTaloniv"
#define MyAppExeName "GeneratorTaloniv.exe"

[Setup]
AppId={{774E31E3-DFFB-4D98-BB4F-EF052097B755}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}

UninstallDisplayIcon={app}\{#MyAppExeName}

PrivilegesRequired=lowest

OutputDir=dist
OutputBaseFilename=GeneratorTaloniv_Setup

Compression=lzma
SolidCompression=yes
WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Tasks]
Name: "desktopicon"; Description: "Створити ярлик на робочому столі"; GroupDescription: "Додаткові параметри:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Видалити {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити {#MyAppName}"; Flags: nowait postinstall skipifsilent
