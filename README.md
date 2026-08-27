# 🎵 SoundScraper — SoundCloud Archive Tool

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-powered-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![Tests](https://img.shields.io/badge/Tests-162%20passing-brightgreen.svg)](#-testes-automatizados)
[![Cross-platform](https://img.shields.io/badge/SO-Windows%20%7C%20Linux%20%7C%20macOS-informational.svg)](#-requisitos)

**Ferramenta para arquivamento de coleções musicais do SoundCloud — com interface Web e CLI.**

[🚀 Início rápido](#-início-rápido) • [🖥️ Interface Web](#️-interface-web) • [⌨️ Modo CLI](#️-modo-cli) • [📂 Arquitetura](#-arquitetura) • [🔌 API](#-api-rest--websocket) • [🧪 Testes](#-testes-automatizados)

</div>

---

## 📋 Visão geral

**SoundScraper** coleta os links de faixas de um perfil/álbum/playlist do SoundCloud e baixa o áudio em
**FLAC** ou **MP3**, com metadados e capa embutidos. Ele tem **dois modos de uso, ambos cross-platform
(Windows, Linux e macOS)**:

- 🖥️ **Interface Web** — backend **FastAPI + WebSocket** servindo um frontend **React (Vite + Tailwind)**,
  com progresso de coleta e download em tempo real.
- ⌨️ **CLI** — script de terminal interativo, ideal para automação e uso rápido sem navegador.

A coleta de links usa um **pipeline com fallback**: tenta primeiro a **API v2 do SoundCloud via HTTP**
(rápida, robusta e **sem navegador**) e, se necessário, recorre ao **navegador (Selenium)**. O download é
feito pelo **yt-dlp** com **FFmpeg**.

> ⚠️ **Uso responsável**: faça backup apenas de conteúdo que você possui/criou ou que tenha permissão/é de
> domínio público. Respeite os direitos autorais e os Termos de Serviço do SoundCloud.

---

## 📦 Baixar o executável (CLI, sem instalar nada)

Toda tag `vX.Y.Z` publica uma [GitHub Release](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/releases/latest) com o **CLI** pronto
para Linux e Windows — sem precisar clonar o repositório nem instalar Python:

- **Linux**: [`soundcloud-downloader-linux-x86_64`](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/releases/latest) — dê `chmod +x` e rode.
- **Windows**: [`soundcloud-downloader-windows-x86_64.exe`](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/releases/latest) — baixe e rode.

A Release **Latest** sempre aponta para a versão publicada mais recente. **FFmpeg** ainda é
necessário no sistema para o download (ver [Requisitos](#-requisitos)); o executável cobre só
o modo CLI — a interface Web continua rodando a partir do código-fonte, com `python start_app.py`
(veja [Início rápido](#-início-rápido) abaixo).

> Toda build do `main` já roda testes e um smoke test em CI, mas só vira Release quando alguém
> empurra uma tag — ver [Como publicar uma Release](#como-publicar-uma-release) mais abaixo.

---

## 🚀 Início rápido

A forma mais simples — **um único comando** instala dependências, builda o frontend, sobe o servidor e abre o
navegador:

```bash
git clone https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader.git
cd SoundScraper-soundcloud_track_scraper_downloader
python start_app.py
```

Na primeira execução, o script cria o ambiente virtual `.venv/` e instala as
dependências Python nele. Isso evita conflitos com instalações Linux protegidas
pelo PEP 668; as dependências não são instaladas no Python do sistema.

Pré-requisitos: **Python 3.10+**. Para a interface web também é preciso **Node.js** (para buildar o frontend);
sem Node, a API REST/WebSocket continua disponível. **FFmpeg** é necessário para o download (ver
[Requisitos](#-requisitos)).

---

## 🖥️ Interface Web

```bash
python start_app.py            # instala + builda + sobe + abre o navegador (http://127.0.0.1:8000)
python start_app.py restart    # reinicia (libera a porta e sobe de novo)
python start_app.py --dev      # desenvolvimento: backend com reload (:8000) + Vite (:5173)
python start_app.py --no-browser   # sobe sem abrir o navegador (servidor/automação)
python start_app.py --no-install   # pula a instalação de dependências
```

Fluxo na interface: cole a URL do SoundCloud → escolha o que coletar → revise as faixas → escolha a pasta e o
formato (FLAC/MP3) → acompanhe coleta e download em tempo real.

> O backend também pode ser iniciado diretamente com `python run_web.py` (launcher simples, usado também no
> empacotamento). O `start_app.py` é o caminho recomendado por instalar dependências e buildar o frontend.

---

## ⌨️ Modo CLI

Para quem prefere o terminal ou quer automatizar — **um único comando**, de qualquer pasta do projeto:

```bash
pip install -r deps/requirements.txt   # alternativa manual (preferencialmente em um venv)
python run_cli.py                      # fluxo completo: coleta + download (com loop "baixar mais?")
python run_cli.py scrape               # só coleta os links (gera o .txt) e encerra
```

O fluxo completo (`python run_cli.py`):
1. **Coleta** os links — cole a URL e escolha entre as **7 opções** (Todas, Populares, Faixas, Álbuns,
   Playlists, Republicações, Curtidas). O TXT de links é gerado automaticamente.
2. **Baixa** o áudio em seguida — seletor de pasta nativo (tkinter, com fallback para texto), escolha do
   formato (FLAC/MP3), download com metadados e abertura automática da pasta. Ao final, pergunta se quer
   baixar mais.

> `run_cli.py` resolve os imports sozinho, então **não é preciso `cd core`**. Funciona em Windows, Linux e
> macOS. (Equivale a `python core/soundcloud_tracks_downloader.py`, mas roda de qualquer pasta.)

---

## 📂 Arquitetura

Separação clara de responsabilidades entre núcleo reutilizável, backend e frontend:

```
SoundScraper/
├── core/                          # 🧠 Núcleo reutilizável (CLI + lógica de coleta/download)
│   ├── soundcloud_track_scraper.py     # CLI de coleta de links
│   ├── soundcloud_tracks_downloader.py # CLI de download (yt-dlp + FFmpeg)
│   ├── browser_handler.py              # WebDriver (fallback) + I/O da API v2
│   ├── crash_logger.py                 # crash log + log de sessão
│   ├── platform_utils.py               # helpers cross-platform (FFmpeg, abrir pasta)
│   └── scraping/                       # 🔍 Pipeline de coleta (DTO + adapters + registry)
│       ├── models.py · config.py · parsers.py · registry.py · base.py · pipeline.py
│       └── adapters/  http_api.py (preferido) · selenium_browser.py (fallback)
│
├── backend/                       # 🌐 API FastAPI + WebSocket
│   ├── main.py                         # app FastAPI (serve a API e o frontend buildado)
│   ├── api/routes/  scraper.py · download.py · config.py
│   └── services/    scraper_service.py · download_service.py
│
├── frontend/                      # 🎨 React + Vite + Tailwind
│   ├── src/  App.jsx · components/ · hooks/ · utils/
│   └── package.json · vite.config.js
│
├── deps/                          # 🔧 Dependências
│   ├── requirements.txt · requirements-dev.txt
│   └── ffmpeg/                          # FFmpeg do Windows (opcional; ver Requisitos)
│
├── tools/                         # 🏗️ Build do executável
│   ├── build_exe.py · soundcloud_tracks_downloader.spec · icon/
│
├── tests/                         # 🧪 Suíte de testes (162 testes)
├── start_app.py                   # ▶️ Inicialização padrão da Web (instala + builda + sobe + abre)
├── run_cli.py                     # ⌨️ Entry point do modo CLI (coleta + download no terminal)
├── run_web.py                     # launcher simples do backend
└── README.md · LICENSE · .gitignore
```

### Pipeline de coleta (core/scraping/)

`pipeline.collect()` tenta os métodos na ordem **mais fácil → fallback** e devolve uma lista deduplicada
(fail-safe: lista vazia se nada for coletado, nunca dado parcial enganoso):

1. **HTTP API v2** (`adapters/http_api.py`) — sem navegador, funciona em qualquer SO.
2. **Selenium** (`adapters/selenium_browser.py`) — usado quando a API não cobre o caso.

O parsing da API vive em `parsers.py` (puro, testável offline) e as 7 opções de coleta ficam num único
`registry.py`. Limites (máximo de faixas/páginas, timeouts) são configuráveis por variável de ambiente em
`config.py` (`SOUNDSCRAPER_MAX_TRACKS`, `SOUNDSCRAPER_MAX_PAGES`, `SOUNDSCRAPER_TIMEOUT_MS`, ...).

---

## 🔌 API REST + WebSocket

O backend (porta 8000) expõe:

| Método | Rota | Descrição |
|---|---|---|
| `GET`  | `/api/info` | Versão do app e info do sistema |
| `POST` | `/api/scrape` | Coleta de links (síncrona) — body `{ "url": "...", "choice": "3" }` |
| `WS`   | `/api/ws/scrape` | Coleta com progresso em tempo real |
| `POST` | `/api/download` | Download (síncrono) — body `{ "tracks": [...], "output_dir": "...", "format": "flac" }` |
| `WS`   | `/api/ws/download` | Download com progresso em tempo real |
| `POST` | `/api/select-folder` | Abre o seletor de pasta nativo do sistema |

**Eventos do WebSocket de coleta** (`/api/ws/scrape`): `log`, `stage`, `track`, `done`, `error`.
**Eventos do WebSocket de download** (`/api/ws/download`): `start`, `complete`, `track_error`, `done`.

---

## 🧪 Testes automatizados

Suíte com **162 testes**, todos offline (sem rede ou acesso real ao SoundCloud — usam mocking e fixtures
sanitizadas) e executando em segundos.

```bash
pip install -r deps/requirements-dev.txt
python -m pytest tests/ -v
```

| Arquivo | Foco | Testes |
|---|---|---|
| `test_browser_handler.py` | WebDriver, I/O HTTP, client_id, rotas da API | 41 |
| `test_scraper.py` | validação de URL, opções, scroll/collect, save TXT | 31 |
| `test_crash_logger.py` | crash handler, SessionLogger, limpeza de logs | 31 |
| `test_downloader.py` | formato, correção de nomes, FFmpeg portável, .spec | 37 |
| `test_scraping_pipeline.py` | parsers offline, registry, pipeline (fallback/fail-safe) | 22 |

---

## 🏗️ Build do executável (Windows)

```bash
python tools/build_exe.py
```

Valida pré-requisitos (PyInstaller, módulos, FFmpeg, Selenium Manager, ícone), limpa builds anteriores, gera o
`.exe` em `dist/` com todas as dependências embutidas e abre a pasta ao concluir. O build empacota o núcleo
(`core/`), o pacote `scraping/` e o FFmpeg do Windows.

Em CI (`.github/workflows/build.yml`), o mesmo executável é gerado para **Linux e Windows** —
`tools/build_ci.py`, reprodutível em runner limpo, sem paths absolutos locais.

### Como publicar uma Release

Todo push para `main` só **valida** o build (testes + smoke test), sem publicar nada — os
binários ficam em CI Artifacts por 30 dias, para depuração. Uma **GitHub Release** nasce só
quando alguém empurra uma tag `vX.Y.Z`:

```bash
git tag v2.6.0
git push origin v2.6.0
```

Isso dispara de novo o build (Linux + Windows) e, se ele passar, publica a Release com os dois
binários anexados, notas geradas a partir dos commits desde a tag anterior (`--generate-notes`),
e marcada como **Latest** — a não ser que uma Release mais nova já exista (comparação por
`sort -V` em `.github/scripts/release-version.sh`, para uma tag antiga nunca sobrescrever a mais
recente como Latest só por ter terminado de publicar depois — problema já visto e corrigido no
Felixo AI Core, ver commit de referência no workflow). Falhas transitórias da API do GitHub
(HTTP 5xx) são reexecutadas sozinhas até 5 vezes, com espera crescente
(`.github/scripts/retry.sh`).

**Convenção de tag**: `vMAJOR.MINOR.PATCH` (ex.: `v2.6.0`). Releases anteriores a esta política
(`v1.0` até `2.5`) foram criadas manualmente e não seguem o prefixo `v` de forma consistente —
não precisam ser corrigidas, mas toda tag nova segue o padrão acima.

---

## 📋 Requisitos

- **Python 3.10+** (testado com 3.12).
- **Node.js** — apenas para buildar/rodar o frontend web (o modo CLI e a API não precisam).
- **FFmpeg** — necessário para extrair/converter o áudio. O SoundScraper procura, nesta ordem:
  1. FFmpeg empacotado no EXE (Windows);
  2. FFmpeg embutido no projeto em `deps/ffmpeg/.../bin/`;
  3. **FFmpeg do sistema no PATH** — recomendado em Linux/macOS:
     - Linux (Debian/Ubuntu): `sudo apt install ffmpeg`
     - macOS (Homebrew): `brew install ffmpeg`
     - Windows: [ffmpeg.org](https://ffmpeg.org/) ou `winget install Gyan.FFmpeg`
- **Google Chrome/Chromium** — **opcional**. Só é usado pelo fallback Selenium; a coleta via API v2 funciona
  sem navegador.

Dependências Python (instaladas por `start_app.py` ou `pip install -r deps/requirements.txt`):
`fastapi`, `uvicorn`, `websockets`, `yt-dlp`, `mutagen`, `selenium`, `webdriver_manager`.

---

## ❗ Problemas comuns

1. **FFmpeg não encontrado** → instale o FFmpeg do sistema (ver acima). O download depende dele.
2. **Porta 8000 ocupada** → `python start_app.py restart` libera a porta e sobe de novo.
3. **`npm` não encontrado** → instale o Node.js para usar a interface web; o CLI/API funcionam sem ele.
4. **Chrome não encontrado** → normal fora do Windows/sem Chrome: a coleta usa a API v2 automaticamente.
5. **Crash inesperado** → veja a pasta `logs/` (crash logs com traceback, versão do Python e do SO).

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Faça um fork, crie uma branch, rode os testes (`python -m pytest tests/`) e abra
um Pull Request. Ao reportar bugs, inclua versão do Python/SO, mensagem de erro e os logs da pasta `logs/`.

### Ideias para quem quiser contribuir
- Caminhos de FFmpeg/Chrome adicionais e detecção mais ampla por SO.
- Empacotamento (PyInstaller) também para Linux/macOS.
- Suporte a outros serviços de áudio.
- Catalogação local da coleção baixada.

---

## 📜 Licença

MIT — veja [LICENSE](LICENSE). Copyright (c) Felipe Alcântara.

## 🙏 Agradecimentos

[yt-dlp](https://github.com/yt-dlp/yt-dlp) · [FFmpeg](https://ffmpeg.org/) · [Selenium](https://www.selenium.dev/) ·
[mutagen](https://github.com/quodlibet/mutagen) · [FastAPI](https://fastapi.tiangolo.com/) ·
[React](https://react.dev/) · [Vite](https://vitejs.dev/) · [pytest](https://pytest.org/)

<div align="center">

**Desenvolvido por [Felipe Alcântara](https://github.com/Felipe-Alcantara)** — *preservando a música digital, uma track por vez* 🎵

</div>
