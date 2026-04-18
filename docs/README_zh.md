# PS MultiInjector

![version](https://img.shields.io/badge/version-1.1.0-blue)

[查看变更日志](./CHANGELOG.md)

多语言 READMEs: [Español](../README.md), [English](./README_en.md), [Português](./README_pt.md), [中文](./README_zh.md), [한국어](./README_ko.md)

PS4/PS5 跨平台 Payload 注入工具（Python + 图形界面），基于 MaNu(TheWizWikii) 的原始思路 https://github.com/TheWizWikii/PS5-PS4-Payload-injector-Pro

## 功能
- 跨平台图形界面（PySide6/Qt）
- 从 GitHub 下载并选择 payload
- 通过 TCP 或 Socat 发送 payload
- 多语言（支持动态切换语言与旗帜）
- Socat 自动解析（缓存、系统 PATH、可选 URL）
- 使用 pydantic-settings 管理配置

## 1.1.0 新特性
- 使用 QSS 重构样式流程，提升跨平台界面一致性。
- 测试环境已适配 Qt 无头模式（`QT_QPA_PLATFORM=offscreen`）。

## 安装

1. 克隆仓库并进入目录：
   ```sh
   git clone <repo-url>
   cd PS_MultiInjector/PS_MultiInjector
   ```
2. 安装依赖（需要 Python 3.8+）。可使用 `uv`（更快）或 `pip`：

   使用 uv（推荐）：
   ```sh
   uv pip install -r requirements.txt
   ```
   或使用 pip：
   ```sh
   pip install -r requirements.txt
   ```
   可选依赖组合：
   ```sh
   # 测试（runtime + pytest）
   uv pip install -r requirements-test.txt

   # 开发（runtime + 测试 + flake8 + watchdog）
   uv pip install -r requirements-dev.txt
   ```
3. 运行应用：
   ```sh
   python src/main.py
   ```

## 项目结构
- `src/` — 主源码
- `tests/` — 单元测试与集成测试（mock）
- `requirements.txt` — 发布/可执行文件运行时依赖
- `requirements-test.txt` — 运行时 + 测试依赖
- `requirements-dev.txt` — 运行时 + 测试 + 开发工具
- `README_zh.md` — 本文件

## 测试

测试位于 `tests/` 目录。

- 激活虚拟环境并安装依赖：
   ```sh
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```
- 运行测试：
   ```sh
   pytest tests
   ```

测试使用包导入（`src.*`）。`tests/conftest.py` 会在 pytest 收集阶段自动将项目根目录加入导入路径。

## 日志与调试

应用崩溃时（尤其是构建后的 `.app`/`.exe`），会自动写入日志：

| 平台 | 日志路径 |
|---|---|
| **macOS** | `~/Library/Logs/PS_MultiInjector/app.log` |
| **Windows** | `%APPDATA%\PS_MultiInjector\Logs\app.log` |
| **Linux** | `~/.local/share/PS_MultiInjector/logs/app.log` |

查看日志：

```bash
# macOS / Linux
cat ~/Library/Logs/PS_MultiInjector/app.log      # macOS
cat ~/.local/share/PS_MultiInjector/logs/app.log  # Linux

# Windows (PowerShell)
type "$env:APPDATA\PS_MultiInjector\Logs\app.log"
```

## Socat 来源（系统/架构）

Socat 解析顺序：
1. 用户数据目录中的缓存二进制。
2. 系统 `PATH` 中的二进制。
3. 配置 URL 下载（仅在有可用来源时）。

当前验证行为：

| 平台 | 架构 | 默认行为 |
|---|---|---|
| macOS | arm64 / x86_64 | 使用 Homebrew 安装的系统 `socat` |
| Linux | x86_64 | 支持自动下载（默认 URL）或系统 `socat` |
| Linux | arm64 | 使用发行版包管理器 |
| Windows | x86_64 | 使用系统 `socat` 或在 `.env` 设置 `SOCAT_WIN_URL` |
| Windows | arm64 | 使用系统/包管理器二进制或自定义内部 URL |

## 说明
- 语言选择器使用 `open_flags` 提供的 Unicode 旗帜。
- 可通过在 `src/lang` 新增 JSON 文件来添加语言。
- 下载 payload 列表与外部 Socat 二进制需要联网。
- 发送前，应用会校验 IP 格式与端口范围（1-65535）。初始 payload 列表加载和发送流程都采用异步执行，以保持界面响应。

## 如何添加新语言

语言选择器会自动发现 `src/lang` 中的 `*.json` 文件，因此新增语言时无需在代码中硬编码语言列表。

推荐步骤：

1. 使用小写 locale 创建新翻译文件，例如：
   - `src/lang/fr-fr.json`
   - `src/lang/ja-jp.json`
2. 从 `src/lang/en-us.json`（或 `src/lang/es-es.json`）复制全部键，仅翻译值。
3. 保持键名为 `snake_case`，不要删除任何键。
4. 运行键一致性测试：
   ```sh
   python -m pytest tests/test_config_and_lang.py -v
   ```
5. 重启应用：新语言会自动出现在选择器中。

说明：
- 文件名就是 locale（如 `en-us`、`es-es`）。
- 旗帜由 locale 的国家代码解析（如 `us`、`es`、`jp`）。
- 语言配置使用完整 locale（`xx-yy`），不再维护基础代码别名（如 `en`、`es`）。

## 使用 `uv` 与 `watchdog` 开发

1. 安装开发依赖：
   ```sh
   uv pip install -r requirements-dev.txt
   ```
2. 运行应用：
   ```sh
   uv run src/main.py
   ```
3. 保存时自动重启：
   ```sh
   watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py
   ```

## 构建本地可执行文件

你可以使用 `ci-cd/` 目录中的脚本在本地为当前操作系统生成原生可执行文件：

- **Linux 或 macOS（Intel 或 ARM）：**
   ```sh
   bash ci-cd/build_local.sh
   ```
- **Windows：**
   在 CMD 或 PowerShell 中运行：
   ```bat
   ci-cd\build_local.bat
   ```

生成的可执行文件位于 `dist/` 目录中，请在各平台分别构建。

## 致谢

- [MaNu (TheWizWikii)](https://github.com/TheWizWikii)
