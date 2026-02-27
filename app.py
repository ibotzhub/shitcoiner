#!/usr/bin/env python3
"""
SHITCOINER — Native Desktop Momentum Scanner
Shitcoin momentum scanner. Not financial advice.
"""

import sys, json, time, math, os, stat, urllib.request, threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton,
        QCheckBox, QComboBox, QSpinBox, QLineEdit, QDialog, QTextEdit,
        QFrame, QSizePolicy, QAbstractItemView, QSystemTrayIcon, QMenu,
        QMessageBox, QFormLayout, QGroupBox, QTabWidget, QStatusBar,
        QDoubleSpinBox, QScrollArea, QSplitter,
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF, QSize, QRectF
    from PyQt6.QtGui import (
        QPainter, QPen, QColor, QBrush, QFont, QFontMetrics,
        QLinearGradient, QPixmap, QAction, QPalette, QIcon,
    )
except ImportError:
    print("PyQt6 not found.\nInstall it: pip install PyQt6")
    sys.exit(1)

# ── Config paths ──────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".shitcoiner"
CONFIG_DIR.mkdir(exist_ok=True)
WATCHLIST_F = CONFIG_DIR / "watchlist.json"
ENV_PATH    = CONFIG_DIR / ".env"

try:
    from dotenv import load_dotenv
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
except ImportError:
    pass

# ── Palette ───────────────────────────────────────────────────────
BG      = "#06060e"
BG2     = "#0c0c1a"
SURF    = "#111124"
BORDER  = "#1a1a30"
TEXT    = "#c8c8e8"
TEXT2   = "#484870"
ACCENT  = "#00ffcc"
BUY     = "#00ff88"
SELL    = "#ff3355"
WARN    = "#ffaa00"
NEW_C   = "#a855f7"
DIM     = "#303050"

# ── Stylesheet ────────────────────────────────────────────────────
QSS = f"""
* {{
    font-family: "Courier New", "Cascadia Code", "Consolas", "Menlo", monospace;
    font-size: 12px;
    color: {TEXT};
    outline: 0;
}}
QMainWindow, QDialog {{ background: {BG}; }}
QWidget {{ background: transparent; }}

QPushButton {{
    background: {BG2};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 5px 14px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QPushButton:hover {{
    border-color: {ACCENT};
    color: {ACCENT};
    background: #00ffcc0a;
}}
QPushButton:pressed {{ background: #00ffcc1a; }}
QPushButton:disabled {{ color: {DIM}; border-color: {SURF}; }}
QPushButton#scan-btn {{
    background: #00ffcc18;
    border: 1px solid {ACCENT};
    color: {ACCENT};
    padding: 7px 22px;
    font-size: 13px;
}}
QPushButton#scan-btn:hover {{ background: #00ffcc30; }}
QPushButton#sell-btn {{
    background: #ff335518;
    border: 1px solid {SELL};
    color: {SELL};
}}
QPushButton#remove-btn {{
    background: transparent; border: none;
    color: {TEXT2}; padding: 2px 6px; font-size: 14px;
    text-transform: none; letter-spacing: 0;
}}
QPushButton#remove-btn:hover {{ color: {SELL}; background: transparent; }}
QPushButton#star-btn {{
    background: transparent; border: none;
    color: {TEXT2}; padding: 2px 6px; font-size: 13px;
    text-transform: none; letter-spacing: 0;
}}
QPushButton#star-btn:hover {{ color: {WARN}; background: transparent; }}
QPushButton#star-btn[starred="true"] {{ color: {WARN}; }}

QTableWidget {{
    background: {BG};
    alternate-background-color: {BG2};
    gridline-color: #0e0e20;
    border: none;
    selection-background-color: #00ffcc12;
    selection-color: {TEXT};
}}
QTableWidget::item {{ padding: 3px 7px; border: none; }}
QTableWidget::item:selected {{ background: #00ffcc0e; }}
QHeaderView::section {{
    background: {BG2};
    color: {TEXT2};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid #0e0e20;
    padding: 5px 8px;
    font-size: 10px;
    letter-spacing: 2px;
}}
QHeaderView::section:last {{ border-right: none; }}

QScrollBar:vertical {{
    background: {BG2}; width: 7px; border: none; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: #00ffcc44; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {BG2}; height: 7px; border: none; margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER}; border-radius: 3px; min-width: 20px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {BG2};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 4px 8px;
    selection-background-color: #00ffcc33;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {BG2};
    border: 1px solid {BORDER};
    selection-background-color: #00ffcc22;
    selection-color: {TEXT};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {SURF};
    border: 1px solid {BORDER};
    width: 14px;
}}

QCheckBox {{ spacing: 7px; color: {TEXT2}; }}
QCheckBox::indicator {{
    width: 13px; height: 13px;
    border: 1px solid {BORDER}; background: {BG2};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT};
    image: none;
}}
QCheckBox:hover {{ color: {TEXT}; }}

QTextEdit {{
    background: {BG2}; border: 1px solid {BORDER};
    color: #9898c8; font-size: 12px; line-height: 1.5;
}}

QDialog {{ background: {BG2}; }}
QGroupBox {{
    border: 1px solid {BORDER}; margin-top: 10px;
    padding: 8px 6px 6px 6px; color: {TEXT2};
    font-size: 10px; letter-spacing: 2px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 6px; color: {TEXT2};
}}
QTabWidget::pane {{ border: 1px solid {BORDER}; background: {BG2}; top: -1px; }}
QTabBar::tab {{
    background: {BG}; color: {TEXT2};
    border: 1px solid {BORDER}; border-bottom: none;
    padding: 5px 14px; font-size: 11px; letter-spacing: 1px;
}}
QTabBar::tab:selected {{ color: {ACCENT}; border-top-color: {ACCENT}; }}
QStatusBar {{
    background: {BG2}; border-top: 1px solid {BORDER};
    color: {TEXT2}; font-size: 10px; letter-spacing: 1px;
}}
QStatusBar::item {{ border: none; }}
QMenu {{
    background: {BG2}; border: 1px solid {BORDER}; color: {TEXT};
}}
QMenu::item:selected {{ background: #00ffcc22; color: {ACCENT}; }}
QMessageBox {{ background: {BG2}; }}
QMessageBox QPushButton {{ min-width: 70px; }}
"""


