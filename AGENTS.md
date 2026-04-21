# PS MultiInjector - Agent Instructions

Cross-platform GUI tool (PySide6/Qt) for injecting payloads into PS4 and PS5 consoles over TCP.
Supported platforms: Linux, Windows, macOS Intel (x86_64), and macOS ARM (arm64).
See [docs/README_en.md](docs/README_en.md) for end-user details.

## Architecture

All application source code lives in src.
Entry point: src/main.py (class App inheriting from QMainWindow).

| Module | Role |
|---|---|
| main.py | Minimal bootstrap/entrypoint that delegates app execution |
| models/payload.py | Simple Payload class (not a dataclass) with constructor and string representation |
| models/settings.py | BaseSettings model loading optional .env values |
| models/version.py | Single source of truth for __version__ |
| services/app_service.py | PySide6 App orchestration, dependency wiring, and run flow |
| services/payload_catalog_service.py | Fetches payload JSON and returns ps4 and ps5 payload lists |
| services/payload_sender.py | PayloadSender abstraction with TCPSender and SocatSender implementations |
| services/sender_factory.py | Factory that selects TCPSender or SocatSender based on config |
| services/config_manager.py | Persists user settings in config.ini using configparser |
| services/lang_manager.py | Preferred runtime i18n manager with t, translate, and load_lang |
| services/language_service.py | UI metadata only: discovers lang codes, builds display labels and selector values |
| services/logging_service.py | Configures app log file routing and exposes injectable logger methods |
| services/endpoint_service.py | Validates and parses IP/port endpoint input |
| services/thread_service.py | Starts daemon threads for background send operations |

## Runtime Paths

- User configuration is persisted through ConfigManager at USER_DATA_DIR/config.ini.
- USER_DATA_DIR is platform-dependent:
	- macOS: ~/Library/Application Support/PS_MultiInjector
	- Windows: %APPDATA%/PS_MultiInjector
	- Linux: ~/.local/share/PS_MultiInjector
- App logs are configured by LoggingService in src/services/logging_service.py:
	- macOS: ~/Library/Logs/PS_MultiInjector/app.log
	- Windows: %APPDATA%/PS_MultiInjector/Logs/app.log
	- Linux: ~/.local/share/PS_MultiInjector/logs/app.log
- Socat cached binaries are stored in USER_DATA_DIR/socat.

## Build, Test, and Run

Development commands:

```sh
# Install runtime dependencies (publication/build)
uv pip install -r requirements.txt

# Install test dependencies
uv pip install -r requirements-test.txt

# Install development dependencies
uv pip install -r requirements-dev.txt

# Run app in development
uv run src/main.py

# Optional auto-restart in development
watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py

# Run tests
python -m pytest tests -v

# Build native executables
python build_local/build_local.py

# Version management (semantic versioning)
python build_local/bump_version.py --dry-run  # Preview version bump
python build_local/bump_version.py             # Apply version bump
```

See [VERSIONING.md](VERSIONING.md) and [VERSIONING_ES.md](VERSIONING_ES.md) for automatic version management during CI/CD builds.

## Mandatory Agent Workflow For Any Code Change

This section is mandatory for all code-writing agents working in this repository.

1. If an agent changes production code under src, it must create or update at least one relevant automated test under tests.
2. The agent must run at least the focused test file for the change.
3. The agent must run the full test suite with python -m pytest tests -v.
4. The agent must perform an application smoke validation:
	 - Preferred on developer machine with desktop session: run python src/main.py and confirm startup.
	 - For headless contexts: run python -c "import src.main" as import-level smoke check.
   - These checks are mandatory by default for every applicable code change; do not wait for the user to request them.
5. The agent must review and update relevant README documentation:
	- If the change affects user-facing behavior, update [docs/README_en.md](docs/README_en.md) or [README.md](README.md).
   - If the change affects development/build process, update relevant sections in [AGENTS.md](AGENTS.md).
   - If no documentation update is needed, briefly note why in the final report.
	- All language readmes must stay aligned: [README.md](README.md), [docs/README_en.md](docs/README_en.md), [docs/README_pt.md](docs/README_pt.md), [docs/README_zh.md](docs/README_zh.md), and [docs/README_ko.md](docs/README_ko.md).
	- When behavior/build/docs change, update all readmes above in the same task.
	- Language files must stay aligned: [src/lang/es-es.json](src/lang/es-es.json), [src/lang/en-us.json](src/lang/en-us.json), [src/lang/pt-pt.json](src/lang/pt-pt.json), [src/lang/zh-cn.json](src/lang/zh-cn.json), and [src/lang/ko-kr.json](src/lang/ko-kr.json).
	- When adding, removing, or renaming translation keys, update all language JSON files above in the same task.
6. The agent must report what was tested, validated, and documented.

No code change is complete unless the test update, validation, and documentation review steps above were executed or explicitly blocked by environment limitations.
- Persist user-facing settings only through services/config_manager.py (ConfigManager).
- Do not read or write config.ini directly from unrelated modules.
- For new persisted settings, add focused getter and setter methods to ConfigManager.

