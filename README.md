# Linux Activity Agent

This agent runs as root and emulates the actions of users with different roles.: admin, developer, user.


## Features ()
- Executes commands from different users
- Simulation of clicks via xdotool
- Logging to a file
- Metrics (execution time, errors)
- Systemd service

## Iinstalling

1. Clone or unpack in `/opt/linux_agent`
2. Install Dependencies:
    sudo apt install python3 python3-pip xdotool
    pip install pyyaml

3. Сreate users:
    sudo useradd -m admin
    sudo useradd -m developer
    sudo useradd -m user
    sudo usermod -aG sudo admin

4. Add in `/etc/sudoers`:
    admin ALL=(ALL) NOPASSWD:ALL
    developer ALL=(ALL) NOPASSWD:ALL
    user ALL=(ALL) NOPASSWD:ALL

5. Install and run the service:
    sudo cp agent.service /etc/systemd/system/
    sudo systemctl daemon-reexec
    sudo systemctl enable agent
    sudo systemctl start agent
