# Linux Activity Agent

This agent runs as root and emulates the actions of users with different roles.: admin, developer, user.


## Features ()
- Executes commands from different users
- Simulation of clicks via xdotool
- Logging to a file
- Metrics (execution time, errors)
- Systemd service

# Iinstalling

Usage on target machine:
## Unpack archive
tar -xzf linux_activity_agent.tar.gz

## Install (will install all applications automatically)
sudo ./install_agent.sh

## The agent will start automatically and will run on schedule.

