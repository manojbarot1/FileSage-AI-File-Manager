<div align="center">

# ◈ FileSage

### AI-Powered File Intelligence for macOS

**Organize your files intelligently using local Ollama, ChatGPT, or Claude — all running natively on your Mac.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green?logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-12%2B-black?logo=apple&logoColor=white)](https://apple.com/macos)

![FileSage Screenshot](docs/screenshot.png)

*FileSage analyzing n8n HTML templates using Gemma4 on Ollama — 16 files, all analyzed and sorted*

</div>

---

## What is FileSage?

FileSage is a native macOS desktop application that uses AI to analyze your files and suggest intelligent folder structures. It reads file names, content previews, and folder context — then recommends where each file should live. You review the suggestions, select what to move, and FileSage does the rest.

**Everything runs locally.** When using Ollama, no file data ever leaves your Mac.

---

## Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | Overview of all sessions, folder stats, file counts, storage usage |
| 📁 **File Manager** | List & grid view, filter by status, select all, bulk move |
| 🤖 **AI Analysis** | Streaming real-time analysis with live progress log |
| 🕐 **Activity Log** | Full history of every file moved, with Reveal in Finder |
| ⚙️ **Settings** | Default folder, database location, cache management |
| 🦙 **Multi-Provider** | Ollama (local), ChatGPT (OpenAI), Claude (Anthropic) |
| 💾 **Persistent Cache** | Sessions remembered across launches via SQLite |
| 👁 **Preview Mode** | See exactly what will move before committing |
| ↺ **Safe by Default** | Files only move when you explicitly confirm |

---

## Requirements

| Requirement | Details |
|---|---|
| macOS | 12 Monterey or later |
| Python | 3.9+ (3.11+ recommended) |
| AI Provider | One of: Ollama (local), OpenAI API key, or Anthropic API key |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/filesage.git
cd filesage
```

### 2. Install Ollama (recommended — fully local, free)

```bash
# Install from https://ollama.ai  or via Homebrew:
brew install ollama

# Pull Gemma4 — recommended for FileSage:
ollama pull gemma4

# Start Ollama (launches automatically if you have the menu bar app):
ollama serve
```

### 3. Run FileSage

```bash
chmod +x run.sh
./run.sh
```

That's it. The script auto-creates a virtual environment and installs all dependencies on first run.

---

## AI Provider Setup

### 🦙 Ollama (Local — Recommended)

No API key needed. Runs entirely on your Mac. Your files never leave your machine.

1. Install Ollama: [ollama.ai](https://ollama.ai)
2. Pull a model (see table below)
3. In FileSage → **AI Analysis** → select **Ollama** → click **Connect**

**Recommended models for file organization:**

| Model | Pull Command | Size | Speed | Notes |
|---|---|---|---|---|
| **gemma4** ⭐ | `ollama pull gemma4` | ~5GB | ⚡ Fast | Best overall — great reasoning and JSON output |
| `qwen2.5:7b` | `ollama pull qwen2.5:7b` | 4.7GB | ⚡ Fast | Excellent structured output |
| `llama3.2` | `ollama pull llama3.2` | 2GB | ⚡ Very fast | Lighter option, still solid |
| `llama3.1:8b` | `ollama pull llama3.1:8b` | 4.7GB | Medium | Very capable |
| `mistral` | `ollama pull mistral` | 4.1GB | ⚡ Fast | Good balance |

> **Recommended:** `gemma4` — as shown in the screenshot, it handles mixed file types and produces clear, descriptive folder suggestions.

```bash
# Quick setup:
ollama pull gemma4
ollama serve
```

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

### Step-by-step workflow

```
1. Launch FileSage  →  ./run.sh
         ↓
2. Dashboard → type or browse to a folder → "Quick Scan"
         ↓
3. FileSage indexes all files
   (reads names, parent folder, up to 200 chars of text content)
         ↓
4. AI Analysis → choose Ollama + gemma4 → "Run AI Analysis"
         ↓
5. Watch the live streaming log as AI processes files in batches of 20
         ↓
6. File Manager → review suggestions
   (green → arrows show the AI-suggested new path + reason)
         ↓
7. Select files → "Preview Move" to dry-run with no changes
         ↓
8. "Move Selected" → confirm → done ✓
         ↓
9. Activity Log → full history, double-click any row → Reveal in Finder
```

### Tips

- **Select specific files before analyzing** — the AI only processes your selection, saving time on large folders
- **Always Preview first** — "Preview Move" shows a complete dry run; zero files are touched
- **Large folders** — files are processed in batches of 20; the live log shows each batch completing
- **Sessions persist** — close and reopen FileSage anytime, your analysis is still there
- **Multiple sessions** — scan different folders independently and switch between them in the sidebar
- **Gemma4 tip** — it performs best when files have meaningful names or readable content

---

## Build a Standalone .app

Create a proper macOS `.app` bundle that anyone can run without Python:

```bash
chmod +x build_mac.sh
./build_mac.sh

# Install to Applications:
cp -r dist/FileSage.app /Applications/
open /Applications/FileSage.app
```

---

## Project Structure

```
filesage/
├── main.py               # Full PyQt6 UI — 5 pages, sidebar navigation
├── core.py               # SQLite database, file scanner, move engine
├── workers.py            # Background QThreads (scan + AI streaming)
├── requirements.txt      # PyQt6, requests
├── run.sh                # One-command launcher with auto venv setup
├── build_mac.sh          # Builds FileSage.app via PyInstaller
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
FileSage (PyQt6 native macOS app)
│
├── MainWindow
│   ├── Sidebar            — navigation + session list + progress bar
│   ├── DashboardPage      — stat cards, folder cards, sessions table
│   ├── FileManagerPage    — file list/grid, filters, select-all, move
│   ├── AIAnalysisPage     — provider cards, config, streaming log
│   ├── ActivityPage       — move history table, Reveal in Finder
│   └── SettingsPage       — storage path, cache, default folder
│
├── ScanWorker  (QThread)
│   └── Walks directory tree → reads previews → writes to SQLite
│
└── AnalyzeWorker  (QThread)
    ├── Ollama    — POST /api/generate  (streaming, local, private)
    ├── OpenAI    — POST /v1/chat/completions  (SSE streaming)
    └── Anthropic — POST /v1/messages  (SSE streaming)

Persistent storage: ~/.filesage/filesage.db  (SQLite)
```

---

## Data & Privacy

| Provider | What is sent | Where |
|---|---|---|
| **Ollama** | Nothing — runs 100% locally | Your Mac only |
| **ChatGPT** | File names, folder names, ≤200 chars of text content per file | OpenAI API |
| **Claude** | File names, folder names, ≤200 chars of text content per file | Anthropic API |

**Full file contents are never sent.** Only short previews are used for context.

The local cache (`~/.filesage/filesage.db`) stores session data, file paths, and AI suggestions. Clear it anytime from **Settings → Clear All Data**.

---

## Troubleshooting

### App won't launch

```bash
# Check Python version (need 3.9+)
python3 --version

# Install newer Python via Homebrew
brew install python@3.11

# Delete venv and retry
rm -rf .venv && ./run.sh
```

### Ollama won't connect

```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags

# Check models are installed
ollama list

# Pull gemma4 if missing
ollama pull gemma4
```

### Analysis returns no suggestions

- Make sure the model is fully downloaded (`ollama list` should show it)
- Try a smaller batch: select 5–10 files manually and analyze just those
- Check the live log in AI Analysis for error messages
- `gemma4` and `qwen2.5:7b` are the most reliable at producing valid JSON

### "No module named PyQt6"

```bash
rm -rf .venv && ./run.sh
```

### TypeError / unexpected keyword argument

You likely have a mix of old and new files. Re-download all files from the repo and replace them together — `main.py`, `workers.py`, and `core.py` must all be from the same version.

### Font warnings in terminal (`Populating font family aliases`)

Harmless — Qt builds its font cache on first launch. The warning is automatically filtered by `run.sh`.

### urllib3 SSL warning

Harmless — Python 3.9 on older macOS uses LibreSSL. Automatically suppressed by `run.sh` and the warning filter in `main.py`.

### Build fails (`build_mac.sh`)

```bash
# Install Xcode command line tools first
xcode-select --install

# Then retry
./build_mac.sh
```

---

## Contributing

Pull requests welcome! Please open an issue first for major changes.

```bash
git clone https://github.com/YOUR_USERNAME/filesage.git
cd filesage
./run.sh    # runs directly from source, no build step needed
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using [PyQt6](https://riverbankcomputing.com/software/pyqt/) · [Ollama](https://ollama.ai) · [Gemma4](https://ollama.com/library/gemma4) · [OpenAI](https://openai.com) · [Anthropic](https://anthropic.com)

</div>
