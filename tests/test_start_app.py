"""Testes do launcher da interface web."""

import sys
from unittest.mock import patch

import start_app


def test_python_executable_falls_back_to_current_interpreter(tmp_path):
    with patch.object(start_app, "VENV_DIR", tmp_path / ".venv"):
        assert start_app.python_executable() == sys.executable


def test_python_executable_uses_project_virtual_environment(tmp_path):
    venv_dir = tmp_path / ".venv"
    python_path = venv_dir / ("Scripts" if start_app.os.name == "nt" else "bin") / (
        "python.exe" if start_app.os.name == "nt" else "python"
    )
    python_path.parent.mkdir(parents=True)
    python_path.touch()

    with patch.object(start_app, "VENV_DIR", venv_dir):
        assert start_app.python_executable() == str(python_path)


def test_install_python_deps_creates_venv_before_installing(tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.touch()
    venv_python = str(tmp_path / ".venv" / "bin" / "python")

    with (
        patch.object(start_app, "ROOT", tmp_path),
        patch.object(start_app, "REQUIREMENTS", requirements),
        patch.object(start_app, "VENV_DIR", tmp_path / ".venv"),
        patch.object(
            start_app,
            "python_executable",
            side_effect=[sys.executable, venv_python],
        ),
        patch.object(start_app.subprocess, "run") as run,
    ):
        start_app.install_python_deps()

    assert run.call_count == 2
    assert run.call_args_list[0].args[0] == [
        sys.executable,
        "-m",
        "venv",
        str(tmp_path / ".venv"),
    ]
    assert run.call_args_list[1].args[0] == [
        venv_python,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements),
    ]
