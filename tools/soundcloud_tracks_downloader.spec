# -*- mode: python ; coding: utf-8 -*-
"""Spec portátil para builds locais do executável SoundScraper."""

import os
import shutil
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


PROJECT_ROOT = Path(SPECPATH).resolve().parent
CORE = PROJECT_ROOT / "core"
ENTRY_POINT = CORE / "soundcloud_tracks_downloader.py"


def _pair(source: Path, destination: str) -> tuple[str, str]:
    return str(source), destination


def _selenium_manager() -> tuple[str, str] | None:
    try:
        import selenium
    except ImportError:
        return None

    platform_dir = "windows" if os.name == "nt" else "macos" if sys.platform == "darwin" else "linux"
    filename = "selenium-manager.exe" if os.name == "nt" else "selenium-manager"
    source = (
        Path(selenium.__file__).resolve().parent
        / "webdriver"
        / "common"
        / platform_dir
        / filename
    )
    if not source.exists():
        return None
    destination = f"selenium/webdriver/common/{platform_dir}"
    return str(source), destination


datas = [
    _pair(CORE / "soundcloud_track_scraper.py", "."),
    _pair(CORE / "browser_handler.py", "."),
    _pair(CORE / "crash_logger.py", "."),
    _pair(CORE / "platform_utils.py", "."),
    _pair(CORE / "scraping", "scraping"),
    _pair(CORE / "downloading", "downloading"),
]

binaries = []
manager = _selenium_manager()
if manager:
    binaries.append(manager)

ffmpeg = shutil.which("ffmpeg")
if ffmpeg:
    binaries.append((ffmpeg, "ffmpeg/bin"))

hiddenimports = [
    "soundcloud_track_scraper",
    "browser_handler",
    "crash_logger",
    "platform_utils",
    "downloading",
    "downloading.options",
    "downloading.metadata",
    "selenium",
    "selenium.webdriver.common.selenium_manager",
    "yt_dlp",
    "mutagen",
]
hiddenimports.extend(collect_submodules("scraping"))

a = Analysis(
    [str(ENTRY_POINT)],
    pathex=[str(CORE)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

icon = PROJECT_ROOT / "tools" / "icon" / "sound_scraper_logo.ico"
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="soundcloud_tracks_downloader",
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
    icon=str(icon) if icon.exists() else None,
)
