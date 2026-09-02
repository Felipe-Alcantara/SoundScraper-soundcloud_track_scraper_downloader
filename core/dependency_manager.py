"""Verificação opcional de dependências para os entry points legados."""

from __future__ import annotations

import importlib
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


def _package_name(requirement: str) -> str:
    """Converte uma linha de requirements no nome importável mais comum."""
    name = requirement.split(";", 1)[0].strip()
    for separator in ("==", ">=", "<=", "~=", ">", "<"):
        name = name.split(separator, 1)[0]
    return name.split("[", 1)[0].strip().replace("-", "_")


def _requirements(requirements_file: Path) -> list[str]:
    """Lê requisitos diretos, ignorando comentários e includes."""
    if not requirements_file.exists():
        return []
    return [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "-"))
    ]


def check_and_install_requirements(
    requirements_file: Path,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] = print,
    python_executable: str = sys.executable,
) -> bool:
    """Verifica pacotes e oferece instalação pelo interpretador atual."""
    packages = _requirements(requirements_file)
    if not requirements_file.exists():
        output_fn(f"⚠️  Arquivo de dependências não encontrado: {requirements_file}")
        return True

    missing: list[str] = []
    output_fn("\n🔍 Verificando dependências do Python\n")
    for requirement in packages:
        package_name = _package_name(requirement)
        try:
            importlib.import_module(package_name)
        except ImportError:
            missing.append(requirement)
            output_fn(f"  ❌ {requirement}")
        else:
            output_fn(f"  ✅ {requirement}")

    if not missing:
        output_fn("\n✅ Todas as dependências estão prontas.\n")
        return True

    output_fn(f"\n⚠️  {len(missing)} pacote(s) estão faltando.")
    reader = input_fn or input
    try:
        answer = reader("Deseja instalar automaticamente agora? (S/N): ").strip().upper()
    except EOFError:
        answer = "N"
    if answer != "S":
        output_fn("Instalação cancelada; o programa pode não funcionar.\n")
        return False

    try:
        subprocess.run(
            [python_executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        output_fn(f"❌ Falha ao instalar dependências: {exc}")
        return False
    output_fn("✅ Dependências instaladas com sucesso.\n")
    return True
