#!/usr/bin/env python3
"""
Script di build per File PexRenamer 

Crea l'eseguibile con PyInstaller e l'installer con Inno Setup.
Il progetto File Renamer è un'applicazione GUI PySide6 per rinominare file in batch.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# ===== CONFIGURAZIONE =====
from src.models.app_models import (
    APP_NAME,
    APP_VERSION,
    APP_ICON_PATH,
    INSTALLER_ICON_PATH,
    MAIN_WINDOW_ICON_PATH,
    BUTTON_FILMS_ICON_PATH,
    BUTTON_SERIES_ICON_PATH,
    BUTTON_MEDIA_INFO_ICON_PATH,
    BUTTON_SETTINGS_ICON_PATH,
)

MAIN_SCRIPT = 'src/main.py'  # Entry point principale dell'applicazione

# Percorsi
ROOT_DIR = Path(__file__).parent.parent  # Torna alla root del progetto

APP_ICON_PATH_ABSOLUTE = ROOT_DIR / APP_ICON_PATH if APP_ICON_PATH else None
INSTALLER_ICON_PATH_ABSOLUTE = (
    ROOT_DIR / INSTALLER_ICON_PATH if INSTALLER_ICON_PATH else None
)

DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
INSTALLER_DIR = ROOT_DIR / "installer"

# Inno Setup compiler (modifica se necessario)
INNO_SETUP_COMPILER = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"


def clean_directories() -> None:
    """Rimuove le cartelle di build precedenti e file .spec."""
    print("🧹 Pulizia cartelle build precedenti...")

    # Rimuovi cartelle
    for directory in [DIST_DIR, BUILD_DIR, INSTALLER_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"   Rimossa: {directory}")

    # Rimuovi tutti i file .spec nella root (caso di cambio nome app)
    spec_files: list[Path] = list(ROOT_DIR.glob("*.spec"))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"   Rimosso: {spec_file}")


def add_icon_resources(cmd: list, separator: str) -> None:
    """Add all icon resources to PyInstaller command.

    Args:
        cmd: PyInstaller command list to modify
        separator: Path separator (';' on Windows, ':' on Unix)
    """
    icon_paths = [
        (APP_ICON_PATH, "App icon"),
        (MAIN_WINDOW_ICON_PATH, "Main window icon"),
        (BUTTON_FILMS_ICON_PATH, "Films button icon"),
        (BUTTON_SERIES_ICON_PATH, "Series button icon"),
        (BUTTON_MEDIA_INFO_ICON_PATH, "Media Info button icon"),
        (BUTTON_SETTINGS_ICON_PATH, "Settings button icon"),
    ]

    for icon_relative_path, description in icon_paths:
        if icon_relative_path:
            icon_absolute = ROOT_DIR / icon_relative_path
            if icon_absolute.exists():
                icon_src = str(icon_absolute)
                icon_dest = str(Path(icon_relative_path).parent)
                cmd.extend(["--add-data", f"{icon_src}{separator}{icon_dest}"])
                print(f"   Added {description}: {icon_relative_path}")
            else:
                print(f"   ⚠️  {description} not found: {icon_relative_path}")


def run_pyinstaller():
    """Esegue PyInstaller per creare l'eseguibile."""
    print("\n📦 Compilazione con PyInstaller...")

    # Verifica che il file principale esista
    if not Path(MAIN_SCRIPT).exists():
        print(f"❌ Errore: {MAIN_SCRIPT} non trovato!")
        sys.exit(1)

    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name",
        APP_NAME,
        "--windowed",  # Nessuna console (usa --console se serve debug)
        "--onedir",  # Cartella con dipendenze
        "--clean",  # Pulisce cache
        "--noconfirm",  # Sovrascrive senza conferma
        # Opzioni specifiche per PySide6
        "--collect-all", "PySide6",  # Include tutti i moduli PySide6
    ]

    # Aggiungi dati extra (assets, ecc.) se esistono
    # Per questo progetto, non ci sono assets da includere al momento
    # Se in futuro verranno aggiunti, decommentare e modificare:
    # assets_path = ROOT_DIR / "src" / "assets"
    # if assets_path.exists():
    #     separator = ";" if sys.platform == "win32" else ":"
    #     cmd.extend(["--add-data", f"{assets_path}{separator}assets"])

    # Aggiungi icona se esiste
    if APP_ICON_PATH_ABSOLUTE and APP_ICON_PATH_ABSOLUTE.exists():
        # Su Windows, PyInstaller preferisce percorsi con backslash o path assoluti
        icon_str = str(APP_ICON_PATH_ABSOLUTE.resolve())
        cmd.extend(["--icon", icon_str])
        print(f"   Icona configurata: {icon_str}")
    else:
        print(f"   ⚠️  Icona non trovata: {APP_ICON_PATH_ABSOLUTE}")

    # Aggiungi tutte le icone come data files (usando la funzione helper)
    separator = ";" if sys.platform == "win32" else ":"
    add_icon_resources(cmd, separator)

    # File principale
    cmd.append(MAIN_SCRIPT)

    # Esegui
    result = subprocess.run(cmd, cwd=ROOT_DIR)

    if result.returncode != 0:
        print("❌ Errore durante la compilazione con PyInstaller!")
        sys.exit(1)

    print("✅ Compilazione completata!")


