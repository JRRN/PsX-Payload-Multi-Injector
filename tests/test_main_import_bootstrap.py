import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from src import main


class MainImportBootstrapTests(unittest.TestCase):
    def test_returns_empty_when_not_frozen(self):
        with patch.object(sys, "frozen", False, create=True):
            inserted = main._bootstrap_frozen_import_paths()

        self.assertEqual(inserted, [])

    def test_inserts_bundle_and_src_paths_when_frozen(self):
        fake_bundle = "/tmp/fake_bundle"
        expected_src = os.path.join(fake_bundle, "src")

        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", fake_bundle, create=True), \
             patch.object(sys, "path", ["/usr/lib/python"]):
            inserted = main._bootstrap_frozen_import_paths()

            self.assertIn(fake_bundle, sys.path)
            self.assertIn(expected_src, sys.path)
            self.assertEqual(inserted, [fake_bundle, expected_src])

    def test_discover_lang_codes_from_json_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            open(os.path.join(tmp_dir, "pt-pt.json"), "w", encoding="utf-8").close()
            open(os.path.join(tmp_dir, "en-us.json"), "w", encoding="utf-8").close()
            open(os.path.join(tmp_dir, "es-es.json"), "w", encoding="utf-8").close()
            open(os.path.join(tmp_dir, "ko-kr.json"), "w", encoding="utf-8").close()
            open(os.path.join(tmp_dir, "._en-us.json"), "w", encoding="utf-8").close()
            open(os.path.join(tmp_dir, "notes.txt"), "w", encoding="utf-8").close()

            codes = main.DEFAULT_LANGUAGE_SERVICE.discover_lang_codes(tmp_dir)

            self.assertEqual(codes, ["es-es", "en-us", "ko-kr", "pt-pt"])

    def test_discover_lang_codes_returns_defaults_when_dir_missing(self):
        codes = main.DEFAULT_LANGUAGE_SERVICE.discover_lang_codes("/path/that/does/not/exist")

        self.assertEqual(codes, ["es-es", "en-us"])

    def test_country_flag_emoji_builds_unicode_flag(self):
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.country_flag_emoji("gb"), "🇬🇧")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.country_flag_emoji("es"), "🇪🇸")

    def test_language_flag_uses_unicode_for_base_language(self):
        flag = main.DEFAULT_LANGUAGE_SERVICE.language_flag("en")

        self.assertEqual(flag, "🇬🇧")

    def test_resolve_country_code_for_regional_language(self):
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.resolve_country_code("pt-br"), "br")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.resolve_country_code("en_us"), "us")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.resolve_country_code("zh-hant"), "cn")

    def test_language_label_for_regional_language(self):
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.language_label("pt-br"), "Português (BR)")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.language_label("en-us"), "English (US)")

    def test_language_flag_uses_unicode_for_regional_language(self):
        flag = main.DEFAULT_LANGUAGE_SERVICE.language_flag("pt-br")

        self.assertEqual(flag, "🇧🇷")

    def test_language_service_base_lang_code_normalizes_locale(self):
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.base_lang_code("zh-cn"), "zh")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.base_lang_code("en_US"), "en")
        self.assertEqual(main.DEFAULT_LANGUAGE_SERVICE.base_lang_code(""), "en")

    def test_ui_font_family_for_linux_cjk(self):
        with patch.object(main.platform, "system", return_value="Linux"):
            self.assertEqual(main._ui_font_family("zh-cn"), "Noto Sans CJK SC")
            self.assertEqual(main._ui_font_family("ko-kr"), "Noto Sans CJK KR")
            self.assertEqual(main._ui_font_family("en-us"), "Noto Sans")

    def test_ui_theme_tokens_include_expected_keys(self):
        with patch.object(main.platform, "system", return_value="Linux"):
            tokens = main._ui_theme_tokens("es-es")

        self.assertIn("font_family", tokens)
        self.assertIn("font_body", tokens)
        self.assertIn("font_label", tokens)
        self.assertIn("status_ok", tokens)
        self.assertIn("button_disabled_bg", tokens)
        self.assertIn("button_disabled_fg", tokens)
        self.assertEqual(tokens["bg"], "#000000")
        self.assertEqual(tokens["accent"], "#1f5f3f")
        self.assertEqual(tokens["accent_text"], "#ffffff")
        self.assertEqual(tokens["button_disabled_bg"], "#d3d3d3")
        self.assertEqual(tokens["font_family"], "Noto Sans")
        self.assertEqual(tokens["font_label"][2], "bold")
        self.assertEqual(tokens["font_button"][1], 14)

    def test_update_send_button_state_uses_disabled_style_without_payload(self):
        app = main.App.__new__(main.App)
        app._is_sending = False
        app._is_loading_payloads = False
        app.cmb_ps4 = Mock()
        app.cmb_ps5 = Mock()
        app.cmb_ps4.currentIndex.return_value = 0
        app.cmb_ps5.currentIndex.return_value = 0
        app.btn_inject = Mock()

        app.update_send_button_state()

        app.btn_inject.setEnabled.assert_called_once_with(False)

    def test_update_send_button_state_uses_primary_style_with_payload(self):
        app = main.App.__new__(main.App)
        app._is_sending = False
        app._is_loading_payloads = False
        app.cmb_ps4 = Mock()
        app.cmb_ps5 = Mock()
        app.cmb_ps4.currentIndex.return_value = 1
        app.cmb_ps5.currentIndex.return_value = 0
        app.btn_inject = Mock()

        app.update_send_button_state()

        app.btn_inject.setEnabled.assert_called_once_with(True)

    def test_validated_endpoint_returns_tuple_and_persists_ip(self):
        app = main.App.__new__(main.App)
        app.endpoint_validator = Mock(return_value=("192.168.0.10", 9020, None))
        app.txt_ip = Mock()
        app.txt_port = Mock()
        app.txt_ip.text.return_value = " 192.168.0.10 "
        app.txt_port.text.return_value = "9020"
        app.config_manager = Mock()
        app.lang_manager = Mock()

        with patch("src.services.app_service.QMessageBox.critical") as critical:
            ip, port = app._validated_endpoint_or_show_error()

        self.assertEqual((ip, port), ("192.168.0.10", 9020))
        app.endpoint_validator.assert_called_once_with("192.168.0.10", "9020")
        app.config_manager.set_ip.assert_called_once_with("192.168.0.10")
        critical.assert_not_called()

    def test_validated_endpoint_shows_error_and_returns_none(self):
        app = main.App.__new__(main.App)
        app.endpoint_validator = Mock(return_value=(None, None, "error_invalid_ip"))
        app.txt_ip = Mock()
        app.txt_port = Mock()
        app.txt_ip.text.return_value = "not-an-ip"
        app.txt_port.text.return_value = "9020"
        app.config_manager = Mock()
        app.lang_manager = Mock()
        app.lang_manager.t.return_value = "Invalid IP"

        with patch("src.services.app_service.QMessageBox.critical") as critical:
            ip, port = app._validated_endpoint_or_show_error()

        self.assertEqual((ip, port), (None, None))
        critical.assert_called_once_with(app, "Error", "Invalid IP")
        app.config_manager.set_ip.assert_not_called()

    def test_layout_metrics_for_compact_header_to_inputs_spacing(self):
        layout = main.LAYOUT_METRICS

        self.assertEqual(layout["top_bar_pady"], (2, 0))
        self.assertEqual(layout["header_frame_pady"], (0, 0))
        self.assertEqual(layout["title_pady"], (0, 0))
        self.assertEqual(layout["content_frame_pady"], (0, 0))

    def test_button_grid_layout_places_send_left_and_browse_right(self):
        layout = main.BUTTON_GRID_LAYOUT

        self.assertEqual(layout["send"]["row"], 4)
        self.assertEqual(layout["browse"]["row"], 4)
        self.assertEqual(layout["send"]["column"], 0)
        self.assertEqual(layout["browse"]["column"], 1)
        self.assertEqual(layout["send"]["sticky"], "w")
        self.assertEqual(layout["browse"]["sticky"], "e")

    def test_ip_port_grid_layout_places_port_below_ip(self):
        layout = main.IP_PORT_GRID_LAYOUT

        self.assertEqual(layout["ip_label"]["row"], 0)
        self.assertEqual(layout["ip_input"]["row"], 0)
        self.assertEqual(layout["port_label"]["row"], 1)
        self.assertEqual(layout["port_input"]["row"], 1)
        self.assertEqual(layout["ip_label"]["column"], 0)
        self.assertEqual(layout["port_label"]["column"], 0)
        self.assertEqual(layout["ip_input"]["column"], 1)
        self.assertEqual(layout["port_input"]["column"], 1)

    def test_language_selector_values_include_flag_and_label(self):
        values = main.DEFAULT_LANGUAGE_SERVICE.language_selector_values(["es-es", "en-us", "ko-kr"])

        self.assertEqual(values, ["🇪🇸 Español (ES)", "🇺🇸 English (US)", "🇰🇷 한국어 (KR)"])

    def test_language_selector_values_strip_when_flag_missing(self):
        with patch.object(main.DEFAULT_LANGUAGE_SERVICE, "language_flag", return_value=""):
            values = main.DEFAULT_LANGUAGE_SERVICE.language_selector_values(["en-us"])

        self.assertEqual(values, ["English (US)"])

    def test_validate_endpoint_accepts_ipv4_and_port_range(self):
        ip, port, error = main.validate_endpoint(" 192.168.0.10 ", "9020")

        self.assertEqual(ip, "192.168.0.10")
        self.assertEqual(port, 9020)
        self.assertIsNone(error)

    def test_validate_endpoint_rejects_invalid_ip(self):
        ip, port, error = main.validate_endpoint("not-an-ip", "9020")

        self.assertIsNone(ip)
        self.assertIsNone(port)
        self.assertEqual(error, "error_invalid_ip")

    def test_validate_endpoint_rejects_out_of_range_port(self):
        ip, port, error = main.validate_endpoint("127.0.0.1", "70000")

        self.assertIsNone(ip)
        self.assertIsNone(port)
        self.assertEqual(error, "error_invalid_port")

    def test_default_dependencies_wire_expected_services(self):
        deps = main.DEFAULT_DEPENDENCIES

        self.assertIsInstance(deps.language_service, main.LanguageService)
        self.assertIsInstance(deps.logging_service, main.LoggingService)
        self.assertIsInstance(deps.theme_service, main.UiThemeService)
        self.assertIs(deps.endpoint_validator, main.validate_endpoint)
        self.assertIs(deps.thread_runner, main.start_daemon_thread)
        self.assertIsInstance(deps.sender_factory, main.SenderFactory)
        self.assertIs(deps.config_manager_cls, main.ConfigManager)
        self.assertIs(deps.lang_manager_cls, main.LangManager)
        self.assertIs(deps.payload_catalog_service_cls, main.PayloadCatalogService)

    def test_app_exposes_widget_builder_methods(self):
        self.assertTrue(hasattr(main.App, "_build_top_bar"))
        self.assertTrue(hasattr(main.App, "_build_title"))
        self.assertTrue(hasattr(main.App, "_build_content"))
        self.assertTrue(hasattr(main.App, "_build_status"))


if __name__ == "__main__":
    unittest.main()
