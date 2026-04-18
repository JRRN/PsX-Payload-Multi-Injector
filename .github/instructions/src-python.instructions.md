---
description: "Use when creating or editing Python files under src, especially GUI, i18n, payload sending, or config modules. Enforces LangManager usage and the configparser ConfigManager pattern used by PS MultiInjector."
name: "PS MultiInjector Python Source Rules"
applyTo: "src/**/*.py"
---
# PS MultiInjector Python Source Rules

- Prefer the existing simple module style in [main.py](../../src/main.py), [services/config_manager.py](../../src/services/config_manager.py), and [services/payload_sender.py](../../src/services/payload_sender.py). Keep changes small and direct.
- For GUI and runtime translation work, use [LangManager](../../src/services/lang_manager.py).
- Keep translation keys in JSON files under `src/lang/` as lowercase `snake_case`. When adding UI text, add the key to every supported language file.
- Keep all language files aligned: `src/lang/es-es.json`, `src/lang/en-us.json`, `src/lang/pt-pt.json`, `src/lang/zh-cn.json`, and `src/lang/ko-kr.json` must expose the same key set.
- Follow the current config pattern: persist user-facing settings through [ConfigManager](../../src/services/config_manager.py), backed by `configparser` and the `[DEFAULT]` section in `config.ini`.
- For new persisted settings, extend `ConfigManager` with focused getter/setter methods instead of reading or writing `config.ini` ad hoc in other modules.
- Keep paths relative to `__file__` and runtime path helpers as this project does for `config.ini`, `lang/`, `assets/`, and socat cache paths.
- Match the current naming conventions: `snake_case` for functions, methods, variables, and files; `PascalCase` for classes. Domain services live in `src/services/` and are named `*Service` or `*Manager`.
- `LanguageService` handles UI metadata only (lang codes, display labels, selector values). It does not load translation files. Use `LangManager` for runtime translations.
- Preserve the existing sender abstraction in [services/payload_sender.py](../../src/services/payload_sender.py): subclasses implement `send(self, ip, port, payload_path)` and keep side effects localized.
- Avoid broad architectural cleanup unless the task requires it. This codebase currently favors straightforward, single-file logic over heavy abstraction.
- All new or modified production code must follow SOLID principles, applied pragmatically to this repository's simple style.

## Mandatory Validation For Any src Code Change

- If you modify production code under `src/`, you must create or update at least one relevant automated test under `tests/`.
- You must run at least the focused test file covering your change.
- You must run the full test suite with `python -m pytest tests -v`.
- You must run an application smoke validation:
	- Preferred: `python src/main.py` and verify startup on desktop environments.
	- Headless fallback: `python -c "import src.main"`.
- These checks are mandatory by default for every applicable code change; do not wait for user prompting.
- You must review whether documentation needs updating:
	- If behavior or API changes, check [README.md](../../README.md), [README_en.md](../../README_en.md), [README_pt.md](../../README_pt.md), [README_zh.md](../../README_zh.md), and [README_ko.md](../../README_ko.md).
	- If configuration/build process affected, check [AGENTS.md](../../AGENTS.md).
	- Keep all readmes above aligned in the same task whenever one is updated.
	- Keep all language files aligned in the same task whenever translation keys change.
	- Update as needed or note if no changes required.
- In your final report, list exactly which tests/smoke checks were run and their outcomes.
- In your final report, include a brief SOLID note explaining how the change preserves or improves design quality.
- In your final report, note any documentation updates made or explain why none were needed.