# ── Utilities ─────────────────────────────────────────────────────
def fmt_price(n) -> str:
    if n is None: return "N/A"
    if n >= 1:    return f"${n:,.2f}"
    if n >= 0.01: return f"${n:.4f}"
    if n >= 0.0001: return f"${n:.6f}"
    return f"${n:.10f}".rstrip("0").rstrip(".")

def fmt_pct(n) -> str:
    if n is None: return "—"
    sign = "+" if n >= 0 else ""
    return f"{sign}{n:.2f}%"

def fmt_vmr(n) -> str:
    return f"{n:.3f}" if n is not None else "—"

def fmt_score(n) -> str:
    return f"{n:.3f}" if n is not None else "—"

def get_signal(score, velocity, vmr):
    if score is None:
        return "⚪", "NO DATA", TEXT2
    rising  = velocity is None or velocity >= 0
    falling = velocity is not None and velocity < 0
    highvol = vmr is not None and vmr > 0.25
    if score >= 0.78 and rising:
        return "●", "STRONG MOMENTUM", BUY
    if score >= 0.62 and highvol:
        return "●", "VOL SPIKE", WARN
    if score < 0.32 and falling:
        return "●", "FADING", SELL
    if highvol and score >= 0.45:
        return "◐", "ACCUMULATION?", TEXT2
    return "○", "LOW SIGNAL", TEXT2

def color_item(item: QTableWidgetItem, color: str):
    item.setForeground(QColor(color))

def right_item(text: str, color: str = TEXT) -> QTableWidgetItem:
    it = QTableWidgetItem(text)
    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    it.setForeground(QColor(color))
    return it

def center_item(text: str, color: str = TEXT) -> QTableWidgetItem:
    it = QTableWidgetItem(text)
    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    it.setForeground(QColor(color))
    return it


# ── Watchlist storage ─────────────────────────────────────────────
def load_watchlist() -> dict:
    try:
        return json.loads(WATCHLIST_F.read_text()) if WATCHLIST_F.exists() else {}
    except Exception:
        return {}

def save_watchlist(wl: dict) -> None:
    WATCHLIST_F.write_text(json.dumps(wl, indent=2))


# ── Score history ─────────────────────────────────────────────────
_score_lock    = threading.Lock()
_score_history: dict[str, list] = {}   # id -> [(ts, score)]
_MAX_HIST      = 30

def record_scores(coins: list[dict]) -> None:
    now = time.time()
    with _score_lock:
        for c in coins:
            cid   = c.get("id")
            score = c.get("trend_score")
            if not cid or score is None:
                continue
            hist = _score_history.setdefault(cid, [])
            hist.append((now, float(score)))
            if len(hist) > _MAX_HIST:
                _score_history[cid] = hist[-_MAX_HIST:]

def score_velocity(cid: str) -> float | None:
    with _score_lock:
        hist = _score_history.get(cid, [])
        return round(hist[-1][1] - hist[0][1], 4) if len(hist) >= 2 else None

def latest_score(cid: str) -> float | None:
    with _score_lock:
        hist = _score_history.get(cid, [])
        return hist[-1][1] if hist else None


