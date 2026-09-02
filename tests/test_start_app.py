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


def test_save_config_preserves_unknown_env_entries(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SOUNDSCRAPER_TOKEN=keep-me\nSOUNDSCRAPER_PORT=9000\n", encoding="utf-8")

    with patch.object(start_app, "ENV_FILE", env_file):
        start_app.save_config(host="0.0.0.0", port=8100, dev_port=5174, open_browser=False)

    content = env_file.read_text(encoding="utf-8")
    assert "SOUNDSCRAPER_TOKEN=keep-me" in content
    assert "SOUNDSCRAPER_PORT=8100" in content
    assert "SOUNDSCRAPER_HOST=0.0.0.0" in content
    assert "SOUNDSCRAPER_DEV_PORT=5174" in content
    assert "SOUNDSCRAPER_OPEN_BROWSER=false" in content


def test_interactive_menu_has_descriptive_exit_option(capsys):
    with patch("builtins.input", return_value="0"):
        assert start_app.interactive_menu() == 0

    output = capsys.readouterr().out
    assert "Iniciar" in output
    assert "Instalar" in output
    assert "Configurar" in output
    assert "Status" in output
    assert "Sair" in output


def test_main_keeps_legacy_automation_flags():
    with (
        patch.object(start_app, "port_in_use", return_value=False),
        patch.object(start_app, "run_production", return_value=0) as run_production,
    ):
        assert start_app.main(["--no-install", "--no-browser"]) == 0

    run_production.assert_called_once_with(False)
