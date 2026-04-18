import os
import platform
import sys
import time
import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    from . import (
        ConfigManager,
        LangManager,
        LoggingService,
        PayloadCatalogService,
        PayloadCatalogNetworkError,
        SenderFactory,
        SocatSender,
        start_daemon_thread,
        validate_endpoint,
    )
    from .language_service import LanguageService
    from .ui_theme_service import (
        BUTTON_GRID_LAYOUT,
        IP_PORT_GRID_LAYOUT,
        LAYOUT_METRICS,
        UiThemeService,
    )
    from ..models.version import __version__
except ImportError:
    from services import (
        ConfigManager,
        LangManager,
        LoggingService,
        PayloadCatalogService,
        PayloadCatalogNetworkError,
        SenderFactory,
        SocatSender,
        start_daemon_thread,
        validate_endpoint,
    )
    from services.language_service import LanguageService
    from services.ui_theme_service import (
        BUTTON_GRID_LAYOUT,
        IP_PORT_GRID_LAYOUT,
        LAYOUT_METRICS,
        UiThemeService,
    )
    from models.version import __version__


def _get_user_data_dir():
    system = platform.system()
    if system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")
    path = os.path.join(base, "PS_MultiInjector")
    os.makedirs(path, exist_ok=True)
    return path


class _ImageCache:
    """Cache for PIL Image objects to avoid redundant disk I/O and processing."""

    def __init__(self):
        self._cache = {}

    def get_image(self, image_path, size=None):
        """Load image from cache or disk. Optional resize if size=(w, h)."""
        cache_key = (image_path, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from PIL import Image

            img = Image.open(image_path)
            if size:
                img = img.resize(size, Image.LANCZOS)
            self._cache[cache_key] = img
            return img
        except Exception as exc:
            logging_service.error("Failed to load image %s: %s", image_path, exc)
            return None

    def clear(self):
        """Clear the cache (useful for testing)."""
        self._cache.clear()


class _PerformanceTracker:
    """Helper to track startup performance milestones."""

    def __init__(self, logger):
        self.logger = logger
        self._start_time = time.time()
        self._marks = {}

    def mark(self, name):
        """Record a timing milestone."""
        elapsed = time.time() - self._start_time
        self._marks[name] = elapsed
        self.logger.debug("PERF [%.2fs] %s", elapsed, name)

    def report(self):
        """Log all recorded milestones."""
        if self._marks:
            self.logger.info("Startup performance: %s", self._marks)


class AppDependencies:
    def __init__(
        self,
        language_service,
        logging_service,
        theme_service,
        endpoint_validator,
        thread_runner,
        sender_factory,
        config_manager_cls,
        lang_manager_cls,
        payload_catalog_service_cls,
    ):
        self.language_service = language_service
        self.logging_service = logging_service
        self.theme_service = theme_service
        self.endpoint_validator = endpoint_validator
        self.thread_runner = thread_runner
        self.sender_factory = sender_factory
        self.config_manager_cls = config_manager_cls
        self.lang_manager_cls = lang_manager_cls
        self.payload_catalog_service_cls = payload_catalog_service_cls


def build_default_dependencies():
    language_service = LanguageService()
    logging_service = LoggingService(platform.system)
    return AppDependencies(
        language_service=language_service,
        logging_service=logging_service,
        theme_service=UiThemeService(language_service, platform.system),
        endpoint_validator=validate_endpoint,
        thread_runner=start_daemon_thread,
        sender_factory=SenderFactory(),
        config_manager_cls=ConfigManager,
        lang_manager_cls=LangManager,
        payload_catalog_service_cls=PayloadCatalogService,
    )


PAYLOADS_URL = (
    "https://raw.githubusercontent.com/JRRN/PsX-Payload-Multi-Injector/main/payloads/payloads.json"
)
SRC_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = getattr(sys, "_MEIPASS", SRC_DIR)
USER_DATA_DIR = _get_user_data_dir()
CONFIG_PATH = os.path.join(USER_DATA_DIR, "config.ini")
LANG_DIR = os.path.join(BASE_DIR, "lang")

dependencies = build_default_dependencies()
language_service = dependencies.language_service
ui_theme_service = dependencies.theme_service
logging_service = dependencies.logging_service
_LOG_FILE = logging_service.setup()

# Image cache for efficient PIL usage
_image_cache = _ImageCache()
# Performance tracking for startup optimization
_perf_tracker = _PerformanceTracker(logging_service)


def ui_font_family(lang_code, platform_system=None):
    system_resolver = platform_system or platform.system
    service = UiThemeService(language_service, system_resolver)
    return service.ui_font_family(lang_code)


def ui_theme_tokens(lang_code, platform_system=None):
    system_resolver = platform_system or platform.system
    service = UiThemeService(language_service, system_resolver)
    return service.ui_theme_tokens(lang_code)


class _LogoWidget(QWidget):
    """Fallback circular PS logo drawn with QPainter when image file is absent."""

    def __init__(self, accent_color, accent_text_color, font_family, parent=None):
        super().__init__(parent)
        self._accent = QColor(accent_color)
        self._accent_text = QColor(accent_text_color)
        self._font_family = font_family
        self.setFixedSize(48, 48)

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._accent)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 40, 40)
        painter.setPen(self._accent_text)
        font = QFont(self._font_family, 18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "PS")


