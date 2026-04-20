import json
import tempfile
import unittest
from pathlib import Path

from src.services.config_manager import ConfigManager
from src.services.lang_manager import LangManager


class ConfigManagerTests(unittest.TestCase):
    def test_creates_default_config_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.ini"

            manager = ConfigManager(str(config_path))

            self.assertTrue(config_path.exists())
            self.assertEqual(manager.get_ip(), "")
            self.assertEqual(manager.get_language(), "es-es")

    def test_persists_ip_and_language_values(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.ini"
            manager = ConfigManager(str(config_path))

            manager.set_ip("192.168.1.77")
            manager.set_language("en")

            reloaded_manager = ConfigManager(str(config_path))
            self.assertEqual(reloaded_manager.get_ip(), "192.168.1.77")
            self.assertEqual(reloaded_manager.get_language(), "en")


class LangManagerTests(unittest.TestCase):
    def test_loads_translations_from_json_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            lang_dir = Path(tmp_dir)
            (lang_dir / "en-us.json").write_text(
                json.dumps({"title": "Injector", "status_ready": "Ready"}),
                encoding="utf-8",
            )

            lang_manager = LangManager(str(lang_dir), "en")

            self.assertEqual(lang_manager.t("title"), "Injector")
            self.assertEqual(lang_manager.translate("status_ready"), "Ready")
            self.assertEqual(lang_manager.lang_code, "en-us")

    def test_returns_key_when_translation_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            lang_dir = Path(tmp_dir)
            (lang_dir / "es-es.json").write_text(
                json.dumps({"title": "Inyector"}),
                encoding="utf-8",
            )

            lang_manager = LangManager(str(lang_dir), "es")

            self.assertEqual(lang_manager.t("missing_key"), "missing_key")

    def test_missing_language_file_results_in_empty_translations(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            lang_manager = LangManager(tmp_dir, "fr")

            self.assertEqual(lang_manager.lang_code, "fr")
            self.assertEqual(lang_manager.translations, {})

    def test_repo_language_files_have_aligned_keys(self):
        repo_root = Path(__file__).resolve().parents[1]
        lang_dir = repo_root / "src" / "lang"
        baseline = json.loads((lang_dir / "en-us.json").read_text(encoding="utf-8"))
        baseline_keys = set(baseline.keys())

        for lang_code in ["es-es", "pt-pt", "zh-cn", "ko-kr"]:
            lang_payload = json.loads((lang_dir / f"{lang_code}.json").read_text(encoding="utf-8"))
            self.assertEqual(set(lang_payload.keys()), baseline_keys)


if __name__ == "__main__":
    unittest.main()
