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

