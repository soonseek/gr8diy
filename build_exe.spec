# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 빌드 설정 파일

사용법:
    pyinstaller build_exe.spec
"""
import os
import sys

block_cipher = None

# spec 파일이 있는 디렉토리 (프로젝트 루트)
SPEC_ROOT = os.path.abspath(SPECPATH)

# PySide6 경로
PYSIDE6_PATH = os.path.join(SPEC_ROOT, 'env', 'Lib', 'site-packages', 'PySide6')

a = Analysis(
    ['app/main.py'],
    pathex=[SPEC_ROOT],
    binaries=[],
    datas=[
        # PySide6 플러그인 수동 포함 (한글 경로 문제 회피)
        (os.path.join(PYSIDE6_PATH, 'plugins', 'platforms'), 'PySide6/plugins/platforms'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'sqldrivers'), 'PySide6/plugins/sqldrivers'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'styles'), 'PySide6/plugins/styles'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'imageformats'), 'PySide6/plugins/imageformats'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSql',
        'PySide6.QtNetwork',
        'qfluentwidgets',
        'qfluentwidgets.common',
        'qfluentwidgets.components',
        'cryptography',
        'cryptography.fernet',
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
    hooksconfig={},  # PySide6 자동 hook 비활성화 (한글 경로 문제)
    runtime_hooks=[],
    excludes=[
        # 불필요한 Qt 바인딩 완전 제외
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PySide2',
        'tkinter',
        '_tkinter',
        'sip',
        # 불필요한 대용량 패키지
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
    ],
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

