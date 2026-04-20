"""Test socat checkbox popup behavior."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services.app_service import App


def _stub_dependencies():
    class _FakeConfigManager:
        def __init__(self, _path):
            self._lang = "en-us"
            self._ip = ""

        def get_language(self):
            return self._lang

        def set_language(self, code):
            self._lang = code

        def get_ip(self):
            return self._ip

        def set_ip(self, ip):
            self._ip = ip

    class _FakeLangManager:
        def __init__(self, _lang_dir, lang_code):
            self.lang_code = lang_code

        def load_lang(self, code):
            self.lang_code = code

        def t(self, key):
            labels = {
                "title": "PS MultiInjector",
                "ip_label": "IP",
                "port_label": "Port",
                "ps4_label": "PS4",
                "ps5_label": "PS5",
                "send_button": "Send",
                "browse_button": "Browse",
                "socat_checkbox": "Use socat",
                "socat_not_found": "socat not found on this system",
                "status_ready": "Ready",
                "status_select": "Select payload",
                "status_updating": "Updating",
                "select_option": "Select...",
            }
            return labels.get(key, key)

    class _FakePayloadCatalogService:
        def __init__(self, _url):
            pass

        def fetch_payloads(self):
            return [], []

    class _FakeLanguageService:
        def discover_lang_codes(self, _lang_dir):
            return ["en-us"]

        def language_selector_values(self, codes):
            return codes

    class _FakeThemeService:
        def ui_theme_tokens(self, _lang_code):
            return {
                "font_family": "Arial",
                "accent": "#0088cc",
                "accent_text": "#ffffff",
            }

        def apply_theme_styles(self, window, _theme_tokens):
            window.setStyleSheet("")

    class _FakeLogger:
        def debug(self, *_args, **_kwargs):
            pass

        def info(self, *_args, **_kwargs):
            pass

        def error(self, *_args, **_kwargs):
            pass

    return SimpleNamespace(
        language_service=_FakeLanguageService(),
        logging_service=_FakeLogger(),
        theme_service=_FakeThemeService(),
        endpoint_validator=lambda ip, port: (ip, int(port or 0), None),
        thread_runner=lambda fn: None,
        sender_factory=SimpleNamespace(create=lambda _use_socat: None),
        config_manager_cls=_FakeConfigManager,
        lang_manager_cls=_FakeLangManager,
        payload_catalog_service_cls=_FakePayloadCatalogService,
    )


class TestSocatCheckboxPopup(unittest.TestCase):
    """Test socat checkbox popup when unavailable."""

    @patch('src.services.app_service.SocatSender.is_available', return_value=False)
    @patch('src.services.app_service.QMessageBox.warning')
    def test_socat_checkbox_shows_popup_when_unavailable(self, mock_warning, mock_is_available):
        """Test that clicking checkbox when socat unavailable shows popup."""
        app = App(dependencies=_stub_dependencies())

        # Simulate checkbox click
        app._on_socat_checkbox_click()

        # Verify popup was shown
        mock_warning.assert_called_once()
        args, _kwargs = mock_warning.call_args

        # QMessageBox.warning(parent, title, message) - positional args
        # args[0]=parent, args[1]=title, args[2]=message
        title = args[1] if len(args) > 1 else ''
        message = args[2] if len(args) > 2 else ''
        self.assertGreater(len(title), 0, "Popup title should not be empty")
        self.assertGreater(len(message), 0, "Popup message should not be empty")
        self.assertIn('socat', message.lower())

        # Verify checkbox state was reverted
        self.assertFalse(app.chk_socat.isChecked())

    @patch('src.services.app_service.SocatSender.is_available', return_value=False)
    def test_socat_checkbox_reverts_on_click_when_unavailable(self, mock_is_available):
        """Test that checkbox state is reverted when socat unavailable."""
        with patch('src.services.app_service.QMessageBox.warning'):
            app = App(dependencies=_stub_dependencies())

            # Try to enable checkbox
            app.chk_socat.setChecked(True)
            app._on_socat_checkbox_click()

            # Should revert to False
            self.assertFalse(app.chk_socat.isChecked())

    @patch('src.services.app_service.SocatSender.is_available', return_value=True)
    def test_socat_checkbox_works_when_available(self, mock_is_available):
        """Test that checkbox works normally when socat is available."""
        with patch('src.services.app_service.QMessageBox.warning') as mock_warning:
            app = App(dependencies=_stub_dependencies())

            # Enable checkbox
            app.chk_socat.setChecked(True)
            app._on_socat_checkbox_click()

            # Popup should NOT be shown
            mock_warning.assert_not_called()

            # Checkbox should remain enabled
            self.assertTrue(app.chk_socat.isChecked())


class TestSocatTranslations(unittest.TestCase):
    """Test that socat messages are translated in all languages."""

    def test_socat_not_found_translated_in_all_languages(self):
        """Verify socat_not_found key exists in all language files."""
        import json
        from pathlib import Path
        
        lang_dir = Path(__file__).parent.parent / 'src' / 'lang'
        # Only get real language files, skip AppleDouble files (._*.json)
        language_files = [f for f in lang_dir.glob('*.json') if not f.name.startswith('._')]
        
        self.assertGreater(len(language_files), 0, "No language files found")
        
        for lang_file in language_files:
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            self.assertIn(
                'socat_not_found',
                lang_data,
                f"socat_not_found translation missing in {lang_file.name}"
            )
            
            # Check message is not empty
            message = lang_data['socat_not_found']
            self.assertGreater(len(message), 0, f"Empty socat_not_found in {lang_file.name}")
            
            # Check message contains installation instructions
            self.assertIn('socat', message.lower(), f"Message doesn't mention socat in {lang_file.name}")


if __name__ == '__main__':
    unittest.main()
