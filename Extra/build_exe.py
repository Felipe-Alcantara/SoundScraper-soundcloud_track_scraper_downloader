"""
build_exe.py — Script para gerar o executável (.exe) do SoundScraper.

Uso:
    python Extra/build_exe.py

O que faz:
  1. Detecta automaticamente o diretório do projeto
  2. Localiza o selenium-manager.exe no ambiente virtual
  3. Gera o .spec em memória com todos os módulos, dependências e ícone
  4. Executa o PyInstaller para criar o EXE em dist/
  5. Exibe o tamanho final e abre a pasta dist/
"""

import os
import sys
import subprocess
import importlib
import shutil
import time


def main():
    # ══════════════════════════════════════════════════════════════
    #  1. Resolver caminhos do projeto
    # ══════════════════════════════════════════════════════════════
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    print("")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  🔧  SOUNDSCRAPER — Build do Executável".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("")
    print(f"📂 Raiz do projeto: {project_root}")
    print("")

    # Caminhos importantes
    entry_point = os.path.join(project_root, 'Arquivos', 'soundcloud_tracks_downloader.py')
    arquivos_dir = os.path.join(project_root, 'Arquivos')
    ffmpeg_bin = os.path.join(project_root, 'Dependencias', 'ffmpeg', 'ffmpeg-8.0-essentials_build', 'bin')
    icon_path = os.path.join(project_root, 'Extra', 'Ícone', 'sound_scraper_logo.ico')
    dist_dir = os.path.join(project_root, 'dist')
    build_dir = os.path.join(project_root, 'build')

    # Módulos do projeto
    modules = ['soundcloud_track_scraper.py', 'browser_handler.py', 'crash_logger.py']

    # ══════════════════════════════════════════════════════════════
    #  2. Validações
    # ══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("🔍  VERIFICANDO PRÉ-REQUISITOS")
    print("═" * 70)
    print("")

    erros = []

    # Entry point
    if os.path.exists(entry_point):
        print(f"  ✅ Entry point: {entry_point}")
    else:
        erros.append(f"Entry point não encontrado: {entry_point}")
        print(f"  ❌ Entry point: NÃO ENCONTRADO")

    # Módulos
    for mod in modules:
        mod_path = os.path.join(arquivos_dir, mod)
        if os.path.exists(mod_path):
            print(f"  ✅ Módulo: {mod}")
        else:
            erros.append(f"Módulo não encontrado: {mod_path}")
            print(f"  ❌ Módulo: {mod} — NÃO ENCONTRADO")

    # FFmpeg
    ffmpeg_exe = os.path.join(ffmpeg_bin, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_exe):
        print(f"  ✅ FFmpeg: {ffmpeg_bin}")
    else:
        erros.append(f"FFmpeg não encontrado: {ffmpeg_exe}")
        print(f"  ❌ FFmpeg: NÃO ENCONTRADO em {ffmpeg_bin}")

    # Ícone
    if os.path.exists(icon_path):
        print(f"  ✅ Ícone: {icon_path}")
    else:
        icon_path = None
        print(f"  ⚠️  Ícone não encontrado (será gerado sem ícone)")

    # Selenium Manager
    selenium_manager_path = None
    try:
        selenium_pkg = importlib.import_module('selenium')
        selenium_dir = os.path.dirname(selenium_pkg.__file__)
        sm_path = os.path.join(selenium_dir, 'webdriver', 'common', 'windows', 'selenium-manager.exe')
        if os.path.exists(sm_path):
            selenium_manager_path = sm_path
            print(f"  ✅ Selenium Manager: {sm_path}")
        else:
            erros.append(f"selenium-manager.exe não encontrado: {sm_path}")
            print(f"  ❌ Selenium Manager: NÃO ENCONTRADO")
    except ImportError:
        erros.append("Selenium não está instalado")
        print(f"  ❌ Selenium: NÃO INSTALADO")

    # PyInstaller
    try:
        import PyInstaller
        print(f"  ✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        erros.append("PyInstaller não está instalado (pip install pyinstaller)")
        print(f"  ❌ PyInstaller: NÃO INSTALADO")

    print("")

    if erros:
        print("═" * 70)
        print("❌  ERROS ENCONTRADOS — Build cancelado")
        print("═" * 70)
        for e in erros:
            print(f"   • {e}")
        print("")
        input("Pressione ENTER para sair...")
        sys.exit(1)

    # ══════════════════════════════════════════════════════════════
    #  3. Limpar builds anteriores
    # ══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("🧹  LIMPANDO BUILDS ANTERIORES")
    print("═" * 70)
    print("")

    for folder in [dist_dir, build_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
            print(f"  🗑️  Removido: {folder}")
        else:
            print(f"  ℹ️  Não existe: {folder}")
    print("")

    # ══════════════════════════════════════════════════════════════
    #  4. Montar comando do PyInstaller
    # ══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("🔨  GERANDO EXECUTÁVEL")
    print("═" * 70)
    print("")

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--console',
        '--name', 'soundcloud_tracks_downloader',
        '--distpath', dist_dir,
        '--workpath', build_dir,
        '--specpath', project_root,

        # Paths de busca de módulos
        '--paths', arquivos_dir,

        # Binários
        '--add-binary', f'{selenium_manager_path};selenium\\webdriver\\common\\windows',

        # Dados — módulos do projeto
        '--add-data', f'{os.path.join(arquivos_dir, "soundcloud_track_scraper.py")};.',
        '--add-data', f'{os.path.join(arquivos_dir, "browser_handler.py")};.',
        '--add-data', f'{os.path.join(arquivos_dir, "crash_logger.py")};.',

        # Dados — FFmpeg
        '--add-data', f'{ffmpeg_bin};ffmpeg\\bin',

        # Hidden imports
        '--hidden-import', 'soundcloud_track_scraper',
        '--hidden-import', 'browser_handler',
        '--hidden-import', 'crash_logger',
        '--hidden-import', 'selenium',
        '--hidden-import', 'selenium.webdriver.common.selenium_manager',
        '--hidden-import', 'yt_dlp',
        '--hidden-import', 'mutagen',

        # Otimizações
        '--upx-dir', '',  # Usa UPX se disponível no PATH
        '--clean',
    ]

    # Ícone (se existir)
    if icon_path:
        cmd.extend(['--icon', icon_path])

    # Entry point (última arg)
    cmd.append(entry_point)

    print("📋 Comando:")
    print(f"   {' '.join(cmd[:6])} ...")
    print("")
    print("⏳ Isso pode levar alguns minutos...")
    print("")

    inicio = time.time()

    result = subprocess.run(cmd, cwd=project_root)

    duracao = time.time() - inicio

    print("")

    # ══════════════════════════════════════════════════════════════
    #  5. Resultado
    # ══════════════════════════════════════════════════════════════
    exe_path = os.path.join(dist_dir, 'soundcloud_tracks_downloader.exe')

    if result.returncode == 0 and os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)

        print("═" * 70)
        print("✅  BUILD CONCLUÍDO COM SUCESSO!")
        print("═" * 70)
        print("")
        print(f"📦 Executável: {exe_path}")
        print(f"📏 Tamanho: {size_mb:.1f} MB")
        print(f"⏱️  Tempo: {duracao:.0f} segundos")
        print("")
        print("═" * 70)
        print("")

        # Abre a pasta dist/
        try:
            os.startfile(dist_dir)
            print("📂 Pasta dist/ aberta no explorador.")
        except Exception:
            pass

        # Limpa pasta build/
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir, ignore_errors=True)
            print("🧹 Pasta build/ removida.")
        print("")
    else:
        print("═" * 70)
        print("❌  ERRO NO BUILD!")
        print("═" * 70)
        print("")
        print(f"Código de saída: {result.returncode}")
        print("Verifique a saída acima para detalhes do erro.")
        print("")
        input("Pressione ENTER para sair...")
        sys.exit(1)


if __name__ == '__main__':
    main()
