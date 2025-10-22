# -*- mode: python ; coding: utf-8 -*-

import os

# Obtém o diretório base do projeto
base_dir = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    [os.path.join(base_dir, 'Arquivos', 'soundcloud_tracks_downloader.py')],
    pathex=[os.path.join(base_dir, 'Arquivos')],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'Dependencias', 'ffmpeg', 'ffmpeg-8.0-essentials_build', 'bin'), os.path.join('ffmpeg', 'bin')),
        (os.path.join(base_dir, 'Dependencias', 'Navegador', 'chrome-win64'), os.path.join('Navegador', 'chrome-win64'))
    ],
    hiddenimports=[],
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
