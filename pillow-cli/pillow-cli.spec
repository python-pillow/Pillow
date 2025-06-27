# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pillow_cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        'PIL.Image',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageOps',
        'PIL.ExifTags',
        'numpy',
        'sklearn.cluster',
        'sklearn.cluster._kmeans',
        'tkinter',
        'tkinter.ttk',
        'argparse',
        'pathlib',
        'json',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pillow-cli',
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
    icon=None,
)
