#!/usr/bin/env python3
"""
Unified Linux Activity Agent
Симулирует активность пользователя в различных приложениях
"""

import os
import sys
import time
import json
import subprocess
import logging
import random
import shutil
import urllib.request
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Встроенная конфигурация пользователя
USER_CONFIG = {
    "user_id": "USR0012345",
    "username": "john_doe",
    "full_name": "John Doe", 
    "role": "Junior Developer",
    "work_schedule": {
        "start_time": "09:00",
        "end_time": "18:00",
        "breaks": [
            {
                "start": "13:00",
                "duration_minutes": 60
            }
        ]
    },
    "operating_system": "Linux Ubuntu 22.04",
    "applications_used": [
        "Visual Studio Code",
        "Google Chrome", 
        "Slack",
        "Docker Desktop"
    ],
    "activity_pattern": "Regular office hours with lunch break",
    "department": "Development",
    "location": "Headquarters"
}

# Конфигурация для установки приложений
INSTALLATION_CONFIG = {
    "vscode": {
        "check_command": "code --version",
        "install_commands": [
            "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg",
            "sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/",
            "sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'",
            "sudo apt update",
            "sudo apt install -y code"
        ]
    },
    "chrome": {
        "check_command": "google-chrome --version",
        "install_commands": [
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
            "sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'",
            "sudo apt update",
            "sudo apt install -y google-chrome-stable"
        ]
    },
    "slack": {
        "check_command": "slack --version",
        "install_commands": [
            "wget https://downloads.slack-edge.com/releases/linux/4.33.90/prod/x64/slack-desktop-4.33.90-amd64.deb",
            "sudo dpkg -i slack-desktop-4.33.90-amd64.deb",
            "sudo apt-get install -f -y"
        ]
    },
    "docker": {
        "check_command": "docker --version",
        "install_commands": [
            "sudo apt-get update",
            "sudo apt-get install -y ca-certificates curl gnupg lsb-release",
            "sudo mkdir -p /etc/apt/keyrings",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
            "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
            "sudo apt-get update",
            "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
            "sudo usermod -aG docker $USER"
        ]
    },
    "xdotool": {
        "check_command": "xdotool version",
        "install_commands": [
            "sudo apt update",
            "sudo apt install -y xdotool"
        ]
    }
}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/activity_agent.log'),
        logging.StreamHandler()
    ]
)

class ApplicationInstaller:
    """Установщик необходимых приложений"""
    
    def __init__(self):
        self.installed_apps = []
    
    def check_root_privileges(self):
        """Проверяет наличие root привилегий"""
        return os.geteuid() == 0
    
    def run_command(self, command, check_output=False):
        """Выполняет команду в системе"""
        try:
            if check_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stderr
        except Exception as e:
            logging.error(f"Command execution failed: {command} - {e}")
            return False, str(e)
    
    def is_app_installed(self, app_key):
        """Проверяет, установлено ли приложение"""
        if app_key not in INSTALLATION_CONFIG:
            return True
        
        check_cmd = INSTALLATION_CONFIG[app_key]["check_command"]
        success, _ = self.run_command(check_cmd, check_output=True)
        return success
    
    def install_app(self, app_key):
        """Устанавливает приложение"""
        if app_key not in INSTALLATION_CONFIG:
            logging.warning(f"No installation config for {app_key}")
            return True
        
        if self.is_app_installed(app_key):
            logging.info(f"{app_key} is already installed")
            return True
        
        logging.info(f"Installing {app_key}...")
        install_commands = INSTALLATION_CONFIG[app_key]["install_commands"]
        
        for cmd in install_commands:
            logging.info(f"Executing: {cmd}")
            success, output = self.run_command(cmd)
            if not success:
                logging.error(f"Failed to execute: {cmd} - {output}")
                return False
            time.sleep(2)  # Пауза между командами
        
        # Проверяем успешность установки
        if self.is_app_installed(app_key):
            logging.info(f"{app_key} installed successfully")
            self.installed_apps.append(app_key)
            return True
        else:
            logging.error(f"Failed to install {app_key}")
            return False
    
    def install_all_dependencies(self):
        """Устанавливает все необходимые зависимости"""
        if not self.check_root_privileges():
            logging.error("Root privileges required for installation")
            return False
        
        # Обновляем систему
        logging.info("Updating system packages...")
        self.run_command("sudo apt update")
        
        # Устанавливаем основные зависимости
        apps_to_install = ["xdotool", "vscode", "chrome", "slack", "docker"]
        
        for app in apps_to_install:
            if not self.install_app(app):
                logging.warning(f"Failed to install {app}, continuing...")
        
        logging.info(f"Installation complete. Installed apps: {self.installed_apps}")
        return True

