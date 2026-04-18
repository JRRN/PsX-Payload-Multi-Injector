import logging
import os


class LanguageService:
    def __init__(self, lang_labels=None, lang_country_codes=None):
        self.lang_labels = lang_labels or {
            "es": "Español",
            "en": "English",
            "pt": "Português",
            "zh": "中文",
            "ko": "한국어",
        }
        self.lang_country_codes = lang_country_codes or {
            "en": "gb",
            "zh": "cn",
            "ko": "kr",
        }

    def base_lang_code(self, lang_code):
        normalized = (lang_code or "").strip().lower().replace("_", "-")
        if not normalized:
            return "en"
        return normalized.split("-")[0]

    def discover_lang_codes(self, lang_dir):
        """Discover available language codes from lang_dir/*.json files."""
        if not os.path.isdir(lang_dir):
            logging.warning("Language directory does not exist: %s", lang_dir)
            return ["es-es", "en-us"]

        lang_codes = sorted(
            file_name[:-5]
            for file_name in os.listdir(lang_dir)
            if file_name.endswith(".json") and not file_name.startswith("._")
        )

        if not lang_codes:
            logging.warning("No language files found in %s", lang_dir)
            return ["es-es", "en-us"]

        preferred = [code for code in ("es-es", "en-us") if code in lang_codes]
        others = [code for code in lang_codes if code not in preferred]
        ordered = preferred + others
        logging.info("Discovered language codes: %s", ordered)
        return ordered

    def language_label(self, lang_code):
        normalized = (lang_code or "").strip().lower().replace("_", "-")
        parts = [part for part in normalized.split("-") if part]
        if not parts:
            return (lang_code or "").upper()

        base_code = parts[0]
        base_label = self.lang_labels.get(base_code, base_code.upper())
        if len(parts) > 1:
            region = parts[1].upper()
            return f"{base_label} ({region})"
        return base_label

    def country_flag_emoji(self, country_code):
        """Build a Unicode flag emoji from a 2-letter country code."""
        code = (country_code or "").strip().upper()
        if len(code) != 2 or not code.isalpha():
            return ""
        base = 127397
        return chr(ord(code[0]) + base) + chr(ord(code[1]) + base)

    def resolve_country_code(self, lang_code):
        normalized = (lang_code or "").strip().lower().replace("_", "-")
        parts = [part for part in normalized.split("-") if part]
        if not parts:
            return ""

        # Example: en-us -> us, pt-br -> br
        if len(parts) > 1 and len(parts[1]) == 2 and parts[1].isalpha():
            return parts[1]

        base_code = parts[0]
        return self.lang_country_codes.get(base_code, base_code)

    def language_flag(self, lang_code):
        country_code = self.resolve_country_code(lang_code)
        return self.country_flag_emoji(country_code)

    def language_selector_values(self, lang_codes):
        return [f"{self.language_flag(code)} {self.language_label(code)}".strip() for code in lang_codes]
