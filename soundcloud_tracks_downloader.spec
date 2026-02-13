# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Arquivos\\soundcloud_tracks_downloader.py'],
    pathex=['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Arquivos'],
    binaries=[('H:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\.venv\\Lib\\site-packages\\selenium\\webdriver\\common\\windows\\selenium-manager.exe', 'selenium\\webdriver\\common\\windows')],
    datas=[('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Arquivos\\soundcloud_track_scraper.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Arquivos\\browser_handler.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Arquivos\\crash_logger.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Dependencias\\ffmpeg\\ffmpeg-8.0-essentials_build\\bin', 'ffmpeg\\bin')],
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
    icon=['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\Extra\\Ícone\\sound_scraper_logo.ico'],
)
