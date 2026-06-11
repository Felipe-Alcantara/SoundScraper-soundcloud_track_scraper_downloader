# 🤖 IA.md — Contexto operacional do SoundScraper

> Memória técnica do projeto para retomada rápida por IA ou por um novo mantenedor.
> Baseado no template do Felixo System Design. Registre **o que foi decidido, testado e aprendido**.
> Datas em `[YYYY-MM-DD]`. Mantenha cada item curto e registre o **porquê**.

---

## 🎯 OBJETIVO DO PROJETO

[2026-06-11] Ferramenta para arquivar coleções do SoundCloud: coleta os links de faixas de um
perfil/álbum/playlist e baixa o áudio em FLAC/MP3 com metadados e capa. Dois modos: **interface Web**
(FastAPI + WebSocket + React) e **CLI**. Público: uso pessoal/open source. Prioridade: simplicidade e
funcionar **cross-platform** (Windows, Linux, macOS).

---

## 🏁 METAS & MILESTONES

- [2026-06-11] ✅ Portabilidade cross-platform (FFmpeg, abertura de pasta, detecção de Chrome).
- [2026-06-11] ✅ `start_app.py` padrão (instala + builda + sobe + abre, com restart/--dev/--no-browser/--no-install).
- [2026-06-11] ✅ Refatoração da coleta no padrão de scraping (DTO + adapters + registry + pipeline).
- [2026-06-11] ✅ README reescrito (Web + CLI) e suíte de testes honesta (155 passando).

---

## 🛠️ STACK & DEPENDÊNCIAS

[2026-06-11] Backend: Python 3.10+ (testado 3.12) · FastAPI · uvicorn · websockets.
[2026-06-11] Frontend: React 19 · Vite 6 · Tailwind 3 (build em `frontend/dist/`, servido pelo backend em prod).
[2026-06-11] Coleta/Download: yt-dlp · mutagen · selenium · webdriver_manager · FFmpeg (sistema ou embutido).
[2026-06-11] Dev/build: pytest · pyinstaller. Runtime em `deps/requirements.txt`; dev em `deps/requirements-dev.txt`.

---

## 📐 DECISÕES DE ARQUITETURA

[2026-06-11] Camadas: `core/` (núcleo reutilizável + CLI) ← `backend/services/` (adapta o núcleo ao WebSocket)
← `backend/api/routes/` (REST/WS) ← `frontend/` (UI desacoplada por WebSocket). Motivo: separar regra de
negócio de I/O e de UI; permitir CLI e Web compartilharem a mesma lógica.

[2026-06-11] Coleta em `core/scraping/` no padrão do GUIA-SCRAPING-MULTIFORMATO (recorte pertinente):
DTO puro (`models.TrackLink`), `SourceAdapter` (Strategy), `registry` das 7 opções, `parsers` puros
(testáveis offline) e `pipeline` com fallback. Ordem: **API v2 HTTP primeiro** (sem navegador, robusto,
cross-platform) e **Selenium como fallback**. Motivo: método mais fácil/estável primeiro; somar um método novo
é registrar um adapter.

[2026-06-11] `browser_handler.py` mantém suas funções públicas, mas delega o **parsing** a `scraping.parsers`
(fonte única de verdade). Motivo: centralizar parsing sem quebrar os 41 testes que fixam a API do módulo nem o
build do EXE.

[2026-06-11] Não migrado para Playwright (decisão do mantenedor): Selenium já está integrado, testado e
empacotado no EXE via Selenium Manager. Playwright/Postgres/captura manual/public_url do guia **não se aplicam**
a um coletor de links para download.

---

## 🎨 DECISÕES DE DESIGN & CONVENÇÕES

[2026-06-11] Código e identificadores em PT-BR/EN misto (mantida a convenção existente do repo).
[2026-06-11] Lógica dependente de SO centralizada em `core/platform_utils.py` (FFmpeg, abrir pasta) — nada de
`os.startfile`/`.exe` hardcoded espalhado.
[2026-06-11] Limites de coleta configuráveis por env (`SOUNDSCRAPER_MAX_TRACKS`, `_MAX_PAGES`, `_TIMEOUT_MS`,
`_SCROLL_ROUNDS`) em `scraping/config.py`.
[2026-06-11] Commits em Conventional Commits (feat/fix/docs/refactor/test/chore), pequenos e por área.

