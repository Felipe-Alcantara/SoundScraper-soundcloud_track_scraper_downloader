# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['soundcloud_tracks_downloader.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/ffmpeg/ffmpeg-7.1', 'ffmpeg'), ('C:/Users/Felipe/Desktop/Programação/Scripts python/Meus projetos em python/SoundScraper/SoundScraper/Chrome-bin', 'Chrome-bin')],
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
    icon=['C:\\Users\\Felipe\\Desktop\\Programação\\Scripts python\\Meus projetos em python\\SoundScraper\\SoundScraper\\Ícone\\sound_scraper_logo.ico'],
)
