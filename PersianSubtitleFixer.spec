# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# bundle the package metadata so importlib.metadata.version() works in
# frozen builds (the titlebar version comes from it)
metadata_datas = copy_metadata('persian-subtitle-fixer')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/comics-mask_97446.ico', 'assets')] + metadata_datas,
    hiddenimports=['PyQt6.sip'],  # Reduced hiddenimports to only what's essential
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # NOTE: 'email' must stay out of this list - importlib.metadata (used
    # for the titlebar version) imports it internally
    excludes=['_gtkagg', '_tkagg', 'blib2to3', 'distutils', 'ftplib', 'html', 'http', 'lib2to3', 'numpy', 'pandas', 'pydoc_data', 'pytz', 'test', 'unittest', 'xml'],  # Exclude unnecessary modules
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PersianSubtitleFixer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols to reduce size
    upx=False,  # UPX-packed python DLLs fail to load ("Invalid access to
    # memory location", v0.4.1 artifact) and attract antivirus false positives
    console=False,  # Changed to False to hide terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/comics-mask_97446.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,  # Strip symbols to reduce size
    upx=False,  # see note above
    upx_exclude=[],
    name='PersianSubtitleFixer'
)

# BUNDLE must wrap the COLLECT result, not the EXE — wrapping EXE produces
# a hollow .app missing PyQt5/python dylib (verified via v0.2.1-test3 artifact)
app = BUNDLE(coll,
             name='PersianSubtitleFixer.app',
             icon="assets/comics-mask_97446.icns",
             bundle_identifier='com.persiansubtitlefixer.app')