---

## 🧪 TESTES IMPORTANTES

[2026-06-11] ✅ Suíte completa: 155 testes, offline (mocking + fixtures sanitizadas), ~2s.
[2026-06-11] ✅ `test_scraping_pipeline.py` (22): parsers da API v2, registry das 7 opções, pipeline
fail-safe/fallback — sem rede.
[2026-06-11] ✅ `test_downloader.py::TestFfmpegPath`: agora exercita `platform_utils.find_ffmpeg()` de verdade
(nome por SO, bundle, PATH, None) — antes falhava sempre fora do Windows.

---

## 🐛 BUGS & FIXES RELEVANTES

[2026-06-11] BUG: app só funcionava no Windows. CAUSA: caminho `ffmpeg.exe` hardcoded (core + backend) e
`os.startfile` (Windows-only). FIX: `core/platform_utils.py` com `find_ffmpeg()` (bundle → projeto → PATH) e
`open_folder()` (startfile/open/xdg-open); detecção de Chrome/Chromium em Linux/macOS em `browser_handler`.

[2026-06-11] BUG: badge "132 passing" falso; `test_ffmpeg_exists_in_project` assertava um binário `.exe` não
versionado. FIX: teste reescrito para validar comportamento real de `find_ffmpeg()` em qualquer SO.

[2026-06-11] BUG: web app não subia a partir de `deps/requirements.txt`. CAUSA: faltavam fastapi/uvicorn/
websockets. FIX: adicionados ao requirements; criado `requirements-dev.txt`.

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

[2026-06-11] SoundCloud API v2 (pública) via HTTP/urllib: extrai `client_id` dos scripts da home e consulta as
rotas REST (`/resolve`, `/users/{id}/{collection}`, `/tracks/{id}`). Sem credenciais/segredos.
[2026-06-11] yt-dlp + FFmpeg para download/conversão. FFmpeg resolvido em runtime (não versionado no repo além
do build do Windows).

---

## 📝 NOTAS GERAIS

[2026-06-11] FFmpeg **não é versionado** (só LICENSE/docs em `deps/ffmpeg/`); em Linux/macOS use o FFmpeg do
sistema (`apt install ffmpeg` / `brew install ffmpeg`).
[2026-06-11] O empacotamento via PyInstaller (`tools/build_exe.py`/`.spec`) gera **EXE de Windows**; build para
Linux/macOS é um trabalho futuro.
[2026-06-11] `core/soundcloud_tracks_downloader.py` chama `main()` no escopo global (sem guarda `__main__`) —
é o entry point do PyInstaller e é importado pelos testes via conftest. Mudar isso exige re-validar o build do
EXE; deixado como pendência intencional.

---

## 🧠 RESUMOS DE DECISÃO

[2026-06-11] CONTEXTO: aplicar o GUIA-SCRAPING-MULTIFORMATO sem quebrar os 41 testes de `browser_handler` nem o
build do EXE. ALTERNATIVAS: (a) reescrever browser_handler e migrar tudo para os adapters; (b) criar o pacote
`scraping/` novo e fazer browser_handler delegar o parsing. DECISÃO: (b) — parsing centralizado em
`scraping.parsers`, funções públicas de browser_handler preservadas. VALIDAÇÃO: 155 testes verdes; backend e CLI
importam; `start_app.py` sobe e responde `/api/info` no Linux.

[2026-06-11] CONTEXTO: ordem dos métodos de coleta. DECISÃO: HTTP API v2 primeiro (mais fácil/robusto, sem
navegador), Selenium como fallback; pipeline para de tentar no primeiro método com resultado. VALIDAÇÃO: testes
de fallback/fail-safe em `test_scraping_pipeline.py`.

---

> **Origem do template**: Felixo System Design — https://github.com/Felipe-Alcantara/Felixo-System-Design
