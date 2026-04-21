import platform


LAYOUT_METRICS = {
    "top_bar_pady": (2, 0),
    "header_frame_pady": (0, 0),
    "title_pady": (0, 0),
    "content_frame_pady": (0, 0),
}

BUTTON_GRID_LAYOUT = {
    "send": {"row": 4, "column": 0, "sticky": "w", "pady": (14, 8)},
    "browse": {"row": 4, "column": 1, "sticky": "e", "pady": (14, 8)},
}

IP_PORT_GRID_LAYOUT = {
    "ip_label": {"row": 0, "column": 0, "sticky": "w", "pady": (0, 6)},
    "ip_input": {"row": 0, "column": 1, "sticky": "w", "pady": (0, 6), "padx": (8, 0)},
    "port_label": {"row": 1, "column": 0, "sticky": "w", "pady": (0, 6)},
    "port_input": {"row": 1, "column": 1, "sticky": "w", "pady": (0, 6), "padx": (8, 0)},
}


class UiThemeService:
    def __init__(self, language_service, platform_system=None):
        self.language_service = language_service
        self.platform_system = platform_system or platform.system

    def ui_font_family(self, lang_code):
        base_code = self.language_service.base_lang_code(lang_code)
        system = self.platform_system()

        if system == "Darwin":
            if base_code == "zh":
                return "PingFang SC"
            if base_code == "ko":
                return "Apple SD Gothic Neo"
            return "SF Pro Text"

        if system == "Windows":
            if base_code == "zh":
                return "Microsoft YaHei UI"
            if base_code == "ko":
                return "Malgun Gothic"
            return "Segoe UI"

        if base_code == "zh":
            return "Noto Sans CJK SC"
        if base_code == "ko":
            return "Noto Sans CJK KR"
        return "Noto Sans"

    def ui_theme_tokens(self, lang_code):
        font_family = self.ui_font_family(lang_code)
        return {
            "bg": "#000000",
            "surface": "#17212e",
            "surface_alt": "#1d2a3a",
            "text": "#f3f7fb",
            "muted": "#9bb0c5",
            "accent": "#1f5f3f",
            "accent_hover": "#2b7a52",
            "accent_text": "#ffffff",
            "button_disabled_bg": "#d3d3d3",
            "button_disabled_fg": "#6f6f6f",
            "status_ok": "#6ee7a8",
            "border": "#2a3a4f",
            "font_family": font_family,
            "font_body": (font_family, 14),
            "font_label": (font_family, 14, "bold"),
            "font_header": (font_family, 20, "bold"),
            "font_button": (font_family, 14, "bold"),
            "font_status": (font_family, 15, "bold"),
        }

    def apply_theme_styles(self, window, theme_tokens):
        """Apply theme to a QMainWindow via Qt Style Sheets (QSS)."""
        ff = theme_tokens["font_family"]
        bg = theme_tokens["bg"]
        surface_alt = theme_tokens["surface_alt"]
        surface = theme_tokens["surface"]
        text = theme_tokens["text"]
        accent = theme_tokens["accent"]
        accent_hover = theme_tokens["accent_hover"]
        accent_text = theme_tokens["accent_text"]
        border = theme_tokens["border"]
        btn_dis_bg = theme_tokens["button_disabled_bg"]
        btn_dis_fg = theme_tokens["button_disabled_fg"]
        status_ok = theme_tokens["status_ok"]

        qss = f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {text};
                font-family: '{ff}';
                font-size: 14pt;
            }}
            QLabel {{
                background-color: transparent;
                color: {text};
                font-size: 14pt;
                font-weight: bold;
            }}
            QLabel#header {{
                color: {accent};
                font-size: 20pt;
                font-weight: bold;
            }}
            QLabel#status {{
                color: {status_ok};
                font-size: 15pt;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {accent};
                color: {accent_text};
                border: none;
                padding: 4px 10px;
                font-size: 14pt;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:disabled {{
                background-color: {btn_dis_bg};
                color: {btn_dis_fg};
            }}
            QComboBox {{
                background-color: {surface_alt};
                color: {text};
                border: 1px solid {border};
                padding: 2px 6px;
                font-size: 14pt;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {surface_alt};
                color: {text};
                selection-background-color: {surface};
                selection-color: {text};
            }}
            QLineEdit {{
                background-color: {surface_alt};
                color: {text};
                border: 1px solid {border};
                padding: 2px 6px;
                font-size: 14pt;
            }}
            QCheckBox {{
                color: {text};
                font-size: 14pt;
            }}
        """
        if hasattr(window, "setStyleSheet"):
            window.setStyleSheet(qss)
