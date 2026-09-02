#!/usr/bin/env python3
"""Executa o gate reproduzível de qualidade do SoundScraper.

O script mantém a ordem do gate em um único ponto para uso local e no CI:
Ruff, auditoria Python, testes Python, instalação limpa do frontend, lint,
testes de comportamento, auditoria npm e build. Não conhece regras de negócio
nem altera arquivos versionados; o ``npm ci`` só recria o diretório ignorado
``frontend/node_modules``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
VENV = ROOT / ".venv"


def _python_executable() -> str:
    """Retorna o Python do projeto quando ele já foi preparado."""
    binary_dir = "Scripts" if os.name == "nt" else "bin"
    binary_name = "python.exe" if os.name == "nt" else "python"
    candidate = VENV / binary_dir / binary_name
    return str(candidate) if candidate.exists() else sys.executable


def _npm_executable() -> str:
    """Retorna o nome portável do executável npm."""
    return "npm.cmd" if os.name == "nt" else "npm"


def _run(label: str, command: list[str], cwd: Path = ROOT) -> None:
    """Exibe e executa uma etapa, preservando o código de saída real."""
    printable = " ".join(command)
    print(f"\n[gate] {label}: {printable}", flush=True)
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"{label} não pode começar: comando não encontrado ({command[0]})."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"{label} falhou com código {exc.returncode}.") from exc


def run_gate(*, skip_frontend: bool = False, skip_install: bool = False) -> int:
    """Executa todas as verificações e retorna 0 quando o gate fecha."""
    python = _python_executable()
    _run("Ruff", [python, "-m", "ruff", "check", "."])
    _run(
        "Auditoria Python",
        [python, "-m", "pip_audit", "-r", str(ROOT / "deps" / "requirements-dev.txt")],
    )
    _run("Testes Python", [python, "-m", "pytest", "tests", "-q"])

    if skip_frontend:
        print("\n[gate] Frontend ignorado por opção explícita.")
        return 0

    npm = _npm_executable()
    if not skip_install:
        _run("Instalação limpa do frontend", [npm, "ci"], cwd=FRONTEND)
    _run("Lint frontend", [npm, "run", "lint"], cwd=FRONTEND)
    _run("Testes frontend", [npm, "test"], cwd=FRONTEND)
    _run("Build frontend", [npm, "run", "build"], cwd=FRONTEND)
    _run("Auditoria npm", [npm, "audit", "--audit-level=high"], cwd=FRONTEND)
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="roda apenas Ruff e testes Python",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="não executa npm ci; útil quando node_modules já foi instalado",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da automação."""
    args = _parse_args(argv)
    try:
        return run_gate(
            skip_frontend=args.skip_frontend,
            skip_install=args.skip_install,
        )
    except RuntimeError as exc:
        print(f"\n[gate] ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
