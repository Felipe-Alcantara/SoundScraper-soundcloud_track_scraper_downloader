# 🔧 Dependências do Projeto

Esta pasta concentra as dependências do **SoundScraper**: a lista de pacotes Python e
o espaço para o FFmpeg embutido (opcional). As dependências Python são instaladas
automaticamente pelo `start_app.py` / `run_cli.py`, então normalmente você não precisa
mexer aqui.

---

## 📦 Conteúdo

| Item | O que é | Versionado no repo? |
|---|---|---|
| `requirements.txt` | Pacotes Python de **runtime** (CLI + Web app) | ✅ Sim |
| `requirements-dev.txt` | Runtime **+** testes (`pytest`) e build (`pyinstaller`) | ✅ Sim |
| `ffmpeg/` | Apenas o `LICENSE` do FFmpeg (exigido para redistribuir o binário) | ⚠️ Parcial — **o binário não** |

> ⚠️ **O binário do FFmpeg não é versionado.** A pasta `ffmpeg/` guarda só a licença e a
> documentação. O SoundScraper resolve o FFmpeg em tempo de execução (ver abaixo).

---

## 🎬 FFmpeg (necessário para o download)

O SoundScraper procura o FFmpeg nesta ordem (ver `core/platform_utils.py → find_ffmpeg()`):

1. **Bundle do executável** — quando rodando como `.exe` empacotado (Windows).
2. **Embutido no projeto** — `deps/ffmpeg/ffmpeg-8.0-essentials_build/bin/ffmpeg(.exe)`,
   se você colocar o binário ali manualmente.
3. **FFmpeg do sistema no PATH** — caminho recomendado em Linux/macOS.

Instalação do FFmpeg do sistema:

```bash
# Linux (Debian/Ubuntu)
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

> O `start_app.py` e o CLI tentam instalar o FFmpeg automaticamente quando ele falta,
> detectando o gerenciador de pacotes do seu sistema.

---

## 🌐 Google Chrome / Chromium (opcional)

O navegador é usado **apenas** pelo fallback de coleta via Selenium. A coleta padrão usa a
**API v2 do SoundCloud via HTTP e não precisa de navegador**, então o Chrome é opcional.

- **Recomendado:** instale o Chrome/Chromium pelo seu sistema — o SoundScraper o detecta
  automaticamente (ver `core/browser_handler.py`).
- Se um navegador portátil for usado, ele fica fora do repositório (a pasta
  `deps/Navegador/` é ignorada pelo Git por causa do tamanho).

---

## 🚀 Instalação rápida

As dependências Python são instaladas automaticamente, mas você pode fazê-lo à mão:

```bash
# Runtime (CLI + Web app)
pip install -r deps/requirements.txt

# Desenvolvimento (runtime + testes + build)
pip install -r deps/requirements-dev.txt
```

Para rodar o projeto, veja o [README principal](../README.md):

```bash
python start_app.py   # interface web (instala + builda + sobe + abre o navegador)
python run_cli.py     # modo CLI (coleta + download no terminal)
```
