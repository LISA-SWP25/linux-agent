# -*- mode: python ; coding: utf-8 -*-
# PyInstaller specification file for Linux Activity Agent

block_cipher = None

a = Analysis(
    ['unified_agent.py'],
    pathex=[],
    binaries=[
        # Добавляем системные утилиты если нужно
        # ('/usr/bin/xdotool', 'bin/'),
    ],
    datas=[
        # Добавляем дополнительные файлы если нужно
    ],
    hiddenimports=[
        'subprocess',
        'logging',
        'json',
        'datetime',
        'random',
        'time',
        'os',
        'sys',
        'shutil',
        'urllib.request',
        'tempfile',
        'pathlib',
        'collections',
        'threading',
        'signal',
        'functools',
        'itertools',
        'socket',
        'platform'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PySide2',
        'wx'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Исключаем ненужные модули для уменьшения размера
a.binaries = [x for x in a.binaries if not x[0].startswith('lib')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries