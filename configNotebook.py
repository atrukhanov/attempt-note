import os
import sys
import subprocess
import argparse
from pathlib import Path

RADICALE_CONFIG_DIR = Path('~/.config/radicale').expanduser()
RADICALE_CONFIG = RADICALE_CONFIG_DIR / '.radicale_config'
RADICALE_CREDENTIALS = RADICALE_CONFIG_DIR / '.credentials'

SERVICE_CONFIG_DIR = Path('~/.config/systemd/user/').expanduser()
SERVICE_CONFIG = SERVICE_CONFIG_DIR / 'radicale.service'

STORAGE_DIR =  Path('~/.NStorage').expanduser()

os.makedirs(RADICALE_CONFIG_PATH, exist_ok=True)
os.makedirs(SERVICE_CONFIG_PATH, exist_ok=True)
os.makedirs(STORAGE, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('command', help='command for launch script functions')

def setup():
    #if pip not installed
    os.system('apt install python3-pip')

    #install server module
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'radicale'])

    #create user
    os.system('sudo apt install apache2-utils')

    user = input("Input new user's name: ")
    os.system(f'htpasswd -c {RADICALE_CREDENTIALS} {user}')
    
    radicale_config_template = '''
    [server]
    # Bind all addresses
    hosts = 0.0.0.0:{0}, [::]:{0}

    [auth]
    type = htpasswd
    htpasswd_filename = {1}
    htpasswd_encryption = md5

    [storage]
    filesystem_folder = {2}
    '''
    print('Input service port:')
    
    port = int(input('Input service port:'))

    with RADICALE_CONFIG.open(mode='w') as radicale_config:
        radicale_config.write(radicale_config_template.format(port, RADICALE_CREDENTIALS, STORAGE_DIR))

    #inint os service
    service_config_template = '''
    [Unit]
    Description=Notebook service

    [Service]
    ExecStart=/usr/bin/env python3 -m radicale --config {}
    Restart=on-failure

    [Install]
    WantedBy=default.target
    '''
    with SERVICE_CONFIG.open(mode='w') as service_config:
        service_config.write(service_config_template.format(RADICALE_CONFIG))
    
    os.system('systemctl --user enable radicale')

def show_config():
    with RADICALE_CONFIG.open(mode='r') as config:
        print(config.read())
 
def service_launch(command):
        os.system(f'systemctl --user {command} radicale')

CONFIG_FUNCTIONS_MAP = {'setup': setup, 'config': show_config}
LAUNCH_FUNCTIONS =  ['start', 'stop', 'status']

if __name__ == '__main__': 
    args = parser.parse_args()
    if args.command in CONFIG_FUNCTIONS_MAP.keys():
        CONFIG_FUNCTIONS_MAP[args.command]()
    elif args.command in LAUNCH_FUNCTIONS:
        service_launch(args.command)
