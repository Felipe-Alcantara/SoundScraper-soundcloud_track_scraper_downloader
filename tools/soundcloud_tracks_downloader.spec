# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\soundcloud_tracks_downloader.py'],
    pathex=['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core'],
    binaries=[('H:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\.venv\\Lib\\site-packages\\selenium\\webdriver\\common\\windows\\selenium-manager.exe', 'selenium\\webdriver\\common\\windows')],
    datas=[('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\soundcloud_track_scraper.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\browser_handler.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\crash_logger.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\platform_utils.py', '.'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\core\\scraping', 'scraping'), ('h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\deps\\ffmpeg\\ffmpeg-8.0-essentials_build\\bin', 'ffmpeg\\bin')],
    hiddenimports=['soundcloud_track_scraper', 'browser_handler', 'crash_logger', 'platform_utils', 'scraping', 'scraping.parsers', 'scraping.pipeline', 'scraping.registry', 'scraping.config', 'scraping.models', 'scraping.base', 'scraping.adapters.http_api', 'scraping.adapters.selenium_browser', 'selenium', 'selenium.webdriver.common.selenium_manager', 'yt_dlp', 'mutagen'],
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
    icon=['h:\\Programação\\GitHub\\Repositórios\\SoundScraper-soundcloud_track_scraper_downloader\\tools\\icon\\sound_scraper_logo.ico'],
)
