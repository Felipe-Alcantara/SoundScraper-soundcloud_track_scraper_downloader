"""
crash_logger.py — Módulo de logging e captura de crashes do SoundScraper.

Gerencia:
  • Criação automática da pasta de logs
  • Captura de exceções não tratadas (crashes)
  • Registro detalhado com data/hora, versão do Python, SO, traceback completo
  • Duplicação da saída do console para arquivo de log (sessão completa)
"""

import os
import sys
import traceback
import platform
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════

SOUNDSCRAPER_VERSION = "1.0"

def _get_logs_folder():
    """
    Retorna o caminho da pasta de logs.
    Se estiver rodando como EXE, usa a pasta ao lado do executável.
    Se estiver rodando como script, usa a pasta do projeto.
    """
    if getattr(sys, 'frozen', False):
        # No EXE: pasta 'logs' ao lado do executável
        base_dir = os.path.dirname(sys.executable)
    else:
        # No script: pasta 'logs' na raiz do projeto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)

    logs_folder = os.path.join(base_dir, 'logs')

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    return logs_folder


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Informações do sistema para diagnóstico
# ══════════════════════════════════════════════════════════════════════

def _get_system_info():
    """Coleta informações do sistema para incluir nos logs de crash."""
    info_lines = [
        f"SoundScraper Versão: {SOUNDSCRAPER_VERSION}",
        f"Python: {sys.version}",
        f"Plataforma: {platform.platform()}",
        f"Sistema: {platform.system()} {platform.release()}",
        f"Arquitetura: {platform.machine()}",
        f"Executável Python: {sys.executable}",
        f"Rodando como EXE: {'Sim' if getattr(sys, 'frozen', False) else 'Não'}",
    ]

    if getattr(sys, 'frozen', False):
        info_lines.append(f"Diretório do EXE: {os.path.dirname(sys.executable)}")
        info_lines.append(f"Bundle temporário: {getattr(sys, '_MEIPASS', 'N/A')}")

    # Tenta pegar versões das dependências
    deps = {
        'selenium': 'selenium',
        'yt_dlp': 'yt_dlp',
        'mutagen': 'mutagen',
    }
    for display_name, module_name in deps.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', getattr(mod, 'version', 'desconhecida'))
            info_lines.append(f"  {display_name}: {version}")
        except ImportError:
            info_lines.append(f"  {display_name}: NÃO instalado")

    return '\n'.join(info_lines)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Logger de crash (exceções não tratadas)
# ══════════════════════════════════════════════════════════════════════