class App(QMainWindow):
    # Signals for thread-safe UI updates from background worker threads
    _sig_payloads_loaded = Signal(object, object)
    _sig_payload_failed = Signal(object)
    _sig_send_ok = Signal(str, str)
    _sig_send_fail = Signal(object)
    _sig_icon_loaded = Signal(str)
    _sig_injecting_status = Signal(str)

    def __init__(
        self,
        language_service=None,
        endpoint_validator=None,
        thread_runner=None,
        sender_factory=None,
        logging_service=None,
        theme_service=None,
        dependencies=None,
    ):
        super().__init__()

        deps = dependencies or globals()["dependencies"]
        self.logger = logging_service or deps.logging_service
        self.logger.debug("App.__init__: starting")
        _perf_tracker.mark("qt.init_start")

        self.language_service = language_service or deps.language_service
        self.theme_service = theme_service or deps.theme_service
        self.endpoint_validator = endpoint_validator or deps.endpoint_validator
        self.thread_runner = thread_runner or deps.thread_runner
        self.sender_factory = sender_factory or deps.sender_factory

        self.logger.debug("App.__init__: ConfigManager")
        self.config_manager = deps.config_manager_cls(CONFIG_PATH)
        _perf_tracker.mark("config_manager")

        self.logger.debug("App.__init__: LangManager")
        self.lang_manager = deps.lang_manager_cls(
            LANG_DIR,
            self.config_manager.get_language(),
        )
        _perf_tracker.mark("lang_manager")

        if self.config_manager.get_language() != self.lang_manager.lang_code:
            self.config_manager.set_language(self.lang_manager.lang_code)

        self.logger.debug("App.__init__: PayloadCatalogService")
        self.payload_repo = deps.payload_catalog_service_cls(PAYLOADS_URL)
        _perf_tracker.mark("payload_repo")

        self.theme_tokens = ui_theme_tokens(self.lang_manager.lang_code)
        _perf_tracker.mark("theme_tokens")

        # Wire signals for thread-safe callbacks
        self._sig_payloads_loaded.connect(self._on_payloads_loaded)
        self._sig_payload_failed.connect(self._on_payload_load_failed)
        self._sig_send_ok.connect(self._on_send_succeeded)
        self._sig_send_fail.connect(self._on_send_failed)
        self._sig_icon_loaded.connect(self._set_window_icon)
        self._sig_injecting_status.connect(self._set_injecting_status)

        self.ps4_payloads = []
        self.ps5_payloads = []
        self._is_sending = False
        self._is_loading_payloads = False

        self.setWindowTitle(f"{self.lang_manager.t('title')} v{__version__}")
        self.setMinimumSize(520, 340)
        self.resize(520, 340)
        self.setFixedHeight(340)

        _perf_tracker.mark("before_create_widgets")
        self._create_central_widget()
        self.create_widgets()
        _perf_tracker.mark("after_create_widgets")

        self._apply_stylesheet()

        # Defer icon loading to background (non-blocking)
        self._load_icon_async()

        self.load_payloads_async()
        _perf_tracker.mark("payloads_async_started")

        self.logger.debug("App initialized successfully")
        _perf_tracker.report()

    def _create_central_widget(self):
        """Set up the central widget and main vertical layout."""
        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._main_layout = QVBoxLayout(self._central)
        self._main_layout.setContentsMargins(0, 4, 0, 4)
        self._main_layout.setSpacing(4)

    def _apply_stylesheet(self):
        self.theme_service.apply_theme_styles(self, self.theme_tokens)

    def _load_icon_async(self):
        """Load app icon path in background thread; set via signal in main thread."""
        def load_icon():
            try:
                if platform.system() == "Windows":
                    ico_path = os.path.join(SRC_DIR, "assets", "app.ico")
                    if os.path.exists(ico_path):
                        self._sig_icon_loaded.emit(ico_path)
                else:
                    png_path = os.path.join(SRC_DIR, "assets", "logo.png")
                    if os.path.exists(png_path):
                        self._sig_icon_loaded.emit(png_path)
            except Exception:
                pass

        self.thread_runner(load_icon)

    def _set_window_icon(self, icon_path):
        """Set window icon from path (called in main thread via signal)."""
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.setWindowIcon(icon)
        except Exception:
            pass

    def _render_default_logo(self, parent_layout):
        """Add a fallback circular PS logo widget to a layout."""
        logo_widget = _LogoWidget(
            self.theme_tokens["accent"],
            self.theme_tokens["accent_text"],
            self.theme_tokens["font_family"],
        )
        parent_layout.addWidget(logo_widget)

    def create_widgets(self):
        self.theme_tokens = self.theme_service.ui_theme_tokens(self.lang_manager.lang_code)
        self._build_top_bar()
        self._build_title()
        self._build_content()
        self._build_status()

    def _build_top_bar(self):
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(
            20,
            LAYOUT_METRICS["top_bar_pady"][0],
            20,
            LAYOUT_METRICS["top_bar_pady"][1],
        )

        icon_frame_layout = QHBoxLayout()
        icon_frame_layout.setContentsMargins(0, 0, 0, 0)
        logo_loaded = False
        try:
            logo_path = os.path.join(SRC_DIR, "assets", "logo.png")
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path).scaled(
                    48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                if not pixmap.isNull():
                    lbl_logo = QLabel()
                    lbl_logo.setPixmap(pixmap)
                    icon_frame_layout.addWidget(lbl_logo)
                    logo_loaded = True
        except Exception:
            pass

        if not logo_loaded:
            self._render_default_logo(icon_frame_layout)

        icon_widget = QWidget()
        icon_widget.setLayout(icon_frame_layout)
        top_layout.addWidget(icon_widget)
        top_layout.addStretch()

        self.lang_codes = self.language_service.discover_lang_codes(LANG_DIR)
        current_language = self.lang_manager.lang_code
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(
            self.language_service.language_selector_values(self.lang_codes)
        )
        if current_language in self.lang_codes:
            self.lang_combo.setCurrentIndex(self.lang_codes.index(current_language))
        else:
            self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setMinimumWidth(180)
        self.lang_combo.activated.connect(self.on_lang_selected)
        top_layout.addWidget(self.lang_combo)

        self._main_layout.addWidget(top_bar)

    def _build_title(self):
        self.lbl_title = QLabel(f"{self.lang_manager.t('title')} v{__version__}")
        self.lbl_title.setObjectName("header")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self._main_layout.addWidget(self.lbl_title)

    def _build_content(self):
        content_widget = QWidget()
        self.content_layout = QGridLayout(content_widget)
        self.content_layout.setContentsMargins(24, 0, 24, 0)
        self.content_layout.setColumnStretch(1, 1)

        self._build_endpoint_inputs()
        self._build_payload_selectors()
        self._build_action_buttons()
        self._build_socat_option()

        self._main_layout.addWidget(content_widget)

    def _build_endpoint_inputs(self):
        self.lbl_ip = QLabel(self.lang_manager.t("ip_label"))
        self.content_layout.addWidget(
            self.lbl_ip,
            IP_PORT_GRID_LAYOUT["ip_label"]["row"],
            IP_PORT_GRID_LAYOUT["ip_label"]["column"],
        )

        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("0.0.0.0")
        saved_ip = (self.config_manager.get_ip() or "").strip()
        if saved_ip:
            self.txt_ip.setText(saved_ip)
        self.content_layout.addWidget(
            self.txt_ip,
            IP_PORT_GRID_LAYOUT["ip_input"]["row"],
            IP_PORT_GRID_LAYOUT["ip_input"]["column"],
        )

        self.lbl_port = QLabel(self.lang_manager.t("port_label"))
        self.content_layout.addWidget(
            self.lbl_port,
            IP_PORT_GRID_LAYOUT["port_label"]["row"],
            IP_PORT_GRID_LAYOUT["port_label"]["column"],
        )

        self.txt_port = QLineEdit()
        self.txt_port.setMaximumWidth(80)
        self.content_layout.addWidget(
            self.txt_port,
            IP_PORT_GRID_LAYOUT["port_input"]["row"],
            IP_PORT_GRID_LAYOUT["port_input"]["column"],
            Qt.AlignLeft,
        )

    def _build_payload_selectors(self):
        self.lbl_ps4 = QLabel(self.lang_manager.t("ps4_label"))
        self.content_layout.addWidget(self.lbl_ps4, 2, 0)

        self.cmb_ps4 = QComboBox()
        self.cmb_ps4.setEnabled(False)
        self.content_layout.addWidget(self.cmb_ps4, 2, 1)

        self.lbl_ps5 = QLabel(self.lang_manager.t("ps5_label"))
        self.content_layout.addWidget(self.lbl_ps5, 3, 0)

        self.cmb_ps5 = QComboBox()
        self.cmb_ps5.setEnabled(False)
        self.content_layout.addWidget(self.cmb_ps5, 3, 1)

    def _build_action_buttons(self):
        self.btn_inject = QPushButton(self.lang_manager.t("send_button"))
        self.btn_inject.clicked.connect(self.send_payload)
        self.content_layout.addWidget(
            self.btn_inject,
            BUTTON_GRID_LAYOUT["send"]["row"],
            BUTTON_GRID_LAYOUT["send"]["column"],
            Qt.AlignLeft,
        )

        self.btn_browse = QPushButton(self.lang_manager.t("browse_button"))
        self.btn_browse.clicked.connect(self.browse_and_send)
        self.content_layout.addWidget(
            self.btn_browse,
            BUTTON_GRID_LAYOUT["browse"]["row"],
            BUTTON_GRID_LAYOUT["browse"]["column"],
            Qt.AlignRight,
        )

    def _build_socat_option(self):
        self.socat_available = SocatSender.is_available()
        self.chk_socat = QCheckBox(self.lang_manager.t("socat_checkbox"))
        self.chk_socat.setChecked(False)
        self.chk_socat.clicked.connect(self._on_socat_checkbox_click)
        self.content_layout.addWidget(self.chk_socat, 5, 0, 1, 2)

        if not self.socat_available:
            self.logger.info("Socat not detected on system - will show popup on click")

    def _on_socat_checkbox_click(self):
        """Handle socat checkbox click - show popup if socat not available."""
        if not self.socat_available:
            self.chk_socat.setChecked(False)
            QMessageBox.warning(
                self,
                self.lang_manager.t("socat_checkbox"),
                self.lang_manager.t("socat_not_found"),
            )
            self.logger.info("User attempted to enable socat but it's not installed")

    def _build_status(self):
        self.lbl_status = QLabel(self.lang_manager.t("status_ready"))
        self.lbl_status.setObjectName("status")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self._main_layout.addWidget(self.lbl_status)

    def on_lang_selected(self, idx=None):
        if idx is None:
            idx = self.lang_combo.currentIndex()
        if idx >= 0:
            code = self.lang_codes[idx]
            self.change_language(code)

    def change_language(self, code):
        self.logger.info("Changing language to %s", code)
        self.config_manager.set_language(code)
        self.lang_manager.load_lang(code)
        self.theme_tokens = self.theme_service.ui_theme_tokens(code)
        self._apply_stylesheet()

        self.lbl_ip.setText(self.lang_manager.t("ip_label"))
        self.lbl_port.setText(self.lang_manager.t("port_label"))
        self.lbl_ps4.setText(self.lang_manager.t("ps4_label"))
        self.lbl_ps5.setText(self.lang_manager.t("ps5_label"))
        self.btn_inject.setText(self.lang_manager.t("send_button"))
        self.btn_browse.setText(self.lang_manager.t("browse_button"))
        self.chk_socat.setText(self.lang_manager.t("socat_checkbox"))

        selector_values = self.language_service.language_selector_values(self.lang_codes)
        current_idx = self.lang_combo.currentIndex()
        self.lang_combo.clear()
        self.lang_combo.addItems(selector_values)
        self.lang_combo.setCurrentIndex(current_idx)

        self.lbl_status.setText(self.lang_manager.t("status_ready"))
        self.lbl_title.setText(f"{self.lang_manager.t('title')} v{__version__}")
        self.setWindowTitle(self.lang_manager.t("title"))

    def _set_payload_loading_state(self, loading):
        self._is_loading_payloads = loading
        if loading:
            self.cmb_ps4.setEnabled(False)
            self.cmb_ps5.setEnabled(False)
            self.lbl_status.setText(self.lang_manager.t("status_updating"))
            self.update_send_button_state()
            return

        self.cmb_ps4.setEnabled(True)
        self.cmb_ps5.setEnabled(True)
        self.update_send_button_state()

    def load_payloads_async(self):
        self.logger.info("Loading payloads")
        self._set_payload_loading_state(True)

        def worker():
            try:
                ps4_payloads, ps5_payloads = self.payload_repo.fetch_payloads()
            except Exception as exc:
                self._sig_payload_failed.emit(exc)
                return
            self._sig_payloads_loaded.emit(ps4_payloads, ps5_payloads)

        self.thread_runner(worker)

    def _on_payloads_loaded(self, ps4_payloads, ps5_payloads):
        self.ps4_payloads = ps4_payloads
        self.ps5_payloads = ps5_payloads

        ps4_values = [self.lang_manager.t("select_option")]
        ps4_values.extend(str(payload) for payload in self.ps4_payloads)
        self.cmb_ps4.clear()
        self.cmb_ps4.addItems(ps4_values)
        self.cmb_ps4.setCurrentIndex(0)

        ps5_values = [self.lang_manager.t("select_option")]
        ps5_values.extend(str(payload) for payload in self.ps5_payloads)
        self.cmb_ps5.clear()
        self.cmb_ps5.addItems(ps5_values)
        self.cmb_ps5.setCurrentIndex(0)

        self.cmb_ps4.activated.connect(self.on_ps4_selected)
        self.cmb_ps5.activated.connect(self.on_ps5_selected)

        self._set_payload_loading_state(False)
        self.lbl_status.setText(self.lang_manager.t("status_select"))
        self.logger.info("Payloads loaded successfully")

    def _on_payload_load_failed(self, exc):
        if isinstance(exc, PayloadCatalogNetworkError):
            self.logger.error("Payload loading failed (network): %s", exc)
            self.lbl_status.setText(self.lang_manager.t("status_error_github"))
            QMessageBox.critical(self, "Error", self.lang_manager.t("error_no_internet"))
        else:
            self.logger.error("Payload loading failed: %s", exc)
            self.lbl_status.setText(self.lang_manager.t("status_error_github"))

        self.cmb_ps4.setEnabled(False)
        self.cmb_ps5.setEnabled(False)
        self._is_loading_payloads = False
        self.update_send_button_state()

    def on_ps4_selected(self, idx=None):
        self._handle_payload_selection(self.cmb_ps4, self.cmb_ps5, self.ps4_payloads)

    def on_ps5_selected(self, idx=None):
        self._handle_payload_selection(self.cmb_ps5, self.cmb_ps4, self.ps5_payloads)

    def _handle_payload_selection(self, selected_combo, other_combo, payloads):
        idx = selected_combo.currentIndex()
        if idx > 0:
            payload = payloads[idx - 1]
            self.txt_port.setText(str(payload.port))
            other_combo.setEnabled(False)
        else:
            other_combo.setEnabled(True)

        if self.cmb_ps4.currentIndex() == 0 and self.cmb_ps5.currentIndex() == 0:
            self.cmb_ps4.setEnabled(True)
            self.cmb_ps5.setEnabled(True)

        self.update_send_button_state()

    def update_send_button_state(self):
        has_payload_selected = (
            self.cmb_ps4.currentIndex() > 0 or self.cmb_ps5.currentIndex() > 0
        )

        if self._is_sending:
            self.btn_inject.setEnabled(False)
            return

        can_send = not self._is_loading_payloads and has_payload_selected
        self.btn_inject.setEnabled(can_send)

    def _set_send_busy(self, busy):
        self._is_sending = busy
        if busy:
            self.btn_inject.setEnabled(False)
            self.btn_browse.setEnabled(False)
            return
        self.btn_browse.setEnabled(True)
        self.update_send_button_state()

    def _validated_endpoint_or_show_error(self):
        ip, port_int, error_key = self.endpoint_validator(
            self.txt_ip.text().strip(), self.txt_port.text()
        )
        if error_key:
            QMessageBox.critical(self, "Error", self.lang_manager.t(error_key))
            return None, None
        self.config_manager.set_ip(ip)
        return ip, port_int

    def _set_injecting_status(self, status_text):
        self.lbl_status.setText(status_text)

    def _send_file_with_sender_async(
        self, ip, port_int, payload_path, success_status_key, success_log
    ):
        use_socat = self.chk_socat.isChecked()
        status_key = "status_injecting_socat" if use_socat else "status_injecting_tcp"
        self.lbl_status.setText(self.lang_manager.t(status_key))
        QApplication.processEvents()
        self._set_send_busy(True)

        def worker():
            try:
                sender = self.sender_factory.create(use_socat)
                sender.send(ip, port_int, payload_path)
            except Exception as exc:
                self._sig_send_fail.emit(exc)
                return
            self._sig_send_ok.emit(success_status_key, success_log)

        self.thread_runner(worker)

    def _on_send_succeeded(self, status_key, log_message):
        self.lbl_status.setText(self.lang_manager.t(status_key))
        self.logger.info(log_message)
        self._set_send_busy(False)

    def _on_send_failed(self, exc):
        self.logger.error("Send failed: %s", exc)
        self.lbl_status.setText(f"X {exc}")
        QMessageBox.critical(self, "Error", str(exc))
        self._set_send_busy(False)

    def _download_and_send_payload_async(self, selected_payload, ip, port_int):
        use_socat = self.chk_socat.isChecked()
        self.lbl_status.setText(self.lang_manager.t("status_downloading"))
        QApplication.processEvents()
        self._set_send_busy(True)

        def worker():
            temp_path = os.path.join(SRC_DIR, "payload_temp.bin")
            try:
                import requests

                response = requests.get(selected_payload.url, timeout=30)
                response.raise_for_status()
                with open(temp_path, "wb") as file_obj:
                    file_obj.write(response.content)

                status_key = "status_injecting_socat" if use_socat else "status_injecting_tcp"
                self._sig_injecting_status.emit(self.lang_manager.t(status_key))

                sender = self.sender_factory.create(use_socat)
                sender.send(ip, port_int, temp_path)
            except Exception as exc:
                self._sig_send_fail.emit(exc)
                return
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            self._sig_send_ok.emit("status_injected", "Payload sent successfully")

        self.thread_runner(worker)

    def send_payload(self):
        self.logger.info("Send payload requested")
        idx_ps4 = self.cmb_ps4.currentIndex()
        idx_ps5 = self.cmb_ps5.currentIndex()
        selected = None
        if idx_ps4 > 0:
            selected = self.ps4_payloads[idx_ps4 - 1]
        elif idx_ps5 > 0:
            selected = self.ps5_payloads[idx_ps5 - 1]
        if not selected:
            QMessageBox.critical(self, "Error", self.lang_manager.t("error_select_payload"))
            return
        ip, port_int = self._validated_endpoint_or_show_error()
        if ip is None:
            return
        self._download_and_send_payload_async(selected, ip, port_int)

    def browse_and_send(self):
        self.logger.info("Browse and send requested")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "",
            "",
            "Payloads (*.bin *.elf *.lua);;All Files (*.*)",
        )
        if not file_path:
            return
        ip, port_int = self._validated_endpoint_or_show_error()
        if ip is None:
            return
        self._send_file_with_sender_async(
            ip,
            port_int,
            file_path,
            "status_sent",
            "Manual payload sent successfully",
        )


def run_main():
    app_qt = QApplication.instance() or QApplication(sys.argv)
    try:
        logging_service.info("Creating App instance")
        window = App()
        window.show()
        logging_service.info("Entering Qt event loop")
        return app_qt.exec()
    except Exception:
        logging_service.critical("Unhandled exception:\n%s", traceback.format_exc())
        try:
            QMessageBox.critical(
                None,
                "PS_MultiInjector - Fatal Error",
                f"The application crashed.\n\nLog: {_LOG_FILE}\n\n{traceback.format_exc()}",
            )
        except Exception:
            pass
        return 1
