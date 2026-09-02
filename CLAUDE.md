# Instruções de trabalho do SoundScraper

As regras canônicas deste repositório estão em [AGENTS.md](AGENTS.md). Leia-o
antes de editar código. Em resumo: use o `.venv`, preserve as fronteiras entre
`core`, services, rotas e frontend, escreva testes de comportamento, mantenha
`README.md`/`IA.md` atualizados e execute `python tools/quality_gate.py` antes
de concluir.

O `start_app.py` é a entrada interativa para instalar, configurar, iniciar e
verificar o aplicativo. Argumentos existentes continuam disponíveis apenas
para automações já suportadas.
