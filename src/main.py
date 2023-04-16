import subprocess
from time import sleep
from yaml import load, Loader
from pprint import pprint
import json
from hashlib import md5

from config_model import Config, Pane

global_config: Config = None
config_hash = ""

def load_config():
    global config_hash
    global global_config

    print("Loading config...")
    config = load(open("config/config.yml"), Loader=Loader)

    # create a hash of the config
    string = json.dumps(config, sort_keys=True)
    hash = md5(string.encode('utf-8')).hexdigest()

    print("Config hash: " + hash)

    if config_hash != hash:
        global_config = Config(**config)
        config_hash = hash

load_config()

if global_config is None:
    print("No config found")
    exit(1)


print("Starting script")

subprocess.call(["tmux", "new-session", "-d", "-s", global_config.session_name])

for (win_index, window) in enumerate(global_config.windows):
    if win_index == 0:
        subprocess.call(["tmux", "rename-window", "-t", f"{global_config.session_name}:{win_index}", f"'{window.name}'"])
    else:
        subprocess.call(["tmux", "new-window", "-t", f"{global_config.session_name}:{win_index}", "-n", f"'{window.name}'"])

    for (index, pane) in enumerate(window.panes):
        p: Pane = pane
        command = f"{pane.command}"
        if p.host is not None:
            host = global_config.hosts
            host_match = [h for h in host if h.name == p.host]

            if len(host_match) == 0:
                print(f"Host '{p.host}' not found")
                exit(1)

            host = host_match[0]

            command = f"ssh -t {host.username}@{host.host} '{command}'"
        
        subprocess.call(
            ["tmux", "send-key", "-t", f"{global_config.session_name}:{win_index}.{index}", f"{command} \r"]
        )


sleep(5)
# # This is a blocking call, so it will wait until the tmux session is closed before continuing
subprocess.call(["tmux", "attach-session", "-t", global_config.session_name])
print("Tmux session closed")

# print("Restarting script...")
