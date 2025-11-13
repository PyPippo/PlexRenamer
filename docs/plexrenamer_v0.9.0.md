# PlexRenamer - Release Notes v0.9.0

**Data Release:** 2025-11-12
**Stato:** Beta - Feature Complete (Settings Pending)

**Lingua:** Italiano | [English](plexrenamer_v0.9.0_EN.md)

---

## Sommario Release

PlexRenamer v0.9.0 rappresenta una release beta completamente funzionale per la normalizzazione dei nomi di file video (film e serie TV) per Plex Media Server. L'applicazione è stabile e pronta all'uso, con tutte le funzionalità core implementate. Manca solo il pannello Settings per considerarla release 1.0.

---

## Funzionalità Implementate

### Core Features

#### 1. Rinominazione Film
- Elaborazione batch di file multipli
- Estrazione automatica dell'anno dal nome file
- Formato standardizzato: `Movie Title (Year) - extras.mkv`
- Supporto per tutti i principali formati video

#### 2. Rinominazione Serie TV
- Elaborazione di intere cartelle stagione
- Normalizzazione numerazione episodi (formato S##E##)
- Richiesta anno singola per tutti gli episodi
- Formato: `Show Title (Year) - S01E01 - Episode Name.mkv`

#### 3. Editing Inline
- Modifica diretta nella tabella di preview
- Validazione in tempo reale
- Feedback visivo immediato sullo stato
- Prevenzione duplicati durante l'editing

#### 4. Sistema di Validazione
- Rilevamento automatico duplicati
- Controllo conflitti file
- Validazione formato in tempo reale
- Indicatori di stato colorati

### Interfaccia Utente

#### Componenti GUI
- **MainWindow**: Finestra principale con layout responsive
- **FileTable**: Tabella editabile con validazione inline
- **StatusBar**: Barra di stato con contatori dinamici
- **CustomButtons**: Pulsanti tematizzati con stili Windows-standard
- **Dialogs**: Dialog per input anno e conferme utente

#### Temi e Styling
- Supporto tema di sistema (chiaro/scuro)
- Palette colori semantica per stati file
- Stili pulsanti consistenti con linee guida Windows
- Separazione tra proprietà strutturali e tematizzabili

### Gestione Dati

#### Modelli
- **MediaType**: Enum per tipi media (MOVIE, SERIES)
- **FileStatus**: Stati validazione file
- **ProcessableFile**: Modello dati per file processabili
- **SessionManager**: Gestione sessione applicazione

#### Business Logic
- **FileAnalyzer**: Parsing e formattazione nomi file
- **MediaInfo**: Estrazione metadati file (durata, codec, risoluzione)
- **Utility Functions**: Helper per validazione e controlli

---

## Modifiche ai File di Configurazione

### 1. src/models/app_models.py

**Percorso:** `src/models/app_models.py`

**Modifiche Applicate:**
```diff
  # App name and version
  APP_NAME = 'PlexRenamer'
- APP_VERSION = '2.0.0'
+ APP_VERSION = '0.9.0'
```

**Motivazione:**
- Aggiornamento versione da 2.0.0 a 0.9.0 (Beta)
- Questa costante è utilizzata da `scripts/build.py` per:
  - Generare il file `.spec` di PyInstaller
  - Creare l'installer con Inno Setup
  - Nominare i file di output (es. `PlexRenamer_Setup_v0.9.0.exe`)

**Utilizzo:**
```python
# In scripts/build.py
from src.models.app_models import APP_NAME, APP_VERSION

# Usato in:
# - Nome eseguibile: {APP_NAME}.exe
# - Nome installer: {APP_NAME}_Setup_v{APP_VERSION}
# - Script Inno Setup: AppVersion={APP_VERSION}
```

### 2. scripts/build.py

**Percorso:** `scripts/build.py`

**Stato:** Nessuna modifica necessaria - Configurazione corretta

**Funzionamento:**
Il file `build.py` è lo script principale per la build dell'applicazione. Importa automaticamente le costanti da `app_models.py`:

```python
from src.models.app_models import (
    APP_NAME,
    APP_VERSION,
    APP_ICON_PATH,
    INSTALLER_ICON_PATH,
    MAIN_WINDOW_ICON_PATH,
    BUTTON_FILMS_ICON_PATH,
    BUTTON_SERIES_ICON_PATH,
)
```

**Processo di Build:**

1. **Pulizia**: Rimuove cartelle `dist/`, `build/`, `installer/` e file `*.spec` precedenti
2. **PyInstaller**:
   - Genera `PlexRenamer.spec` con nome e versione da `app_models.py`
   - Crea eseguibile `PlexRenamer.exe` in `dist/PlexRenamer/`
   - Include tutte le icone e dipendenze PySide6
3. **Inno Setup**:
   - Genera script `.iss` con versione corrente
   - Crea installer `PlexRenamer_Setup_v0.9.0.exe` in `installer/`

**Output Generati:**
```
dist/PlexRenamer/PlexRenamer.exe          # Eseguibile standalone
installer/PlexRenamer_Setup_v0.9.0.exe    # Installer Windows
PlexRenamer.spec                           # Spec PyInstaller (ignored da git)
```

**Esecuzione:**
```bash
python scripts/build.py
```

### 3. README.md

**Percorso:** `README.md`

**Modifiche Applicate:**

1. **Aggiornamento versione e status:**
```diff
- **Version:** 1.0.0
- **Status:** Production Ready ✅
+ **Version:** 0.9.0
+ **Status:** Beta - Settings Pending ⚙️
```

2. **Riscrittura sezione Installation:**
   - Aggiunta **Opzione 1: Windows Installer** (consigliato)
     - Istruzioni download e installazione `PlexRenamer_Setup_v0.9.0.exe`
     - Descrizione features (Start Menu, desktop shortcut, cleanup automatico)

   - Aggiunta **Opzione 2: Portable Version**
     - Istruzioni download ed estrazione `PlexRenamer_Portable_v0.9.0.zip`
     - Descrizione features (no install, USB ready, self-contained)

   - Rinominata vecchia sezione in **Opzione 3: Run from Source** (per sviluppatori)
     - Mantenute istruzioni Python esistenti

   - Aggiunta sezione **Building from Source**
     - Istruzioni per eseguire `python scripts/build.py`
     - Descrizione output generati (portable + installer)
     - Lista requirements per build

**Motivazione:**
- Allineamento versione con `app_models.py`
- Indicazione corretta dello stato Beta
- Trasparenza sulla funzionalità mancante (Settings)
- **Documentazione completa opzioni di installazione per utenti finali**
- **Chiarezza su come ottenere e usare gli eseguibili**
- **Distinzione tra utenti finali e sviluppatori**

### 4. .gitignore

**Percorso:** `.gitignore`

**Modifiche Applicate:**
```diff
- # Deprecated/Backup Files
- docs/development_steps/
+ # Documentation folder (excluded from repository)
+ docs/
```

**Motivazione:**
- Esclusione completa della cartella `docs/` dal repository
- Semplificazione della gestione della documentazione
- La cartella docs contiene solo documentazione di sviluppo non necessaria per gli utenti finali

**Sezioni Rilevanti del .gitignore:**

```gitignore
# esempi su cui testare l'app
data_set/

# build e installer
dist/
installer/
build/
*.spec

# Documentation folder (excluded from repository)
docs/

# Application configuration (user-specific)
config/

# Python-specific ignores
__pycache__/
*.py[codz]
.venv/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
```

### 2. README.md

**Percorso:** `README.md`

**Stato Attuale:**
- Documentazione completa dell'applicazione
- Versione dichiarata: 1.0.0 (da aggiornare a 0.9.0)
- Status: Production Ready (da aggiornare a Beta)

**Modifiche Suggerite per Consistenza:**
```diff
- **Version:** 1.0.0
- **Status:** Production Ready ✅
+ **Version:** 0.9.0
+ **Status:** Beta - Settings Pending ⚙️
```

### 3. requirements.txt

**Percorso:** `requirements.txt`

**Contenuto Attuale:**
```
PySide6>=6.9.3
pyinstaller>=6.16.0
pymediainfo>=6.1.0
```

**Stato:** Nessuna modifica necessaria
- Tutte le dipendenze sono aggiornate
- Versioni minime specificate correttamente
- Pronto per produzione

### 4. PlexRenamer.spec

**Percorso:** `PlexRenamer.spec`

**Stato:** Nessuna modifica necessaria
- Configurazione PyInstaller corretta
- Tutti gli assets e icone inclusi
- Modalità console disabilitata (GUI app)
- Icona applicazione configurata

**Note:**
- File generato automaticamente da PyInstaller
- Incluso nel .gitignore (pattern `*.spec`)
- Percorsi assoluti specifici della macchina di sviluppo

---

## Struttura del Progetto

```
Renamer V 2.0/
├── .gitignore              ✅ Aggiornato (esclude docs/)
├── .vscode/                # Configurazione VS Code
├── README.md               # Documentazione principale
├── requirements.txt        ✅ Nessuna modifica
├── PlexRenamer.spec        # Config PyInstaller (ignored)
├── run.py                  # Launcher applicazione
│
├── src/                    # Codice sorgente
│   ├── __init__.py
│   ├── main.py            # Entry point
│   │
│   ├── core/              # Logica business
│   │   ├── file_analyzer.py
│   │   ├── session_manager.py
│   │   └── _utility.py
│   │
│   ├── gui/               # Interfaccia utente
│   │   ├── main_window.py
│   │   ├── file_table.py
│   │   ├── status_bar.py
│   │   ├── buttons.py
│   │   └── dialogs.py
│   │
│   ├── models/            # Modelli dati
│   │   ├── media_types.py
│   │   └── gui_models.py
│   │
│   ├── media_info/        # Estrazione metadati
│   │   └── media_info.py
│   │
│   ├── presenters/        # Layer presentazione (MVP pattern)
│   │   └── __init__.py
│   │
│   ├── utils/             # Utilities
│   │   └── logging_config.py
│   │
│   └── assets/            # Risorse
│       └── icons/
│
├── tests/                 # Test suite
│   ├── test_real_world_data.py
│   ├── test_gui_components.py
│   ├── test_main_window.py
│   └── test_integration.py
│
├── scripts/               # Script di utilità
│
├── config/                # Configurazioni utente (ignored)
├── data_set/              # Dataset di test (ignored)
├── docs/                  # Documentazione (ignored)
├── dist/                  # Build output (ignored)
├── build/                 # Build temp (ignored)
└── installer/             # Installer output (ignored)
```

---

## Formati File Supportati

### Video
`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`

### Pattern Episodi
- `S01E01`, `s01e01` (formato standard)
- `1x01`, `3x9` (formato alternativo)

### Range Anni Validi
- Minimo: 1895 (primo film commerciale)
- Massimo: Anno corrente
- Definito in: `src/models/gui_models.py::MIN_VALID_YEAR`

---

## Indicatori di Stato

| Icona | Status | Descrizione |
|-------|--------|-------------|
| ✅ | Ready | File pronto per rinomina |
| ⚠️ | Needs Year | Anno mancante, richiede input |
| ❌ | Invalid | Formato invalido, non processabile |
| ⏭️ | Already Normalized | File già in formato corretto |
| ⚠️ | Duplicate | Nome file duplicato rilevato |

---

## Limitazioni Conosciute

### Funzionalità Mancanti
- ❌ **Pannello Settings** (previsto per v1.0)
  - Configurazione range anni
  - Preferenze tema
  - Opzioni formattazione
  - Impostazioni percorsi

### Limitazioni Tecniche
- Scansione solo di cartelle flat (no ricorsione sottocartelle)
- Nessuna funzionalità Undo/Redo
- Sessione-based (non si possono mixare film e serie)
- No preview file multimediale

---

## Roadmap v1.0

### Priorità Alta
- [ ] Implementare pannello Settings
- [ ] Configurazione range anni personalizzabili
- [ ] Salvataggio/caricamento preferenze utente

### Priorità Media
- [ ] Funzionalità Undo/Redo
- [ ] Storico rinominazioni
- [ ] Statistiche batch

### Priorità Bassa
- [ ] Preview file multimediale
- [ ] Scansione ricorsiva cartelle
- [ ] Filtri avanzati
- [ ] Customizzazione tema

---

## Note Tecniche

### Architettura
- **Pattern:** MVP (Model-View-Presenter) in transizione
- **Framework UI:** PySide6 (Qt for Python)
- **Type Hints:** Completi su tutto il codebase
- **Docstrings:** Google-style su tutte le funzioni pubbliche

### Best Practices Applicate
- Separazione concerns (core/gui/models)
- Componenti riusabili e modulari
- Validazione dati multi-livello
- Gestione errori robusta
- Logging configurabile

### Testing
- Test componenti GUI
- Test integrazione
- Test con dati reali
- Visual testing disponibile

---

## Installazione e Utilizzo

### Installazione

```bash
# Clone repository
cd "path/to/Renamer V 2.0"

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
# oppure
python src/main.py
```

### Build Eseguibile

```bash
# Build con PyInstaller
pyinstaller PlexRenamer.spec

# Output in dist/PlexRenamer/
```

---

## Workflow Utente

### Film
1. Click **"Add Movie 🎬"**
2. Seleziona uno o più file video
3. Rivedi preview (doppio click per editare)
4. Click **"Apply Changes"** per rinominare
5. Click **"Start Over"** per nuovo batch

### Serie TV
1. Click **"Add Series 📺"**
2. Seleziona cartella stagione (es. "Season 1")
3. Inserisci anno se richiesto
4. Rivedi preview (doppio click per editare)
5. Click **"Apply Changes"** per rinominare
6. Click **"Start Over"** per nuova stagione

---

## Credits

**Sviluppo:** Qoder Project
**Framework:** PySide6 (Qt for Python)
**Media Info:** pymediainfo
**Build Tool:** PyInstaller

---

## Licenza

Educational and Personal Use

---

## Riepilogo Modifiche per Release 0.9.0

### File Modificati

1. **[src/models/app_models.py](src/models/app_models.py:13)**
   - `APP_VERSION`: `2.0.0` → `0.9.0`

2. **[README.md](README.md)**
   - `Version`: `1.0.0` → `0.9.0`
   - `Status`: `Production Ready ✅` → `Beta - Settings Pending ⚙️`
   - **Ristrutturazione completa orientata all'utente finale:**
     - Nuova sezione **Screenshots** con 3 immagini (Series, Movie Editing, Results)
     - Sezione **Download** prominente con link a releases GitHub
     - **Installation Options** espansa:
       - Option 1: Windows Installer (consigliato)
       - Option 2: Portable Version
       - System Requirements dettagliati
     - Nuova sezione **Quick Start Guide** (Movies e TV Series)
     - Nuova sezione **File Status Indicators** (tabella)
     - Nuova sezione **FAQ & Support** con domande comuni
     - Sezione **For Developers** ridotta con rimando a DEVELOPMENT.md
     - Aggiunta **Roadmap** con versioni future
     - Sezione **Credits** espansa con link alle dipendenze
   - **Documentazione tecnica spostata** in `docs/DEVELOPMENT.md`

3. **[.gitignore](.gitignore:10-11)**
   - Aggiunta esclusione completa cartella `docs/`

4. **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**
   - **Nuovo file creato** con documentazione tecnica completa
   - Contenuto:
     - Getting Started (setup ambiente sviluppo)
     - Project Structure (struttura dettagliata cartelle)
     - Architecture Overview (layers e key components)
     - Design Principles (validation pipeline, safety features)
     - Development Workflow (branching, commits, PR)
     - Building & Packaging (processo build completo)
     - Testing (struttura test e come eseguirli)
     - Code Quality (type hints, docstrings, style)
     - Configuration (year range, formati, patterns)
     - Contributing (guida per contributors)

### File Verificati (Nessuna Modifica)

- **[scripts/build.py](scripts/build.py)**: Configurazione corretta, importa versione da `app_models.py`
- **[requirements.txt](requirements.txt)**: Dipendenze aggiornate
- **PlexRenamer.spec**: Generato automaticamente da `build.py` (ignorato da git)

### Prossimi Passi

**Per eseguire il commit della release 0.9.0:**

```bash
# 1. Inizializza repository git (se non già fatto)
git init

# 2. Aggiungi tutti i file (docs/ sarà automaticamente escluso)
git add -A

# 3. Verifica cosa verrà committato
git status

# 4. Crea il commit della release
git commit -m "Release 0.9.0 - PlexRenamer Beta

Initial release of PlexRenamer, a PySide6-based desktop application for
standardizing video file names for movies and TV series.

Features:
- Movie and TV series batch renaming
- Inline editing with real-time validation
- Duplicate detection and conflict prevention
- Smart year extraction and validation
- Status indicators and visual feedback
- Windows-standard themed UI

Configuration Changes:
- Updated app_models.py version to 0.9.0 (Beta status)
- Updated README.md version and status
- Updated .gitignore to exclude docs/ folder

Missing for v1.0:
- Settings panel implementation"

# 5. (Opzionale) Crea tag per la release
git tag -a v0.9.0 -m "Release 0.9.0 - Beta"

# 6. (Opzionale) Push su remote repository
git remote add origin <url-repository>
git push -u origin main
git push --tags
```

---

**Release Status:** ✅ Beta - Fully Functional
**Next Milestone:** v1.0 - Settings Implementation
**Release Date:** 2025-11-12
