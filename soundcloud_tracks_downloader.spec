# -*- mode: python ; coding: utf-8 -*-

import os

# Obtém o diretório base do projeto (onde está o .spec)
base_dir = os.path.dirname(os.path.abspath(SPEC))

# Localiza o selenium-manager.exe automaticamente
import importlib
selenium_path = os.path.dirname(importlib.import_module('selenium').__file__)
selenium_manager_src = os.path.join(selenium_path, 'webdriver', 'common', 'windows', 'selenium-manager.exe')

a = Analysis(
    [os.path.join(base_dir, 'Arquivos', 'soundcloud_tracks_downloader.py')],
    pathex=[os.path.join(base_dir, 'Arquivos')],
    binaries=[
        # Inclui o selenium-manager.exe para que funcione no EXE
        (selenium_manager_src, os.path.join('selenium', 'webdriver', 'common', 'windows')),
    ],
    datas=[
        (os.path.join(base_dir, 'Arquivos', 'soundcloud_track_scraper.py'), '.'),
        (os.path.join(base_dir, 'Arquivos', 'browser_handler.py'), '.'),
        (os.path.join(base_dir, 'Arquivos', 'crash_logger.py'), '.'),
        (os.path.join(base_dir, 'Dependencias', 'ffmpeg', 'ffmpeg-8.0-essentials_build', 'bin'), os.path.join('ffmpeg', 'bin')),
    ],
    hiddenimports=['soundcloud_track_scraper', 'browser_handler', 'crash_logger', 'selenium', 'selenium.webdriver.common.selenium_manager', 'yt_dlp', 'mutagen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='soundcloud_tracks_downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[os.path.join(base_dir, 'Extra', 'Ícone', 'sound_scraper_logo.ico')] if os.path.exists(os.path.join(base_dir, 'Extra', 'Ícone', 'sound_scraper_logo.ico')) else None,
)
