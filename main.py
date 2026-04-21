"""
FileSage — Enterprise AI File Manager
Complete multi-page native macOS application
"""
import warnings
# Suppress urllib3 LibreSSL warning (harmless on older macOS)
warnings.filterwarnings("ignore", message=".*LibreSSL.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys, os, math, platform
from datetime import datetime
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QComboBox, QCheckBox,
    QListWidget, QListWidgetItem, QFileDialog, QProgressBar, QTextEdit,
    QMessageBox, QStackedWidget, QDialog, QDialogButtonBox, QStatusBar,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QButtonGroup, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon

import core
from workers import ScanWorker, AnalyzeWorker

# ── Enterprise Palette ─────────────────────────────────────────────────────────
C = {
    "bg":           "#07071a",
    "surface":      "#0d0d26",
    "card":         "#12122e",
    "card2":        "#17173a",
    "card_hover":   "#1c1c44",
    "border":       "#1e1e42",
    "border2":      "#2a2a58",

    "primary":      "#6366f1",
    "primary_hi":   "#818cf8",
    "primary_dim":  "#2d2b6e",
    "primary_glow": "rgba(99,102,241,0.12)",

    "violet":       "#8b5cf6",
    "violet_hi":    "#a78bfa",
    "violet_dim":   "#3b1f8c",

    "green":        "#10b981",
    "green_hi":     "#34d399",
    "green_dim":    "#064e35",

    "amber":        "#f59e0b",
    "amber_hi":     "#fbbf24",
    "amber_dim":    "#78350f",

    "red":          "#ef4444",
    "red_dim":      "#7f1d1d",

    "blue":         "#3b82f6",
    "blue_dim":     "#1e3a8a",

    "cyan":         "#06b6d4",

    "folder_a":     "#f97316",
    "folder_b":     "#6366f1",
    "folder_c":     "#10b981",
    "folder_d":     "#8b5cf6",

    "text":         "#e2e8f0",
    "text2":        "#94a3b8",
    "text3":        "#334155",
    "muted":        "#64748b",
    "white":        "#ffffff",
}

FOLDER_COLORS = [C["folder_a"], C["folder_b"], C["folder_c"], C["folder_d"],
                 "#ec4899", "#06b6d4", "#84cc16", "#f59e0b"]

STYLE = f"""
QMainWindow {{ background:{C['bg']}; }}
QWidget     {{ background:{C['bg']}; color:{C['text']};
               font-family:"Helvetica Neue","Segoe UI","Ubuntu","Arial",sans-serif;
               font-size:13px; }}

/* ── Sidebar ── */
#sidebar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #110d2e, stop:0.5 #0d0d24, stop:1 {C['bg']});
    border-right:1px solid {C['border']};
}}

/* ── Top bar ── */
#topbar {{
    background:{C['surface']};
    border-bottom:1px solid {C['border']};
}}

/* ── Page background ── */
#page {{ background:{C['bg']}; }}

/* ── Cards ── */
#card {{
    background:{C['card']};
    border:1px solid {C['border']};
    border-radius:10px;
}}
#card:hover {{
    background:{C['card2']};
    border-color:{C['border2']};
}}

/* ── Inputs ── */
QLineEdit {{
    background:{C['card2']}; border:1px solid {C['border2']};
    border-radius:7px; padding:7px 12px;
    color:{C['text']}; font-size:13px;
    selection-background-color:{C['primary_dim']};
}}
QLineEdit:focus {{ border-color:{C['primary']}; }}
QLineEdit::placeholder {{ color:{C['text3']}; }}

/* ── Combo ── */
QComboBox {{
    background:{C['card2']}; border:1px solid {C['border2']};
    border-radius:7px; padding:7px 12px;
    color:{C['text']}; font-size:13px; min-height:20px;
}}
QComboBox:focus {{ border-color:{C['primary']}; }}
QComboBox::drop-down {{ border:none; width:24px; }}
QComboBox::down-arrow {{
    border-left:4px solid transparent; border-right:4px solid transparent;
    border-top:5px solid {C['muted']}; margin-right:8px;
}}
QComboBox QAbstractItemView {{
    background:{C['card2']}; border:1px solid {C['border2']};
    selection-background-color:{C['primary_dim']};
    color:{C['text']}; padding:4px; outline:none;
}}

/* ── Buttons — base ── */
QPushButton {{
    background:{C['card2']}; border:1px solid {C['border2']};
    border-radius:7px; padding:8px 16px;
    color:{C['text2']}; font-size:13px; font-weight:500;
}}
QPushButton:hover  {{ background:{C['card_hover']}; border-color:{C['border2']}; color:{C['text']}; }}
QPushButton:pressed {{ background:{C['card']}; }}
QPushButton:disabled {{ color:{C['text3']}; border-color:{C['border']}; }}

/* Primary */
QPushButton#btn_primary {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {C['primary_hi']},stop:1 {C['primary']});
    border:1px solid {C['primary']}; border-bottom:2px solid #3730a3;
    color:{C['white']}; font-weight:700;
}}
QPushButton#btn_primary:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #a5b4fc,stop:1 {C['primary_hi']});
}}
QPushButton#btn_primary:disabled {{
    background:{C['primary_dim']}; border-color:{C['primary_dim']}; color:{C['text3']};
}}

/* Accent violet */
QPushButton#btn_accent {{
    background:{C['primary_glow']}; border:1px solid {C['primary_dim']};
    border-bottom:2px solid #1e1b4b; color:{C['primary_hi']}; font-weight:600;
}}
QPushButton#btn_accent:hover {{
    background:rgba(99,102,241,0.2); border-color:{C['primary']};
}}
QPushButton#btn_accent:disabled {{
    background:transparent; border-color:{C['border']}; color:{C['text3']};
}}

/* Green */
QPushButton#btn_green {{
    background:rgba(16,185,129,0.08); border:1px solid {C['green_dim']};
    border-bottom:2px solid #022c22; color:{C['green']}; font-weight:600;
}}
QPushButton#btn_green:hover {{
    background:rgba(16,185,129,0.18); border-color:{C['green']};
}}
QPushButton#btn_green:disabled {{
    background:transparent; border-color:{C['border']}; color:{C['text3']};
}}

/* Danger */
QPushButton#btn_danger {{
    background:rgba(239,68,68,0.07); border:1px solid {C['red_dim']};
    border-bottom:2px solid #450a0a; color:{C['red']};
}}
QPushButton#btn_danger:hover {{ background:rgba(239,68,68,0.16); border-color:{C['red']}; }}

/* Ghost (outline) */
QPushButton#btn_ghost {{
    background:transparent; border:1px solid {C['border2']};
    border-radius:7px; color:{C['text2']};
}}
QPushButton#btn_ghost:hover {{ border-color:{C['primary']}; color:{C['primary_hi']}; }}

/* Nav buttons */
QPushButton#nav_btn {{
    background:transparent; border:none; border-radius:8px;
    padding:9px 14px; color:{C['muted']};
    font-size:13px; font-weight:500; text-align:left;
}}
QPushButton#nav_btn:hover {{ background:rgba(255,255,255,0.05); color:{C['text']}; }}
QPushButton#nav_btn:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(99,102,241,0.25), stop:1 rgba(99,102,241,0.05));
    border-left:2px solid {C['primary']};
    color:{C['primary_hi']}; font-weight:600;
}}

/* Small utility */
QPushButton#btn_sm {{
    background:{C['card2']}; border:1px solid {C['border']};
    border-radius:6px; padding:5px 12px;
    color:{C['text2']}; font-size:12px;
}}
QPushButton#btn_sm:hover {{ border-color:{C['border2']}; color:{C['text']}; }}
QPushButton#btn_sm:checked {{
    background:{C['primary_glow']}; border-color:{C['primary_dim']};
    color:{C['primary_hi']}; font-weight:600;
}}

/* ── Table ── */
QTableWidget {{
    background:{C['card']}; border:none; gridline-color:{C['border']};
    border-radius:8px; outline:none;
}}
QTableWidget::item {{ padding:8px 12px; border-bottom:1px solid {C['border']}; color:{C['text2']}; }}
QTableWidget::item:selected {{ background:{C['primary_glow']}; color:{C['primary_hi']}; }}
QTableWidget::item:hover {{ background:{C['card2']}; color:{C['text']}; }}
QHeaderView::section {{
    background:{C['card2']}; border:none; border-bottom:1px solid {C['border']};
    padding:8px 12px; color:{C['muted']}; font-size:11px;
    font-weight:700; letter-spacing:0.8px; text-transform:uppercase;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{ background:transparent; width:5px; margin:0; }}
QScrollBar::handle:vertical {{ background:{C['border2']}; border-radius:3px; min-height:24px; }}
QScrollBar::handle:vertical:hover {{ background:{C['muted']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{ background:transparent; height:5px; }}
QScrollBar::handle:horizontal {{ background:{C['border2']}; border-radius:3px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}

/* ── Progress ── */
QProgressBar {{
    background:{C['border']}; border:none; border-radius:4px; height:6px;
}}
QProgressBar::chunk {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C['primary']}, stop:1 {C['violet']});
    border-radius:4px;
}}

/* ── TextEdit ── */
QTextEdit {{
    background:{C['bg']}; border:1px solid {C['border']}; border-radius:8px;
    color:{C['text2']}; font-family:"Menlo","Consolas","DejaVu Sans Mono","Courier New",monospace;
    font-size:11px; padding:8px;
}}

/* ── Status bar ── */
QStatusBar {{
    background:{C['surface']}; border-top:1px solid {C['border']};
    color:{C['text3']}; font-size:11px; padding:0 12px;
}}

/* ── Checkbox ── */
QCheckBox {{ spacing:7px; color:{C['text2']}; }}
QCheckBox::indicator {{
    width:15px; height:15px; border-radius:4px;
    border:1.5px solid {C['border2']}; background:{C['card2']};
}}
QCheckBox::indicator:checked {{ background:{C['primary']}; border-color:{C['primary']}; }}
QCheckBox::indicator:hover {{ border-color:{C['primary']}; }}

/* ── ToolTip ── */
QToolTip {{
    background:{C['card2']}; border:1px solid {C['border2']};
    color:{C['text']}; font-size:12px; padding:5px 9px; border-radius:6px;
}}

/* ── ListWidget ── */
QListWidget {{ background:transparent; border:none; outline:none; }}
QListWidget::item {{
    background:{C['card']}; border:1px solid {C['border']};
    border-radius:6px; margin:2px 4px; padding:8px 10px; color:{C['text2']};
}}
QListWidget::item:selected {{
    background:{C['primary_glow']}; border-color:{C['primary_dim']}; color:{C['primary_hi']};
}}
QListWidget::item:hover:!selected {{
    background:{C['card2']}; border-color:{C['border2']}; color:{C['text']};
}}
"""

# ── Constants ──────────────────────────────────────────────────────────────────
OPENAI_MODELS    = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
ANTHROPIC_MODELS = ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5",
                    "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class Div(QFrame):
    """Horizontal divider line."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{C['border']}; border:none;")


class StatCard(QFrame):
    def __init__(self, icon, label, value="—", sub="", color=None, parent=None):
        super().__init__(parent)
        color = color or C["primary"]
        self.setObjectName("card")
        self.setMinimumHeight(100)
        lo = QVBoxLayout(self); lo.setContentsMargins(18,16,18,16); lo.setSpacing(6)

        top = QHBoxLayout(); top.setSpacing(10)
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            f"background:{color}22; color:{color}; font-size:18px;"
            f"border-radius:9px; border:1px solid {color}44;"
        )
        top.addWidget(icon_lbl)
        top.addStretch()
        lo.addLayout(top)

        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(
            f"font-size:26px; font-weight:800; color:{C['white']}; background:transparent;"
        )
        lo.addWidget(self.val_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size:12px; font-weight:600; color:{C['text2']}; background:transparent;")
        lo.addWidget(lbl)

        if sub:
            self.sub_lbl = QLabel(sub)
            self.sub_lbl.setStyleSheet(f"font-size:11px; color:{C['text3']}; background:transparent;")
            lo.addWidget(self.sub_lbl)
        else:
            self.sub_lbl = None

    def update_value(self, v, sub=None):
        self.val_lbl.setText(str(v))
        if sub and self.sub_lbl: self.sub_lbl.setText(sub)


class FolderCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, data: Dict, color: str, parent=None):
        super().__init__(parent)
        self.folder_name = data.get("parent_folder") or "(root)"
        self.setObjectName("card")
        self.setFixedHeight(190)
        self.setMinimumWidth(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(data, color)

    def _build(self, d, color):
        lo = QVBoxLayout(self); lo.setContentsMargins(16,16,16,14); lo.setSpacing(8)

        # Icon
        icon_wrap = QWidget(); icon_wrap.setStyleSheet("background:transparent;")
        iw = QHBoxLayout(icon_wrap); iw.setContentsMargins(0,0,0,0)
        icon = QLabel("🗂")
        icon.setFixedSize(52, 52)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {color}cc,stop:1 {color}88);"
            f"border:1px solid {color}55; border-radius:14px; font-size:26px;"
        )
        iw.addWidget(icon); iw.addStretch()

        # File count badge
        cnt = QLabel(str(d.get("file_count", 0)))
        cnt.setStyleSheet(
            f"background:{color}22; color:{color}; font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace;"
            f"font-size:10px; font-weight:700; border:1px solid {color}44;"
            f"border-radius:10px; padding:1px 7px;"
        )
        cnt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        iw.addWidget(cnt)
        lo.addWidget(icon_wrap)

        # Name
        name = QLabel(self.folder_name)
        name.setStyleSheet(
            f"font-size:13px; font-weight:700; color:{C['white']}; background:transparent;"
        )
        name.setWordWrap(False)
        fm = name.fontMetrics()
        name.setText(fm.elidedText(self.folder_name, Qt.TextElideMode.ElideRight, 160))
        lo.addWidget(name)

        # Size
        size = QLabel(core.fmt_size(d.get("total_size") or 0))
        size.setStyleSheet(f"font-size:12px; color:{C['text2']}; background:transparent;")
        lo.addWidget(size)

        lo.addStretch()

        # Bottom stats bar
        bottom = QHBoxLayout(); bottom.setSpacing(6)
        analyzed = d.get("analyzed", 0) or 0
        total    = d.get("file_count", 1) or 1
        pct = int(analyzed / total * 100)

        bar = QProgressBar()
        bar.setRange(0, 100); bar.setValue(pct); bar.setFixedHeight(3)
        bar.setTextVisible(False)
        bar.setStyleSheet(f"""
            QProgressBar {{ background:{C['border']}; border:none; border-radius:2px; }}
            QProgressBar::chunk {{ background:{color}; border-radius:2px; }}
        """)
        lo.addWidget(bar)

        pct_lbl = QLabel(f"{pct}% analyzed")
        pct_lbl.setStyleSheet(f"font-size:10px; color:{C['text3']}; background:transparent;")
        bottom.addWidget(pct_lbl)

        moved = d.get("moved", 0) or 0
        if moved:
            mv = QLabel(f"✓ {moved} moved")
            mv.setStyleSheet(f"font-size:10px; color:{C['green']}; background:transparent;")
            bottom.addWidget(mv)
        bottom.addStretch()
        lo.addLayout(bottom)

    def mousePressEvent(self, _): self.clicked.emit(self.folder_name)


class FileRowWidget(QFrame):
    """Compact file row for list view."""
    toggled = pyqtSignal(int, bool)

    def __init__(self, f: Dict, parent=None):
        super().__init__(parent)
        self.fid = f["id"]
        self.file_data = f
        self.setObjectName("card")
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(False)
        self._build(f)

    def _build(self, f):
        lo = QHBoxLayout(self); lo.setContentsMargins(10,0,12,0); lo.setSpacing(10)

        self.checkbox = QCheckBox(); self.checkbox.setFixedSize(16,16)
        if f.get("moved"): self.checkbox.setEnabled(False)
        self.checkbox.stateChanged.connect(self._toggle)
        lo.addWidget(self.checkbox)

        icon = QLabel(core.file_icon(f.get("extension","")))
        icon.setStyleSheet("font-size:16px; background:transparent;"); icon.setFixedWidth(20)
        lo.addWidget(icon)

        # Info
        info = QVBoxLayout(); info.setSpacing(1); info.setContentsMargins(0,0,0,0)
        n = QLabel(f.get("filename",""))
        n.setStyleSheet(f"font-weight:600; color:{C['text']}; background:transparent; font-size:12.5px;")
        info.addWidget(n)
        p = QLabel(f"…/{f.get('parent_folder','')}/")
        p.setStyleSheet(f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:10px; color:{C['text3']}; background:transparent;")
        info.addWidget(p)
        lo.addLayout(info, 1)

        # Suggestion
        if f.get("ai_suggested_path") and not f.get("moved"):
            sg = QHBoxLayout(); sg.setSpacing(4); sg.setContentsMargins(0,0,0,0)
            arr = QLabel("→")
            arr.setStyleSheet(f"color:{C['green']}; font-weight:700; font-size:11px; background:transparent;")
            sg.addWidget(arr)
            sp = QLabel(f.get("ai_suggested_path",""))
            sp.setStyleSheet(
                f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:10.5px;"
                f"color:{C['green']}; background:transparent;"
            )
            sg.addWidget(sp)
            if f.get("ai_reason"):
                rs = QLabel(f"— {f['ai_reason']}")
                rs.setStyleSheet(f"font-size:10px; color:{C['text3']}; font-style:italic; background:transparent;")
                sg.addWidget(rs)
            sg.addStretch()
            lo.addLayout(sg, 2)

        # Right
        right = QVBoxLayout(); right.setSpacing(3); right.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        sz = QLabel(core.fmt_size(f.get("size_bytes",0)))
        sz.setStyleSheet(f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:10px; color:{C['muted']}; background:transparent;")
        right.addWidget(sz, 0, Qt.AlignmentFlag.AlignRight)
        if f.get("moved"):
            b = self._badge("moved", C["green"], C["green_dim"])
        elif f.get("ai_suggested_path"):
            b = self._badge("sorted", C["primary_hi"], C["primary_dim"])
        else:
            b = self._badge("unsorted", C["muted"], C["card2"])
        right.addWidget(b, 0, Qt.AlignmentFlag.AlignRight)
        lo.addLayout(right)
        if f.get("moved"): self.setEnabled(False)

    def _badge(self, t, fg, bg):
        l = QLabel(t); l.setStyleSheet(
            f"font-size:9px; color:{fg}; background:{bg}; border:1px solid {fg}44;"
            f"border-radius:8px; padding:1px 7px;"
        )
        return l

    def _apply_style(self, sel):
        if sel:
            self.setStyleSheet(f"QFrame#card{{background:{C['primary_glow']};border:1px solid {C['primary_dim']};border-radius:8px;margin:1px 0;}}")
        else:
            self.setStyleSheet(f"QFrame#card{{background:{C['card']};border:1px solid {C['border']};border-radius:8px;margin:1px 0;}}QFrame#card:hover{{background:{C['card2']};border-color:{C['border2']};}}")

    def _toggle(self, s):
        self._apply_style(s == Qt.CheckState.Checked.value)
        self.toggled.emit(self.fid, s == Qt.CheckState.Checked.value)

    def mousePressEvent(self, _):
        if not self.file_data.get("moved"): self.checkbox.setChecked(not self.checkbox.isChecked())

    def set_checked(self, v):
        if not self.file_data.get("moved"): self.checkbox.setChecked(v)

    def is_checked(self): return self.checkbox.isChecked()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    scan_requested    = pyqtSignal(str)
    session_selected  = pyqtSignal(int)
    goto_files        = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("page"); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Scroll wrapper
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none; background:{C['bg']};}}")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget(); inner.setStyleSheet(f"background:{C['bg']};")
        vb = QVBoxLayout(inner); vb.setContentsMargins(28,28,28,28); vb.setSpacing(24)

        # ── Header ──
        hdr = QHBoxLayout(); hdr.setSpacing(12)
        left = QVBoxLayout(); left.setSpacing(2)
        now = datetime.now()
        h = now.hour
        greet = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
        g = QLabel(f"{greet} ✦")
        g.setStyleSheet(f"font-size:22px; font-weight:800; color:{C['white']}; background:transparent;")
        left.addWidget(g)
        s = QLabel("AI-powered file intelligence · organize smarter")
        s.setStyleSheet(f"font-size:13px; color:{C['text2']}; background:transparent;")
        left.addWidget(s)
        hdr.addLayout(left); hdr.addStretch()

        # Quick scan
        self.quick_path = QLineEdit(); self.quick_path.setFixedWidth(300)
        self.quick_path.setPlaceholderText("Drop a folder path to scan…")
        hdr.addWidget(self.quick_path)
        scan_btn = QPushButton("⌕  Quick Scan"); scan_btn.setObjectName("btn_primary")
        scan_btn.clicked.connect(lambda: self.scan_requested.emit(self.quick_path.text().strip()))
        hdr.addWidget(scan_btn)
        browse_btn = QPushButton("…"); browse_btn.setObjectName("btn_ghost")
        browse_btn.setFixedWidth(36)
        browse_btn.clicked.connect(self._browse)
        hdr.addWidget(browse_btn)
        vb.addLayout(hdr)

        # ── Stats row ──
        self.stat_files    = StatCard("📄", "Total Files",    "0", color=C["primary"])
        self.stat_analyzed = StatCard("🤖", "AI Analyzed",    "0", color=C["violet"])
        self.stat_moved    = StatCard("📦", "Files Moved",    "0", color=C["green"])
        self.stat_sessions = StatCard("🗂", "Sessions",       "0", color=C["amber"])
        self.stat_size     = StatCard("💾", "Total Size",     "0 B", color=C["cyan"])

        stats_row = QHBoxLayout(); stats_row.setSpacing(14)
        for s in [self.stat_files, self.stat_analyzed, self.stat_moved,
                  self.stat_sessions, self.stat_size]:
            stats_row.addWidget(s, 1)
        vb.addLayout(stats_row)

        # ── Folder overview ──
        fhdr = QHBoxLayout()
        fl = QLabel("Folder Overview"); fl.setStyleSheet(
            f"font-size:16px; font-weight:700; color:{C['white']}; background:transparent;"
        )
        fhdr.addWidget(fl); fhdr.addStretch()
        self.session_combo = QComboBox(); self.session_combo.setFixedWidth(260)
        self.session_combo.currentIndexChanged.connect(self._on_session_change)
        fhdr.addWidget(self.session_combo)
        view_files_btn = QPushButton("View Files →"); view_files_btn.setObjectName("btn_sm")
        view_files_btn.clicked.connect(self.goto_files.emit)
        fhdr.addWidget(view_files_btn)
        vb.addLayout(fhdr)

        # Folder grid
        self.folder_scroll = QScrollArea(); self.folder_scroll.setWidgetResizable(True)
        self.folder_scroll.setFixedHeight(220)
        self.folder_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.folder_scroll.setStyleSheet(f"QScrollArea{{border:none; background:transparent;}}")
        self.folder_container = QWidget(); self.folder_container.setStyleSheet("background:transparent;")
        self.folder_layout = QHBoxLayout(self.folder_container)
        self.folder_layout.setContentsMargins(0,0,0,0); self.folder_layout.setSpacing(14)
        self.folder_layout.addStretch()
        self.folder_scroll.setWidget(self.folder_container)
        self.folder_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        vb.addWidget(self.folder_scroll)

        # ── Recent Sessions ──
        rl = QLabel("Recent Sessions")
        rl.setStyleSheet(f"font-size:16px; font-weight:700; color:{C['white']}; background:transparent;")
        vb.addWidget(rl)

        self.sessions_table = QTableWidget(0, 5)
        self.sessions_table.setHorizontalHeaderLabels(["Folder", "Files", "Analyzed", "Status", "Date"])
        self.sessions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5): self.sessions_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.sessions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sessions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sessions_table.setShowGrid(False)
        self.sessions_table.verticalHeader().setVisible(False)
        self.sessions_table.setAlternatingRowColors(False)
        self.sessions_table.setFixedHeight(250)
        self.sessions_table.cellDoubleClicked.connect(self._on_table_double_click)
        vb.addWidget(self.sessions_table)
        vb.addStretch()

        scroll.setWidget(inner); root.addWidget(scroll)

    def _browse(self):
        p = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if p: self.quick_path.setText(p)

    def _on_session_change(self, idx):
        sid = self.session_combo.itemData(idx)
        if sid: self._load_folders(sid)

    def _on_table_double_click(self, row, _):
        item = self.sessions_table.item(row, 0)
        if item:
            sid = item.data(Qt.ItemDataRole.UserRole)
            if sid: self.session_selected.emit(sid)

    def refresh(self, active_sid=None):
        stats = core.get_stats()
        self.stat_files.update_value(f"{stats['total']:,}")
        self.stat_analyzed.update_value(f"{stats['analyzed']:,}")
        self.stat_moved.update_value(f"{stats['moved']:,}")
        self.stat_sessions.update_value(str(stats['sessions']))
        self.stat_size.update_value(core.fmt_size(stats['size']))

        sessions = core.get_sessions()

        # Session combo
        self.session_combo.blockSignals(True)
        self.session_combo.clear()
        for s in sessions:
            label = f"{os.path.basename(s['folder_path'])} ({s['file_count'] or 0} files)"
            self.session_combo.addItem(label, s["id"])
        self.session_combo.blockSignals(False)

        # Table
        self.sessions_table.setRowCount(0)
        for s in sessions:
            row = self.sessions_table.rowCount()
            self.sessions_table.insertRow(row)
            path_item = QTableWidgetItem(s["folder_path"])
            path_item.setData(Qt.ItemDataRole.UserRole, s["id"])
            path_item.setForeground(QColor(C["text"]))
            self.sessions_table.setItem(row, 0, path_item)
            for col, val in enumerate([
                str(s["file_count"] or 0),
                str(s["analyzed_count"] or 0),
                s["status"],
                (s.get("created_at") or "")[:16],
            ], 1):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(C["text2"]))
                if col == 3:
                    colors = {"analyzed": C["green"], "scanned": C["amber"], "scanning": C["primary"]}
                    it.setForeground(QColor(colors.get(val, C["muted"])))
                self.sessions_table.setItem(row, col, it)
            self.sessions_table.setRowHeight(row, 44)

        # Folders for latest session
        sid = active_sid or (sessions[0]["id"] if sessions else None)
        if sid:
            idx = next((i for i in range(self.session_combo.count()) if self.session_combo.itemData(i) == sid), 0)
            self.session_combo.setCurrentIndex(idx)
            self._load_folders(sid)

    def _load_folders(self, sid):
        while self.folder_layout.count() > 1:
            item = self.folder_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        groups = core.get_folder_groups(sid)
        if not groups:
            lbl = QLabel("No files scanned yet")
            lbl.setStyleSheet(f"color:{C['text3']}; padding:40px; background:transparent;")
            self.folder_layout.insertWidget(0, lbl)
            return
        for i, g in enumerate(groups[:12]):
            card = FolderCard(g, FOLDER_COLORS[i % len(FOLDER_COLORS)])
            card.setFixedWidth(190)
            self.folder_layout.insertWidget(i, card)


# ── FileManagerPage ────────────────────────────────────────────────────────────
class FileManagerPage(QWidget):
    move_requested = pyqtSignal(list, bool)

    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("page")
        self.current_files: List[Dict] = []
        self.session_id: Optional[int] = None
        self._filter = "all"
        self._view   = "list"    # "list" | "grid"
        self._cards: List[FileRowWidget] = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.stack = QStackedWidget()

        # ── Empty state ──
        empty = QWidget(); el = QVBoxLayout(empty)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter); el.setSpacing(12)
        eg = QLabel("🗂"); eg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eg.setStyleSheet(f"font-size:60px; background:transparent;")
        el.addWidget(eg)
        et = QLabel("No session loaded"); et.setAlignment(Qt.AlignmentFlag.AlignCenter)
        et.setStyleSheet(f"font-size:18px; font-weight:700; color:{C['border2']}; background:transparent;")
        el.addWidget(et)
        es = QLabel("Go to Dashboard → scan a folder → come back here.")
        es.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es.setStyleSheet(f"font-size:13px; color:{C['text3']}; background:transparent;")
        el.addWidget(es)
        self.stack.addWidget(empty)   # 0

        # ── Session view ──
        sv = QWidget(); sl = QVBoxLayout(sv); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)

        # Sub-toolbar
        tb = QWidget(); tb.setFixedHeight(56)
        tb.setStyleSheet(f"background:{C['surface']}; border-bottom:1px solid {C['border']};")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(20,0,20,0); tbl.setSpacing(10)

        # Path + meta
        ic = QVBoxLayout(); ic.setSpacing(1)
        self.path_lbl = QLabel("—")
        self.path_lbl.setStyleSheet(
            f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:12px;"
            f"color:{C['primary_hi']}; background:transparent; font-weight:600;"
        )
        self.meta_lbl = QLabel("")
        self.meta_lbl.setStyleSheet(f"font-size:11px; color:{C['text3']}; background:transparent;")
        ic.addWidget(self.path_lbl); ic.addWidget(self.meta_lbl)
        tbl.addLayout(ic)
        tbl.addStretch()

        # Search
        self.search = QLineEdit(); self.search.setPlaceholderText("Search files…")
        self.search.setFixedWidth(200); self.search.textChanged.connect(self._render)
        tbl.addWidget(self.search)

        # Filter buttons
        self.filter_btns: Dict[str, QPushButton] = {}
        for k, lbl in [("all","All"),("suggested","Suggested"),("unsorted","Unsorted"),("moved","Moved")]:
            btn = QPushButton(lbl); btn.setObjectName("btn_sm"); btn.setCheckable(True)
            btn.setChecked(k=="all"); btn.setFixedHeight(30)
            btn.clicked.connect(lambda _, key=k: self._set_filter(key))
            self.filter_btns[k] = btn; tbl.addWidget(btn)

        tbl.addWidget(self._vdiv())

        # View toggle
        self.list_btn = QPushButton("☰"); self.list_btn.setObjectName("btn_sm")
        self.list_btn.setCheckable(True); self.list_btn.setChecked(True)
        self.list_btn.setFixedSize(32,30)
        self.list_btn.clicked.connect(lambda: self._set_view("list"))
        self.grid_btn = QPushButton("⊞"); self.grid_btn.setObjectName("btn_sm")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setFixedSize(32,30)
        self.grid_btn.clicked.connect(lambda: self._set_view("grid"))
        tbl.addWidget(self.list_btn); tbl.addWidget(self.grid_btn)
        sl.addWidget(tb)

        # File scroll
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea{{border:none; background:{C['bg']};}}")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_container = QWidget(); self.list_container.setStyleSheet(f"background:{C['bg']};")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(20,14,20,14); self.list_layout.setSpacing(0)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_container)
        sl.addWidget(self.scroll, 1)

        # Action bar
        ab = QWidget(); ab.setFixedHeight(56)
        ab.setStyleSheet(f"background:{C['surface']}; border-top:1px solid {C['border']};")
        abl = QHBoxLayout(ab); abl.setContentsMargins(20,0,20,0); abl.setSpacing(10)

        self.sel_all_cb = QCheckBox()
        self.sel_all_cb.stateChanged.connect(self._toggle_all)
        abl.addWidget(self.sel_all_cb)
        all_lbl = QLabel("Select all")
        all_lbl.setStyleSheet(f"font-size:13px; color:{C['text2']}; background:transparent;")
        all_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        all_lbl.mousePressEvent = lambda _: self.sel_all_cb.setChecked(not self.sel_all_cb.isChecked())
        abl.addWidget(all_lbl)
        self.sel_lbl = QLabel("0 selected")
        self.sel_lbl.setStyleSheet(f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:12px; color:{C['text3']}; background:transparent;")
        abl.addWidget(self.sel_lbl)
        abl.addStretch()
        self.preview_btn = QPushButton("⊙  Preview Move"); self.preview_btn.setObjectName("btn_green")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(lambda: self._emit_move(True))
        abl.addWidget(self.preview_btn)
        self.move_btn = QPushButton("⊳  Move Selected"); self.move_btn.setObjectName("btn_primary")
        self.move_btn.setEnabled(False)
        self.move_btn.clicked.connect(lambda: self._emit_move(False))
        abl.addWidget(self.move_btn)
        sl.addWidget(ab)

        self.stack.addWidget(sv)  # 1
        root.addWidget(self.stack)
        self.stack.setCurrentIndex(0)

    def _vdiv(self):
        d = QFrame(); d.setFixedSize(1,28)
        d.setStyleSheet(f"background:{C['border']};"); return d

    def load_session(self, sid: int):
        self.session_id = sid
        self.current_files = core.get_files(sid)
        s = core.get_session(sid)
        if s:
            self.path_lbl.setText(s["folder_path"])
            analyzed = sum(1 for f in self.current_files if f.get("ai_suggested_path"))
            moved    = sum(1 for f in self.current_files if f.get("moved"))
            self.meta_lbl.setText(
                f"{len(self.current_files)} files  ·  {analyzed} analyzed  ·  {moved} moved"
                + (f"  ·  {s['model_used']}" if s.get("model_used") else "")
            )
        self.stack.setCurrentIndex(1)
        self.sel_all_cb.blockSignals(True); self.sel_all_cb.setChecked(False); self.sel_all_cb.blockSignals(False)
        self._render()

    def _set_filter(self, key):
        self._filter = key
        for k, b in self.filter_btns.items(): b.setChecked(k==key)
        self.sel_all_cb.blockSignals(True); self.sel_all_cb.setChecked(False); self.sel_all_cb.blockSignals(False)
        self._render()

    def _set_view(self, v):
        self._view = v
        self.list_btn.setChecked(v=="list"); self.grid_btn.setChecked(v=="grid")
        self._render()

    def _render(self):
        search = self.search.text().lower()
        files  = self.current_files
        if self._filter == "suggested": files = [f for f in files if f.get("ai_suggested_path") and not f.get("moved")]
        elif self._filter == "unsorted": files = [f for f in files if not f.get("ai_suggested_path") and not f.get("moved")]
        elif self._filter == "moved": files = [f for f in files if f.get("moved")]
        if search:
            files = [f for f in files if
                     search in (f.get("filename") or "").lower() or
                     search in (f.get("parent_folder") or "").lower() or
                     search in (f.get("ai_suggested_path") or "").lower()]

        for c in self._cards: c.setParent(None)
        self._cards.clear()
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not files:
            lbl = QLabel("No files match current filter")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color:{C['text3']}; font-size:13px; padding:40px; background:transparent;")
            self.list_layout.insertWidget(0, lbl); self._update_count(); return

        if self._view == "grid":
            self._render_grid(files)
        else:
            self._render_list(files)
        self._update_count()

    def _render_list(self, files):
        groups: Dict[str,List] = {}
        for f in files: groups.setdefault(f.get("parent_folder") or "(root)", []).append(f)
        idx = 0
        for grp, gfiles in groups.items():
            gh = QLabel(f"📁  {grp}  ({len(gfiles)})")
            gh.setStyleSheet(
                f"font-size:10.5px; font-weight:700; letter-spacing:0.8px;"
                f"color:{C['muted']}; background:{C['bg']}; padding:10px 0 4px;"
            )
            self.list_layout.insertWidget(idx, gh); idx += 1
            for f in gfiles:
                card = FileRowWidget(f)
                card.toggled.connect(lambda *_: self._update_count())
                self.list_layout.insertWidget(idx, card)
                self._cards.append(card); idx += 1

    def _render_grid(self, files):
        groups: Dict[str,List] = {}
        for f in files: groups.setdefault(f.get("parent_folder") or "(root)", []).append(f)
        idx = 0
        for grp, gfiles in groups.items():
            gh = QLabel(f"📁  {grp}  ({len(gfiles)})")
            gh.setStyleSheet(f"font-size:10.5px; font-weight:700; color:{C['muted']}; background:{C['bg']}; padding:10px 0 4px;")
            self.list_layout.insertWidget(idx, gh); idx += 1
            # Mini folder stats card for grid
            gc = QFrame(); gc.setObjectName("card"); gc.setFixedHeight(70)
            gcl = QHBoxLayout(gc); gcl.setContentsMargins(14,8,14,8); gcl.setSpacing(16)
            gcl.addWidget(QLabel(f"📁  <b>{grp}</b><br><small>{len(gfiles)} files</small>"))
            analyzed = sum(1 for f in gfiles if f.get("ai_suggested_path"))
            bar_w = QWidget(); bar_w.setStyleSheet("background:transparent;")
            bar_l = QVBoxLayout(bar_w); bar_l.setContentsMargins(0,0,0,0); bar_l.setSpacing(2)
            pb = QProgressBar(); pb.setRange(0,100); pb.setValue(int(analyzed/len(gfiles)*100) if gfiles else 0)
            pb.setFixedHeight(4); pb.setTextVisible(False)
            bar_l.addWidget(QLabel(f"<small>{analyzed}/{len(gfiles)} analyzed</small>"))
            bar_l.addWidget(pb)
            gcl.addWidget(bar_w, 1)
            self.list_layout.insertWidget(idx, gc); idx += 1
            # Files in grid (3 per row)
            for i in range(0, len(gfiles), 3):
                row_w = QWidget(); row_w.setStyleSheet("background:transparent;")
                row_l = QHBoxLayout(row_w); row_l.setContentsMargins(0,0,0,0); row_l.setSpacing(8)
                for f in gfiles[i:i+3]:
                    card = FileRowWidget(f)
                    card.toggled.connect(lambda *_: self._update_count())
                    row_l.addWidget(card, 1); self._cards.append(card)
                if len(gfiles[i:i+3]) < 3: row_l.addStretch()
                self.list_layout.insertWidget(idx, row_w); idx += 1

    def _toggle_all(self, state):
        for c in self._cards: c.set_checked(state == Qt.CheckState.Checked.value)
        self._update_count()

    def _update_count(self):
        ids = self._sel_ids(); n = len(ids)
        self.sel_lbl.setText(f"{n} selected")
        self.move_btn.setEnabled(n > 0); self.preview_btn.setEnabled(n > 0)

    def _sel_ids(self): return [c.fid for c in self._cards if c.is_checked()]
    def get_selected_ids(self): return self._sel_ids()
    def _emit_move(self, dry): ids=self._sel_ids(); ids and self.move_requested.emit(ids, dry)


# ── AIAnalysisPage ─────────────────────────────────────────────────────────────
class AIAnalysisPage(QWidget):
    analyze_requested = pyqtSignal(str, str, str, str, list)  # provider, model, url, key, file_ids

    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("page"); self._build()
        self._active_sid: Optional[int] = None

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:{C['bg']};}}")
        inner = QWidget(); inner.setStyleSheet(f"background:{C['bg']};")
        vb = QVBoxLayout(inner); vb.setContentsMargins(28,28,28,28); vb.setSpacing(24)

        # Title
        t = QLabel("AI Analysis"); t.setStyleSheet(
            f"font-size:22px; font-weight:800; color:{C['white']}; background:transparent;"
        ); vb.addWidget(t)
        s = QLabel("Select your AI provider and run intelligent file organization.")
        s.setStyleSheet(f"font-size:13px; color:{C['text2']}; background:transparent;")
        vb.addWidget(s)

        # ── Provider cards ──
        prow = QHBoxLayout(); prow.setSpacing(14)
        self._provider_btns: Dict[str, QPushButton] = {}
        providers = [
            ("Ollama",  "🦙", C["green"],   "Run locally on your Mac — fully private"),
            ("ChatGPT", "✦",  "#10a37f",    "OpenAI GPT-4o — fast and capable"),
            ("Claude",  "◈",  C["violet"],  "Anthropic Claude — great at analysis"),
        ]
        self._provider = "Ollama"
        for name, icon, color, desc in providers:
            btn = QFrame(); btn.setObjectName("card"); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            bl = QVBoxLayout(btn); bl.setContentsMargins(16,14,16,14); bl.setSpacing(6)
            ic = QLabel(icon); ic.setStyleSheet(
                f"font-size:24px; background:{color}22; color:{color};"
                f"border-radius:10px; border:1px solid {color}44; padding:6px;"
            ); ic.setFixedSize(46,46); ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(ic)
            nl = QLabel(name); nl.setStyleSheet(
                f"font-size:14px; font-weight:700; color:{C['white']}; background:transparent;"
            ); bl.addWidget(nl)
            dl = QLabel(desc); dl.setStyleSheet(
                f"font-size:11px; color:{C['text2']}; background:transparent;"
            ); dl.setWordWrap(True); bl.addWidget(dl)
            btn.mouseReleaseEvent = lambda _, n=name: self._select_provider(n)
            btn.setMinimumHeight(140)
            self._provider_btns[name] = btn; prow.addWidget(btn, 1)
        vb.addLayout(prow)

        # ── Config panels ──
        self.config_stack = QStackedWidget()

        # Ollama config
        ow = QWidget(); ow.setStyleSheet("background:transparent;")
        ol = QVBoxLayout(ow); ol.setContentsMargins(0,0,0,0); ol.setSpacing(10)
        url_row = QHBoxLayout(); url_row.setSpacing(8)
        url_lbl = QLabel("Ollama URL"); url_lbl.setStyleSheet(f"font-size:12px;color:{C['text2']};background:transparent;min-width:80px;")
        url_row.addWidget(url_lbl)
        self.ollama_url = QLineEdit("http://localhost:11434")
        url_row.addWidget(self.ollama_url, 1)
        self.ollama_connect_btn = QPushButton("Connect"); self.ollama_connect_btn.setObjectName("btn_green")
        self.ollama_connect_btn.setFixedWidth(90)
        self.ollama_connect_btn.clicked.connect(self._connect_ollama)
        url_row.addWidget(self.ollama_connect_btn)
        ol.addLayout(url_row)
        self.ollama_status = QLabel("● Not connected")
        self.ollama_status.setStyleSheet(f"font-size:11.5px; color:{C['text3']}; background:transparent;")
        ol.addWidget(self.ollama_status)
        model_row = QHBoxLayout(); model_row.setSpacing(8)
        model_lbl = QLabel("Model"); model_lbl.setStyleSheet(f"font-size:12px;color:{C['text2']};background:transparent;min-width:80px;")
        model_row.addWidget(model_lbl)
        self.ollama_model = QComboBox(); self.ollama_model.addItem("— connect first —"); self.ollama_model.setEnabled(False)
        model_row.addWidget(self.ollama_model, 1)
        ol.addLayout(model_row)
        self.config_stack.addWidget(ow)  # 0 = ollama

        # API key config (ChatGPT/Claude)
        aw = QWidget(); aw.setStyleSheet("background:transparent;")
        al = QVBoxLayout(aw); al.setContentsMargins(0,0,0,0); al.setSpacing(10)
        key_row = QHBoxLayout(); key_row.setSpacing(8)
        key_lbl = QLabel("API Key"); key_lbl.setStyleSheet(f"font-size:12px;color:{C['text2']};background:transparent;min-width:80px;")
        key_row.addWidget(key_lbl)
        self.api_key = QLineEdit(); self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-...")
        key_row.addWidget(self.api_key, 1)
        show_btn = QPushButton("👁"); show_btn.setObjectName("btn_sm")
        show_btn.setFixedSize(32,32); show_btn.setCheckable(True)
        show_btn.toggled.connect(lambda v: self.api_key.setEchoMode(QLineEdit.EchoMode.Normal if v else QLineEdit.EchoMode.Password))
        key_row.addWidget(show_btn)
        al.addLayout(key_row)
        model_row2 = QHBoxLayout(); model_row2.setSpacing(8)
        model_lbl2 = QLabel("Model"); model_lbl2.setStyleSheet(f"font-size:12px;color:{C['text2']};background:transparent;min-width:80px;")
        model_row2.addWidget(model_lbl2)
        self.api_model = QComboBox(); self.api_model.addItems(OPENAI_MODELS)
        model_row2.addWidget(self.api_model, 1)
        al.addLayout(model_row2)
        self.api_test_btn = QPushButton("✓  Test Connection"); self.api_test_btn.setObjectName("btn_sm")
        self.api_test_btn.setFixedWidth(160); self.api_test_btn.clicked.connect(self._test_api)
        al.addWidget(self.api_test_btn)
        self.api_status = QLabel("")
        self.api_status.setStyleSheet(f"font-size:11.5px; color:{C['green']}; background:transparent;")
        al.addWidget(self.api_status)
        self.config_stack.addWidget(aw)  # 1 = api

        vb.addWidget(self.config_stack)
        self._select_provider("Ollama")

        # ── Analyze options ──
        vb.addWidget(self._hdiv())
        opt_row = QHBoxLayout(); opt_row.setSpacing(12)
        self.scope_lbl = QLabel("Scope: All files in current session")
        self.scope_lbl.setStyleSheet(f"font-size:12px; color:{C['text2']}; background:transparent;")
        opt_row.addWidget(self.scope_lbl)
        opt_row.addStretch()
        self.analyze_btn = QPushButton("◈   Run AI Analysis"); self.analyze_btn.setObjectName("btn_primary")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._run)
        opt_row.addWidget(self.analyze_btn)
        vb.addLayout(opt_row)

        # ── Progress panel ──
        self.progress_frame = QFrame(); self.progress_frame.setObjectName("card")
        self.progress_frame.setVisible(False)
        pfl = QVBoxLayout(self.progress_frame); pfl.setContentsMargins(16,14,16,14); pfl.setSpacing(8)

        ph = QHBoxLayout()
        self.prog_title = QLabel("Analysis in progress…")
        self.prog_title.setStyleSheet(f"font-size:13px; font-weight:700; color:{C['white']}; background:transparent;")
        ph.addWidget(self.prog_title); ph.addStretch()
        self.prog_batch = QLabel("")
        self.prog_batch.setStyleSheet(f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:11px; color:{C['text3']}; background:transparent;")
        ph.addWidget(self.prog_batch)
        pfl.addLayout(ph)

        self.prog_bar = QProgressBar(); self.prog_bar.setRange(0,100); self.prog_bar.setValue(0)
        self.prog_bar.setFixedHeight(6); self.prog_bar.setTextVisible(False)
        pfl.addWidget(self.prog_bar)

        self.prog_log = QTextEdit(); self.prog_log.setReadOnly(True); self.prog_log.setFixedHeight(160)
        pfl.addWidget(self.prog_log)
        vb.addWidget(self.progress_frame)
        vb.addStretch()

        scroll.setWidget(inner); root.addWidget(scroll)

    def _hdiv(self):
        d = QFrame(); d.setFixedHeight(1)
        d.setStyleSheet(f"background:{C['border']}; border:none;"); return d

    def _select_provider(self, name):
        self._provider = name
        colors = {"Ollama": C["green"], "ChatGPT": "#10a37f", "Claude": C["violet"]}
        for n, btn in self._provider_btns.items():
            c = colors[n] if n == name else None
            if c:
                btn.setStyleSheet(f"QFrame#card{{background:{c}18;border:2px solid {c}66;border-radius:10px;}}")
            else:
                btn.setStyleSheet(f"QFrame#card{{background:{C['card']};border:1px solid {C['border']};border-radius:10px;}}QFrame#card:hover{{background:{C['card2']};border-color:{C['border2']};}}")

        if name == "Ollama":
            self.config_stack.setCurrentIndex(0)
        else:
            self.config_stack.setCurrentIndex(1)
            self.api_model.clear()
            self.api_model.addItems(ANTHROPIC_MODELS if name == "Claude" else OPENAI_MODELS)
            self.api_key.setPlaceholderText("sk-ant-..." if name == "Claude" else "sk-proj-...")

    def _connect_ollama(self):
        url = self.ollama_url.text().strip()
        self.ollama_connect_btn.setEnabled(False); self.ollama_connect_btn.setText("…")
        try:
            import requests as rq
            r = rq.get(f"{url}/api/tags", timeout=5)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models",[])]
                self.ollama_model.clear()
                if models:
                    self.ollama_model.addItems(models); self.ollama_model.setEnabled(True)
                    self.ollama_status.setText(f"● Connected — {len(models)} model(s) available")
                    self.ollama_status.setStyleSheet(f"font-size:11.5px;color:{C['green']};background:transparent;")
                else:
                    self.ollama_model.addItem("No models found")
                    self.ollama_status.setText("● Connected but no models installed")
                    self.ollama_status.setStyleSheet(f"font-size:11.5px;color:{C['amber']};background:transparent;")
            else: raise Exception(f"HTTP {r.status_code}")
        except Exception as e:
            self.ollama_status.setText(f"● Cannot connect: {e}")
            self.ollama_status.setStyleSheet(f"font-size:11.5px;color:{C['red']};background:transparent;")
        finally:
            self.ollama_connect_btn.setEnabled(True); self.ollama_connect_btn.setText("Connect")

    def _test_api(self):
        import requests as rq
        key = self.api_key.text().strip()
        if not key: self.api_status.setText("Enter API key first"); return
        self.api_status.setText("Testing…")
        try:
            if self._provider == "ChatGPT":
                r = rq.get("https://api.openai.com/v1/models",
                            headers={"Authorization": f"Bearer {key}"}, timeout=8)
                self.api_status.setText("● Connected to OpenAI" if r.ok else f"● Error {r.status_code}")
            else:
                r = rq.get("https://api.anthropic.com/v1/models",
                            headers={"x-api-key":key,"anthropic-version":"2023-06-01"}, timeout=8)
                self.api_status.setText("● Connected to Anthropic" if r.ok else f"● Error {r.status_code}")
            color = C["green"] if "Connected" in self.api_status.text() else C["red"]
            self.api_status.setStyleSheet(f"font-size:11.5px;color:{color};background:transparent;")
        except Exception as e:
            self.api_status.setText(f"● {e}")
            self.api_status.setStyleSheet(f"font-size:11.5px;color:{C['red']};background:transparent;")

    def _run(self):
        if self._provider == "Ollama":
            model = self.ollama_model.currentText()
            url   = self.ollama_url.text().strip()
            key   = ""
        else:
            model = self.api_model.currentText()
            url   = ""
            key   = self.api_key.text().strip()
        self.analyze_requested.emit(self._provider, model, url, key, [])

    def set_session(self, sid: Optional[int]):
        self._active_sid = sid
        self.analyze_btn.setEnabled(sid is not None)
        if sid:
            s = core.get_session(sid)
            n = len(core.get_files(sid))
            self.scope_lbl.setText(f"Scope: All {n} files in  {os.path.basename(s['folder_path']) if s else '—'}")

    # Progress API
    def show_progress(self, title="Analyzing…"):
        self.progress_frame.setVisible(True)
        self.prog_log.clear(); self.prog_bar.setValue(0)
        self.prog_title.setText(title)
        self.prog_title.setStyleSheet(f"font-size:13px;font-weight:700;color:{C['white']};background:transparent;")

    def log_line(self, msg, level=""):
        col = {"ok":C["green"],"err":C["red"],"info":C["primary_hi"]}.get(level, C["text2"])
        self.prog_log.append(f'<span style="color:{col};">{msg}</span>')
        sb = self.prog_log.verticalScrollBar(); sb.setValue(sb.maximum())

    def set_progress(self, b, t):
        self.prog_bar.setValue(int(b/max(t,1)*100)); self.prog_batch.setText(f"batch {b}/{t}")

    def set_done(self, msg="✓ Analysis complete"):
        self.prog_bar.setValue(100); self.prog_title.setText(msg)
        self.prog_title.setStyleSheet(f"font-size:13px;font-weight:700;color:{C['green']};background:transparent;")


# ── ActivityPage ───────────────────────────────────────────────────────────────
class ActivityPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("page"); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(28,28,28,28); root.setSpacing(16)

        hdr = QHBoxLayout()
        t = QLabel("Activity Log"); t.setStyleSheet(
            f"font-size:22px; font-weight:800; color:{C['white']}; background:transparent;"
        ); hdr.addWidget(t); hdr.addStretch()
        ref = QPushButton("↺  Refresh"); ref.setObjectName("btn_sm"); ref.clicked.connect(self.refresh)
        hdr.addWidget(ref)
        root.addLayout(hdr)
        s = QLabel("All file moves — double-click a row to reveal in Finder.")
        s.setStyleSheet(f"font-size:13px; color:{C['text2']}; background:transparent;")
        root.addWidget(s)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["File", "From", "To", "Session", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self._reveal)
        root.addWidget(self.table, 1)

    def refresh(self):
        moves = core.get_all_moves()
        self.table.setRowCount(0)
        for m in moves:
            r = self.table.rowCount(); self.table.insertRow(r)
            vals = [
                m.get("filename",""),
                m.get("from_path",""),
                m.get("to_path",""),
                os.path.basename(m.get("folder_path","")),
                (m.get("moved_at","") or "")[:16],
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v); it.setForeground(QColor(C["text2"]))
                if c == 0: it.setForeground(QColor(C["text"]))
                self.table.setItem(r, c, it)
                self.table.setItem(r, c, it)
            self.table.setRowHeight(r, 40)
        if not moves:
            r = self.table.rowCount(); self.table.insertRow(r)
            it = QTableWidgetItem("No file moves recorded yet")
            it.setForeground(QColor(C["text3"])); self.table.setItem(r, 0, it)

    def _reveal(self, row, _):
        item = self.table.item(row, 2)
        if not item or not item.text():
            return
        path = item.text()
        system = platform.system()
        if system == "Darwin":
            os.system(f'open -R "{path}"')
        elif system == "Windows":
            os.system(f'explorer /select,"{path}"')
        else:  # Linux / other
            folder = os.path.dirname(path)
            os.system(f'xdg-open "{folder}"')


# ── SettingsPage ───────────────────────────────────────────────────────────────
class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("page"); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(28,28,28,28); root.setSpacing(24)
        t = QLabel("Settings"); t.setStyleSheet(
            f"font-size:22px; font-weight:800; color:{C['white']}; background:transparent;"
        ); root.addWidget(t)

        def section(title):
            l = QLabel(title); l.setStyleSheet(
                f"font-size:11px; font-weight:700; letter-spacing:1.4px;"
                f"color:{C['muted']}; background:transparent; text-transform:uppercase; padding-top:8px;"
            ); return l

        def row(label, widget, note=""):
            w = QWidget(); w.setStyleSheet("background:transparent;")
            lo = QHBoxLayout(w); lo.setContentsMargins(0,0,0,0); lo.setSpacing(16)
            lbl = QLabel(label); lbl.setFixedWidth(160)
            lbl.setStyleSheet(f"font-size:13px; color:{C['text2']}; background:transparent;")
            lo.addWidget(lbl); lo.addWidget(widget, 1)
            if note:
                nl = QLabel(note); nl.setStyleSheet(f"font-size:11px; color:{C['text3']}; background:transparent;")
                lo.addWidget(nl)
            return w

        root.addWidget(section("Storage"))
        db_lbl = QLabel(core.DB_PATH)
        db_lbl.setStyleSheet(f"font-family:'Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace; font-size:11.5px; color:{C['primary_hi']}; background:transparent;")
        root.addWidget(row("Database location", db_lbl))

        clear_btn = QPushButton("⚠  Clear All Data"); clear_btn.setObjectName("btn_danger")
        clear_btn.setFixedWidth(180)
        clear_btn.clicked.connect(self._clear)
        root.addWidget(row("Clear cache", clear_btn, "Removes all sessions and analysis. Files are NOT affected."))

        root.addWidget(section("Default Paths"))
        self.default_folder = QLineEdit(os.path.expanduser("~/Downloads"))
        browse = QPushButton("…"); browse.setObjectName("btn_sm"); browse.setFixedWidth(32)
        browse.clicked.connect(lambda: (p := QFileDialog.getExistingDirectory(self, "Select", self.default_folder.text())) and self.default_folder.setText(p))
        row_w = QWidget(); row_w.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(row_w); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)
        rl.addWidget(self.default_folder, 1); rl.addWidget(browse)
        root.addWidget(row("Default folder", row_w))

        root.addWidget(section("About"))
        about = QLabel("FileSage v1.0 · AI-powered file organization · Built with PyQt6 + Ollama/OpenAI/Anthropic")
        about.setStyleSheet(f"font-size:12px; color:{C['text3']}; background:transparent;")
        about.setWordWrap(True)
        root.addWidget(about)
        root.addStretch()

    def _clear(self):
        if QMessageBox.question(self, "Clear All Data",
            "Delete ALL sessions and analysis data?\n\n(Your actual files are NOT affected.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            core.clear_all()
            QMessageBox.information(self, "Done", "All data cleared.")

    def get_default_folder(self): return self.default_folder.text()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

class Sidebar(QWidget):
    nav_changed = pyqtSignal(str)   # page name

    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("sidebar"); self.setFixedWidth(210); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Logo
        logo = QWidget(); logo.setFixedHeight(58)
        logo.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(logo); ll.setContentsMargins(16,0,16,0); ll.setSpacing(10)
        gem = QLabel("◈"); gem.setFixedSize(34,34); gem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gem.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C['primary_hi']},stop:1 {C['violet']});"
            f"color:{C['white']}; font-size:17px; font-weight:900; border-radius:9px;"
        )
        ll.addWidget(gem)
        nc = QVBoxLayout(); nc.setSpacing(0)
        n1 = QLabel("FileSage"); n1.setStyleSheet(
            f"font-size:15px; font-weight:800; letter-spacing:-0.3px; color:{C['white']}; background:transparent;"
        )
        n2 = QLabel("File Intelligence"); n2.setStyleSheet(
            f"font-size:9.5px; color:{C['text3']}; background:transparent;"
        )
        nc.addWidget(n1); nc.addWidget(n2); ll.addLayout(nc); ll.addStretch()
        root.addWidget(logo)

        root.addWidget(self._divider())

        # Nav buttons
        nav_wrap = QWidget(); nav_wrap.setStyleSheet("background:transparent;")
        nl = QVBoxLayout(nav_wrap); nl.setContentsMargins(10,12,10,12); nl.setSpacing(2)

        self._nav_btns: Dict[str, QPushButton] = {}
        nav_items = [
            ("dashboard", "📊  Dashboard",    True),
            ("files",     "📁  File Manager", False),
            ("ai",        "🤖  AI Analysis",  False),
            ("activity",  "🕐  Activity",     False),
            ("settings",  "⚙   Settings",     False),
        ]
        for page, label, active in nav_items:
            btn = QPushButton(label); btn.setObjectName("nav_btn")
            btn.setCheckable(True); btn.setChecked(active)
            btn.setFixedHeight(38); btn.setMinimumWidth(0)
            btn.clicked.connect(lambda _, p=page: self._on_nav(p))
            self._nav_btns[page] = btn; nl.addWidget(btn)

        root.addWidget(nav_wrap)
        root.addWidget(self._divider())

        # Current session info
        self.session_frame = QWidget(); self.session_frame.setStyleSheet("background:transparent;")
        sf = QVBoxLayout(self.session_frame); sf.setContentsMargins(12,10,12,10); sf.setSpacing(4)
        sl = QLabel("CURRENT SESSION"); sl.setStyleSheet(
            f"font-size:9px; font-weight:700; letter-spacing:1.2px; color:{C['text3']}; background:transparent;"
        ); sf.addWidget(sl)
        self.session_name = QLabel("None"); self.session_name.setStyleSheet(
            f"font-size:11.5px; font-weight:600; color:{C['primary_hi']}; background:transparent;"
        ); self.session_name.setWordWrap(True)
        sf.addWidget(self.session_name)
        self.session_meta = QLabel("")
        self.session_meta.setStyleSheet(f"font-size:10px; color:{C['text3']}; background:transparent;")
        sf.addWidget(self.session_meta)

        pb_wrap = QWidget(); pb_wrap.setStyleSheet("background:transparent;")
        pbl = QVBoxLayout(pb_wrap); pbl.setContentsMargins(0,2,0,0); pbl.setSpacing(2)
        self.session_bar = QProgressBar(); self.session_bar.setRange(0,100)
        self.session_bar.setValue(0); self.session_bar.setFixedHeight(4); self.session_bar.setTextVisible(False)
        pbl.addWidget(self.session_bar)
        sf.addWidget(pb_wrap)
        root.addWidget(self.session_frame)
        root.addWidget(self._divider())

        # Recent sessions list
        sl2 = QLabel("RECENT"); sl2.setStyleSheet(
            f"font-size:9px; font-weight:700; letter-spacing:1.2px; color:{C['text3']}; background:transparent; padding:8px 12px 4px;"
        ); root.addWidget(sl2)

        self.session_list = QListWidget(); self.session_list.setSpacing(1)
        self.session_list.setStyleSheet(f"""
            QListWidget {{ background:transparent; border:none; padding:0 8px; }}
            QListWidget::item {{
                background:{C['card']}; border:1px solid {C['border']};
                border-radius:6px; margin:1px 0; padding:6px 8px; color:{C['text2']};
                font-size:11.5px;
            }}
            QListWidget::item:selected {{
                background:{C['primary_glow']}; border-color:{C['primary_dim']}; color:{C['primary_hi']};
            }}
            QListWidget::item:hover:!selected {{
                background:{C['card2']}; border-color:{C['border2']}; color:{C['text']};
            }}
        """)
        root.addWidget(self.session_list, 1)
        root.addStretch()

    def _divider(self):
        d = QFrame(); d.setFixedHeight(1)
        d.setStyleSheet(f"background:{C['border']}; border:none;"); return d

    def _on_nav(self, page):
        for p, b in self._nav_btns.items(): b.setChecked(p == page)
        self.nav_changed.emit(page)

    def set_active_page(self, page):
        for p, b in self._nav_btns.items(): b.setChecked(p == page)

    def update_session(self, sid: Optional[int]):
        if not sid:
            self.session_name.setText("None"); self.session_meta.setText(""); self.session_bar.setValue(0); return
        s = core.get_session(sid)
        if not s: return
        files = core.get_files(sid)
        analyzed = sum(1 for f in files if f.get("ai_suggested_path"))
        total    = len(files) or 1
        self.session_name.setText(os.path.basename(s["folder_path"]))
        self.session_meta.setText(f"{total} files  ·  {int(analyzed/total*100)}% analyzed")
        self.session_bar.setValue(int(analyzed/total*100))

    def refresh_list(self, active_id=None):
        self.session_list.clear()
        sessions = core.get_sessions()
        for s in sessions[:8]:
            item = QListWidgetItem(
                f"{os.path.basename(s['folder_path'])}\n{s['file_count'] or 0} files  ·  {s['status']}"
            )
            item.setData(Qt.ItemDataRole.UserRole, s["id"])
            item.setToolTip(s["folder_path"])
            self.session_list.addItem(item)
            if s["id"] == active_id: self.session_list.setCurrentItem(item)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileSage — AI File Manager")
        self.resize(1280, 800); self.setMinimumSize(960, 640)
        self._active: Optional[int] = None
        self._scan_w:  Optional[ScanWorker]    = None
        self._ana_w:   Optional[AnalyzeWorker] = None
        core.init_db()
        self._build()
        self._refresh()
        # Auto-load last session
        sessions = core.get_sessions()
        if sessions: self._set_session(sessions[0]["id"])

    def _build(self):
        central = QWidget(); central.setObjectName("page")
        cl = QVBoxLayout(central); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)

        # ── Top bar ──
        topbar = QWidget(); topbar.setObjectName("topbar"); topbar.setFixedHeight(52)
        tl = QHBoxLayout(topbar); tl.setContentsMargins(16,0,16,0); tl.setSpacing(12)

        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"font-size:11px; color:{C['text3']}; background:transparent;")
        tl.addWidget(self.status_indicator)

        self.topbar_title = QLabel("FileSage")
        self.topbar_title.setStyleSheet(
            f"font-size:14px; font-weight:700; color:{C['text']}; background:transparent;"
        )
        tl.addWidget(self.topbar_title)
        tl.addStretch()

        # Global search
        self.global_search = QLineEdit(); self.global_search.setFixedWidth(260)
        self.global_search.setPlaceholderText("⌕  Search files across sessions…")
        tl.addWidget(self.global_search)

        # Scan button in topbar
        self.topbar_scan = QPushButton("⌕  Scan Folder"); self.topbar_scan.setObjectName("btn_accent")
        self.topbar_scan.clicked.connect(self._quick_scan)
        tl.addWidget(self.topbar_scan)

        self.topbar_analyze = QPushButton("◈  Analyze"); self.topbar_analyze.setObjectName("btn_primary")
        self.topbar_analyze.setEnabled(False)
        self.topbar_analyze.clicked.connect(lambda: self._goto("ai"))
        tl.addWidget(self.topbar_analyze)

        cl.addWidget(topbar)

        # ── Body: Sidebar + Content ──
        body = QWidget(); body.setStyleSheet(f"background:{C['bg']};")
        bl = QHBoxLayout(body); bl.setContentsMargins(0,0,0,0); bl.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._goto)
        self.sidebar.session_list.itemClicked.connect(
            lambda item: self._set_session(item.data(Qt.ItemDataRole.UserRole))
        )
        bl.addWidget(self.sidebar)

        # Pages stack
        self.pages = QStackedWidget()
        self.page_map: Dict[str, int] = {}

        self.dashboard = DashboardPage()
        self.dashboard.scan_requested.connect(self._do_scan)
        self.dashboard.session_selected.connect(self._set_session)
        self.dashboard.goto_files.connect(lambda: self._goto("files"))
        self._add_page("dashboard", self.dashboard)

        self.file_manager = FileManagerPage()
        self.file_manager.move_requested.connect(self._move)
        self._add_page("files", self.file_manager)

        self.ai_page = AIAnalysisPage()
        self.ai_page.analyze_requested.connect(self._analyze)
        self._add_page("ai", self.ai_page)

        self.activity = ActivityPage()
        self._add_page("activity", self.activity)

        self.settings_page = SettingsPage()
        self._add_page("settings", self.settings_page)

        bl.addWidget(self.pages, 1)
        cl.addWidget(body, 1)

        self.setCentralWidget(central)
        self.sb = QStatusBar(); self.setStatusBar(self.sb)
        self.sb.showMessage("Ready  ·  FileSage v1.0")

    def _add_page(self, name, widget):
        idx = self.pages.addWidget(widget); self.page_map[name] = idx

    def _goto(self, page):
        self.pages.setCurrentIndex(self.page_map.get(page, 0))
        self.sidebar.set_active_page(page)
        if page == "activity": self.activity.refresh()

    # ── Scan ──
    def _quick_scan(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan",
                                                   self.settings_page.get_default_folder())
        if folder: self._do_scan(folder)

    def _do_scan(self, folder):
        if not folder: return
        if not os.path.isdir(folder):
            QMessageBox.warning(self, "Not found", f"Directory not found:\n{folder}"); return
        self.topbar_scan.setEnabled(False); self.topbar_scan.setText("⏳  Scanning…")
        self.sb.showMessage(f"Scanning {folder}…")
        self._scan_w = ScanWorker(folder)
        self._scan_w.progress.connect(lambda n: self.sb.showMessage(f"Scanning… {n} files found"))
        self._scan_w.finished.connect(self._scan_done)
        self._scan_w.error.connect(lambda e: (
            QMessageBox.critical(self, "Scan Error", e),
            self.topbar_scan.setEnabled(True),
            self.topbar_scan.setText("⌕  Scan Folder"),
        ))
        self._scan_w.finished.connect(lambda *_: (
            self.topbar_scan.setEnabled(True),
            self.topbar_scan.setText("⌕  Scan Folder"),
        ))
        self._scan_w.start()

    def _scan_done(self, sid, count):
        self._set_session(sid)
        self._refresh()
        self.sb.showMessage(f"Scan complete — {count} files found")
        # Go to files page
        self._goto("files")

    def _set_session(self, sid: int):
        self._active = sid
        self.file_manager.load_session(sid)
        self.ai_page.set_session(sid)
        self.sidebar.update_session(sid)
        self.sidebar.refresh_list(active_id=sid)
        self.topbar_analyze.setEnabled(True)
        s = core.get_session(sid)
        if s:
            self.topbar_title.setText(os.path.basename(s["folder_path"]))
            self.status_indicator.setText("●")
            self.status_indicator.setStyleSheet(f"font-size:11px;color:{C['green']};background:transparent;")
        self.dashboard.refresh(active_sid=sid)

    def _refresh(self):
        self.dashboard.refresh(active_sid=self._active)
        self.sidebar.refresh_list(active_id=self._active)

    # ── Analyze ──
    def _analyze(self, provider, model, url, key, file_ids):
        if not self._active:
            QMessageBox.warning(self, "No session", "Scan a folder first."); return
        if not model or model.startswith("—"):
            QMessageBox.warning(self, "No model", "Select a model first."); return
        if provider != "Ollama" and not key:
            QMessageBox.warning(self, "No API key", f"Enter your {provider} API key."); return

        selected = self.file_manager.get_selected_ids()
        self.ai_page.show_progress(f"Analyzing with {model.split(':')[0]}…")
        self.ai_page.log_line(f"Provider: {provider}  |  Model: {model}", "info")
        self.ai_page.log_line(f"Files: {'selected ' + str(len(selected)) if selected else 'all'}", "info")

        pmap = {"Ollama": "ollama", "ChatGPT": "openai", "Claude": "anthropic"}
        self._ana_w = AnalyzeWorker(
            session_id=self._active, provider=pmap[provider],
            model=model, ollama_url=url or "http://localhost:11434",
            api_key=key, file_ids=selected if selected else None,
        )
        self._ana_w.log.connect(lambda m, lv: self.ai_page.log_line(m, lv))
        self._ana_w.batch_done.connect(lambda b, t, _: (
            self.ai_page.set_progress(b, t),
            self.file_manager.load_session(self._active),
        ))
        self._ana_w.finished.connect(self._analyze_done)
        self._ana_w.error.connect(lambda e: (
            self.ai_page.log_line(f"Error: {e}", "err"),
            self.ai_page.set_done("⚠ Analysis failed"),
            self.sb.showMessage("Analysis failed"),
        ))
        self.sb.showMessage("Analyzing…")
        self._ana_w.start()

    def _analyze_done(self):
        self.ai_page.set_done("✓ Analysis complete")
        self.ai_page.log_line("Review file suggestions in File Manager →", "ok")
        self._set_session(self._active)
        self.sb.showMessage("Analysis complete — switch to File Manager to review")

    # ── Move ──
    def _move(self, ids, dry_run):
        if not self._active: return
        if not dry_run:
            if QMessageBox.question(self, "Confirm Move",
                f"Move {len(ids)} file(s) to AI-suggested paths?\nThis cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) != QMessageBox.StandardButton.Yes: return
        results = core.move_files(self._active, ids, dry_run=dry_run)
        self._show_results(results, dry_run)
        if not dry_run:
            self._set_session(self._active); self.activity.refresh()

    def _show_results(self, results, dry_run):
        d = QDialog(self); d.setWindowTitle("Preview" if dry_run else "Move Results")
        d.setMinimumSize(620,420)
        lo = QVBoxLayout(d); lo.setContentsMargins(16,16,16,16); lo.setSpacing(10)
        moved = sum(1 for r in results if r["status"]=="moved")
        tl = QLabel("Preview — no files touched" if dry_run else f"{moved} file(s) moved successfully")
        tl.setStyleSheet(f"font-size:14px; font-weight:700; color:{C['white']}; background:transparent;")
        lo.addWidget(tl)
        txt = QTextEdit(); txt.setReadOnly(True)
        for r in results:
            s = r["status"]
            c = {"moved":C["green"],"preview":C["primary_hi"],"error":C["red"]}.get(s, C["muted"])
            lbl = {"moved":"✓ MOVED","preview":"→ PREVIEW","error":f"✕ {r.get('message','')}"}.get(s, s)
            txt.append(f'<span style="color:{c};font-weight:600;">{lbl}</span>')
            txt.append(f'<span style="color:{C["muted"]};">  From: {r.get("from","")}</span>')
            if r.get("to"): txt.append(f'<span style="color:{C["text2"]};">  →    {r["to"]}</span>')
            txt.append("")
        lo.addWidget(txt, 1)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(d.reject); lo.addWidget(btns); d.exec()


# ── Entry ──────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FileSage"); app.setStyle("Fusion")

    # Pick the best available system font per platform
    from PyQt6.QtGui import QFont
    _system = platform.system()
    if _system == "Darwin":
        _font_name = "Helvetica Neue"
    elif _system == "Windows":
        _font_name = "Segoe UI"
    else:  # Linux
        _font_name = "Ubuntu"
    app_font = QFont(_font_name)
    if not app_font.exactMatch():
        app_font = QFont("Arial")
    app_font.setPointSize(13)
    app.setFont(app_font)

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(C["bg"]))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(C["text"]))
    pal.setColor(QPalette.ColorRole.Base,            QColor(C["card"]))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(C["surface"]))
    pal.setColor(QPalette.ColorRole.Text,            QColor(C["text"]))
    pal.setColor(QPalette.ColorRole.Button,          QColor(C["card2"]))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(C["text"]))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(C["primary_dim"]))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(C["primary_hi"]))
    app.setPalette(pal); app.setStyleSheet(STYLE)

    win = MainWindow(); win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