class ActivityUtils:
    """Утилиты для работы с активностью"""
    
    @staticmethod
    def get_application_commands(app_name):
        """Возвращает команды для работы с приложением"""
        app_configs = {
            "Visual Studio Code": {
                "open": "code",
                "close": "pkill -f code",
                "activities": [
                    {
                        "description": "Opening a file",
                        "commands": [
                            "xdotool key ctrl+o",
                            "sleep 2",
                            "xdotool type 'main.py'",
                            "xdotool key Return"
                        ]
                    },
                    {
                        "description": "Typing code",
                        "commands": [
                            "xdotool type 'print(\"Hello World\")'",
                            "xdotool key Return", 
                            "xdotool key ctrl+s"
                        ]
                    },
                    {
                        "description": "Search in files",
                        "commands": [
                            "xdotool key ctrl+shift+f",
                            "sleep 1",
                            "xdotool type 'function'",
                            "xdotool key Return"
                        ]
                    }
                ]
            },
            "Slack": {
                "open": "slack",
                "close": "pkill -f slack",
                "activities": [
                    {
                        "description": "Checking messages",
                        "commands": [
                            "xdotool key ctrl+k",
                            "sleep 1",
                            "xdotool type 'general'",
                            "xdotool key Return"
                        ]
                    },
                    {
                        "description": "Typing message", 
                        "commands": [
                            "xdotool type 'Good morning team!'",
                            "xdotool key Return"
                        ]
                    }
                ]
            },
            "Google Chrome": {
                "open": "google-chrome",
                "close": "pkill -f chrome",
                "activities": [
                    {
                        "description": "Browsing documentation",
                        "commands": [
                            "xdotool key ctrl+l",
                            "xdotool type 'https://docs.python.org'",
                            "xdotool key Return",
                            "sleep 5",
                            "xdotool key ctrl+f",
                            "xdotool type 'function'"
                        ]
                    },
                    {
                        "description": "Opening new tab",
                        "commands": [
                            "xdotool key ctrl+t",
                            "xdotool type 'https://stackoverflow.com'",
                            "xdotool key Return"
                        ]
                    },
                    {
                        "description": "Scrolling page",
                        "commands": [
                            "xdotool key Page_Down",
                            "sleep 2",
                            "xdotool key Page_Down", 
                            "sleep 2",
                            "xdotool key Page_Up"
                        ]
                    }
                ]
            },
            "Docker Desktop": {
                "open": "docker",
                "close": "pkill -f docker",
                "activities": [
                    {
                        "description": "Checking containers",
                        "commands": [
                            "docker ps",
                            "sleep 2",
                            "docker images"
                        ]
                    },
                    {
                        "description": "Building image",
                        "commands": [
                            "docker build -t test-app .",
                            "sleep 10"
                        ]
                    }
                ]
            }
        }
        return app_configs.get(app_name, {})
    
    @staticmethod
    def is_work_time(current_time, work_schedule):
        """Проверяет, находится ли текущее время в рабочих часах"""
        current_time_only = current_time.time()
        
        start_time = datetime.strptime(work_schedule['start_time'], '%H:%M').time()
        end_time = datetime.strptime(work_schedule['end_time'], '%H:%M').time()
        
        return start_time <= current_time_only <= end_time
    
    @staticmethod
    def is_break_time(current_time, work_schedule):
        """Проверяет, находится ли текущее время в обеденном перерыве"""
        current_time_only = current_time.time()
        
        breaks = work_schedule.get('breaks', [])
        for break_info in breaks:
            break_start = datetime.strptime(break_info['start'], '%H:%M').time()
            break_duration = break_info['duration_minutes']
            
            # Вычисляем время окончания перерыва
            break_start_dt = datetime.combine(current_time.date(), break_start)
            break_end_dt = break_start_dt + timedelta(minutes=break_duration)
            break_end = break_end_dt.time()
            
            if break_start <= current_time_only <= break_end:
                return True
        
        return False