# ── Sparkline widget ──────────────────────────────────────────────
class SparklineWidget(QWidget):
    def __init__(self, prices: list[float] | None = None, parent=None):
        super().__init__(parent)
        self.prices = prices or []
        self.setFixedSize(80, 26)

    def set_prices(self, prices: list[float]):
        self.prices = prices
        self.update()

    def paintEvent(self, event):
        if len(self.prices) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width() - 2, self.height() - 4
        mn, mx = min(self.prices), max(self.prices)
        rng = mx - mn or 1
        color = QColor(BUY) if self.prices[-1] >= self.prices[0] else QColor(SELL)

        # Subtle fill
        pts = []
        for i, p in enumerate(self.prices):
            x = 1 + (i / (len(self.prices) - 1)) * w
            y = 2 + (1 - (p - mn) / rng) * h
            pts.append(QPointF(x, y))

        # Draw line
        pen = QPen(color, 1.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

        # Endpoint dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(pts[-1], 2.5, 2.5)
        painter.end()


# ── Worker threads ────────────────────────────────────────────────
class ScanWorker(QThread):
    progress  = pyqtSignal(str)
    finished  = pyqtSignal(list)
    error     = pyqtSignal(str)

    def __init__(self, top_n=25, fetch=500, exclude_blue_chips=True):
        super().__init__()
        self.top_n              = top_n
        self.fetch              = fetch
        self.exclude_blue_chips = exclude_blue_chips

    def run(self):
        try:
            from market_data import get_all_market_data, fetch_trending, RateLimitError
            from analysis    import rank_coins

            self.progress.emit(f"Fetching top {self.fetch} coins from CoinGecko…")
            market_coins = get_all_market_data(top_n=self.fetch)

            self.progress.emit("Fetching trending data…")
            trending = []
            try:
                trending = fetch_trending()
            except Exception:
                pass

            self.progress.emit("Scoring coins…")
            ranked = rank_coins(
                market_coins,
                trending_coins=trending or None,
                exclude_blue_chips=self.exclude_blue_chips,
            )
            coins = ranked[:self.top_n]
            record_scores(coins)

            # Download icons in-thread (best-effort)
            self.progress.emit("Loading coin icons…")
            for c in coins:
                img_url = c.get("image") or ""
                if img_url.startswith("https://"):
                    try:
                        data = urllib.request.urlopen(img_url, timeout=4).read()
                        px   = QPixmap()
                        px.loadFromData(data)
                        c["_pixmap"] = px.scaled(
                            20, 20,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    except Exception:
                        c["_pixmap"] = None
                else:
                    c["_pixmap"] = None

            self.finished.emit(coins)

        except Exception as e:
            self.error.emit(str(e))


class PricePoller(QThread):
    updated = pyqtSignal(dict)   # {coin_id: {current_price, ...}}
    failed  = pyqtSignal(str)

    INTERVAL = 10_000  # ms

    def __init__(self, ids: list[str]):
        super().__init__()
        self.ids      = ids
        self._running = True

    def stop(self):
        self._running = False
        self.quit()

    def run(self):
        while self._running:
            if self.ids:
                try:
                    from market_data import fetch_simple_prices
                    data = fetch_simple_prices(self.ids)
                    # Attach score info
                    for cid, d in data.items():
                        d["trend_score"]    = latest_score(cid)
                        d["score_velocity"] = score_velocity(cid)
                    self.updated.emit(data)
                except Exception as e:
                    self.failed.emit(str(e))
            self.msleep(self.INTERVAL)


# ── Add to Bag dialog ─────────────────────────────────────────────
class AddToBagDialog(QDialog):
    def __init__(self, coin: dict, parent=None):
        super().__init__(parent)
        self.coin   = coin
        self.result_data = None
        self.setWindowTitle("ADD TO BAG")
        self.setMinimumWidth(380)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(16, 16, 16, 16)

        # Header
        sym   = QLabel(f"⚡ {self.coin.get('symbol','?').upper()}")
        sym.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ACCENT}; letter-spacing:3px;")
        name  = QLabel(self.coin.get("name", ""))
        name.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        price = QLabel(f"Current price: {fmt_price(self.coin.get('current_price'))}")
        price.setStyleSheet(f"color:{TEXT2}; font-size:11px; margin-bottom:4px;")
        lay.addWidget(sym)
        lay.addWidget(name)
        lay.addWidget(price)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};"); lay.addWidget(sep)

        # Position group
        pos_box = QGroupBox("POSITION  (optional)")
        pf = QFormLayout(pos_box)
        pf.setSpacing(8)
        self.in_price  = QDoubleSpinBox(); self.in_price.setDecimals(10); self.in_price.setMaximum(1e9)
        self.in_price.setValue(self.coin.get("current_price") or 0)
        self.in_amount = QDoubleSpinBox(); self.in_amount.setDecimals(2); self.in_amount.setMaximum(1e15)
        self.in_amount.setValue(0)
        pf.addRow("Entry price (USD):", self.in_price)
        pf.addRow("Number of coins:",  self.in_amount)
        lay.addWidget(pos_box)

        # Alert group
        alert_box = QGroupBox("ALERTS  (optional)")
        af = QFormLayout(alert_box)
        af.setSpacing(8)
        self.in_alert_price = QDoubleSpinBox(); self.in_alert_price.setDecimals(10); self.in_alert_price.setMaximum(1e9)
        self.in_alert_score = QDoubleSpinBox(); self.in_alert_score.setDecimals(2)
        self.in_alert_score.setMinimum(0); self.in_alert_score.setMaximum(1); self.in_alert_score.setSingleStep(0.05)
        af.addRow("🔴 Alert if price drops below:", self.in_alert_price)
        af.addRow("🟡 Alert if score drops below:", self.in_alert_score)
        lay.addWidget(alert_box)

        # Risk notice
        risk = QLabel("⚠  Signals are momentum indicators only.\nNot buy/sell advice. Shitcoins can go to zero.")
        risk.setStyleSheet(f"color:{SELL}; font-size:10px; padding:6px 0;")
        risk.setWordWrap(True)
        lay.addWidget(risk)

        # Buttons
        btns = QHBoxLayout()
        save = QPushButton("ADD TO BAG")
        save.setObjectName("scan-btn")
        save.clicked.connect(self._save)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        btns.addWidget(save); btns.addWidget(cancel)
        lay.addLayout(btns)

    def _save(self):
        wl = load_watchlist()
        wl[self.coin["id"]] = {
            "id":         self.coin["id"],
            "symbol":     self.coin.get("symbol","").upper(),
            "name":       self.coin.get("name",""),
            "image":      self.coin.get("image",""),
            "buyPrice":   self.in_price.value()  or None,
            "buyAmount":  self.in_amount.value() or None,
            "alertPrice": self.in_alert_price.value() or None,
            "alertScore": self.in_alert_score.value() or None,
            "addedAt":    time.time(),
        }
        save_watchlist(wl)
        self.accept()