## Sender Rules

- Preserve the existing sender abstraction in payload_sender.py.
- Implement or modify behavior in concrete senders without leaking side effects into GUI code.
- Keep send signature as send(self, ip, port, payload_path).

## Performance Optimization

The app startup has been optimized to minimize blocking operations and disk I/O. Key improvements include:

### Image Caching (`_ImageCache`)
- Caches PIL Image objects to avoid redundant disk reads and image processing.
- Separate cache keys per image path and size to reuse exact resized versions.
- Gracefully handles missing files by logging and returning `None` instead of crashing.

### Startup Profiling (`_PerformanceTracker`)
- Records timing milestones throughout app initialization.
- Logs debug-level marks (e.g., `qt.init_start`, `config_manager`, `theme_tokens`, `payloads_async_started`).
- Generates an info-level summary report on completion.
- Use `_perf_tracker.mark("milestone_name")` to add new profiling points.

### Icon Loading (Non-blocking)
- App icon (`logo.png` or `app.ico`) is now loaded in a background thread via `_load_icon_async()`.
- Uses `_image_cache` to reduce redundant PIL operations.
- Window initialization completes before icon loading finishes, improving perceived startup time.

### Implications for Agents
- When modifying app initialization, use `_perf_tracker.mark()` to instrument new bottlenecks.
- Image loading for UI elements should use `_image_cache.get_image()` instead of direct PIL calls.
- Avoid heavy operations in `__init__`; defer to background threads or after `mainloop()` if possible.
- Run `python -m pytest tests/test_performance_optimization.py -v` to verify caching/tracking behavior.

## Socat Notes

- SocatSender attempts resolution in this order: cached binary, configured download URL (where available), system PATH.
- Linux x86_64 auto-download is supported via settings.socat_linux_x64_url.
- Windows optional download can be configured with settings.socat_win_url.
- Darwin public auto-download URLs are treated as unreliable; PATH or cached binary is often required.
- **Socat Availability Detection**: Use `SocatSender.is_available()` to check if socat is available on the system (checks PATH and cached binaries).
- **Binary Validation**: Downloaded socat binaries are validated by running `socat --version` to ensure integrity.
- **Configurable Timeout**: Socat operations have a configurable timeout via `settings.socat_timeout` (default: 30 seconds for PS4/PS5 payload injection).
- **Enhanced Error Logging**: Socat errors now log detailed stderr output and timeout duration for better troubleshooting.
- **UI Integration**: Socat checkbox displays a popup with localized installation instructions when clicked if socat is not available. The message is fully translated in all supported languages (English, Spanish, Portuguese, Chinese, Korean). Checkbox works normally when socat is detected.

## Naming and Style

- snake_case for functions, methods, variables, and files.
- PascalCase for classes.
- Keep changes direct and small; avoid broad refactors unless explicitly requested.

## Automatic Version Management

The project uses **Semantic Versioning** with automatic version bumping during CI/CD builds:

- Each push to `main` triggers the pipeline to analyze commits
- Commits using conventional format trigger version bumps:
	- `feat:` → minor bump (for example: `X.Y.Z` → `X.(Y+1).0`)
	- `fix:` → patch bump (for example: `X.Y.Z` → `X.Y.(Z+1)`)
	- `breaking:` → major bump (for example: `X.Y.Z` → `(X+1).0.0`)
  - `docs:`, `chore:`, `test:` → no bump
- Version bumping pipeline automatically:
  - Updates `src/models/version.py`
	- Updates `docs/CHANGELOG.md`
	- Creates git tags (e.g., `v1.0.0`)
  - Builds executables with new version
  - Creates GitHub Release

For details and examples, see [VERSIONING.md](VERSIONING.md) (English) or [VERSIONING_ES.md](VERSIONING_ES.md) (Spanish).

Local testing:
```sh
# Preview version bump without changes
python build_local/bump_version.py --dry-run

# Apply version bump locally
python build_local/bump_version.py

# Show version bump demonstration
bash build_local/demo_version.sh
```

## SOLID Requirement

- Any new or modified production code must follow SOLID principles.
- Apply SOLID pragmatically to this codebase style: improve design clarity without introducing unnecessary abstraction.
- In particular:
	- Single Responsibility: keep GUI orchestration in main.py and isolate domain behavior in focused modules.
	- Open/Closed: prefer extending existing abstractions (for example PayloadSender implementations) instead of editing unrelated flows.
	- Liskov Substitution: preserve behavior contracts when subclassing abstractions.
	- Interface Segregation: avoid forcing modules to depend on methods they do not use.
	- Dependency Inversion: depend on abstractions where it improves testability and maintainability.

## Dependencies

Dependencies are split by purpose:

- Runtime/publication: requirements.txt
- Testing: requirements-test.txt
- Development: requirements-dev.txt

Current runtime code uses modules that require:

- requests
- pydantic
- pydantic-settings
- Pillow (PIL)

If dependency definitions are touched, keep requirements and runtime imports aligned.