class ActivityAgent:
    """Главный класс агента активности"""
    
    def __init__(self, config):
        self.config = config
        self.current_app = None
        self.app_start_time = None
        self.session_duration = random.randint(300, 900)  # 5-15 минут активности
        self.utils = ActivityUtils()
    
    def run_command(self, command):
        """Выполняет команду и логирует результат"""
        start_time = time.time()
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            duration = time.time() - start_time
            if result.returncode == 0:
                logging.info(f"SUCCESS: {command} (duration: {duration:.2f}s)")
            else:
                logging.warning(f"COMMAND FAILED: {command} - {result.stderr}")
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"ERROR: {command} (duration: {duration:.2f}s) - {e}")
    
    def open_application(self, app_name):
        """Открывает приложение"""
        commands = self.utils.get_application_commands(app_name)
        if commands and 'open' in commands:
            logging.info(f"Opening application: {app_name}")
            self.run_command(commands['open'])
            self.current_app = app_name
            self.app_start_time = time.time()
            return True
        return False
    
    def close_application(self, app_name):
        """Закрывает приложение"""
        commands = self.utils.get_application_commands(app_name)
        if commands and 'close' in commands:
            logging.info(f"Closing application: {app_name}")
            self.run_command(commands['close'])
        self.current_app = None
        self.app_start_time = None
    
    def simulate_activity(self, app_name):
        """Эмулирует активность в приложении"""
        commands = self.utils.get_application_commands(app_name)
        if commands and 'activities' in commands:
            activity = random.choice(commands['activities'])
            logging.info(f"Simulating activity in {app_name}: {activity['description']}")
            
            for cmd in activity['commands']:
                self.run_command(cmd)
                time.sleep(random.uniform(1, 3))  # Пауза между командами
    
    def should_switch_app(self):
        """Определяет, нужно ли переключиться на другое приложение"""
        if not self.current_app or not self.app_start_time:
            return True
        
        elapsed = time.time() - self.app_start_time
        return elapsed >= self.session_duration
    
    def get_next_app(self):
        """Выбирает следующее приложение для работы"""
        apps = self.config.get('applications_used', [])
        if not apps:
            return None
        
        # Исключаем текущее приложение для разнообразия
        available_apps = [app for app in apps if app != self.current_app]
        if not available_apps:
            available_apps = apps
        
        return random.choice(available_apps)
    
    def run(self):
        """Основной цикл работы агента"""
        logging.info(f"Starting activity agent for user: {self.config.get('username', 'unknown')}")
        logging.info(f"Role: {self.config.get('role', 'unknown')}")
        logging.info(f"Work schedule: {self.config.get('work_schedule', {})}")
        
        while True:
            current_time = datetime.now()
            
            # Проверяем, рабочее ли время
            if not self.utils.is_work_time(current_time, self.config['work_schedule']):
                if self.current_app:
                    logging.info("Work time ended, closing current application")
                    self.close_application(self.current_app)
                
                # Ждем до начала следующего рабочего дня
                logging.info("Outside work hours, sleeping...")
                time.sleep(300)  # Проверяем каждые 5 минут
                continue
            
            # Проверяем, не время ли перерыва
            if self.utils.is_break_time(current_time, self.config['work_schedule']):
                if self.current_app:
                    logging.info("Break time, closing current application")
                    self.close_application(self.current_app)
                
                logging.info("Break time, sleeping...")
                time.sleep(300)  # Проверяем каждые 5 минут
                continue
            
            # Определяем, нужно ли переключить приложение
            if self.should_switch_app():
                # Закрываем текущее приложение
                if self.current_app:
                    self.close_application(self.current_app)
                
                # Пауза между приложениями
                pause_time = random.randint(30, 120)  # 30 секунд - 2 минуты
                logging.info(f"Pausing for {pause_time} seconds between applications")
                time.sleep(pause_time)
                
                # Открываем новое приложение
                next_app = self.get_next_app()
                if next_app and self.open_application(next_app):
                    self.session_duration = random.randint(300, 900)  # Новая длительность сессии
                    time.sleep(5)  # Даем время приложению запуститься
            
            # Эмулируем активность в текущем приложении
            if self.current_app:
                self.simulate_activity(self.current_app)
            
            # Пауза между активностями
            activity_pause = random.randint(10, 60)  # 10 секунд - 1 минута
            time.sleep(activity_pause)

