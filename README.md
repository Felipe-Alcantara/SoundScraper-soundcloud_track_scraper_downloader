# 🎵 SoundScraper - Professional SoundCloud Archive Tool

<div align="center">

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-Automated-43B02A.svg)](https://www.selenium.dev/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Powered-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![Tests](https://img.shields.io/badge/Tests-132%20passing-brightgreen.svg)](#-testes-automatizados)
[![Version](https://img.shields.io/badge/Version-1.0-orange.svg)](#)

**Uma solução completa e profissional para arquivamento de coleções musicais do SoundCloud**

[🚀 Início Rápido](#-início-rápido) • [📖 Documentação](#-índice) • [💾 Download Executável](#-versão-executável-para-download-imediato) • [🔧 Instalação](#-como-usar) • [🧪 Testes](#-testes-automatizados)

</div>

---

## 📋 Visão Geral

**SoundScraper** é uma ferramenta robusta e automatizada desenvolvida para preservação digital e backup de coleções musicais do SoundCloud. Diferente de downloaders simples, o SoundScraper oferece uma solução enterprise-grade que combina web scraping inteligente com **fallback HTTP via API v2**, processamento automatizado de metadados, sistema de crash logging, e gerenciamento de dependências auto-configurável.

### 🎯 Para Quem É Esta Ferramenta?

- **🎨 Artistas e Produtores**: Faça backup seguro de suas obras e portfólio
- **🎧 Curadores e DJs**: Arquive playlists e sets completos com metadados preservados
- **📚 Colecionadores**: Mantenha bibliotecas musicais organizadas e offline
- **🏢 Arquivistas Digitais**: Preserve conteúdo cultural com metadados completos
- **💼 Profissionais de Mídia**: Gerencie assets de áudio com rastreabilidade total

### ✨ Diferenciais Competitivos

#### 🔄 **Download em Massa Inteligente**
Não se limita a tracks individuais - baixe perfis completos incluindo:
- Discografias inteiras de artistas
- Playlists e sets completos
- Álbuns e EPs organizados
- Tracks populares e relacionados
- Curtidas e reposts de perfil
- Remixes e colaborações

#### 🌐 **Scraping Dual-Mode (Selenium + HTTP Fallback)**
Estratégia de coleta de links em duas camadas:
- **Modo Primário (Selenium)**: Navegação automatizada com Chrome headless, scroll infinito inteligente e seletores CSS robustos
- **Modo Fallback (HTTP API v2)**: Quando o navegador falha ou não está disponível, o SoundScraper usa a **API pública v2 do SoundCloud** via `urllib` puro (sem dependências extra), extraindo `client_id` automaticamente e consultando as rotas REST da API — funciona **sem navegador nenhum**

#### 📊 **Metadados Profissionais**
Cada arquivo baixado inclui automaticamente:
- **Informações do Artista**: Nome, perfil, links sociais
- **Detalhes da Track**: Título, descrição, gênero, BPM
- **Metadados Técnicos**: Data de upload, encoder, formato
- **Artwork Embutido**: Capa em alta resolução incorporada ao arquivo
- **Tags Personalizadas**: Palavras-chave, licença, comentários
- **Rastreabilidade**: Link original, data de backup, ferramenta utilizada

#### 🛠️ **Zero Configuration Setup**
- ✅ Verificação automática de dependências Python
- ✅ Instalação assistida com prompts inteligentes
- ✅ FFmpeg incluído (sem downloads externos)
- ✅ ChromeDriver auto-gerenciado com **3 estratégias de fallback**
- ✅ HTTP fallback funciona **sem Chrome instalado**
- ✅ Valores padrão inteligentes para todos os inputs
- ✅ Tratamento robusto de erros com mensagens claras

#### 🎨 **Interface Profissional com UX Aprimorado**
- Interface CLI moderna com emojis e formatação elegante
- **Seletor de pasta nativo** via `tkinter.filedialog` (com fallback para texto)
- **Nome do TXT gerado automaticamente** a partir da URL do perfil
- **Loop contínuo**: ao terminar, pergunta se deseja baixar mais músicas
- **Abertura automática da pasta** de destino após concluir os downloads
- Feedback visual em tempo real do progresso
- Mensagens de erro descritivas e acionáveis

#### 🛡️ **Sistema de Crash Logging**
- **Captura automática de exceções** não tratadas via `sys.excepthook`
- **Log de sessão completo**: toda saída do console duplicada para arquivo
- **Logs detalhados**: versão do Python, SO, traceback completo com data/hora
- **Auto-limpeza**: mantém no máximo 20 logs, removendo os mais antigos
- Pasta `logs/` com crash logs e logs de sessão separados

#### 📦 **Distribuição Standalone**
- Executável Windows (.exe) com todas as dependências embutidas
- Não requer Python, pip ou configuração manual
- **~130 MB** de solução plug-and-play (otimizado)
- **Script de build automatizado** (`Extra/build_exe.py`) para gerar o EXE

---

# 🎵 SoundCloud Music Downloader 🎶

## ⚡ Início Rápido

### Para Iniciantes (3 passos simples):

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader.git
   cd SoundScraper-soundcloud_track_scraper_downloader
   ```

2. **Instale o Google Chrome** (recomendado, mas **não obrigatório** — o fallback HTTP funciona sem Chrome):
   - 🌐 Baixe em: https://www.google.com/chrome/

3. **Execute o programa:**
   ```bash
   cd Arquivos
   python soundcloud_tracks_downloader.py
   ```

   ✨ **Pronto!** O script verificará e instalará automaticamente todas as dependências Python necessárias.

> 💡 **Sem Chrome?** Sem problema! Se o Selenium falhar ao abrir o navegador, o SoundScraper automaticamente usa o **modo HTTP (API v2)** para coletar os links. Nenhuma configuração adicional é necessária.

---

## 📖 Índice

1. [🚀 Versão Executável para Download Imediato](#-versão-executável-para-download-imediato)
2. [📂 Arquitetura do Projeto](#-arquitetura-do-projeto)
3. [📜 Módulos e Funções](#-módulos-e-funções)
   - [1. browser_handler.py — Motor de Navegação e HTTP](#1-browser_handlerpy--motor-de-navegação-e-http)
   - [2. crash_logger.py — Sistema de Logging](#2-crash_loggerpy--sistema-de-logging)
   - [3. soundcloud_track_scraper.py — Web Scraper](#3-soundcloud_track_scraperpy--web-scraper)
   - [4. soundcloud_tracks_downloader.py — Download Engine](#4-soundcloud_tracks_downloaderpy--download-engine)
4. [🚀 Como Usar](#-como-usar)
5. [🧪 Testes Automatizados](#-testes-automatizados)
6. [🏗️ Build do Executável](#️-build-do-executável)
7. [❗ Possíveis Problemas e Soluções](#-possíveis-problemas-e-soluções)
8. [📋 Requisitos](#-requisitos)
9. [📁 Estrutura de Saída](#-estrutura-de-saída)

---

## 🚀 Versão Executável para Download Imediato

Uma versão executável do downloader está disponível para facilitar ainda mais o uso da ferramenta. Com o arquivo `.exe`, você não precisa de um ambiente de desenvolvimento, IDEs, bibliotecas ou instalar dependências. Basta baixar ⬇️ e rodar ▶️ diretamente o executável, o que torna o processo extremamente simples e rápido 🏃💨!

📝 **Nota sobre o tamanho do executável**: O arquivo `.exe` tem aproximadamente **~130 MB** 🗂️. Ele contém todas as dependências necessárias embutidas, incluindo o Selenium 🕷️, o codec FFmpeg 🎥 e o Selenium Manager para gerenciamento automático do ChromeDriver. Todo esse conteúdo é necessário para garantir que o programa funcione de maneira autônoma 🤖, sem precisar de configurações adicionais.

Caso você prefira uma versão personalizada ou queira verificar o código, pode utilizar o código-fonte 📝, que é totalmente transparente e pode ser auditado diretamente.

### 🔨 Gerando o Executável Você Mesmo

Use o **script de build automatizado** incluído no projeto:

```bash
python Extra/build_exe.py
```

O script valida todos os pré-requisitos (módulos, FFmpeg, Selenium Manager, PyInstaller, ícone), limpa builds anteriores, compila o executável com todas as dependências e abre a pasta `dist/` automaticamente ao concluir.

---

## 📂 Arquitetura do Projeto

SoundScraper foi desenvolvido com uma **arquitetura modular de 4 camadas**, separando claramente as responsabilidades de navegação/HTTP, logging, scraping e download. Esta abordagem garante manutenibilidade, testabilidade (132 testes automatizados) e permite fácil extensão de funcionalidades.

### 🏗️ Estrutura de Diretórios

```
SoundScraper/
├── Arquivos/                              # 📜 Módulos principais (4 arquivos)
│   ├── browser_handler.py                 # 🌐 Motor de navegação + HTTP fallback
│   ├── crash_logger.py                    # 🛡️ Sistema de crash logging
│   ├── soundcloud_track_scraper.py        # 🔍 Web scraper (Selenium + HTTP)
│   └── soundcloud_tracks_downloader.py    # ⬇️ Download engine com yt-dlp
│
├── Dependencias/                          # 🔧 Dependências externas
│   ├── ffmpeg/                            # Codec de áudio (incluído)
│   │   └── ffmpeg-8.0-essentials_build/
│   │       └── bin/                       # ffmpeg.exe, ffprobe.exe
│   └── requirements.txt                   # Dependências Python
│
├── Extra/                                 # 🎨 Recursos adicionais
│   ├── build_exe.py                       # 🏗️ Script automatizado de build
│   ├── DLP Isolado/                       # Módulo DLP standalone
│   │   └── dlp.py
│   └── Ícone/                             # Ícone da aplicação (.ico)
│
├── tests/                                 # 🧪 Suite de testes (132 testes)
│   ├── conftest.py                        # Fixtures compartilhadas
│   ├── test_browser_handler.py            # 39 testes do browser_handler
│   ├── test_crash_logger.py               # 22 testes do crash_logger
│   ├── test_downloader.py                 # 22 testes do downloader
│   ├── test_scraper.py                    # 25 testes do scraper
│   └── __init__.py
│
├── logs/                                  # 📋 Logs automáticos (gitignored)
│   ├── crash_*.log                        # Logs de crash com traceback
│   └── sessao_*.log                       # Logs de sessão completos
│
├── soundcloud_tracks_downloader.spec      # ⚙️ Configuração PyInstaller
├── README.md                              # 📖 Esta documentação
├── LICENSE                                # ⚖️ Licença MIT
└── .gitignore                             # 🚫 Configuração Git
```

### 🔌 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    SOUNDSCRAPER v1.0                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐  ┌─────────────────────────┐  │
│  │   crash_logger.py    │  │   browser_handler.py    │  │
│  │  ─────────────────   │  │  ─────────────────────  │  │
│  │  • sys.excepthook    │  │  • WebDriver 3-fallback │  │
│  │  • SessionLogger     │  │  • HTTP API v2 fallback │  │
│  │  • Auto-cleanup      │  │  • Selenium Manager     │  │
│  └──────────┬───────────┘  └───────────┬─────────────┘  │
│             │                          │                 │
│  ┌──────────▼──────────────────────────▼─────────────┐  │
│  │         soundcloud_track_scraper.py               │  │
│  │  ─────────────────────────────────────────────    │  │
│  │  • Selenium scraping  → fallback HTTP scraping    │  │
│  │  • Auto-nome do TXT   • MAX_ATTEMPTS = 3         │  │
│  │  • 7 opções de coleta • Scroll infinito           │  │
│  └──────────────────────────┬────────────────────────┘  │
│                              │                           │
│  ┌──────────────────────────▼────────────────────────┐  │
│  │       soundcloud_tracks_downloader.py             │  │
│  │  ─────────────────────────────────────────────    │  │
│  │  • yt-dlp download    • Folder picker nativo      │  │
│  │  • Metadados custom   • Loop de downloads         │  │
│  │  • FFmpeg pipeline    • Auto-open pasta destino   │  │
│  │  • FLAC / MP3         • Delete TXT após uso       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📜 Módulos e Funções

### 1. `browser_handler.py` — Motor de Navegação e HTTP

> **Novo módulo** que centraliza toda a lógica de navegação web e comunicação HTTP. Separa completamente as preocupações de I/O do scraper.

Este módulo implementa **duas estratégias de coleta** com fallback automático:

#### 🔧 Funções de Infraestrutura

| Função | Descrição |
|--------|-----------|
| `_get_base_path()` | Detecta o caminho base do projeto (compatível com `sys._MEIPASS` do PyInstaller para EXE) |
| `_find_chrome_binary()` | Busca o Chrome em múltiplos locais: `Program Files`, `LocalAppData`, Chrome portátil |
| `_find_bundled_chromedriver()` | Localiza ChromeDriver bundled na estrutura do projeto |
| `get_selenium_version()` | Retorna a versão do Selenium instalada |
| `_setup_selenium_manager_for_exe()` | Configura o Selenium Manager quando rodando como EXE empacotado |

#### 🌐 WebDriver com 3 Estratégias de Fallback

| Estratégia | Descrição |
|------------|-----------|
| **1ª** ChromeDriver Bundled | Tenta usar um ChromeDriver incluído localmente no projeto |
| **2ª** Selenium Manager | Usa o gerenciador nativo do Selenium 4.6+ para baixar o driver correto automaticamente |
| **3ª** webdriver-manager | Fallback final usando o pacote `webdriver_manager` do pip |

- *Função principal*: `get_webdriver()` — Tenta cada estratégia em sequência; retorna o WebDriver funcional ou `None` se todas falharem.

#### 📡 HTTP Fallback (API v2 do SoundCloud)

Quando o navegador não está disponível, o módulo usa **requisições HTTP puras** (apenas `urllib`, sem dependências extras):

| Função | Descrição |
|--------|-----------|
| `_http_get(url, headers)` | Requisição GET com User-Agent realista e tratamento de erros |
| `_extract_client_id(html_content)` | Extrai automaticamente o `client_id` do SoundCloud analisando os scripts JS da página |
| `_resolve_soundcloud_url(url, client_id)` | Resolve URL do perfil para obter `user_id` e dados via API |
| `_get_collection_tracks(user_id, collection_type, client_id)` | Coleta tracks de um perfil usando a API REST com paginação automática (`linked_partitioning`) |
| `_get_set_tracks(set_url, client_id)` | Coleta tracks de um set/playlist/álbum específico via API |
| `http_fallback_scraper(soundcloud_link, choice)` | Função principal do fallback — mapeia as 7 opções do menu para as rotas corretas da API |

---

### 2. `crash_logger.py` — Sistema de Logging

> **Novo módulo** que fornece captura automática de crashes e logging completo de sessão.

| Componente | Descrição |
|------------|-----------|
| `SOUNDSCRAPER_VERSION` | Constante de versão (`"1.0"`) usada nos logs |
| `_get_logs_folder()` | Determina a pasta de logs (compatível com EXE e script) |
| `_crash_handler(exc_type, exc_value, exc_tb)` | Substitui `sys.excepthook` — salva crash logs com: data/hora, versão Python, SO, traceback completo |
| `SessionLogger` | Classe que duplica `sys.stdout` e `sys.stderr` — tudo que aparece no console é salvo em `sessao_*.log` |
| `_cleanup_old_logs(max_logs=20)` | Remove automaticamente logs antigos quando a pasta excede 20 arquivos |
| `inicializar_logger()` | Função de inicialização — cria pasta, instala crash handler, inicia SessionLogger, executa limpeza |

**Exemplo de crash log gerado:**
```
══════════════════════════════════════════════════════════════
                  SOUNDSCRAPER - CRASH LOG
══════════════════════════════════════════════════════════════
  Data/Hora   : 2025-01-15 14:32:10
  Versão      : 1.0
  Python      : 3.14.2
  SO          : Windows-11-10.0.26100-SP0
  Executável  : soundcloud_tracks_downloader.exe
══════════════════════════════════════════════════════════════

Traceback (most recent call last):
  File "soundcloud_tracks_downloader.py", line 42, in main
    ...
```

---

### 3. `soundcloud_track_scraper.py` — Web Scraper

Este script coleta os links 🔗 de faixas de um perfil do SoundCloud. Ele tenta primeiro via **Selenium** e, caso falhe, usa automaticamente o **HTTP fallback** do `browser_handler.py`.

| Função | Descrição |
|--------|-----------|
| `check_and_install_requirements()` | Verifica e instala dependências Python automaticamente (protegido com `if __name__ == '__main__':`) |
| `get_soundcloud_link()` | Solicita e valida o link do perfil do SoundCloud |
| `get_user_choice(artist_url)` | Menu interativo com **7 opções** de coleta: Todas, Faixas Populares, Faixas, Álbuns, Playlists, Reposts, Curtidos |
| `scroll_and_collect_tracks(driver, ...)` | Scroll infinito inteligente com `MAX_ATTEMPTS = 3` (otimizado de 5 para 3) e coleta via seletores CSS |
| `save_track_links(filename, tracks)` | Salva links coletados em arquivo TXT |
| `soundcloud_track_scraper()` | **Função principal** — orquestra o fluxo: link → opção → Selenium → (fallback HTTP) → salvar TXT |

**Melhorias recentes:**
- 📝 **Nome do TXT gerado automaticamente** a partir da URL (ex: `artista_tracks.txt`) — sem precisar digitar
- ⚡ **MAX_ATTEMPTS reduzido de 5 para 3** — scraping mais rápido sem perda de conteúdo
- 🔄 **Fallback HTTP transparente** — se o Selenium falhar, o HTTP assume sem intervenção do usuário
- 🐛 **Correção do mapeamento `opcoes_nomes`** — todas as 7 opções funcionam corretamente

---

### 4. `soundcloud_tracks_downloader.py` — Download Engine

Script principal do SoundScraper. Orquestra todo o fluxo de download, processamento de metadados e organização dos arquivos.

| Função / Classe | Descrição |
|------------------|-----------|
| `check_and_install_requirements()` | Verificação de dependências com instalação automática |
| `CustomMetadataPP` (classe) | Post-processor do yt-dlp que injeta metadados personalizados (artista, álbum, gênero, artwork, data de backup, link original, etc.) |
| `_selecionar_pasta()` | **Seletor de pasta nativo** via `tkinter.filedialog.askdirectory()` — abre janela do sistema para escolher a pasta destino; fallback para input de texto se tkinter não estiver disponível |
| `_solicitar_formato()` | Solicita formato de áudio: **FLAC** (lossless) ou **MP3** (320kbps) |
| `_download_url(url, index, total, ydl_opts)` | Download individual com yt-dlp, retry automático e tratamento de erros |
| `_corrigir_nome_arquivo(output_folder)` | Renomeia arquivos removendo "NA" e substituindo `_` por espaços |
| `main()` | **Função principal** com loop `while True` — ao terminar os downloads, pergunta "Deseja baixar mais músicas? (S/N)" |

**Melhorias recentes:**
- 📂 **Seletor de pasta nativo**: Janela do sistema operacional para escolher a pasta de destino (sem digitar caminhos)
- 🔄 **Loop contínuo**: Após completar os downloads, o programa pergunta se deseja continuar com mais músicas
- 📁 **Abertura automática da pasta**: `os.startfile()` abre a pasta de destino automaticamente ao concluir
- 🗑️ **Limpeza do TXT**: O arquivo de links é deletado automaticamente após a leitura das URLs
- 🏗️ **Arquitetura `main()`**: Toda a lógica encapsulada em função `main()` — sem código solto no escopo global

---

## 🚀 Como Usar

### Opção 1: Executável (mais simples)

1. Baixe o `.exe` da seção [Releases](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/releases)
2. Execute o arquivo — tudo já está embutido
3. Cole o link do perfil/playlist do SoundCloud
4. Escolha a opção de coleta (faixas, álbuns, playlists, etc.)
5. Selecione a pasta de destino na janela que abrirá
6. Escolha o formato (FLAC ou MP3)
7. Aguarde os downloads — a pasta abrirá automaticamente ao concluir!

### Opção 2: Código-fonte

1. **Clone e entre no repositório:**
   ```bash
   git clone https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader.git
   cd SoundScraper-soundcloud_track_scraper_downloader
   ```

2. **Instale as dependências** (ou deixe o script instalar automaticamente):
   ```bash
   pip install -r Dependencias/requirements.txt
   ```

3. **Execute o programa:**
   ```bash
   cd Arquivos
   python soundcloud_tracks_downloader.py
   ```

4. **Siga as instruções na tela:**
   - Cole o link do perfil do SoundCloud
   - Escolha o que deseja coletar (1-7)
   - O TXT com os links será gerado automaticamente
   - Selecione a pasta de destino (janela nativa ou digite o caminho)
   - Escolha FLAC ou MP3
   - Aguarde os downloads!
   - Ao finalizar, a pasta abrirá automaticamente
   - Escolha se deseja baixar mais músicas ou encerrar

> **💡 Dica:** O Google Chrome é recomendado mas **não obrigatório**. Se não estiver instalado, o fallback HTTP via API v2 é usado automaticamente.

---

## 🧪 Testes Automatizados

O SoundScraper possui uma **suite completa de 132 testes automatizados** cobrindo todos os módulos:

### Executando os Testes

```bash
# Na raiz do projeto
python -m pytest tests/ -v
```

### Cobertura por Módulo

| Arquivo de Teste | Módulo Testado | Testes | Descrição |
|-------------------|---------------|--------|-----------|
| `test_browser_handler.py` | `browser_handler.py` | **39** | WebDriver fallback, HTTP requests, client_id extraction, API routes, URL resolution |
| `test_scraper.py` | `soundcloud_track_scraper.py` | **25** | Validação de links, opções do menu, scroll/collect, save, auto-nome do TXT |
| `test_crash_logger.py` | `crash_logger.py` | **22** | Crash handler, SessionLogger, log cleanup, pasta de logs, formato dos logs |
| `test_downloader.py` | `soundcloud_tracks_downloader.py` | **22** | Seleção de formato, correção de nomes, download pipeline, folder picker, metadata PP |
| `conftest.py` | — | — | Fixtures compartilhadas: `tmp_path`, mocks de WebDriver, URLs de teste |

### Resultado Esperado

```
============================= 132 passed in ~1.7s =============================
```

Todos os testes usam **mocking** (sem acesso real à internet ou ao SoundCloud) e executam em menos de 2 segundos.

---

## 🏗️ Build do Executável

O SoundScraper inclui um **script de build automatizado** que gera o executável `.exe` com todas as dependências:

### Uso

```bash
python Extra/build_exe.py
```

### O que o script faz:

1. ✅ **Valida pré-requisitos**: PyInstaller, módulos Python, FFmpeg, Selenium Manager, ícone
2. 🧹 **Limpa builds anteriores**: Remove `dist/` e `build/`
3. 🏗️ **Compila o executável**: PyInstaller com single-file, ícone personalizado, todos os binários e dados
4. 📊 **Mostra estatísticas**: Tamanho final, tempo de build
5. 📂 **Abre a pasta de saída**: `dist/` é aberta automaticamente
6. 🧹 **Limpa artefatos**: Remove pasta `build/` após compilação

### Dependências do Build

| Dependência | Uso |
|-------------|-----|
| PyInstaller | Empacotamento em `.exe` |
| FFmpeg 8.0 | Embutido para processamento de áudio |
| Selenium Manager | Embutido para gerenciamento do ChromeDriver |
| Ícone (`.ico`) | Personalização do executável |

---

## ❗ Possíveis Problemas e Soluções

1. **"cannot find Chrome binary"**: O Google Chrome não está instalado ou não foi encontrado.
   - **Solução**: Instale o Google Chrome em: https://www.google.com/chrome/
   - O script tenta encontrar o Chrome automaticamente em `Program Files`, `Program Files (x86)` e `LocalAppData`
   - **Alternativa**: O SoundScraper usará automaticamente o **fallback HTTP** se o Chrome não estiver disponível — não é obrigatório!

2. **Dependências Python Faltando**: Erros sobre módulos não encontrados (selenium, yt_dlp, etc.):
   - **Solução**: Execute o script normalmente! Ele verificará automaticamente as dependências e oferecerá instalá-las
   - Ou instale manualmente com: `pip install -r Dependencias/requirements.txt`

3. **WebDriver não inicia**: O driver de navegador é incompatível 🚫:
   - **Solução**: O SoundScraper tenta **3 estratégias de fallback** automaticamente:
     1. ChromeDriver bundled local
     2. Selenium Manager (Selenium 4.6+)
     3. webdriver-manager (pip)
   - Se todas falharem, o **HTTP fallback** assume automaticamente
   - Para limpar cache do driver: delete a pasta `.wdm` no diretório do usuário

4. **Erro ao Baixar Faixas**: Link incorreto ou inacessível:
   - **Solução**: Verifique se o link do SoundCloud está correto e acessível
   - O FFmpeg já está incluído no repositório, não precisa instalar separadamente

5. **Problemas com o FFmpeg**: O FFmpeg já vem incluído na pasta do projeto 🔧:
   - **Solução**: Não é necessário instalar o FFmpeg separadamente
   - O script usa automaticamente o FFmpeg de `Dependencias/ffmpeg/ffmpeg-8.0-essentials_build/bin/`

6. **Crash inesperado do programa**:
   - **Solução**: Verifique a pasta `logs/` na raiz do projeto — crash logs detalhados são gerados automaticamente com traceback completo, versão do Python e do SO

---

## 📋 Requisitos

### Requisitos do Sistema:
- **Python 3.6 ou superior** 🐍 (testado com Python 3.14)
- **Google Chrome** 🌐 — **recomendado**, mas **não obrigatório** (o fallback HTTP funciona sem navegador)

### Dependências Python (instalação automática disponível):
| Pacote | Uso |
|--------|-----|
| `selenium` | Automação web (scraping via navegador) |
| `webdriver_manager` | Gerenciamento automático do ChromeDriver |
| `yt-dlp` | Download de áudio do SoundCloud |
| `mutagen` | Manipulação e enriquecimento de metadados |

### Incluído no Repositório:
- **FFmpeg 8.0** 🎥 (em `Dependencias/ffmpeg/ffmpeg-8.0-essentials_build/bin/`)

### Para Desenvolvimento/Testes:
- `pytest` — Execução dos 132 testes automatizados
- `pyinstaller` — Build do executável

**Verificação Automática de Dependências**: O script verifica automaticamente se todas as dependências Python estão instaladas e oferece instalá-las caso estejam faltando. Basta executar o script e seguir as instruções na tela! ✨

---

## 📁 Estrutura de Saída

Os arquivos de áudio 🔊 baixados serão salvos na pasta selecionada pelo usuário 📂 (via seletor nativo ou input de texto), com metadados adicionais 📋 e miniaturas incorporadas 🖼️ (quando disponíveis). Os arquivos serão nomeados seguindo o padrão `uploader - artista - título.ext`, facilitando a organização e localização das faixas 🔍.

Após a conclusão dos downloads:
- ✅ A pasta de destino é **aberta automaticamente** no explorador de arquivos
- 🗑️ O arquivo TXT de links é **deletado automaticamente** (limpeza)
- 🔄 O programa pergunta se deseja **baixar mais músicas** antes de encerrar

---

## 🔐 Segurança e Privacidade

### Transparência Total
- **Código Open Source**: Todo o código está disponível para inspeção
- **Sem Telemetria**: Nenhum dado é coletado ou enviado externamente
- **Execução Local**: Todo processamento acontece na sua máquina
- **Sem Backdoors**: Código auditável e verificável com antivírus
- **Logs Locais**: Crash logs ficam apenas na sua máquina, na pasta `logs/`

### Uso Responsável
⚠️ **IMPORTANTE**: Esta ferramenta foi desenvolvida exclusivamente para:
- Backup pessoal de conteúdo que você possui/criou
- Arquivamento de conteúdo de domínio público
- Preservação cultural e educacional
- Downloads de conteúdo com permissão explícita do criador

**Respeite os direitos autorais e os Termos de Serviço do SoundCloud.** O desenvolvedor não se responsabiliza pelo uso inadequado desta ferramenta.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você encontrou um bug, tem uma sugestão de funcionalidade ou quer melhorar a documentação:

1. **Fork** este repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. **Abra** um Pull Request

### 🐛 Reportando Bugs
Ao reportar bugs, por favor inclua:
- Versão do Python e do sistema operacional
- Mensagem de erro completa
- Crashlogs da pasta `logs/` (se disponíveis)
- Passos para reproduzir o problema

### 🧪 Rodando os Testes Antes de Contribuir
```bash
python -m pytest tests/ -v
# Todos os 132 testes devem passar
```

---

## 📊 Roadmap e Funcionalidades Futuras

- [x] 🌐 Fallback HTTP via API v2 (sem necessidade de navegador)
- [x] 🛡️ Sistema de crash logging e logs de sessão
- [x] 🧪 Suite completa de testes automatizados (132 testes)
- [x] 🏗️ Script de build automatizado para EXE
- [x] 📂 Seletor de pasta nativo via tkinter
- [x] 🔄 Loop contínuo de downloads
- [x] 📁 Abertura automática da pasta de destino
- [ ] 🌐 Interface Web com Flask/Django
- [ ] 🎨 GUI Desktop com PyQt/Tkinter
- [ ] 📱 Suporte para playlists privadas (com autenticação)
- [ ] 🔄 Sistema de sincronização automática
- [ ] 📊 Dashboard de estatísticas de downloads
- [ ] 🎵 Suporte para outros serviços (Bandcamp, Mixcloud)
- [ ] 🗄️ Banco de dados SQLite para catalogação
- [ ] 🔍 Sistema de busca na coleção baixada
- [ ] 🎛️ Editor de metadados em batch
- [ ] ☁️ Upload automático para cloud storage

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License - Copyright (c) 2025 Felipe Alcântara

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 👤 Autor

**Felipe Alcântara**
- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)
- Repositório: [SoundScraper](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader)

---

## 🙏 Agradecimentos

Este projeto não seria possível sem estas ferramentas open source incríveis:

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - O melhor downloader de mídia disponível
- **[Selenium](https://www.selenium.dev/)** - Automação web robusta e confiável
- **[FFmpeg](https://ffmpeg.org/)** - O canivete suíço do processamento multimídia
- **[webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)** - Gerenciamento automático de drivers
- **[mutagen](https://github.com/quodlibet/mutagen)** - Manipulação de metadados de áudio
- **[PyInstaller](https://pyinstaller.org/)** - Empacotamento do executável standalone
- **[pytest](https://pytest.org/)** - Framework de testes robusto e extensível

Um agradecimento especial à comunidade SoundCloud e aos artistas que tornam a plataforma um ecossistema musical vibrante! 🎶

---

## 📞 Suporte

Se você encontrou valor neste projeto:

- ⭐ **Dê uma Star** no repositório
- 🐛 **Reporte bugs** abrindo issues (inclua logs da pasta `logs/`!)
- 💡 **Sugira features** nas discussions
- 🤝 **Contribua** com pull requests
- 📢 **Compartilhe** com outros usuários

---

<div align="center">

**Desenvolvido com ❤️ e ☕ por [Felipe Alcântara](https://github.com/Felipe-Alcantara)**

*Preservando a música digital, uma track por vez* 🎵

[![GitHub Stars](https://img.shields.io/github/stars/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader?style=social)](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader?style=social)](https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/network/members)

</div>
