# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-17
### Added
- New locale-based translation files: `src/lang/es-es.json`, `src/lang/en-us.json`, `src/lang/pt-pt.json`, `src/lang/zh-cn.json`, and `src/lang/ko-kr.json`.
- New translated readmes: `README_pt.md`, `README_zh.md`, and `README_ko.md`.
- New "How to add a new language" guidance across readmes.

### Changed
- Language discovery and runtime i18n now follow locale file naming (`xx-yy.json`) for better scalability.
- `LangManager` now resolves legacy language values (`es`, `en`, etc.) to locale files with compatibility fallbacks.
- Config default language moved to `es-es`.
- `settings.language` is now a free-form locale string instead of a hardcoded literal list.
- Language discovery now ignores AppleDouble metadata files (`._*.json`) on macOS.
- Agent instructions now explicitly require running mandatory validation checks by default after applicable code changes.
- Payload sending now runs asynchronously to keep the UI responsive during downloads and transfers.
- Initial payload list loading now runs asynchronously to avoid blocking the GUI at startup.
- Main window is now horizontally resizable with a minimum size to better accommodate locale-dependent text lengths.
- Language resolution now uses strict locale-based matching (`xx-yy`) and locale-prefix fallback without maintaining base-code aliases (`en`, `es`, etc.).

### Fixed
- Language selector robustness when locale and country code formats vary (for example `en-us`, `pt-br`).
- Documentation parity gaps across non-English readmes.
- Endpoint validation now enforces real IP parsing and valid port ranges (1-65535) before sending payloads.

### Validation
- Focused tests: `tests/test_config_and_lang.py -v` and `tests/test_main_import_bootstrap.py -v`.
- Full suite: `python -m pytest tests -v`.
- Smoke check: `python -c "import src.main"`.

## [1.0.0] - 2026-04-16
### Added
- Initial public release
- Cross-platform GUI for PS4/PS5 payload injection
- Multi-language support (Spanish, English)
- Socat auto-download and TCP/Socat payload sending
- Modern UI, Unicode flag selector, config and language modularization
- GitHub Actions pipeline for tests and multiplatform builds
- Versioning system and build artifact naming