def create_service_file():
    """Создает файл сервиса для systemd на основе оригинального agent.service"""
    service_content = """[Unit]
Description=Linux Activity Agent - User Activity Simulator
After=network.target graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/local/bin/activity_agent --daemon
WorkingDirectory=/opt/linux_agent
Restart=always
RestartSec=10
User=root
Group=root

# Переменные окружения для GUI приложений
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/user/.Xauthority

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=activity-agent

# Ограничения ресурсов
MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
"""
    
    try:
        with open('/etc/systemd/system/activity-agent.service', 'w') as f:
            f.write(service_content)
        logging.info("Service file created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create service file: {e}")
        return False

def setup_autostart():
    """Настраивает автозапуск агента используя оригинальную конфигурацию agent.service"""
    try:
        # Создаем рабочую директорию как указано в оригинальном сервисе
        work_dir = '/opt/linux_agent'
        os.makedirs(work_dir, exist_ok=True)
        
        # Копируем исполняемый файл в системную директорию
        current_path = os.path.abspath(sys.argv[0])
        target_path = '/usr/local/bin/activity_agent'
        
        if current_path != target_path:
            shutil.copy2(current_path, target_path)
            os.chmod(target_path, 0o755)
            logging.info(f"Agent copied to {target_path}")
        
        # Также копируем в рабочую директорию для совместимости
        work_agent_path = os.path.join(work_dir, 'activity_agent')
        if current_path != work_agent_path:
            shutil.copy2(current_path, work_agent_path)
            os.chmod(work_agent_path, 0o755)
            logging.info(f"Agent also copied to {work_agent_path}")
        
        # Создаем файл сервиса на основе оригинального agent.service
        if create_service_file():
            # Перезагружаем systemd и включаем сервис
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', 'activity-agent.service'], check=True)
            logging.info("Service enabled for autostart using original agent.service configuration")
            return True
        
    except Exception as e:
        logging.error(f"Failed to setup autostart: {e}")
        return False

def main():
    """Главная функция"""
    logging.info("Starting Unified Linux Activity Agent")
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install':
            # Режим установки
            logging.info("Installation mode activated")
            installer = ApplicationInstaller()
            
            if not installer.check_root_privileges():
                logging.error("Root privileges required for installation")
                sys.exit(1)
            
            # Устанавливаем зависимости
            installer.install_all_dependencies()
            
            # Настраиваем автозапуск
            setup_autostart()
            
            logging.info("Installation completed. Starting agent...")
            
        elif sys.argv[1] == '--daemon':
            # Режим демона (запуск через systemd)
            logging.info("Daemon mode activated")
    
    # Создаем и запускаем агента
    agent = ActivityAgent(USER_CONFIG)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logging.info("Agent stopped by user")
        if agent.current_app:
            agent.close_application(agent.current_app)
    except Exception as e:
        logging.error(f"Agent crashed: {e}")
        if agent.current_app:
            agent.close_application(agent.current_app)

if __name__ == "__main__":
    main()
