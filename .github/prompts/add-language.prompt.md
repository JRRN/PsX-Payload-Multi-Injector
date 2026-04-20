---
description: "Add a new i18n language to PS MultiInjector. Use when creating a new src/lang/<code>.json file, copying existing translation keys, and wiring the language and flag into the PySide6 UI."
name: "Add Language"
argument-hint: "<language code> <display name> <flag country code>"
agent: "agent"
---
Add a new UI language to PS MultiInjector.

Project references:
- [LangManager](../../src/services/lang_manager.py)
- [Main UI language selector](../../src/services/app_service.py)
- [English translations](../../src/lang/en-us.json)
- [Spanish translations](../../src/lang/es-es.json)
- [Agent instructions](../../AGENTS.md)

Requirements:
- Work only on language-related files and the language selector wiring.
- Use `LangManager` and the existing `src/lang/<locale-code>.json` structure (for example `en-us.json`).
- Start from the existing keys in `en-us.json` or `es-es.json`. Do not invent a smaller key set.
- Create the new `src/lang/<locale-code>.json` file with every existing translation key present.
- Keep JSON valid UTF-8 and preserve the current lowercase `snake_case` translation keys.
- Update the UI language selector in `src/services/app_service.py` so the new language appears in `lang_codes`, `lang_labels`, and `flag_unicode`.
- Use `open_flags.get_flags_by_country(...)` with the provided country code for the selector flag.
- Do not switch new code to `lang_utils.Lang`; this repo uses `LangManager` in the GUI.
- Do not change the default language unless explicitly asked.

If the argument is incomplete, infer as much as possible from the request and ask only for the missing language code, display name, or flag country code.

Expected output:
- The new translation JSON file.
- The minimal `src/services/app_service.py` updates needed to expose the language in the selector.
- A short note listing any untranslated strings that were left copied from the source language.
