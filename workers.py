"""
FileSage Workers — QThread workers supporting Ollama, OpenAI, and Anthropic
"""
import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
import core


class ScanWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int)   # session_id, total_count
    error    = pyqtSignal(str)

    def __init__(self, folder: str):
        super().__init__()
        self.folder = folder

    def run(self):
        try:
            sid   = core.create_session(self.folder)
            count = core.scan_folder(self.folder, sid,
                                     progress_cb=lambda c: self.progress.emit(c))
            core.finish_session(sid, "scanned")
            self.finished.emit(sid, count)
        except Exception as e:
            self.error.emit(str(e))


class AnalyzeWorker(QThread):
    token      = pyqtSignal(str)
    batch_done = pyqtSignal(int, int, list)   # batch_num, total_batches, suggestions
    finished   = pyqtSignal()
    error      = pyqtSignal(str)
    log        = pyqtSignal(str, str)          # message, level (info/ok/err)

    def __init__(self, session_id: int, provider: str, model: str,
                 ollama_url: str = "http://localhost:11434",
                 api_key: str = "",
                 file_ids=None):
        super().__init__()
        self.session_id = session_id
        self.provider   = provider   # "ollama" | "openai" | "anthropic"
        self.model      = model
        self.ollama_url = ollama_url.rstrip("/")
        self.api_key    = api_key
        self.file_ids   = file_ids

    def run(self):
        try:
            session = core.get_session(self.session_id)
            files   = core.get_files(self.session_id)
            if self.file_ids:
                id_set = set(self.file_ids)
                files  = [f for f in files if f["id"] in id_set]
            files = [f for f in files if not f["moved"]]
            if not files:
                self.error.emit("No files to analyze.")
                return

            batch_size    = 20
            total         = len(files)
            total_batches = (total + batch_size - 1) // batch_size
            self.log.emit(f"Analyzing {total} files in {total_batches} batch(es) via {self.provider}", "info")

            for b_idx in range(total_batches):
                if self.isInterruptionRequested():
                    break
                batch = files[b_idx * batch_size: (b_idx + 1) * batch_size]
                self._process_batch(batch, b_idx + 1, total_batches, session["folder_path"])

            core.finish_session(self.session_id, "analyzed", self.model)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def _build_prompt(self, batch, base_dir):
        lines = "\n".join(
            f"ID:{f['id']} | File:{f['filename']} | Folder:{f['parent_folder']} | "
            f"Type:{core.file_category(f['extension'])} | Ext:{f['extension']} | "
            f"Preview:{(f['content_preview'] or '')[:200]}"
            for f in batch
        )
        return f"""You are an expert file organizer. Analyze these files and suggest a logical folder structure.

Base directory: {base_dir}

Files:
{lines}

Rules:
- Suggest relative subdirectory paths from the base directory
- Group by project, type, date, or topic — whichever makes most sense
- Use clear descriptive folder names, max 4 levels deep
- Code: group by project/language; Media: by type and year; Docs: by topic and year

Respond with ONLY a valid JSON array, no markdown fences, no explanation:
[{{"id": <number>, "suggested_path": "<relative/path>", "reason": "<brief reason>"}}, ...]"""

    def _parse_and_save(self, full_text, session_id):
        start = full_text.find("[")
        end   = full_text.rfind("]") + 1
        if start < 0 or end <= start:
            return []
        suggestions = json.loads(full_text[start:end])
        for s in suggestions:
            core.update_suggestion(s["id"], s.get("suggested_path", ""), s.get("reason", ""))
        return suggestions

    def _process_batch(self, batch, batch_num, total_batches, base_dir):
        prompt = self._build_prompt(batch, base_dir)
        try:
            full_text = ""
            if self.provider == "ollama":
                full_text = self._call_ollama(prompt)
            elif self.provider == "openai":
                full_text = self._call_openai(prompt)
            elif self.provider == "anthropic":
                full_text = self._call_anthropic(prompt)

            suggestions = self._parse_and_save(full_text, self.session_id)
            self.log.emit(
                f"✓ Batch {batch_num}/{total_batches} — {len(suggestions)} suggestions", "ok"
            )
            self.batch_done.emit(batch_num, total_batches, suggestions)
        except requests.exceptions.ConnectionError as e:
            msg = f"Batch {batch_num}: Connection error — {e}"
            self.log.emit(msg, "err")
            self.error.emit(msg)
        except requests.exceptions.HTTPError as e:
            msg = f"Batch {batch_num}: HTTP {e.response.status_code} — {e.response.text[:200]}"
            self.log.emit(msg, "err")
            self.error.emit(msg)
        except Exception as e:
            self.log.emit(f"Batch {batch_num} error: {e}", "err")

    # ── Ollama ──
    def _call_ollama(self, prompt) -> str:
        full = ""
        with requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": True},
            stream=True, timeout=180,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if self.isInterruptionRequested(): break
                if not line: continue
                try:
                    tok = json.loads(line).get("response", "")
                    full += tok
                    self.token.emit(tok)
                except Exception:
                    pass
        return full

    # ── OpenAI ──
    def _call_openai(self, prompt) -> str:
        full = ""
        with requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"},
            json={"model": self.model,
                  "messages": [{"role": "user", "content": prompt}],
                  "stream": True},
            stream=True, timeout=180,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if self.isInterruptionRequested(): break
                if not line: continue
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    text = text[6:]
                if text == "[DONE]": break
                try:
                    tok = json.loads(text)["choices"][0]["delta"].get("content", "")
                    full += tok
                    self.token.emit(tok)
                except Exception:
                    pass
        return full

    # ── Anthropic ──
    def _call_anthropic(self, prompt) -> str:
        full = ""
        with requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"},
            json={"model": self.model,
                  "max_tokens": 4096,
                  "messages": [{"role": "user", "content": prompt}],
                  "stream": True},
            stream=True, timeout=180,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if self.isInterruptionRequested(): break
                if not line: continue
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    try:
                        ev = json.loads(text[6:])
                        if ev.get("type") == "content_block_delta":
                            tok = ev["delta"].get("text", "")
                            full += tok
                            self.token.emit(tok)
                    except Exception:
                        pass
        return full
