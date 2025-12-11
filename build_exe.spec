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
        # PySide6 플러그인은 자동 수집되도록 주석 처리 (한글 경로 문제 회피)
        # ('env/Lib/site-packages/PySide6/plugins', 'PySide6/plugins'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSql',
        'PySide6.QtNetwork',
        'qfluentwidgets',
        'cryptography',
        'requests',
        'numpy',
        'pandas',
        'markdown',
        'markdown.extensions',
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.fenced_code',
    ],
    hookspath=[],
    hooksconfig={
        'pyside6': {
            'plugins': ['platforms', 'sqldrivers', 'styles'],
        }
    },
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PyQt6', 
        'PySide2',
        'tkinter',
        '_tkinter',
    ],  # 불필요한 Qt 바인딩 제외
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
    name='Gr8 DIY',
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
    name='Gr8 DIY',
)