# ── Settings dialog ───────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self.setMinimumWidth(420)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(16, 16, 16, 16)

        title = QLabel("⚙  API KEYS")
        title.setStyleSheet(f"color:{ACCENT}; font-size:14px; font-weight:bold; letter-spacing:3px;")
        lay.addWidget(title)

        tabs = QTabWidget()

        # ── AI tab ──
        ai_w = QWidget(); af = QFormLayout(ai_w); af.setSpacing(10); af.setContentsMargins(10,10,10,10)
        note = QLabel("Add one key to enable AI commentary on scan results.\nKeys are stored locally in ~/.shitcoiner/.env")
        note.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        note.setWordWrap(True)
        self.openai_key    = QLineEdit(); self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("sk-...")
        self.anthropic_key = QLineEdit(); self.anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key.setPlaceholderText("sk-ant-...")
        af.addRow(note)
        af.addRow("OpenAI API Key:",    self.openai_key)
        af.addRow("Anthropic API Key:", self.anthropic_key)
        tabs.addTab(ai_w, "AI COMMENTARY")

        # ── Exchange tab ──
        ex_w = QWidget(); ef = QFormLayout(ex_w); ef.setSpacing(10); ef.setContentsMargins(10,10,10,10)
        warn = QLabel("⚠  This app does NOT trade. Future use only.\nNever share API keys. Use read-only keys only.")
        warn.setStyleSheet(f"color:{SELL}; font-size:11px;")
        warn.setWordWrap(True)
        self.binance_key    = QLineEdit(); self.binance_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.binance_secret = QLineEdit(); self.binance_secret.setEchoMode(QLineEdit.EchoMode.Password)
        ef.addRow(warn)
        ef.addRow("Binance API Key:", self.binance_key)
        ef.addRow("Binance Secret:",  self.binance_secret)
        tabs.addTab(ex_w, "EXCHANGE")

        lay.addWidget(tabs)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        lay.addWidget(self._status)

        btns = QHBoxLayout()
        save   = QPushButton("SAVE KEYS"); save.setObjectName("scan-btn"); save.clicked.connect(self._save)
        cancel = QPushButton("CLOSE"); cancel.clicked.connect(self.accept)
        btns.addWidget(save); btns.addWidget(cancel)
        lay.addLayout(btns)

    def _save(self):
        try:
            from dotenv import set_key
        except ImportError:
            self._status.setStyleSheet(f"color:{SELL};")
            self._status.setText("python-dotenv not installed — run: pip install python-dotenv")
            return

        saved = []
        for env_key, v in [
            ("OPENAI_API_KEY",    self.openai_key.text().strip()),
            ("ANTHROPIC_API_KEY", self.anthropic_key.text().strip()),
            ("BINANCE_API_KEY",   self.binance_key.text().strip()),
            ("BINANCE_SECRET",    self.binance_secret.text().strip()),
        ]:
            if v:
                if not ENV_PATH.exists(): ENV_PATH.touch()
                set_key(str(ENV_PATH), env_key, v)
                os.environ[env_key] = v
                saved.append(env_key)

        if not ENV_PATH.exists():
            self._status.setStyleSheet(f"color:{SELL};")
            self._status.setText("Enter at least one key to save.")
            return

        try: ENV_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception: pass

        for f in [self.openai_key, self.anthropic_key, self.binance_key, self.binance_secret]:
            f.clear()

        self._status.setStyleSheet(f"color:{BUY};")
        self._status.setText(f"Saved: {', '.join(saved) or 'nothing new'}")