def create_inno_setup_script():
    """Crea lo script .iss per Inno Setup."""
    print("\n📝 Creazione script Inno Setup...")

    INSTALLER_DIR.mkdir(exist_ok=True)

    iss_content = f"""
; Script generato automaticamente per Inno Setup
#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "File Renamer Team"
#define MyAppURL "https://github.com/yourusername/renamer-v2"
#define MyAppExeName "{APP_NAME}.exe"

[Setup]
AppId={{{{7A3B4C5D-8E9F-4A1B-9C2D-3E4F5A6B7C8D}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
OutputDir={INSTALLER_DIR.as_posix()}
OutputBaseFilename={APP_NAME}_Setup_v{APP_VERSION}
{'SetupIconFile=' + INSTALLER_ICON_PATH_ABSOLUTE.as_posix() if INSTALLER_ICON_PATH_ABSOLUTE and INSTALLER_ICON_PATH_ABSOLUTE.exists() else '; Nessuna icona configurata'}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "{(DIST_DIR / APP_NAME).as_posix()}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{userappdata}}\\{APP_NAME}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    ConfigDir := ExpandConstant('{{userappdata}}\\{APP_NAME}');
    if DirExists(ConfigDir) then
    begin
      if MsgBox('Vuoi rimuovere anche i file di configurazione e le impostazioni salvate?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(ConfigDir, True, True, True);
      end;
    end;
  end;
end;
"""

    iss_path = INSTALLER_DIR / f"{APP_NAME}_setup.iss"
    iss_path.write_text(iss_content.strip(), encoding='utf-8')

    print(f"✅ Script creato: {iss_path}")
    return iss_path


def compile_installer(iss_path):
    """Compila l'installer con Inno Setup."""
    print("\n🔨 Compilazione installer con Inno Setup...")

    if not Path(INNO_SETUP_COMPILER).exists():
        print(f"⚠️  Inno Setup non trovato in: {INNO_SETUP_COMPILER}")
        print("   Scaricalo da: https://jrsoftware.org/isdl.php")
        print(f"   Script ISS salvato in: {iss_path}")
        print("   Puoi compilarlo manualmente.")
        return

    result = subprocess.run([INNO_SETUP_COMPILER, str(iss_path)])

    if result.returncode != 0:
        print("❌ Errore durante la compilazione dell'installer!")
        sys.exit(1)

    print("✅ Installer creato con successo!")
    print(f"   Posizione: {INSTALLER_DIR}")


def main():
    """Funzione principale."""
    print(f"🚀 Build di {APP_NAME} v{APP_VERSION}")
    print("=" * 50)

    try:
        # 1. Pulizia
        clean_directories()

        # 2. PyInstaller
        run_pyinstaller()

        # 3. Verifica che l'eseguibile esista
        exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
        if not exe_path.exists():
            print(f"❌ Eseguibile non trovato: {exe_path}")
            sys.exit(1)

        # 4. Crea script Inno Setup
        iss_path = create_inno_setup_script()

        # 5. Compila installer
        compile_installer(iss_path)

        print("\n" + "=" * 50)
        print("✨ Build completata con successo!")
        print(f"📁 Eseguibile: {exe_path}")
        print(f"📦 Installer: {INSTALLER_DIR}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
