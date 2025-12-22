# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\송민정\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\PySide6\\plugins\\platforms', 'PySide6/plugins/platforms'), ('C:\\Users\\송민정\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\PySide6\\plugins\\sqldrivers', 'PySide6/plugins/sqldrivers'), ('C:\\Users\\송민정\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\PySide6\\plugins\\styles', 'PySide6/plugins/styles'), ('C:\\Users\\송민정\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\PySide6\\plugins\\imageformats', 'PySide6/plugins/imageformats')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtSql', 'PySide6.QtNetwork', 'qfluentwidgets', 'cryptography', 'cryptography.fernet', 'requests', 'numpy', 'pandas', 'markdown'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'tkinter', 'matplotlib', 'scipy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Gr8 DIY',
)