# ── My Bag panel ──────────────────────────────────────────────────
class BagPanel(QWidget):
    request_remove = pyqtSignal(str)

    COLS = ["COIN", "PRICE", "24H %", "SIGNAL", "SCORE", "P&L", "ALERTS", ""]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._price_cache: dict[str, dict] = {}
        self._fired: set[str]              = set()
        self._tray: QSystemTrayIcon | None = None
        self._build()

    def set_tray(self, tray: QSystemTrayIcon):
        self._tray = tray

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        self._title = QLabel("🎒  MY BAG")
        self._title.setStyleSheet(f"color:{ACCENT}; font-weight:bold; font-size:13px; letter-spacing:2px;")
        self._poll_lbl = QLabel("")
        self._poll_lbl.setStyleSheet(f"color:{TEXT2}; font-size:10px;")
        hdr.addWidget(self._title)
        hdr.addStretch()
        hdr.addWidget(self._poll_lbl)
        lay.addLayout(hdr)

        self._table = QTableWidget(0, len(self.COLS))
        self._table.setHorizontalHeaderLabels(self.COLS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, len(self.COLS)):
            self._table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setMaximumHeight(160)
        lay.addWidget(self._table)

        self._empty = QLabel("No coins in bag  —  star a coin from the scan results")
        self._empty.setStyleSheet(f"color:{TEXT2}; font-size:11px; padding:10px 0; letter-spacing:1px;")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._empty)
        self._refresh_view()

    def update_prices(self, data: dict, ts: str = ""):
        self._price_cache.update(data)
        self._poll_lbl.setText(f"Updated {ts}" if ts else "")
        self._refresh_view()
        self._check_alerts()

    def refresh(self):
        self._refresh_view()

    def _refresh_view(self):
        wl = load_watchlist()
        if not wl:
            self._table.setVisible(False)
            self._empty.setVisible(True)
            return
        self._table.setVisible(True)
        self._empty.setVisible(False)

        self._table.setRowCount(0)
        for cid, pos in wl.items():
            px    = self._price_cache.get(cid, {})
            price = px.get("current_price")
            p24   = px.get("price_change_percentage_24h")
            vmr   = px.get("vol_mcap_ratio")
            score = px.get("trend_score") or latest_score(cid)
            vel   = px.get("score_velocity") or score_velocity(cid)

            dot, label, color = get_signal(score, vel, vmr)
            p24_color  = BUY if (p24 or 0) >= 0 else SELL

            row = self._table.rowCount()
            self._table.insertRow(row)

            # Coin
            coin_txt = f"{pos.get('symbol','?')}  {pos.get('name','')[:18]}"
            self._table.setItem(row, 0, QTableWidgetItem(coin_txt))

            # Price
            self._table.setItem(row, 1, right_item(fmt_price(price)))

            # 24h%
            self._table.setItem(row, 2, right_item(fmt_pct(p24), p24_color))

            # Signal
            sig_item = QTableWidgetItem(f"  {dot}  {label}")
            sig_item.setForeground(QColor(color))
            self._table.setItem(row, 3, sig_item)

            # Score + velocity
            vel_arrow = ("  ▲" if vel > 0.005 else "  ▼" if vel < -0.005 else "") if vel is not None else ""
            vel_color = BUY if (vel or 0) > 0.005 else (SELL if (vel or 0) < -0.005 else TEXT2)
            sc_item   = QTableWidgetItem(fmt_score(score) + vel_arrow)
            sc_item.setForeground(QColor(vel_color if vel_arrow else ACCENT))
            self._table.setItem(row, 4, sc_item)

            # P&L
            pnl_txt = "—"; pnl_color = TEXT2
            bp, ba = pos.get("buyPrice"), pos.get("buyAmount")
            if bp and ba and price is not None:
                pnl     = (price - bp) * ba
                pnl_pct = ((price / bp) - 1) * 100
                sign    = "+" if pnl >= 0 else ""
                pnl_txt = f"{sign}${pnl:,.2f}  ({sign}{pnl_pct:.1f}%)"
                pnl_color = BUY if pnl >= 0 else SELL
            self._table.setItem(row, 5, right_item(pnl_txt, pnl_color))

            # Alerts
            parts = []
            if pos.get("alertPrice"): parts.append(f"P<{fmt_price(pos['alertPrice'])}")
            if pos.get("alertScore"): parts.append(f"S<{pos['alertScore']}")
            alert_item = QTableWidgetItem("🔔 " + "  ".join(parts) if parts else "—")
            alert_item.setForeground(QColor(WARN if parts else TEXT2))
            self._table.setItem(row, 6, alert_item)

            # Remove button
            rm = QPushButton("✕"); rm.setObjectName("remove-btn")
            rm.clicked.connect(lambda _, i=cid: self._remove(i))
            self._table.setCellWidget(row, 7, rm)

        self._table.resizeRowsToContents()

    def _remove(self, cid: str):
        wl = load_watchlist()
        wl.pop(cid, None)
        save_watchlist(wl)
        self._refresh_view()

    def _check_alerts(self):
        wl = load_watchlist()
        for cid, pos in wl.items():
            px    = self._price_cache.get(cid, {})
            price = px.get("current_price")
            score = px.get("trend_score") or latest_score(cid)
            sym   = pos.get("symbol", cid)

            if pos.get("alertPrice") and price is not None and price < pos["alertPrice"]:
                key = f"price_{cid}_{pos['alertPrice']}"
                if key not in self._fired:
                    self._fired.add(key)
                    self._notify(f"⚠ {sym} PRICE ALERT",
                                 f"Dropped to {fmt_price(price)} (below {fmt_price(pos['alertPrice'])})")

            if pos.get("alertScore") and score is not None and score < pos["alertScore"]:
                key = f"score_{cid}_{pos['alertScore']}"
                if key not in self._fired:
                    self._fired.add(key)
                    self._notify(f"📉 {sym} MOMENTUM DROP",
                                 f"Score fell to {fmt_score(score)} (below {pos['alertScore']})")

    def _notify(self, title: str, msg: str):
        if self._tray and QSystemTrayIcon.isSystemTrayAvailable():
            self._tray.showMessage(title, msg, QSystemTrayIcon.MessageIcon.Warning, 5000)


