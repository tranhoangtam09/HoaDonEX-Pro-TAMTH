[Setup]
AppId={{9A3D2C1F-7F18-4E6D-9F11-2C6E1A4A2026}
AppName=HOA DON EX PRO – TAMTH
AppVersion=1.0.0
AppPublisher=TAMTH
DefaultDirName={autopf}\HoaDonEX_PRO_TAMTH
DefaultGroupName=HOA DON EX PRO – TAMTH
OutputDir=dist
OutputBaseFilename=HoaDonEX_PRO_TAMTH_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\HoaDonEX_PRO_TAMTH.exe

[Languages]
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng ngoài Desktop"; GroupDescription: "Tùy chọn:"; Flags: unchecked

[Files]
Source: "dist\HoaDonEX_PRO_TAMTH\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HOA DON EX PRO – TAMTH"; Filename: "{app}\HoaDonEX_PRO_TAMTH.exe"
Name: "{autodesktop}\HOA DON EX PRO – TAMTH"; Filename: "{app}\HoaDonEX_PRO_TAMTH.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HoaDonEX_PRO_TAMTH.exe"; Description: "Khởi chạy HOA DON EX PRO – TAMTH"; Flags: postinstall nowait skipifsilent
