#!/bin/bash

# Скрипт для сборки единого исполняемого файла агента
set -e

echo "Building Unified Linux Activity Agent..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Устанавливаем PyInstaller
echo "Installing PyInstaller..."
pip3 install pyinstaller

# Создаем spec файл для PyInstaller
cat > activity_agent.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['unified_agent.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
        'pathlib'
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
    name='activity_agent',
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
)
EOF

# Сборка
echo "Building executable..."
pyinstaller --clean activity_agent.spec

# Проверяем результат
if [ -f "dist/activity_agent" ]; then
    echo "Build successful!"
    echo "Executable: $(pwd)/dist/activity_agent"
    echo "Size: $(du -h dist/activity_agent | cut -f1)"
    
    # Делаем файл исполняемым
    chmod +x dist/activity_agent
    
    # Создаем инсталлятор
    echo "Creating installer script..."
    cat > dist/install_agent.sh << 'INSTALL_EOF'
#!/bin/bash

# Установщик Linux Activity Agent (использует оригинальную структуру agent.service)
set -e

AGENT_PATH="./activity_agent"
INSTALL_DIR="/opt/linux_agent"
SERVICE_FILE="/etc/systemd/system/activity-agent.service"

echo "Linux Activity Agent Installer"
echo "=============================="
echo "Using original agent.service configuration"

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Проверяем наличие файла агента
if [ ! -f "$AGENT_PATH" ]; then
    echo "Error: activity_agent file not found in current directory"
    exit 1
fi

# Создаем директорию установки (как в оригинальном agent.service)
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Копируем агента в рабочую директорию
echo "Installing agent to $INSTALL_DIR..."
cp "$AGENT_PATH" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/activity_agent"

# Также копируем в системную директорию для удобства
echo "Installing agent to /usr/local/bin..."
cp "$AGENT_PATH" "/usr/local/bin/activity_agent"
chmod +x "/usr/local/bin/activity_agent"

# Запускаем установку зависимостей
echo "Installing dependencies and setting up service..."
"$INSTALL_DIR/activity_agent" --install

echo "Installation completed!"
echo "Agent installed to: $INSTALL_DIR/activity_agent"
echo "System binary: /usr/local/bin/activity_agent"
echo "Service: activity-agent.service"
echo "Working directory: $INSTALL_DIR (as per original agent.service)"
echo ""
echo "To start the agent:"
echo "  sudo systemctl start activity-agent"
echo ""
echo "To check status:"
echo "  sudo systemctl status activity-agent"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u activity-agent -f"
echo ""
echo "Service will use XAUTHORITY=/home/user/.Xauthority as per original config"

INSTALL_EOF

    chmod +x dist/install_agent.sh
    
    echo ""
    echo "Files created:"
    echo "  - dist/activity_agent (main executable)"
    echo "  - dist/install_agent.sh (installer script)"
    echo ""
    echo "Usage:"
    echo "  1. Copy both files to target machine"
    echo "  2. Run: sudo ./install_agent.sh"
    echo "  3. Agent will be installed and auto-started"
    
else
    echo "Build failed!"
    exit 1
fi

# Опционально: создаем архив для распространения
echo "Creating distribution archive..."
cd dist
tar -czf linux_activity_agent.tar.gz activity_agent install_agent.sh
echo "Distribution package: dist/linux_activity_agent.tar.gz"

echo "Build process completed successfully!"
