# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('D:\\git\\ModernLamComptabilite\\src\\ui\\styles.qss', 'ui'), ('D:\\git\\ModernLamComptabilite\\src\\pdf_settings.json', '.'), ('D:\\git\\GoldShop\\venv\\Lib\\site-packages\\mysql\\connector\\plugins', 'mysql/connector/plugins'), ('D:\\git\\GoldShop\\venv\\Lib\\site-packages\\mysql\\connector\\locales', 'mysql/connector/locales'), ('D:\\git\\ModernLamComptabilite\\src\\logo.png', '.')]
binaries = []
hiddenimports = ['mysql.connector.plugins.mysql_native_password', 'sqlalchemy', 'openpyxl']
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mysql.connector')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pandas')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=['D:\\git\\ModernLamComptabilite\\src'],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FINANCELAM',
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
    icon=['D:\\git\\ModernLamComptabilite\\src\\logo.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FINANCELAM',
)
