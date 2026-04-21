<div align="center">

# ◈ FileSage

### AI-Powered File Intelligence

**Organize your files intelligently using local Ollama, ChatGPT, or Claude.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green?logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-12%2B-black?logo=apple&logoColor=white)](https://apple.com/macos)
[![Windows](https://img.shields.io/badge/Windows-10%2B-0078d4?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![Linux](https://img.shields.io/badge/Linux-Ubuntu%20%2F%20Fedora%20%2F%20Arch-orange?logo=linux&logoColor=white)](https://kernel.org)

![FileSage Screenshot](docs/screenshot.png)

*FileSage analyzing n8n HTML templates using Gemma4 on Ollama — 16 files, all analyzed and sorted*

</div>

---

## What is FileSage?

FileSage is a native desktop application that uses AI to analyze your files and suggest intelligent folder structures. It reads file names, content previews, and folder context — then recommends where each file should live. You review the suggestions, select what to move, and FileSage does the rest.

**When using Ollama, everything runs locally — no file data ever leaves your machine.**

---

## Platform Support

| Platform | Status | Launcher | Notes |
|---|---|---|---|
| **macOS** 12+ | ✅ Fully supported | `./run.sh` | Native feel, Menlo font, Reveal in Finder |
| **Windows** 10/11 | ✅ Fully supported | `run.bat` | Segoe UI font, Reveal in Explorer |
| **Linux** (Ubuntu, Fedora, Arch) | ✅ Fully supported | `./run.sh` | Ubuntu/DejaVu font, opens parent folder |

---

## Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | Overview of all sessions, folder stats, file counts, storage usage |
| 📁 **File Manager** | List & grid view, filter by status, select all, bulk move |
| 🤖 **AI Analysis** | Streaming real-time analysis with live progress log |
| 🕐 **Activity Log** | Full history of every file moved, reveal in file browser |
| ⚙️ **Settings** | Default folder, database location, cache management |
| 🦙 **Multi-Provider** | Ollama (local), ChatGPT (OpenAI), Claude (Anthropic) |
| 💾 **Persistent Cache** | Sessions remembered across launches via SQLite |
| 👁 **Preview Mode** | See exactly what will move before committing |
| ↺ **Safe by Default** | Files only move when you explicitly confirm |

---

## Requirements

| Requirement | macOS | Windows | Linux |
|---|---|---|---|
| Python | 3.9+ | 3.9+ | 3.9+ |
| Install method | `brew install python` | [python.org](https://python.org/downloads) | `apt install python3` |
| AI (local) | Ollama | Ollama | Ollama |
| AI (cloud) | OpenAI / Anthropic key | OpenAI / Anthropic key | OpenAI / Anthropic key |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/manojbarot1/FileSage-AI-File-Manager.git
cd FileSage-AI-File-Manager
```

### 2. Install Ollama (recommended — fully local, free)

**macOS / Linux:**
```bash
# Download from https://ollama.ai  or via Homebrew:
brew install ollama

ollama pull gemma4    # recommended model
ollama serve          # start (auto-starts if you have the menu bar app)
```

**Windows:**
```
1. Download the installer from https://ollama.ai
2. Run OllamaSetup.exe — it installs and auto-starts
3. Open Command Prompt or PowerShell:
   ollama pull gemma4
```

### 3. Run FileSage

**macOS / Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```
Double-click run.bat
— or —
Open Command Prompt in the project folder and run:
  run.bat
```

The launcher auto-creates a virtual environment and installs all dependencies on first run.

---

## AI Provider Setup

### 🦙 Ollama (Local — Recommended)

No API key needed. Runs entirely on your machine. Files never leave your device.

**Recommended models for file organization:**

| Model | Pull Command | Size | Speed | Notes |
|---|---|---|---|---|
| **gemma4** ⭐ | `ollama pull gemma4` | ~5GB | ⚡ Fast | Best overall — great reasoning and JSON |
| `qwen2.5:7b` | `ollama pull qwen2.5:7b` | 4.7GB | ⚡ Fast | Excellent structured output |
| `llama3.2` | `ollama pull llama3.2` | 2GB | ⚡ Very fast | Lighter option, still solid |
| `llama3.1:8b` | `ollama pull llama3.1:8b` | 4.7GB | Medium | Very capable |
| `mistral` | `ollama pull mistral` | 4.1GB | ⚡ Fast | Good balance |

> **Recommended:** `gemma4` — as shown in the screenshot, it handles mixed file types and produces clear, descriptive folder suggestions.

---

### ✦ ChatGPT (OpenAI)

1. Get an API key at [platform.openai.com](https://platform.openai.com)
2. In FileSage → **AI Analysis** → select **ChatGPT**
3. Paste your `sk-proj-...` key → click **Test Connection**

**Supported models:** `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`

> **Cost estimate:** ~$0.01–0.05 per 100 files with `gpt-4o-mini`

---

### ◈ Claude (Anthropic)

1. Get an API key at [console.anthropic.com](https://console.anthropic.com)
2. In FileSage → **AI Analysis** → select **Claude**
3. Paste your `sk-ant-...` key → click **Test Connection**

**Supported models:** `claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5`

---

## How to Use

```
1. Launch FileSage  →  ./run.sh  (or run.bat on Windows)
         ↓
2. Dashboard → browse to a folder → "Quick Scan"
         ↓
3. FileSage indexes all files
   (reads names, parent folder, up to 200 chars of text content)
         ↓
4. AI Analysis → choose Ollama + gemma4 → "Run AI Analysis"
         ↓
5. Watch the live streaming log as AI processes files in batches of 20
         ↓
6. File Manager → review suggestions
   (green arrows show the AI-suggested new path + reason)
         ↓
7. Select files → "Preview Move" to dry-run with zero changes made
         ↓
8. "Move Selected" → confirm → done ✓
         ↓
9. Activity Log → full history, double-click any row → reveal in file browser
```

### Tips

- **Select specific files before analyzing** — the AI only processes your selection, saving time on large folders
- **Always Preview first** — zero files are touched until you confirm Move
- **Large folders** — files are processed in batches of 20; the live log shows each batch completing
- **Sessions persist** — close and reopen FileSage anytime, your analysis is still there
- **Gemma4 tip** — performs best when files have meaningful names or readable text content

---

## Build a Standalone Executable

**macOS — `.app` bundle:**
```bash
chmod +x build_mac.sh
./build_mac.sh
cp -r dist/FileSage.app /Applications/
```

**Windows — `.exe` (requires PyInstaller):**
```bat
pip install pyinstaller
pyinstaller --name FileSage --windowed --onedir --noconfirm main.py
:: Executable will be at dist\FileSage\FileSage.exe
```

**Linux — standalone binary:**
```bash
pip install pyinstaller
pyinstaller --name filesage --windowed --onedir --noconfirm main.py
# Binary at dist/filesage/filesage
```

---

## Project Structure

```
FileSage-AI-File-Manager/
├── main.py               # Full PyQt6 UI — 5 pages, sidebar navigation
├── core.py               # SQLite database, file scanner, move engine
├── workers.py            # Background QThreads (scan + AI streaming)
├── requirements.txt      # PyQt6, requests
├── run.sh                # Launcher for macOS / Linux
├── run.bat               # Launcher for Windows
├── build_mac.sh          # Builds FileSage.app via PyInstaller (macOS)
├── docs/
│   └── screenshot.png    # App screenshot
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions syntax check
├── .gitignore
├── LICENSE               # MIT
└── README.md
```

### Architecture

```
FileSage (PyQt6 — cross-platform native UI)
│
├── MainWindow
│   ├── Sidebar            — navigation + session list + progress bar
│   ├── DashboardPage      — stat cards, folder cards, sessions table
│   ├── FileManagerPage    — file list/grid, filters, select-all, move
│   ├── AIAnalysisPage     — provider cards, config, streaming log
│   ├── ActivityPage       — move history, reveal in file browser
│   └── SettingsPage       — storage path, cache, default folder
│
├── ScanWorker  (QThread)  — non-blocking file indexing
└── AnalyzeWorker (QThread)
    ├── Ollama    — /api/generate streaming (local)
    ├── OpenAI    — /v1/chat/completions SSE streaming
    └── Anthropic — /v1/messages SSE streaming

Storage: ~/.filesage/filesage.db  (SQLite, cross-platform)
```

---

## Data & Privacy

| Provider | What is sent | Where |
|---|---|---|
| **Ollama** | Nothing — 100% local | Your machine only |
| **ChatGPT** | File names, folder names, ≤200 chars of text per file | OpenAI API |
| **Claude** | File names, folder names, ≤200 chars of text per file | Anthropic API |

Full file contents are **never** sent. Only short previews are used for context.

---

## Troubleshooting

### macOS

```bash
# Font warning in terminal — harmless, filtered by run.sh
# SSL warning — harmless, suppressed automatically

# App won't start — check Python version
python3 --version        # need 3.9+
brew install python@3.11 # upgrade if needed
rm -rf .venv && ./run.sh # fresh install
```

```bash
# Ollama won't connect
ollama serve
curl http://localhost:11434/api/tags
ollama list
ollama pull gemma4
```

---

### Windows

```bat
:: Python not found — install from python.org
:: Make sure "Add Python to PATH" is checked during install

:: Verify Python is on PATH
python --version

:: Fresh install
rmdir /s /q .venv
run.bat

:: Ollama not connecting — make sure Ollama is running
:: Check system tray for the Ollama icon
:: Or open PowerShell and run: ollama serve
```

**Windows-specific notes:**
- Use `run.bat` — not `run.sh` (unless you have WSL or Git Bash)
- PyQt6 requires the [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) — install it if the app fails to start
- "Reveal in Explorer" opens the file's parent folder with the file selected

---

### Linux

```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv   # Ubuntu/Debian
sudo dnf install python3 python3-pip                # Fedora
sudo pacman -S python python-pip                    # Arch

# PyQt6 may need system Qt libraries on some distros
sudo apt install libgl1 libegl1                     # Ubuntu/Debian

# Run
chmod +x run.sh && ./run.sh

# Ollama on Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull gemma4
ollama serve
```

**Linux-specific notes:**
- "Reveal in Finder" opens the file's parent folder using `xdg-open`
- On headless servers, PyQt6 requires a display (use a desktop environment or Xvfb)
- Font rendering uses Ubuntu or DejaVu Sans automatically

---

### All Platforms

| Problem | Fix |
|---|---|
| `No module named PyQt6` | `rm -rf .venv` then re-run launcher |
| `TypeError: unexpected keyword argument` | All three files (`main.py`, `workers.py`, `core.py`) must be from the same version |
| Analysis returns no suggestions | Try with 5–10 selected files first; check the live log for errors |
| `gemma4` not found | `ollama pull gemma4` then restart Ollama |
| Build fails | Install PyInstaller: `pip install pyinstaller` |

---

## Contributing

Pull requests welcome. Please open an issue first for major changes.

```bash
git clone https://github.com/manojbarot1/FileSage-AI-File-Manager.git
cd FileSage-AI-File-Manager
./run.sh      # macOS / Linux
# run.bat     # Windows
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using [PyQt6](https://riverbankcomputing.com/software/pyqt/) · [Ollama](https://ollama.ai) · [Gemma4](https://ollama.com/library/gemma4) · [OpenAI](https://openai.com) · [Anthropic](https://anthropic.com)

**macOS · Windows · Linux**

</div>
