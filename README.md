# 🎵 SoundScraper - Professional SoundCloud Archive Tool

<div align="center">

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-Automated-43B02A.svg)](https://www.selenium.dev/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Powered-red.svg)](https://github.com/yt-dlp/yt-dlp)

**Uma solução completa e profissional para arquivamento de coleções musicais do SoundCloud**

[🚀 Início Rápido](#-início-rápido) • [📖 Documentação](#-índice) • [💾 Download Executável](#-versão-executável-para-download-imediato) • [🔧 Instalação](#-como-usar)

</div>

---

## 📋 Visão Geral

**SoundScraper** é uma ferramenta robusta e automatizada desenvolvida para preservação digital e backup de coleções musicais do SoundCloud. Diferente de downloaders simples, o SoundScraper oferece uma solução enterprise-grade que combina web scraping inteligente, processamento automatizado de metadados, e gerenciamento de dependências auto-configurável.

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
- ✅ ChromeDriver auto-gerenciado via webdriver-manager
- ✅ Valores padrão inteligentes para todos os inputs
- ✅ Tratamento robusto de erros com mensagens claras

#### 🎨 **Interface Profissional**
- Interface CLI moderna com emojis e formatação elegante
- Feedback visual em tempo real do progresso
- Mensagens de erro descritivas e acionáveis
- Prompts interativos com valores padrão sensatos
- Logs detalhados para troubleshooting

#### 📦 **Distribuição Standalone**
- Executável Windows (.exe) com todas as dependências embutidas
- Não requer Python, pip ou configuração manual
- Navegador Chrome portátil incluído
- ~418MB de solução plug-and-play

---

# 🎵 SoundCloud Music Downloader 🎶

## ⚡ Início Rápido

### Para Iniciantes (3 passos simples):

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader.git
   cd SoundScraper-soundcloud_track_scraper_downloader
   ```

2. **Instale o Google Chrome** (se ainda não tiver):
   - 🌐 Baixe em: https://www.google.com/chrome/
   - OU baixe o Chrome portátil: https://storage.googleapis.com/chrome-for-testing-public/114.0.5708.0/win64/chrome-win64.zip
   - Extraia o Chrome portátil para: `Dependencias/Navegador/`

3. **Execute o programa:**
   ```bash
   cd Arquivos
   python soundcloud_tracks_downloader.py
   ```
   
   ✨ **Pronto!** O script verificará e instalará automaticamente todas as dependências Python necessárias.

---

## 📖 Índice

1. [🚀 Versão Executável para Download Imediato](#-versão-executável-para-download-imediato)
2. [📂 Estrutura do Projeto](#-estrutura-do-projeto)
3. [📜 Arquivos e Funções](#-arquivos-e-funções)
   - [1. soundcloud_track_scraper.py](#1-soundcloud_track_scraperpy)
   - [2. soundcloud_tracks_downloader.py](#2-soundcloud_tracks_downloaderpy)
4. [🚀 Como Usar](#-como-usar)
5. [❗ Possíveis Problemas e Soluções](#-possíveis-problemas-e-soluções)
6. [📋 Requisitos](#-requisitos)
7. [📁 Estrutura de Saída](#-estrutura-de-saída)
8. [🔚 Conclusão](#-conclusão)

---

## 🚀 Versão Executável para Download Imediato

Uma versão executável do downloader está disponível para facilitar ainda mais o uso da ferramenta. Com o arquivo .exe, você não precisa de um ambiente de desenvolvimento, IDEs, bibliotecas ou instalar dependências. Basta baixar ⬇️ e rodar ▶️ diretamente o executável, o que torna o processo extremamente simples e rápido 🏃💨! Esta é a maneira mais fácil de começar a baixar suas músicas favoritas 🎶 do SoundCloud sem complicações adicionais.

📝 Nota sobre o tamanho do executável: O arquivo .exe tem aproximadamente 418 MB 🗂️. Isso acontece porque ele contém todas as dependências necessárias embutidas, incluindo o Selenium 🕷️, o codec FFmpeg 🎥, e até mesmo o navegador 🌐 utilizado para acessar as músicas. Todo esse conteúdo é necessário para garantir que o programa funcione de maneira autônoma 🤖, sem precisar de configurações adicionais. Essa versão do .exe foi pensada exclusivamente para a facilidade de uso 💡 e não foi otimizada em termos de tamanho, pois o objetivo é ser um "quebra-galho" que funcione para qualquer pessoa sem complicações 🔧. Caso você prefira uma versão mais leve ou esteja desconfiado do tamanho, pode utilizar o código-fonte 📝, que é mais transparente, além de poder ser verificado com antivírus 🛡️ ou examinado diretamente para garantir que está de acordo com a descrição deste repositório.

Essa versão do executável foi projetada pensando em simplicidade e acessibilidade 🚪, não em eficiência de tamanho ⚖️. Se você tiver preocupações com segurança 🔒 ou quiser mais controle sobre as dependências, recomendamos que faça uso do código-fonte 👨‍💻. Assim, você pode personalizar 🔧 as configurações, instalar apenas o que precisar e verificar 🔍 o conteúdo de cada parte do programa para garantir a confiança no que está sendo executado.

---

## 📂 Arquitetura do Projeto

SoundScraper foi desenvolvido com uma arquitetura modular e escalável, separando claramente as responsabilidades de scraping, download e processamento de metadados. Esta abordagem garante manutenibilidade, testabilidade e permite fácil extensão de funcionalidades.

### �️ Estrutura de Diretórios

```
SoundScraper/
├── Arquivos/                          # 📜 Scripts principais
│   ├── soundcloud_track_scraper.py    # Web scraper com Selenium
│   └── soundcloud_tracks_downloader.py # Download engine com yt-dlp
│
├── Dependencias/                      # 🔧 Dependências externas
│   ├── ffmpeg/                        # Codec de áudio (incluído)
│   │   └── ffmpeg-8.0-essentials_build/
│   ├── Navegador/                     # Chrome portátil (opcional)
│   │   └── chrome-win64/
│   └── requirements.txt               # Dependências Python
│
├── Extra/                             # 🎨 Recursos adicionais
│   └── Ícone/                         # Ícones da aplicação
│
├── build/                             # 🏗️ Arquivos de build (gitignored)
├── dist/                              # 📦 Executável compilado (gitignored)
├── README.md                          # 📖 Documentação
├── LICENSE                            # ⚖️ Licença MIT
└── .gitignore                         # 🚫 Configuração Git
```

### 🔌 Componentes Principais

#### **1. Web Scraping Engine** (`soundcloud_track_scraper.py`)
Motor de scraping automatizado baseado em Selenium com:
- **WebDriver Auto-configurável**: Detecção inteligente de Chrome (sistema ou portátil)
- **Scroll Infinito Inteligente**: Carregamento dinâmico de todas as tracks
- **Seletores CSS Robustos**: Extração confiável de links mesmo com mudanças no DOM
- **Modo Headless**: Execução sem interface gráfica para performance máxima
- **Anti-detecção**: Flags do Chrome para evitar bloqueios
- **Verificação de Dependências**: Check automático com instalação assistida

#### **2. Download & Metadata Engine** (`soundcloud_tracks_downloader.py`)
Sistema completo de download e enriquecimento de metadados:
- **yt-dlp Integration**: Download otimizado com retry automático
- **Custom Metadata Processor**: Post-processor proprietário para metadados estendidos
- **FFmpeg Pipeline**: Conversão e embedding de artwork automatizados
- **Format Selection**: Suporte FLAC (lossless) e MP3 (320kbps)
- **Path Management**: Caminhos relativos para portabilidade total
- **Input Validation**: Valores padrão inteligentes para todos os prompts
- **Progress Feedback**: Status em tempo real com emojis e formatação

#### **3. Dependency Manager** (Integrado nos scripts)
Sistema automático de gerenciamento de dependências:
- Verifica instalação de cada pacote Python
- Oferece instalação interativa via pip
- Valida disponibilidade do FFmpeg local
- Detecta Chrome em múltiplos caminhos
- Fornece mensagens de erro acionáveis

---

## 📜 Arquivos e Funções

### 1. soundcloud_track_scraper.py

Este script tem como objetivo coletar os links 🔗 de faixas 🎶 de um perfil do SoundCloud usando Selenium 🕷️. Ele realiza a navegação automatizada 🚗 no perfil escolhido e armazena os links das músicas em um arquivo de texto 📝, facilitando o download posterior dessas músicas de forma eficiente 💨. As principais funcionalidades do script são:

   1. **Configuração do WebDriver**: O script utiliza `webdriver-manager` 🔧 para gerenciar e iniciar o WebDriver de forma automática 🤖, dispensando a necessidade de instalar o driver manualmente.

      - *Função*: `get_webdriver()` - Inicializa o WebDriver do Chromium usando opções de execução sem interface gráfica 🖥️ (modo headless).

2. **Obtenção do Link do Perfil**: O script solicita ao usuário 👤 o link 🔗 do perfil do SoundCloud e uma opção sobre o que deseja coletar (ex: faixas populares 🔥, álbuns 💿, playlists 🎶).

      - *Função*: `get_soundcloud_link()` - Realiza a validação do link do perfil e permite ao usuário selecionar entre faixas 🎵, álbuns 💿, playlists 🎧 e outras opções.

3. **Rolagem da Página e Coleta de Faixas**: O script rola a página do perfil 📜 para carregar mais faixas e coleta os links usando seletores CSS.
      
      - *Função*: `scroll_and_collect_tracks()` - A cada rolagem, os links são coletados e armazenados em uma lista 📋, garantindo que todas as músicas estejam disponíveis para download.

4. **Salvar Links Coletados**: Os links das faixas coletadas são salvos em um arquivo de texto 📝, permitindo seu uso posterior para download.
      
      - *Função*: `save_track_links()` - Salva os links em um arquivo especificado pelo usuário. Dessa forma, o processo de download pode ser realizado em outro momento de forma prática e organizada 📦.

O `soundcloud_track_scraper.py` é responsável por coletar todos os links relevantes 🔗 para o download e facilitar o acesso a qualquer tipo de faixa dentro do perfil, como playlists 🎧, álbuns 💿 ou faixas populares 🔥. Essa funcionalidade de coleta é essencial para quem deseja fazer backups completos dos perfis do SoundCloud, oferecendo um controle detalhado sobre o que será baixado.

---

### 2. soundcloud_tracks_downloader.py

Este script é responsável por fazer o download ⬇️ das faixas coletadas usando o yt_dlp 📥. As principais funcionalidades do script são descritas em uma ordem lógica 🧩 que facilita o entendimento do processo, garantindo que o usuário tenha uma experiência completa e organizada:

1. **Coleta de Links**: O script utiliza o arquivo gerado pelo `soundcloud_track_scraper.py` para obter os URLs 🔗 das faixas.
   
      - *Variável*: `filename` - Recebe o nome do arquivo que contém os links das músicas 🎶 que serão baixadas.

2. **Solicitação de Formato de Áudio**: O script solicita ao usuário 👤 o formato de áudio desejado 🎵 para download: FLAC (sem perdas) ou MP3 (compatível e de menor tamanho 📏).
   
      - *Função*: `solicitar_formato()` - Define o formato de áudio para o processo de download, proporcionando uma escolha que depende da qualidade ⭐ ou compatibilidade que o usuário deseja.

3. **Configuração do yt_dlp**: O script configura o yt_dlp para baixar as faixas de áudio 🔊, incorporar metadados 📋, incluir miniaturas 🖼️ e realizar o processamento final dos arquivos.

      - *Variável*: `ydl_opts` - Contém as opções de download, como formato desejado, caminho de saída 📂, e uso de FFmpeg para processamento. Isso garante que as músicas baixadas estejam no formato correto e com todas as informações necessárias.

4. **Download e Processamento dos Arquivos**: Para cada URL 🔗, o yt_dlp realiza o download e aplica o processamento adicional, como a inclusão de metadados personalizados 📝.
   
      - *Função*: `download_url()` - Realiza o download de cada URL, adicionando metadados personalizados como o nome do artista 🎨, álbum 💿, gênero 🎶, entre outros, garantindo que a biblioteca musical do usuário esteja bem organizada e com informações completas.

5. **Correção dos Nomes dos Arquivos**: Após o download ⬇️, o script verifica os arquivos baixados e corrige o nome removendo possíveis caracteres indesejados 🚫 ou padronizações.
   
      - *Função*: `corrigir_nome_arquivo()` - Renomeia arquivos removendo "NA" e substituindo caracteres como "_" por espaços para melhorar a legibilidade dos nomes dos arquivos 📂. Isso torna os arquivos mais fáceis de identificar e organizar, aprimorando a experiência do usuário.

O `soundcloud_tracks_downloader.py` vai além de apenas baixar as faixas, ele cuida para que as músicas tenham informações corretas e sejam devidamente organizadas. Dessa forma, o usuário não precisa se preocupar com metadados faltando ou arquivos com nomes confusos, tornando a experiência final muito mais fluida 🌊.

---

## 🚀 Como Usar

1. **Configurações Iniciais**: Certifique-se de ter instalado Python 🐍, Selenium 🕷️, `webdriver-manager` 🔧, yt_dlp 📥 e FFmpeg 🎥. Esses requisitos são essenciais para o funcionamento correto da ferramenta e para evitar problemas durante a execução.

2. **Executar o Downloader de Faixas**:

   - O módulo `soundcloud_track_scraper.py` já é utilizado pelo `soundcloud_tracks_downloader.py` para coletar os links das músicas 🎶.

   - Forneça o link 🔗 do perfil do SoundCloud e escolha o que deseja coletar (faixas 🎵, playlists 🎧, álbuns 💿, etc.). A flexibilidade da ferramenta permite ao usuário optar por baixar um perfil inteiro ou apenas parte dele.

   - Você pode optar por baixar o perfil inteiro, incluindo discografias 📀, remixes 🎚️, coleções 📚, playlists inteiras 🎧, curtidas do perfil ❤️, faixas populares 🔥 e até faixas relacionadas 🔗 ao artista. Esta característica torna a ferramenta ideal para colecionadores 🗂️ e usuários que desejam realizar backups completos, diferenciando-a de outros downloaders comuns. Assim, é possível realizar o download de grandes coleções de faixas em um único processo, de maneira prática e eficiente. A ferramenta não se limita apenas a downloads pontuais; ela é pensada para quem deseja ter tudo salvo localmente, sem limitações.

3. **Download das Faixas**:

   - Execute `soundcloud_tracks_downloader.py`.

   - Informe o nome do arquivo de links e o formato de áudio desejado 🔊. É possível escolher entre formatos de alta qualidade (FLAC) ou formatos mais leves e compatíveis (MP3).

   - As faixas serão baixadas e processadas conforme as configurações escolhidas, incluindo a possibilidade de baixar todas as faixas de um perfil, playlists completas ou faixas específicas com metadados personalizados 📝. Isso significa que o usuário não precisa se preocupar com arquivos faltando ou com baixa qualidade de áudio 🔉.

A ferramenta oferece uma experiência completa 🏆 para quem deseja baixar e organizar faixas do SoundCloud, seja para uso pessoal, backups 🔄 ou mesmo curadoria de coleções musicais 🎶. Cada etapa foi pensada para tornar o processo o mais automatizado 🤖 e fácil possível.

---

## ❗ Possíveis Problemas e Soluções

1. **"cannot find Chrome binary"**: Este erro significa que o Google Chrome não está instalado ou não foi encontrado. 
   - **Solução**: Instale o Google Chrome em: https://www.google.com/chrome/
   - O script tenta encontrar o Chrome automaticamente nos locais padrão do Windows
   - Alternativamente, coloque uma versão portátil do Chrome na pasta `Chrome-bin` do projeto

2. **Dependências Python Faltando**: Se você receber erros sobre módulos não encontrados (selenium, yt_dlp, etc.):
   - **Solução**: Execute o script normalmente! Ele verificará automaticamente as dependências e oferecerá instalá-las
   - Ou instale manualmente com: `pip install -r requirements.txt`

3. **Driver de Navegador Incompatível**: Se o WebDriver não iniciar 🚫:
   - **Solução**: O `webdriver-manager` baixa automaticamente a versão correta do ChromeDriver
   - Se o problema persistir, delete a pasta `.wdm` em seu diretório de usuário e tente novamente

4. **Erro ao Baixar Faixas**: Certifique-se de que o link está correto e que o yt_dlp está configurado adequadamente ⛔.
   - **Solução**: Verifique se o link do SoundCloud está correto e acessível
   - O FFmpeg já está incluído no repositório, não precisa instalar separadamente

5. **Problemas com o FFmpeg**: O FFmpeg já vem incluído na pasta `ffmpeg/` do projeto 🔧.
   - **Solução**: Não é necessário instalar o FFmpeg separadamente
   - O script usa automaticamente o FFmpeg da pasta do repositório

---

## 📋 Requisitos

### Requisitos do Sistema:
- **Python 3.6 ou superior** 🐍
- **Google Chrome** instalado no sistema 🌐 (obrigatório para o Selenium funcionar)

### Dependências Python (instalação automática disponível):
- Selenium 🕷️
- yt_dlp 📥
- webdriver-manager 🔧

### Incluído no Repositório:
- FFmpeg 🎥 (localizado na pasta `ffmpeg/ffmpeg-8.0-essentials_build/`)

⚠️ **IMPORTANTE**: O Google Chrome **DEVE** estar instalado no sistema para que o script funcione. O script tentará localizá-lo automaticamente nos seguintes locais:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

Se você não tiver o Chrome instalado, baixe-o em: https://www.google.com/chrome/

**Verificação Automática de Dependências**: O script verifica automaticamente se todas as dependências Python estão instaladas e oferece instalá-las caso estejam faltando. Basta executar o script e seguir as instruções na tela! ✨

Esses requisitos garantem que a ferramenta funcione corretamente ✅ e que todas as funcionalidades estejam disponíveis. O FFmpeg, por exemplo, é crucial para processar as faixas baixadas 🎶, enquanto o Selenium permite a navegação automatizada 🌐.

---

## 📁 Estrutura de Saída

Os arquivos de áudio 🔊 baixados serão salvos na pasta especificada pelo usuário 📂, com metadados adicionais 📋 e miniaturas incorporadas 🖼️ (quando disponíveis). Os arquivos serão nomeados seguindo o padrão `uploader - artista - título.ext`, facilitando a organização e localização das faixas 🔍. Isso garante que a coleção de músicas do usuário seja facilmente navegável 🚀 e intuitiva, além de preservar todas as informações relevantes sobre cada faixa.

Além disso, o processo de correção dos nomes dos arquivos visa garantir que não existam nomes duplicados ou difíceis de ler 👓. Isso melhora a organização da biblioteca de áudio, deixando-a mais limpa e acessível.

---

---

## � Segurança e Privacidade

### Transparência Total
- **Código Open Source**: Todo o código está disponível para inspeção
- **Sem Telemetria**: Nenhum dado é coletado ou enviado externamente
- **Execução Local**: Todo processamento acontece na sua máquina
- **Sem Backdoors**: Código auditável e verificável com antivírus

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
- Passos para reproduzir o problema
- Logs relevantes (se disponível)

---

## 📊 Roadmap e Funcionalidades Futuras

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

## � Autor

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

Um agradecimento especial à comunidade SoundCloud e aos artistas que tornam a plataforma um ecossistema musical vibrante! 🎶

---

## 📞 Suporte

Se você encontrou valor neste projeto:

- ⭐ **Dê uma Star** no repositório
- 🐛 **Reporte bugs** abrindo issues
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