# Dependências do Projeto

Esta pasta contém as dependências necessárias para o funcionamento do SoundScraper.

## 📦 Conteúdo

### ✅ Incluído no Repositório:
- **ffmpeg/** - Codec de áudio (já incluído)
- **requirements.txt** - Lista de pacotes Python necessários

### ⬇️ Precisa Baixar Separadamente:

#### **Navegador/chrome-win64/** - Google Chrome Portátil
O Chrome portátil não está incluído no repositório devido ao tamanho (>100MB).

**Opção 1 - Instalar Chrome no Sistema (Recomendado):**
- Baixe e instale: https://www.google.com/chrome/
- O script detectará automaticamente

**Opção 2 - Usar Chrome Portátil:**
1. Baixe o Chrome for Testing (versão 114.0.5708.0): 
   - **Link direto:** https://storage.googleapis.com/chrome-for-testing-public/114.0.5708.0/win64/chrome-win64.zip
2. Extraia o conteúdo do arquivo ZIP para: `Dependencias/Navegador/`
3. Certifique-se de que existe: `Dependencias/Navegador/chrome-win64/chrome.exe`

**Estrutura esperada:**
```
Dependencias/
├── Navegador/
│   └── chrome-win64/
│       ├── chrome.exe  ← arquivo principal
│       ├── chrome.dll
│       └── ... (outros arquivos)
├── ffmpeg/
│   └── ffmpeg-8.0-essentials_build/
└── requirements.txt
```

## 🚀 Instalação Rápida

1. Clone o repositório
2. Instale o Chrome (sistema ou portátil)
3. Execute: `cd Arquivos && python soundcloud_tracks_downloader.py`
4. O script verificará e instalará as dependências Python automaticamente

## ℹ️ Notas

- O ffmpeg já está incluído, não precisa baixar
- As dependências Python são instaladas automaticamente pelo script
- O Chrome é necessário para o Selenium funcionar
