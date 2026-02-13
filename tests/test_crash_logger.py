"""
test_crash_logger.py — Testes automatizados para o módulo crash_logger.

Testa:
  • Resolução da pasta de logs (frozen vs script)
  • Coleta de informações do sistema
  • Geração de logs de crash
  • Handler de exceções (sys.excepthook)
  • SessionLogger (duplicação de streams)
  • Limpeza de logs antigos
  • Inicialização do sistema de logging
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from io import StringIO

import crash_logger as cl


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Pasta de logs
# ══════════════════════════════════════════════════════════════════════

class TestGetLogsFolder:
    """Testa _get_logs_folder()."""

    def test_returns_existing_directory(self, mock_not_frozen):
        """Deve retornar um diretório que existe (cria se necessário)."""
        result = cl._get_logs_folder()
        assert os.path.isdir(result)
        assert result.endswith('logs')

    def test_creates_folder_if_missing(self, mock_not_frozen, temp_dir):
        """Deve criar a pasta de logs automaticamente."""
        logs_path = os.path.join(temp_dir, 'logs')
        assert not os.path.exists(logs_path)

        # Simula que o script está no temp_dir/Arquivos/
        fake_script = os.path.join(temp_dir, 'Arquivos', 'crash_logger.py')
        os.makedirs(os.path.dirname(fake_script), exist_ok=True)

        with patch.object(cl, '__file__', fake_script):
            with patch('os.path.abspath', return_value=fake_script):
                result = cl._get_logs_folder()
                assert os.path.isdir(result)

    def test_frozen_mode_uses_exe_directory(self, mock_frozen, temp_dir):
        """No modo EXE, deve usar diretório ao lado do executável."""
        mock_frozen(temp_dir)
        # Em frozen mode, usa os.path.dirname(sys.executable)
        with patch.object(sys, 'executable', os.path.join(temp_dir, 'app.exe')):
            result = cl._get_logs_folder()
            assert result == os.path.join(temp_dir, 'logs')
            assert os.path.isdir(result)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Informações do sistema
# ══════════════════════════════════════════════════════════════════════

class TestGetSystemInfo:
    """Testa _get_system_info()."""

    def test_returns_string(self):
        """Deve retornar uma string."""
        result = cl._get_system_info()
        assert isinstance(result, str)

    def test_contains_python_version(self):
        """Deve conter a versão do Python."""
        result = cl._get_system_info()
        assert 'Python' in result

    def test_contains_platform_info(self):
        """Deve conter informações da plataforma."""
        result = cl._get_system_info()
        assert 'Plataforma' in result

    def test_contains_soundscraper_version(self):
        """Deve conter a versão do SoundScraper."""
        result = cl._get_system_info()
        assert 'SoundScraper' in result
        assert cl.SOUNDSCRAPER_VERSION in result

    def test_contains_frozen_status(self):
        """Deve indicar se está rodando como EXE."""
        result = cl._get_system_info()
        assert 'Rodando como EXE' in result

    def test_contains_dependency_versions(self):
        """Deve listar versões das dependências."""
        result = cl._get_system_info()
        # Deve tentar listar selenium, yt_dlp, mutagen
        assert 'selenium' in result or 'yt_dlp' in result

    def test_frozen_mode_shows_exe_dir(self, mock_frozen, temp_dir):
        """No modo EXE, deve mostrar diretório do EXE e bundle."""
        mock_frozen(temp_dir)
        with patch.object(sys, 'executable', os.path.join(temp_dir, 'app.exe')):
            result = cl._get_system_info()
            assert 'Diretório do EXE' in result
            assert 'Bundle temporário' in result


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Geração de log de crash
# ══════════════════════════════════════════════════════════════════════

class TestGenerateCrashLog:
    """Testa _generate_crash_log()."""

    def test_creates_log_file(self, temp_dir):
        """Deve criar um arquivo de log de crash."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            try:
                raise ValueError("Erro de teste")
            except ValueError:
                exc_type, exc_value, exc_tb = sys.exc_info()
                log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)

            assert log_path is not None
            assert os.path.exists(log_path)

    def test_log_contains_error_info(self, temp_dir):
        """O log deve conter informações do erro."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            try:
                raise RuntimeError("mensagem do crash")
            except RuntimeError:
                exc_type, exc_value, exc_tb = sys.exc_info()
                log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)

            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'RuntimeError' in content
            assert 'mensagem do crash' in content

    def test_log_filename_format(self, temp_dir):
        """O nome do arquivo deve seguir o formato crash_YYYY-MM-DD_HH-MM-SS.log."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            try:
                raise Exception("test")
            except Exception:
                exc_type, exc_value, exc_tb = sys.exc_info()
                log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)

            filename = os.path.basename(log_path)
            assert filename.startswith('crash_')
            assert filename.endswith('.log')

    def test_log_contains_system_info(self, temp_dir):
        """O log deve conter informações do sistema."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            try:
                raise Exception("test")
            except Exception:
                exc_type, exc_value, exc_tb = sys.exc_info()
                log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)

            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'Python' in content
            assert 'TRACEBACK' in content
            assert 'RELATÓRIO DE CRASH' in content

    def test_log_contains_github_link(self, temp_dir):
        """O log deve conter link para issues do GitHub."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            try:
                raise Exception("test")
            except Exception:
                exc_type, exc_value, exc_tb = sys.exc_info()
                log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)

            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'github.com' in content

    def test_fallback_to_cwd_on_permission_error(self, temp_dir):
        """Se não conseguir salvar na pasta de logs, deve tentar o cwd."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            with patch('builtins.open', side_effect=[PermissionError("denied"), MagicMock()]):
                try:
                    raise Exception("test")
                except Exception:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    # Não deve crashar mesmo se não conseguir salvar
                    log_path = cl._generate_crash_log(exc_type, exc_value, exc_tb)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: Handler de crashes
# ══════════════════════════════════════════════════════════════════════

class TestCrashHandler:
    """Testa _crash_handler()."""

    def test_keyboard_interrupt_exits_gracefully(self):
        """KeyboardInterrupt deve sair sem gerar log de crash."""
        with pytest.raises(SystemExit) as exc_info:
            cl._crash_handler(KeyboardInterrupt, KeyboardInterrupt(""), None)
        assert exc_info.value.code == 0

    def test_generates_log_for_normal_exception(self, temp_dir):
        """Exceção normal deve gerar log de crash."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            with patch('builtins.input', return_value=''):  # Mock do "Pressione ENTER"
                try:
                    raise ValueError("test exception")
                except ValueError:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    cl._crash_handler(exc_type, exc_value, exc_tb)

            # Verifica que um crash log foi criado
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('crash_')]
            assert len(log_files) >= 1

    def test_handles_eoferror_on_input(self, temp_dir):
        """Deve tratar EOFError no input (ex: redirecionamento de stdin)."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            with patch('builtins.input', side_effect=EOFError):
                try:
                    raise RuntimeError("test")
                except RuntimeError:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    # Não deve crashar
                    cl._crash_handler(exc_type, exc_value, exc_tb)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 5: SessionLogger
# ══════════════════════════════════════════════════════════════════════

class TestSessionLogger:
    """Testa a classe SessionLogger."""

    def test_writes_to_both_streams(self, temp_dir):
        """Deve escrever tanto no stream original quanto no arquivo."""
        log_path = os.path.join(temp_dir, 'test_session.log')
        original = StringIO()

        logger = cl.SessionLogger(log_path, original)
        logger.write("test message\n")
        logger.flush()
        logger.close()

        # Verifica stream original
        assert "test message" in original.getvalue()

        # Verifica arquivo
        with open(log_path, 'r', encoding='utf-8') as f:
            assert "test message" in f.read()

    def test_flush_works(self, temp_dir):
        """flush() não deve crashar."""
        log_path = os.path.join(temp_dir, 'test_flush.log')
        original = StringIO()
        logger = cl.SessionLogger(log_path, original)
        logger.flush()  # Não deve lançar exceção
        logger.close()

    def test_close_works(self, temp_dir):
        """close() deve fechar o arquivo sem erro."""
        log_path = os.path.join(temp_dir, 'test_close.log')
        original = StringIO()
        logger = cl.SessionLogger(log_path, original)
        logger.close()  # Não deve lançar exceção

    def test_getattr_delegates_to_original(self, temp_dir):
        """Atributos não definidos devem ser delegados ao stream original."""
        log_path = os.path.join(temp_dir, 'test_getattr.log')
        original = StringIO()
        logger = cl.SessionLogger(log_path, original)

        # StringIO tem 'getvalue' — deve ser acessível via logger
        assert hasattr(logger, 'getvalue')
        logger.close()

    def test_survives_original_write_error(self, temp_dir):
        """Deve continuar funcionando se o stream original falhar."""
        log_path = os.path.join(temp_dir, 'test_survive.log')
        broken_stream = MagicMock()
        broken_stream.write.side_effect = Exception("broken pipe")

        logger = cl.SessionLogger(log_path, broken_stream)
        logger.write("test")  # Não deve crashar
        logger.close()


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 6: Limpeza de logs antigos
# ══════════════════════════════════════════════════════════════════════

class TestCleanupOldLogs:
    """Testa _cleanup_old_logs()."""

    def test_keeps_max_logs(self, temp_dir):
        """Deve manter no máximo max_logs arquivos de cada tipo."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            # Cria 25 logs de crash e 25 de sessão
            import time
            for i in range(25):
                for prefix in ['crash_', 'sessao_']:
                    filepath = os.path.join(temp_dir, f"{prefix}2024-01-01_{i:02d}-00-00.log")
                    with open(filepath, 'w') as f:
                        f.write(f"test {i}")
                    # Garante timestamps diferentes
                    os.utime(filepath, (time.time() + i, time.time() + i))

            cl._cleanup_old_logs(max_logs=10)

            crash_remaining = [f for f in os.listdir(temp_dir) if f.startswith('crash_')]
            session_remaining = [f for f in os.listdir(temp_dir) if f.startswith('sessao_')]

            assert len(crash_remaining) <= 10
            assert len(session_remaining) <= 10

    def test_does_nothing_when_under_limit(self, temp_dir):
        """Não deve remover nada se estiver abaixo do limite."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            for i in range(3):
                filepath = os.path.join(temp_dir, f"crash_2024-01-01_{i:02d}-00-00.log")
                with open(filepath, 'w') as f:
                    f.write("test")

            cl._cleanup_old_logs(max_logs=20)

            remaining = [f for f in os.listdir(temp_dir) if f.startswith('crash_')]
            assert len(remaining) == 3

    def test_no_crash_on_permission_error(self, temp_dir):
        """Não deve crashar se houver erro de permissão."""
        with patch.object(cl, '_get_logs_folder', side_effect=PermissionError):
            cl._cleanup_old_logs()  # Não deve lançar exceção

    def test_no_crash_on_empty_folder(self, temp_dir):
        """Não deve crashar com pasta vazia."""
        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            cl._cleanup_old_logs()  # Não deve lançar exceção


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 7: Inicialização
# ══════════════════════════════════════════════════════════════════════

class TestInicializarLogger:
    """Testa inicializar_logger()."""

    def test_sets_excepthook(self, temp_dir):
        """Deve configurar sys.excepthook para _crash_handler."""
        original_hook = sys.excepthook

        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            cl.inicializar_logger()
            assert sys.excepthook == cl._crash_handler

        # Restaura
        sys.excepthook = original_hook

    def test_returns_session_log_path(self, temp_dir):
        """Deve retornar o caminho do log de sessão."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with patch.object(cl, '_get_logs_folder', return_value=temp_dir):
            result = cl.inicializar_logger()

        # Restaura stdout/stderr originais (o logger os substituiu)
        if isinstance(sys.stdout, cl.SessionLogger):
            sys.stdout.close()
        if isinstance(sys.stderr, cl.SessionLogger):
            sys.stderr.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        assert result is not None
        assert result.endswith('.log')
        assert 'sessao_' in result

    def test_version_constant_exists(self):
        """A constante SOUNDSCRAPER_VERSION deve existir."""
        assert hasattr(cl, 'SOUNDSCRAPER_VERSION')
        assert isinstance(cl.SOUNDSCRAPER_VERSION, str)
        assert len(cl.SOUNDSCRAPER_VERSION) > 0
