import json
import logging
import os
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class LangCodeResolverStrategy(ABC):
    @abstractmethod
    def resolve(self, normalized_code, lang_dir):
        raise NotImplementedError


class ExactLangCodeResolver(LangCodeResolverStrategy):
    def resolve(self, normalized_code, lang_dir):
        if not normalized_code:
            return None
        exact_path = os.path.join(lang_dir, f"{normalized_code}.json")
        if os.path.exists(exact_path):
            return normalized_code
        return None


class PrefixLangCodeResolver(LangCodeResolverStrategy):
    def resolve(self, normalized_code, lang_dir):
        if not normalized_code or not os.path.isdir(lang_dir):
            return None
        base_code = normalized_code.split("-")[0]
        prefixed = sorted(
            file_name[:-5]
            for file_name in os.listdir(lang_dir)
            if file_name.endswith(".json") and file_name.startswith(f"{base_code}-") and not file_name.startswith("._")
        )
        if prefixed:
            return prefixed[0]
        return None


DEFAULT_LANG_RESOLVERS = (
    ExactLangCodeResolver(),
    PrefixLangCodeResolver(),
)


class LangManager:
    def __init__(self, lang_dir, default_lang="es-es", resolvers=None):
        self.lang_dir = lang_dir
        self.resolvers = tuple(resolvers or DEFAULT_LANG_RESOLVERS)
        self.lang_code = default_lang
        logger.debug("LangManager init with lang_dir=%s default_lang=%s", lang_dir, default_lang)
        self.translations = self.load_lang(default_lang)

    def _resolve_lang_code(self, lang_code):
        normalized = (lang_code or "").strip().lower().replace("_", "-")
        if not normalized:
            return None

        for resolver in self.resolvers:
            resolved = resolver.resolve(normalized, self.lang_dir)
            if resolved:
                return resolved

        return None

    def load_lang(self, lang_code):
        resolved_code = self._resolve_lang_code(lang_code)
        path = os.path.join(self.lang_dir, f"{resolved_code}.json") if resolved_code else ""
        logger.debug("Loading translations from %s", path)
        if resolved_code and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file_obj:
                self.translations = json.load(file_obj)
            logger.info(
                "Loaded translations for lang=%s (resolved=%s, %d keys)",
                lang_code,
                resolved_code,
                len(self.translations),
            )
            self.lang_code = resolved_code
        else:
            self.translations = {}
            logger.warning("Translation file not found for lang=%s at %s", lang_code, path)
            self.lang_code = lang_code
        return self.translations

    def translate(self, key):
        return self.translations.get(key, key)

    t = translate