# ── Main window ───────────────────────────────────────────────────
SCAN_COLS = ["#", "☆", "", "COIN", "7D CHART", "PRICE", "24H %", "V/MCAP", "SIGNAL", "SCORE", "CAP #"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHITCOINER")
        self.setMinimumSize(1000, 700)
        self._coins: list[dict] = []
        self._poller: PricePoller | None = None
        self._scan_worker: ScanWorker | None = None
        self._build()
        self._setup_tray()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet(f"background:{BG2}; border-bottom:1px solid {BORDER};")
        hdr_frame.setFixedHeight(56)
        hdr_lay = QHBoxLayout(hdr_frame)
        hdr_lay.setContentsMargins(18, 0, 18, 0)

        name_lbl = QLabel("⚡  SHITCOINER")
        name_lbl.setStyleSheet(
            f"color:{ACCENT}; font-size:20px; font-weight:bold; letter-spacing:4px;"
        )
        sub_lbl = QLabel("MOMENTUM SCANNER  //  NOT FINANCIAL ADVICE")
        sub_lbl.setStyleSheet(f"color:{TEXT2}; font-size:9px; letter-spacing:2px;")

        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        name_col.addWidget(name_lbl)
        name_col.addWidget(sub_lbl)

        settings_btn = QPushButton("⚙  SETTINGS")
        settings_btn.clicked.connect(self._open_settings)
        about_btn = QPushButton("?")
        about_btn.setFixedWidth(36)
        about_btn.clicked.connect(self._show_about)

        hdr_lay.addLayout(name_col)
        hdr_lay.addStretch()
        hdr_lay.addWidget(settings_btn)
        hdr_lay.addWidget(about_btn)
        root.addWidget(hdr_frame)

        # ── Toolbar ──────────────────────────────────────────────
        tb_frame = QFrame()
        tb_frame.setStyleSheet(f"background:{BG2}; border-bottom:1px solid {BORDER}; padding:6px 0;")
        tb_lay = QHBoxLayout(tb_frame)
        tb_lay.setContentsMargins(14, 4, 14, 4)
        tb_lay.setSpacing(10)

        self._scan_btn = QPushButton("▶  RUN SCAN")
        self._scan_btn.setObjectName("scan-btn")
        self._scan_btn.clicked.connect(self._run_scan)

        self._ai_btn = QPushButton("🤖  AI TAKE")
        self._ai_btn.clicked.connect(self._get_ai)

        sep1 = QFrame(); sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color:{BORDER}; max-width:1px;")

        topn_lbl = QLabel("TOP:")
        topn_lbl.setStyleSheet(f"color:{TEXT2};")
        self._topn = QSpinBox()
        self._topn.setRange(5, 100); self._topn.setValue(25); self._topn.setFixedWidth(58)

        fetch_lbl = QLabel("FETCH:")
        fetch_lbl.setStyleSheet(f"color:{TEXT2};")
        self._fetch = QComboBox(); self._fetch.setFixedWidth(90)
        self._fetch.addItems(["TOP 300", "TOP 500"])
        self._fetch.setCurrentIndex(1)

        self._bluechip = QCheckBox("INCLUDE BLUE CHIPS")

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"color:{BORDER}; max-width:1px;")

        self._status_lbl = QLabel("READY")
        self._status_lbl.setStyleSheet(f"color:{TEXT2}; font-size:11px; letter-spacing:1px;")

        for w in [self._scan_btn, self._ai_btn, sep1, topn_lbl, self._topn,
                  fetch_lbl, self._fetch, self._bluechip, sep2, self._status_lbl]:
            tb_lay.addWidget(w)
        tb_lay.addStretch()
        root.addWidget(tb_frame)

        # ── Content area ─────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(14, 10, 14, 10)
        c_lay.setSpacing(12)

        # Bag panel
        self._bag = BagPanel()
        c_lay.addWidget(self._bag)

        sep3 = QFrame(); sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet(f"color:{BORDER}; max-height:1px; margin:2px 0;")
        c_lay.addWidget(sep3)

        # Scan results label
        self._results_lbl = QLabel("SCAN RESULTS")
        self._results_lbl.setStyleSheet(
            f"color:{TEXT2}; font-size:10px; letter-spacing:3px; padding:2px 0;"
        )
        c_lay.addWidget(self._results_lbl)

        # Scan table
        self._table = QTableWidget(0, len(SCAN_COLS))
        self._table.setHorizontalHeaderLabels(SCAN_COLS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setSortingEnabled(False)

        hv = self._table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # #
        hv.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # star
        hv.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # icon
        hv.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # name
        hv.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)             # chart
        self._table.setColumnWidth(4, 88)
        for c in range(5, len(SCAN_COLS)):
            hv.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)

        c_lay.addWidget(self._table, 1)

        # AI panel
        self._ai_lbl = QLabel("AI COMMENTARY")
        self._ai_lbl.setStyleSheet(f"color:{TEXT2}; font-size:10px; letter-spacing:3px; padding:2px 0;")
        self._ai_txt = QTextEdit()
        self._ai_txt.setReadOnly(True)
        self._ai_txt.setMaximumHeight(120)
        self._ai_txt.setPlaceholderText(
            "Run a scan, add an API key in Settings, then click 'AI TAKE' for plain-English shitcoin commentary."
        )
        self._ai_txt.setVisible(False)
        self._ai_lbl.setVisible(False)
        c_lay.addWidget(self._ai_lbl)
        c_lay.addWidget(self._ai_txt)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(scroll, 1)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._sb_lbl = QLabel("SHITCOINER  //  NOT FINANCIAL ADVICE  //  USE AT YOUR OWN RISK")
        self._sb_lbl.setStyleSheet(f"color:{TEXT2}; letter-spacing:1px;")
        sb.addPermanentWidget(self._sb_lbl)

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        px = QPixmap(16, 16)
        px.fill(QColor(ACCENT))
        self._tray = QSystemTrayIcon(QIcon(px), self)
        menu = QMenu()
        act_show = QAction("Show SHITCOINER", self)
        act_show.triggered.connect(self.show)
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(QApplication.quit)
        menu.addAction(act_show); menu.addAction(act_quit)
        self._tray.setContextMenu(menu)
        self._tray.setToolTip("SHITCOINER")
        self._tray.show()
        self._bag.set_tray(self._tray)

    def _set_status(self, msg: str, color: str = TEXT2):
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(f"color:{color}; font-size:11px; letter-spacing:1px;")

    def _run_scan(self):
        if self._scan_worker and self._scan_worker.isRunning():
            return
        self._scan_btn.setEnabled(False)
        self._set_status("SCANNING…", WARN)
        self._table.setRowCount(0)

        fetch_val = 300 if self._fetch.currentIndex() == 0 else 500
        self._scan_worker = ScanWorker(
            top_n=self._topn.value(),
            fetch=fetch_val,
            exclude_blue_chips=not self._bluechip.isChecked(),
        )
        self._scan_worker.progress.connect(lambda m: self._set_status(m, WARN))
        self._scan_worker.finished.connect(self._on_scan_done)
        self._scan_worker.error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _on_scan_done(self, coins: list[dict]):
        self._coins = coins
        self._scan_btn.setEnabled(True)
        self._set_status(f"DONE  —  {len(coins)} COINS RANKED", BUY)
        self._results_lbl.setText(f"SCAN RESULTS  [{len(coins)} coins]")
        self._render_table(coins)
        self._start_poller()

    def _on_scan_error(self, msg: str):
        self._scan_btn.setEnabled(True)
        self._set_status(f"ERROR: {msg[:80]}", SELL)

    def _render_table(self, coins: list[dict]):
        self._table.setRowCount(0)
        wl = load_watchlist()

        for c in coins:
            cid    = c.get("id", "")
            sym    = c.get("symbol","").upper()
            name   = c.get("name","")[:22]
            price  = c.get("current_price")
            p24    = c.get("price_change_percentage_24h")
            vmr    = c.get("vol_mcap_ratio")
            score  = c.get("trend_score")
            vel    = score_velocity(cid)
            rank   = c.get("rank", 0)
            cap_r  = c.get("market_cap_rank")
            is_new = c.get("newly_listed", False)

            dot, label, sig_color = get_signal(score, vel, vmr)
            p24_color = BUY if (p24 or 0) >= 0 else SELL
            vel_arrow = ("  ▲" if (vel or 0) > 0.005 else "  ▼" if (vel or 0) < -0.005 else "")

            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 34)

            # # rank
            self._table.setItem(row, 0, center_item(str(rank), ACCENT))

            # ☆ star
            star_btn = QPushButton("⭐" if cid in wl else "☆")
            star_btn.setObjectName("star-btn")
            if cid in wl: star_btn.setProperty("starred", "true")
            star_btn.clicked.connect(lambda _, ci=cid, co=c: self._toggle_bag(ci, co))
            self._table.setCellWidget(row, 1, star_btn)

            # Icon
            icon_lbl = QLabel()
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if c.get("_pixmap"):
                icon_lbl.setPixmap(c["_pixmap"])
            else:
                icon_lbl.setText(sym[:2])
                icon_lbl.setStyleSheet(f"color:{ACCENT}; font-size:10px; font-weight:bold;")
            self._table.setCellWidget(row, 2, icon_lbl)

            # Name
            new_tag = "  [NEW]" if is_new else ""
            name_item = QTableWidgetItem(f"{sym}{new_tag}\n{name}")
            name_item.setForeground(QColor(TEXT))
            self._table.setItem(row, 3, name_item)

            # Sparkline
            sp = SparklineWidget(c.get("sparkline", []))
            sp.setStyleSheet(f"background:{BG};")
            sp_wrap = QWidget()
            sp_lay  = QHBoxLayout(sp_wrap)
            sp_lay.setContentsMargins(4, 0, 4, 0)
            sp_lay.addWidget(sp)
            self._table.setCellWidget(row, 4, sp_wrap)

            # Price
            self._table.setItem(row, 5, right_item(fmt_price(price)))

            # 24h %
            self._table.setItem(row, 6, right_item(fmt_pct(p24), p24_color))

            # V/MCap
            self._table.setItem(row, 7, right_item(fmt_vmr(vmr), WARN))

            # Signal
            sig_item = QTableWidgetItem(f"  {dot}  {label}")
            sig_item.setForeground(QColor(sig_color))
            self._table.setItem(row, 8, sig_item)

            # Score
            sc_item = QTableWidgetItem(fmt_score(score) + vel_arrow)
            sc_item.setForeground(QColor(
                BUY if vel_arrow == "  ▲" else (SELL if vel_arrow == "  ▼" else ACCENT)
            ))
            sc_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 9, sc_item)

            # Cap rank
            self._table.setItem(row, 10, center_item(f"#{cap_r}" if cap_r else "—", TEXT2))

        self._table.resizeRowsToContents()

    def _toggle_bag(self, cid: str, coin: dict):
        wl = load_watchlist()
        if cid in wl:
            wl.pop(cid)
            save_watchlist(wl)
            self._bag.refresh()
            self._render_table(self._coins)
        else:
            dlg = AddToBagDialog(coin, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._bag.refresh()
                self._render_table(self._coins)
                self._start_poller()

    def _start_poller(self):
        wl = load_watchlist()
        if not wl:
            return
        if self._poller and self._poller.isRunning():
            self._poller.ids = list(wl.keys())
            return
        self._poller = PricePoller(list(wl.keys()))
        self._poller.updated.connect(self._on_prices)
        self._poller.failed.connect(lambda e: self._set_status(f"POLL ERR: {e[:60]}", SELL))
        self._poller.start()

    def _on_prices(self, data: dict):
        ts = time.strftime("%H:%M:%S")
        self._bag.update_prices(data, ts)
        # update wl ids in poller
        if self._poller:
            self._poller.ids = list(load_watchlist().keys())

    def _get_ai(self):
        if not self._coins:
            QMessageBox.information(self, "SHITCOINER", "Run a scan first.")
            return
        self._ai_btn.setEnabled(False)
        self._set_status("ASKING AI…", WARN)
        self._ai_txt.setVisible(True)
        self._ai_lbl.setVisible(True)
        self._ai_txt.setPlainText("Thinking…")

        coins_snapshot = list(self._coins)

        class _AIWorker(QThread):
            done = pyqtSignal(str, str)   # text, error
            def run(self_inner):
                try:
                    from ai_commentary import get_ai_commentary
                    text, err = get_ai_commentary(coins_snapshot)
                    self_inner.done.emit(text or "", err or "")
                except Exception as e:
                    self_inner.done.emit("", str(e))

        self._ai_worker = _AIWorker(self)
        def _on_ai_done(text, err):
            self._ai_btn.setEnabled(True)
            if err:
                self._ai_txt.setPlainText(f"Error: {err}")
                self._set_status("AI FAILED", SELL)
            else:
                self._ai_txt.setPlainText(text)
                self._set_status("AI DONE", BUY)
        self._ai_worker.done.connect(_on_ai_done)
        self._ai_worker.start()

    def _open_settings(self):
        SettingsDialog(self).exec()

    def _show_about(self):
        QMessageBox.about(self, "SHITCOINER",
            "SHITCOINER  v2.0\n\n"
            "Shitcoin momentum scanner.\n"
            "Data from CoinGecko (free API).\n\n"
            "NOT FINANCIAL ADVICE.\n"
            "Shitcoins can go to zero.\n"
            "Only risk money you can afford to lose entirely."
        )

    def closeEvent(self, event):
        if self._poller and self._poller.isRunning():
            self._poller.stop()
            self._poller.wait(1000)
        event.accept()


# ── Entry point ───────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SHITCOINER")
    app.setStyleSheet(QSS)

    # Force dark palette everywhere (especially for native dialogs)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(BG))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Base,            QColor(BG2))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(SURF))
    pal.setColor(QPalette.ColorRole.Text,            QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Button,          QColor(BG2))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(BG))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
