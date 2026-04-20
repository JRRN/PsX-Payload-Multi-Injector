# PS MultiInjector

![version](https://img.shields.io/badge/version-1.0.0-blue)

[Ver changelog](./CHANGELOG.md)

READMEs por idioma: [Español](../README.md), [English](./README_en.md), [Português](./README_pt.md), [中文](./README_zh.md), [한국어](./README_ko.md)

Injetor multiplataforma de payloads para PS4/PS5 em Python com interface gráfica, baseado na ideia original de MaNu(TheWizWikii) https://github.com/TheWizWikii/PS5-PS4-Payload-injector-Pro

## Funcionalidades
- Interface gráfica multiplataforma (PySide6/Qt)
- Download e seleção de payloads via GitHub
- Envio de payloads por TCP ou Socat
- Multi-idioma (troca dinâmica de idioma com bandeiras)
- Resolução automática do Socat com cache, PATH do sistema e URLs opcionais
- Configuração com pydantic-settings

## Novidade na versão 1.0.0
- Pipeline de estilos renovado com QSS para uma UI mais consistente entre plataformas.
- Ajustes de testes para execução headless com Qt (`QT_QPA_PLATFORM=offscreen`).

## Instalação

1. Clone o repositório e entre na pasta:
   ```sh
   git clone <repo-url>
   cd PsX-Payload-Multi-Injector
   ```
2. Instale as dependências (requer Python 3.8+). Você pode usar `uv` (mais rápido) ou `pip`:

   Com uv (recomendado):
   ```sh
   uv pip install -r requirements.txt
   ```
   Ou com pip:
   ```sh
   pip install -r requirements.txt
   ```
   Perfis opcionais:
   ```sh
   # Testes (runtime + pytest)
   uv pip install -r requirements-test.txt

   # Desenvolvimento (runtime + teste + flake8 + watchdog)
   uv pip install -r requirements-dev.txt
   ```
3. Execute o app:
   ```sh
   python src/main.py
   ```

## Estrutura do projeto
- `src/` — Código-fonte principal
- `tests/` — Testes unitários e de integração com mocks
- `requirements.txt` — Dependências de runtime para publicação/executável
- `requirements-test.txt` — Runtime + dependências de teste
- `requirements-dev.txt` — Runtime + teste + ferramentas de desenvolvimento
- `README_pt.md` — Este arquivo

## Testes

A suíte de testes fica em `tests/`.

- Ative seu ambiente virtual e instale dependências:
   ```sh
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```
- Execute os testes:
   ```sh
   pytest tests
   ```

A suíte usa imports de pacote (`src.*`). `tests/conftest.py` adiciona a raiz do projeto ao path durante a coleta do `pytest`, então não é necessário exportar `PYTHONPATH`.

## Logs e Depuração

Quando o aplicativo falha (especialmente no `.app`/`.exe` compilado), um arquivo de log é gravado automaticamente:

| Plataforma | Caminho do log |
|---|---|
| **macOS** | `~/Library/Logs/PS_MultiInjector/app.log` |
| **Windows** | `%APPDATA%\PS_MultiInjector\Logs\app.log` |
| **Linux** | `~/.local/share/PS_MultiInjector/logs/app.log` |

Ler logs após falha:

```bash
# macOS / Linux
cat ~/Library/Logs/PS_MultiInjector/app.log      # macOS
cat ~/.local/share/PS_MultiInjector/logs/app.log  # Linux

# Windows (PowerShell)
type "$env:APPDATA\PS_MultiInjector\Logs\app.log"
```

Ao executar como bundle compilado (`PyInstaller`), `stdout` e `stderr` também são redirecionados para este arquivo.

## Dependências

### Dependências de Runtime
- **Python 3.8+** (obrigatório)
- **PySide6** (framework Qt para a interface gráfica)
- **socat** (opcional, mas recomendado para injeção de payloads em PS4/PS5)
   - Sem socat: apenas o método TCP fica disponível
   - Com socat: métodos TCP e Socat ficam disponíveis

### Instalando o Socat

Socat é uma dependência opcional, mas recomendada para injeção avançada de payloads em PS4/PS5. O app detecta automaticamente sua disponibilidade e desativa o checkbox de Socat quando não está instalado.

**macOS (Intel e Apple Silicon)**
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
Quatro opções:
1. **WSL (Recomendado)** — Instale o Windows Subsystem for Linux e use os comandos Linux acima
2. **MSYS2/Cygwin** — Instale via gerenciador de pacotes
3. **scoop** — `scoop install socat`
4. **Binário manual** — Veja [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md) para instruções por sistema

### Instalação manual do binário

Para colocar manualmente o binário do socat no diretório da aplicação, consulte [SOCAT_MANUAL_SETUP.md](SOCAT_MANUAL_SETUP.md).

**Caminhos rápidos:**
- **macOS:** `~/Library/Application Support/PS_MultiInjector/socat/`
- **Windows:** `%APPDATA%\PS_MultiInjector\socat\`
- **Linux:** `~/.local/share/PS_MultiInjector/socat/`

Se o socat não for encontrado, o app:
- Mostra instruções de instalação
- Desativa o checkbox "Enable SOCAT"
- Continua permitindo injeção via TCP

## Uso do Socat para PS4/PS5

Socat oferece um método alternativo ao TCP para injeção de payloads em consoles PS4/PS5.

Detecção automática no app:
- Se encontrado: checkbox "Enable SOCAT" ativo
- Se não encontrado: checkbox desativado com instruções de instalação

## Fontes do Socat (SO/Arquitetura)

A ordem de resolução do Socat é:
1. Binário em cache no diretório de dados do usuário.
2. Binário do sistema encontrado no `PATH`.
3. Download pela URL configurada (apenas quando existe fonte válida/configurada).

Fontes validadas e comportamento atual:

| Plataforma | Arquitetura | Comportamento padrão |
|---|---|---|
| macOS | arm64 / x86_64 | Usar `socat` do sistema via Homebrew (`brew install socat`) |
| Linux | x86_64 | Suporta auto-download (URL padrão) ou `socat` do sistema |
| Linux | arm64 | Usar pacote da distro (`apt`, `dnf`, `pacman`) |
| Windows | x86_64 | Usar `socat` do sistema (MSYS2/Cygwin) ou definir `SOCAT_WIN_URL` |
| Windows | arm64 | Usar binário do sistema/gerenciador de pacotes ou URL interna |

Notas:
- URLs públicas antigas de static-binaries para macOS e Windows não são confiáveis e não são usadas por padrão.
- Você pode sobrescrever URLs via `.env` se controla uma fonte confiável.
- Binários de Socat em cache ficam no diretório de dados do usuário.
- Operações com Socat têm timeout configurável (padrão: 30 segundos) para injeção de payloads em PS4/PS5.

## Notas
- O seletor de idioma usa bandeiras Unicode via `open_flags` (sem imagens locais).
- É possível adicionar novos idiomas criando JSON em `src/lang`.
- É necessária conexão com internet para baixar a lista de payloads e binários externos do Socat.
- A lista de payloads deve estar em JSON com seções `PS4` e/ou `PS5`.
- Antes do envio, o app valida o formato de IP e o intervalo de porta (1-65535). Tanto a carga inicial de payloads quanto o envio rodam em segundo plano para manter a interface responsiva.

## Como adicionar um novo idioma

O seletor de idiomas detecta automaticamente arquivos `*.json` em `src/lang`, então você não precisa hardcodar listas de idiomas no código.

Passos recomendados:

1. Crie um novo arquivo de tradução com locale em minúsculas, por exemplo:
   - `src/lang/fr-fr.json`
   - `src/lang/ja-jp.json`
2. Copie todas as chaves de `src/lang/en-us.json` (ou `src/lang/es-es.json`) e traduza apenas os valores.
3. Mantenha as chaves em `snake_case` e não remova nenhuma.
4. Rode os testes de paridade de chaves:
   ```sh
   python -m pytest tests/test_config_and_lang.py -v
   ```
5. Reinicie o app: o novo idioma aparecerá automaticamente no seletor.

Notas:
- O nome do arquivo define o locale (`en-us`, `es-es`, etc.).
- A bandeira é resolvida pelo país do locale (`us`, `es`, `jp`, etc.).
- A configuração de idioma usa locales completos (`xx-yy`). Aliases de código base (`en`, `es`, etc.) não são mantidos.

## Uso de `uv` e `watchdog` para desenvolvimento

Para um fluxo de desenvolvimento rápido:

1. Instale dependências:
   ```sh
   uv pip install -r requirements-dev.txt
   ```
2. Execute o app:
   ```sh
   uv run src/main.py
   ```
3. Auto-restart ao salvar arquivos:
   ```sh
   watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py
   ```

## Gerar executáveis nativos

Você pode gerar um executável nativo para seu sistema operacional local usando os scripts em `build_local/`:

- **Linux, macOS ou Windows:**
   ```sh
   python build_local/build_local.py
   ```

Isso irá gerar um executável na pasta `dist/` com nome e versão para sua arquitetura e sistema operacional.

## Agradecimentos

- [MaNu (TheWizWikii)](https://github.com/TheWizWikii)
