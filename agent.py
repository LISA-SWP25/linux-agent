import os
import time
import subprocess
import logging
from datetime import datetime
from utils import load_yaml, choose_random_command

CONFIG = load_yaml("config.yaml")

logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def run_as(user, command):
    start_time = time.time()
    try:
        subprocess.run(["sudo", "-u", user, "bash", "-c", command], check=True)
        duration = time.time() - start_time
        logging.info(f"[{user}] SUCCESS: {command} (duration: {duration:.2f}s)")
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        logging.error(f"[{user}] ERROR: {command} (duration: {duration:.2f}s) - {e}")

def type_text(text):
    subprocess.run(["xdotool", "type", "--delay", "100", text])

def main():
    users = CONFIG["users"]
    while True:
        user = random.choice(users)
        role_path = os.path.join("roles", f"{user}.yaml")
        role_data = load_yaml(role_path)
        cmd = choose_random_command(role_data["commands"])

        if "type:" in cmd:
            text = cmd.split("type:")[1].strip()
            type_text(text)
            logging.info(f"[{user}] TYPED: {text}")
        else:
            run_as(user, cmd)

        wait_time = random.randint(CONFIG["run_interval_min"], CONFIG["run_interval_max"])
        logging.info(f"Waiting {wait_time}s before next action")
        time.sleep(wait_time)

if __name__ == "__main__":
    import random
    main()
