import tempfile
import unittest
from unittest.mock import Mock

from src.services.endpoint_service import validate_endpoint
from src.services.language_service import LanguageService
from src.services.lang_manager import LangManager
from src.services.payload_sender import SocatSender


class LanguageServiceTests(unittest.TestCase):
    def test_discover_lang_codes_prioritizes_es_and_en(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            open(f"{tmp_dir}/pt-pt.json", "w", encoding="utf-8").close()
            open(f"{tmp_dir}/en-us.json", "w", encoding="utf-8").close()
            open(f"{tmp_dir}/es-es.json", "w", encoding="utf-8").close()

            service = LanguageService()
            codes = service.discover_lang_codes(tmp_dir)

        self.assertEqual(codes[0:2], ["es-es", "en-us"])

    def test_language_selector_values_uses_unicode_flags(self):
        service = LanguageService()
        values = service.language_selector_values(["en-us", "pt-br"])

        self.assertEqual(values, ["🇺🇸 English (US)", "🇧🇷 Português (BR)"])


class EndpointServiceTests(unittest.TestCase):
    def test_validate_endpoint_valid_data(self):
        ip, port, error = validate_endpoint("127.0.0.1", "9020")

        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 9020)
        self.assertIsNone(error)

    def test_validate_endpoint_invalid_port(self):
        ip, port, error = validate_endpoint("127.0.0.1", "70000")

        self.assertIsNone(ip)
        self.assertIsNone(port)
        self.assertEqual(error, "error_invalid_port")


class LangManagerStrategyTests(unittest.TestCase):
    def test_lang_manager_uses_injected_resolver_strategy(self):
        class ForcedResolver:
            def resolve(self, normalized_code, lang_dir):
                return "en-us"

        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(f"{tmp_dir}/en-us.json", "w", encoding="utf-8") as file_obj:
                file_obj.write('{"title": "Injected"}')

            manager = LangManager(tmp_dir, default_lang="es-es", resolvers=[ForcedResolver()])

        self.assertEqual(manager.lang_code, "en-us")
        self.assertEqual(manager.t("title"), "Injected")


class SocatSenderStrategyTests(unittest.TestCase):
    def test_socat_sender_uses_first_strategy_that_resolves(self):
        first = Mock()
        first.resolve.return_value = None
        second = Mock()
        second.resolve.return_value = "/tmp/fake-socat"
        third = Mock()

        sender = SocatSender(resolvers=[first, second, third])
        context = Mock()

        resolved = sender._resolve_socat_exec(context)

        self.assertEqual(resolved, "/tmp/fake-socat")
        first.resolve.assert_called_once_with(context)
        second.resolve.assert_called_once_with(context)
        third.resolve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
