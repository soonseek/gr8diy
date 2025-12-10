# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 빌드 설정 파일

사용법:
    pyinstaller build_exe.spec
"""

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # PySide6 플러그인
        ('env/Lib/site-packages/PySide6/plugins', 'PySide6/plugins'),
        # 설정 파일들 (필요 시)
        # ('config/*.py', 'config'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSql',
        'qfluentwidgets',
        'cryptography',
        'requests',
        'numpy',
        'pandas',
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
    [],
    exclude_binaries=True,
    name='OKX_Trading_Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 모드 (콘솔 숨김)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일 경로 (필요 시)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OKX_Trading_Bot',
)

