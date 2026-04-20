# PS MultiInjector

![version](https://img.shields.io/badge/version-1.0.0-blue)

[변경 이력 보기](./CHANGELOG.md)

언어별 README: [Español](../README.md), [English](./README_en.md), [Português](./README_pt.md), [中文](./README_zh.md), [한국어](./README_ko.md)

PS4/PS5용 크로스플랫폼 페이로드 인젝터(Python GUI)로, MaNu(TheWizWikii)의 원 아이디어를 기반으로 합니다.
https://github.com/TheWizWikii/PS5-PS4-Payload-injector-Pro

## 주요 기능
- 크로스플랫폼 GUI (PySide6/Qt)
- GitHub에서 페이로드 목록 다운로드 및 선택
- TCP 또는 Socat으로 페이로드 전송
- 다국어 지원(플래그 포함 동적 언어 전환)
- Socat 자동 해석(캐시, 시스템 PATH, 선택 URL)
- pydantic-settings 기반 설정

## 1.0.0 신규 기능
- QSS 기반 스타일 파이프라인으로 플랫폼 간 UI 일관성을 강화했습니다.
- Qt 헤드리스 실행을 위한 테스트 설정을 반영했습니다 (`QT_QPA_PLATFORM=offscreen`).

## 설치

1. 저장소를 클론하고 폴더로 이동:
   ```sh
   git clone <repo-url>
   cd PsX-Payload-Multi-Injector
   ```
2. 의존성 설치(Python 3.8+ 필요). `uv`(권장) 또는 `pip` 사용:

   uv 사용(권장):
   ```sh
   uv pip install -r requirements.txt
   ```
   또는 pip 사용:
   ```sh
   pip install -r requirements.txt
   ```
   선택 프로필:
   ```sh
   # 테스트 (runtime + pytest)
   uv pip install -r requirements-test.txt

   # 개발 (runtime + test + flake8 + watchdog)
   uv pip install -r requirements-dev.txt
   ```
3. 앱 실행:
   ```sh
   python src/main.py
   ```

## 프로젝트 구조
- `src/` — 메인 소스 코드
- `tests/` — 단위/통합(mock) 테스트
- `requirements.txt` — 배포/실행 파일용 런타임 의존성
- `requirements-test.txt` — 런타임 + 테스트 의존성
- `requirements-dev.txt` — 런타임 + 테스트 + 개발 도구
- `README_ko.md` — 이 문서

## 테스트

테스트 스위트는 `tests/`에 있습니다.

- 가상환경 활성화 및 의존성 설치:
   ```sh
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```
- 테스트 실행:
   ```sh
   pytest tests
   ```

테스트는 패키지 임포트(`src.*`)를 사용하며, `tests/conftest.py`가 pytest 수집 시 프로젝트 루트를 경로에 추가합니다.

## 로그 및 디버깅

앱이 크래시할 때(특히 빌드된 `.app`/`.exe`) 로그 파일이 자동 생성됩니다.

| 플랫폼 | 로그 경로 |
|---|---|
| **macOS** | `~/Library/Logs/PS_MultiInjector/app.log` |
| **Windows** | `%APPDATA%\PS_MultiInjector\Logs\app.log` |
| **Linux** | `~/.local/share/PS_MultiInjector/logs/app.log` |

로그 확인:

```bash
# macOS / Linux
cat ~/Library/Logs/PS_MultiInjector/app.log      # macOS
cat ~/.local/share/PS_MultiInjector/logs/app.log  # Linux

# Windows (PowerShell)
type "$env:APPDATA\PS_MultiInjector\Logs\app.log"
```

컴파일된 번들(`PyInstaller`)로 실행하면 `stdout`과 `stderr`도 이 로그 파일로 리다이렉트됩니다. 개발 모드(`uv run src/main.py`)에서는 로그가 파일에 기록되면서 터미널에서도 오류를 확인할 수 있습니다.

## 의존성

### 런타임 의존성
- **Python 3.8+** (필수)
- **PySide6** (Qt GUI 프레임워크)
- **socat** (선택 사항이지만 PS4/PS5 페이로드 주입에 권장)
   - socat 미설치: TCP 방식만 사용 가능
   - socat 설치: TCP/Socat 모두 사용 가능

### Socat 설치

Socat은 선택 사항이지만 권장됩니다. 앱은 Socat 사용 가능 여부를 자동 감지하며, 없으면 Socat 체크박스를 비활성화합니다.

**macOS (Intel & Apple Silicon)**
```bash
brew install socat
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt install socat
```

**Linux (Fedora/RHEL)**
```bash
sudo dnf install socat
```

**Linux (Arch)**
```bash
sudo pacman -S socat
```

**Windows**
네 가지 방법:
1. **WSL (권장)** — Windows Subsystem for Linux를 설치한 뒤 위 Linux 명령 사용
2. **MSYS2/Cygwin** — 패키지 매니저로 설치
3. **scoop** — `scoop install socat`
4. **수동 바이너리** — [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md) 참고

### 수동 바이너리 설치

앱 디렉터리에 socat 바이너리를 수동으로 배치하려면 [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md)를 참고하세요.

**빠른 경로:**
- **macOS:** `~/Library/Application Support/PS_MultiInjector/socat/`
- **Windows:** `%APPDATA%\PS_MultiInjector\socat\`
- **Linux:** `~/.local/share/PS_MultiInjector/socat/`

socat을 찾지 못하면 앱은:
- 설치 방법 안내를 표시
- "Enable SOCAT" 체크박스를 비활성화
- TCP 기반 주입은 계속 허용

## PS4/PS5에서 Socat 사용

Socat은 PS4/PS5 페이로드 주입에서 TCP의 대체 전송 방식을 제공합니다.

앱의 자동 감지 동작:
- 감지됨: "Enable SOCAT" 체크박스 활성
- 미감지: 체크박스 비활성 + 설치 안내 표시

## Socat 소스 (OS/아키텍처)

Socat 해석 순서:
1. 사용자 데이터 폴더의 캐시 바이너리
2. 시스템 `PATH`의 바이너리
3. 설정된 URL 다운로드(유효 소스가 있을 때만)

현재 기본 동작:

| 플랫폼 | 아키텍처 | 기본 동작 |
|---|---|---|
| macOS | arm64 / x86_64 | Homebrew의 시스템 `socat` 사용 |
| Linux | x86_64 | 자동 다운로드(기본 URL) 또는 시스템 `socat` |
| Linux | arm64 | 배포판 패키지 사용 |
| Windows | x86_64 | 시스템 `socat` 또는 `.env`의 `SOCAT_WIN_URL` |
| Windows | arm64 | 시스템/패키지 바이너리 또는 커스텀 URL |

참고:
- macOS/Windows용 기존 public static-binaries URL은 신뢰성이 낮아 기본값으로 사용하지 않습니다.
- 신뢰 가능한 내부 바이너리 소스가 있다면 `.env`로 URL을 재정의할 수 있습니다.
- 캐시된 Socat 바이너리는 사용자 데이터 디렉터리에 저장됩니다(앱 번들 내부 아님).
- Socat 동작은 설정 가능한 타임아웃(기본 30초)을 사용합니다.

## 참고
- 언어 선택기는 `open_flags` 기반 Unicode 플래그를 사용합니다.
- `src/lang`에 JSON을 추가하면 새 언어를 확장할 수 있습니다.
- 페이로드 목록 및 외부 Socat 바이너리 다운로드에는 인터넷이 필요합니다.
- 페이로드 목록은 `PS4` 및/또는 `PS5` 섹션을 포함한 JSON 형식이어야 합니다.
- 전송 전에 앱이 IP 형식과 포트 범위(1-65535)를 검증합니다. 초기 페이로드 목록 로딩과 전송 모두 비동기로 처리되어 UI 응답성을 유지합니다.

## 새 언어 추가 방법

언어 선택기는 `src/lang`의 `*.json` 파일을 자동 탐지하므로, 새 번역을 추가할 때 코드에 언어 목록을 하드코딩할 필요가 없습니다.

권장 절차:

1. 소문자 locale 코드로 새 번역 파일 생성:
   - `src/lang/fr-fr.json`
   - `src/lang/ja-jp.json`
2. `src/lang/en-us.json`(또는 `src/lang/es-es.json`)의 모든 키를 복사하고 값만 번역합니다.
3. 키는 `snake_case`를 유지하고 삭제하지 않습니다.
4. 키 정합성 테스트 실행:
   ```sh
   python -m pytest tests/test_config_and_lang.py -v
   ```
5. 앱을 재시작하면 새 언어가 자동으로 선택기에 나타납니다.

참고:
- 파일명이 locale을 정의합니다(`en-us`, `es-es` 등).
- 플래그는 locale의 국가 코드(`us`, `es`, `jp` 등)로 해석됩니다.
- 언어 설정은 전체 locale 코드(`xx-yy`)를 사용하며, 기본 코드 별칭(`en`, `es` 등)은 유지하지 않습니다.

## 개발에서 `uv`와 `watchdog` 사용

1. 개발 의존성 설치:
   ```sh
   uv pip install -r requirements-dev.txt
   ```
2. 앱 실행:
   ```sh
   uv run src/main.py
   ```
3. 저장 시 자동 재시작:
   ```sh
   watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py
   ```

## 네이티브 실행 파일 빌드

`build_local/` 스크립트를 사용해 현재 운영체제용 네이티브 실행 파일을 로컬에서 생성할 수 있습니다.

- **Linux, macOS, 또는 Windows:**
   ```sh
   python build_local/build_local.py
   ```

실행 파일은 `dist/` 폴더에 생성됩니다.

## 감사의 말

- [MaNu (TheWizWikii)](https://github.com/TheWizWikii)
