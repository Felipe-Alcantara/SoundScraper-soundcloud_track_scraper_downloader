# AGENTS.md — roteiro de trabalho do SoundScraper

Este repositório é um aplicativo cross-platform com duas interfaces: uma Web
(FastAPI + React) e uma CLI. O padrão de qualidade adotado é o Felixo System
Design; a cópia local ignorada em `Padrão de qualidade - Felixo System Design/`
serve apenas como referência. A fonte pública é o repositório
`Felipe-Alcantara/Felixo-System-Design`.

## Antes de alterar

1. Leia `IA.md`, `README.md` e o módulo que será alterado.
2. Preserve a separação `core/` → `backend/services/` → `backend/api/` → `frontend/`.
3. Não coloque segredos, caminhos locais ou artefatos gerados no Git.
4. Se a alteração mudar comportamento, escreva o teste de regressão antes ou
   junto da implementação e atualize `README.md` e `IA.md` no mesmo passo.

## Fonte de verdade do ambiente

Use Python 3.10+ dentro de `.venv/`. Os arquivos de dependência usam versões
exatas para que o mesmo checkout possa ser auditado e reproduzido.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r deps/requirements-dev.txt
```

No Windows, troque `.venv/bin/python` por `.venv/Scripts/python.exe`.

## Gate local

O comando completo é:

```bash
python tools/quality_gate.py
```

Os passos individuais, úteis para isolar uma falha, são:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest tests/ -q
npm ci --prefix frontend
npm run lint --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
```

O frontend não precisa de rede durante os testes de comportamento. O build
carrega apenas os artefatos gerados pelo Vite.

## Organização e versionamento

- `core/scraping/` concentra coleta, adapters e parsing.
- `backend/services/` orquestra casos de uso sem conhecer HTTP.
- `backend/api/routes/` valida entrada e traduz o contrato HTTP/WebSocket.
- `tools/` contém automações reutilizáveis de build e qualidade.
- `start_app.py` é a porta de entrada interativa; os argumentos antigos são
  mantidos somente para automação compatível.
- Commits seguem Conventional Commits e devem ser pequenos e coesos.
- Trabalhe no `main` para ajustes simples; esta task usa branch porque cruza
  várias camadas e altera a estrutura do projeto.

## Limitações conhecidas

O CI valida Linux e Windows. O macOS continua sendo uma plataforma suportada
por desenho e precisa de validação manual quando a mudança tocar integrações
específicas do sistema.