def _generate_crash_log(exc_type, exc_value, exc_traceback):
    """
    Gera um arquivo de log detalhado quando ocorre um crash.
    Chamada automaticamente pelo sys.excepthook.
    """
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
    timestamp_display = timestamp.strftime('%d/%m/%Y às %H:%M:%S')

    logs_folder = _get_logs_folder()
    log_filename = f"crash_{timestamp_str}.log"
    log_path = os.path.join(logs_folder, log_filename)

    # Monta o conteúdo do log
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)

    log_content = f"""╔══════════════════════════════════════════════════════════════════════╗
║             SOUNDSCRAPER — RELATÓRIO DE CRASH                       ║
╚══════════════════════════════════════════════════════════════════════╝

📅 Data/Hora: {timestamp_display}
📄 Arquivo de log: {log_filename}

══════════════════════════════════════════════════════════════════════
📋 INFORMAÇÕES DO SISTEMA
══════════════════════════════════════════════════════════════════════

{_get_system_info()}

══════════════════════════════════════════════════════════════════════
❌ ERRO / EXCEÇÃO
══════════════════════════════════════════════════════════════════════

Tipo: {exc_type.__name__ if exc_type else 'Desconhecido'}
Mensagem: {exc_value}

══════════════════════════════════════════════════════════════════════
🔍 TRACEBACK COMPLETO
══════════════════════════════════════════════════════════════════════

{tb_text}
══════════════════════════════════════════════════════════════════════
💡 O QUE FAZER COM ESTE LOG?
══════════════════════════════════════════════════════════════════════

Se este erro persistir, abra uma issue no GitHub com este arquivo:
→ https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/issues

Inclua este arquivo de log completo para ajudar na análise do problema.
══════════════════════════════════════════════════════════════════════
"""

    # Salva o log
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
    except Exception:
        # Se não conseguir salvar na pasta padrão, tenta no diretório atual
        fallback_path = os.path.join(os.getcwd(), log_filename)
        try:
            with open(fallback_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            log_path = fallback_path
        except Exception:
            log_path = None

    return log_path


def _crash_handler(exc_type, exc_value, exc_traceback):
    """
    Handler global de exceções não tratadas.
    Substitui o sys.excepthook padrão para gerar logs de crash.
    """
    # Ignora KeyboardInterrupt (Ctrl+C) — não é crash
    if issubclass(exc_type, KeyboardInterrupt):
        print("")
        print("═" * 70)
        print("⚠️  Programa interrompido pelo usuário (Ctrl+C)")
        print("═" * 70)
        print("")
        sys.exit(0)

    # Gera o log de crash
    log_path = _generate_crash_log(exc_type, exc_value, exc_traceback)

    # Mostra a mensagem de crash para o usuário
    print("")
    print("")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  💥  OOPS! O SOUNDSCRAPER ENCONTROU UM ERRO INESPERADO  💥".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("")
    print(f"❌ Erro: {exc_type.__name__}: {exc_value}")
    print("")

    if log_path:
        print("═" * 70)
        print("📝  LOG DE CRASH GERADO COM SUCESSO")
        print("═" * 70)
        print("")
        print(f"📂 Arquivo: {log_path}")
        print("")
        print("💡 Envie este arquivo ao abrir uma issue no GitHub:")
        print("   → https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader/issues")
    else:
        print("⚠️  Não foi possível salvar o log de crash em disco.")
        print("")
        print("🔍 Traceback do erro:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

    print("")
    print("═" * 70)
    print("")

    # Mantém a janela aberta para o usuário ver a mensagem
    try:
        input("Pressione ENTER para encerrar...")
    except EOFError:
        pass


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Logger de sessão (duplica console para arquivo)
# ══════════════════════════════════════════════════════════════════════

class SessionLogger:
    """
    Duplica toda a saída do console (stdout/stderr) para um arquivo de log.
    Assim, além do crash log, temos a sessão completa para diagnóstico.
    """

    def __init__(self, log_path, original_stream):
        self.log_file = open(log_path, 'a', encoding='utf-8', errors='replace')
        self.original_stream = original_stream

    def write(self, message):
        """Escreve tanto no console quanto no arquivo."""
        try:
            self.original_stream.write(message)
        except Exception:
            pass
        try:
            self.log_file.write(message)
            self.log_file.flush()
        except Exception:
            pass

    def flush(self):
        """Força escrita dos buffers."""
        try:
            self.original_stream.flush()
        except Exception:
            pass
        try:
            self.log_file.flush()
        except Exception:
            pass

    def close(self):
        """Fecha o arquivo de log."""
        try:
            self.log_file.close()
        except Exception:
            pass

    # Necessário para compatibilidade com código que checa atributos do stream
    def __getattr__(self, name):
        return getattr(self.original_stream, name)


def _start_session_log():
    """
    Inicia o log de sessão — toda saída do console é salva em arquivo.
    Retorna o caminho do arquivo de log criado.
    """
    timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logs_folder = _get_logs_folder()
    session_log_path = os.path.join(logs_folder, f"sessao_{timestamp_str}.log")

    # Cabeçalho do log de sessão
    try:
        with open(session_log_path, 'w', encoding='utf-8') as f:
            f.write(f"╔══════════════════════════════════════════════════════════════════════╗\n")
            f.write(f"║             SOUNDSCRAPER — LOG DE SESSÃO                            ║\n")
            f.write(f"╚══════════════════════════════════════════════════════════════════════╝\n")
            f.write(f"\n")
            f.write(f"📅 Início: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
            f.write(f"\n")
            f.write(f"{_get_system_info()}\n")
            f.write(f"\n")
            f.write(f"══════════════════════════════════════════════════════════════════════\n")
            f.write(f"📋 SAÍDA DO PROGRAMA\n")
            f.write(f"══════════════════════════════════════════════════════════════════════\n")
            f.write(f"\n")
    except Exception:
        return None

    # Redireciona stdout e stderr para o SessionLogger
    sys.stdout = SessionLogger(session_log_path, sys.stdout)
    sys.stderr = SessionLogger(session_log_path, sys.stderr)

    return session_log_path


def _cleanup_old_logs(max_logs=20):
    """
    Remove logs antigos para não acumular demais.
    Mantém apenas os últimos 'max_logs' arquivos de cada tipo.
    """
    try:
        logs_folder = _get_logs_folder()
        all_logs = sorted(
            [f for f in os.listdir(logs_folder) if f.endswith('.log')],
            key=lambda f: os.path.getmtime(os.path.join(logs_folder, f)),
            reverse=True
        )

        # Separa por tipo
        crash_logs = [f for f in all_logs if f.startswith('crash_')]
        session_logs = [f for f in all_logs if f.startswith('sessao_')]

        # Remove logs excedentes
        for log_list in [crash_logs, session_logs]:
            for old_log in log_list[max_logs:]:
                try:
                    os.remove(os.path.join(logs_folder, old_log))
                except Exception:
                    pass
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: Função principal de inicialização
# ══════════════════════════════════════════════════════════════════════

def inicializar_logger():
    """
    Inicializa todo o sistema de logging do SoundScraper.
    Deve ser chamada NO INÍCIO do programa principal.

    O que faz:
      1. Instala o handler global de crashes (sys.excepthook)
      2. Inicia o log de sessão (duplica console para arquivo)
      3. Limpa logs antigos para não acumular

    Retorna o caminho do arquivo de log da sessão.
    """
    print("")
    print("─" * 70)
    print("📝  SISTEMA DE LOG")
    print("─" * 70)
    print("")

    # 1. Handler de crashes
    sys.excepthook = _crash_handler
    print("✅ Handler de crashes ativado")

    # 2. Log de sessão
    session_log = _start_session_log()
    if session_log:
        print(f"✅ Log de sessão iniciado: {session_log}")
    else:
        print("⚠️  Não foi possível iniciar o log de sessão")

    # 3. Limpeza de logs antigos
    _cleanup_old_logs()
    print("✅ Limpeza de logs antigos concluída")

    logs_folder = _get_logs_folder()
    print(f"📂 Pasta de logs: {logs_folder}")
    print("")
    print("─" * 70)
    print("")

    return session_log
