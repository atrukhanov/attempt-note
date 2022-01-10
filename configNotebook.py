import os
import sys
import subprocess
import argparse

RADICALE_CONFIG_PATH = os.environ['HOME'] + '/.config/radicale'
SERVICE_CONFIG_PATH = os.environ['HOME'] + '/.config/systemd/user/'
STORAGE = os.environ['HOME'] + '/.NStorage'

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
    os.system('mkdir {}'.format(RADICALE_CONFIG_PATH)) 

    print("Input new user's name:")
    user = input()
    os.system('htpasswd -c {}/.credentials {}'.format(RADICALE_CONFIG_PATH, user))

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
    port = int(input())

    with open(RADICALE_CONFIG_PATH + '/.radicale_config', 'w') as radicale_config:
        radicale_config.write(radicale_config_template.format(port, RADICALE_CONFIG_PATH + '/.credentials', STORAGE))

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
    with open(SERVICE_CONFIG_PATH + '/radicale.service', 'w') as service_config:
        service_config.write(service_config_template.format(RADICALE_CONFIG_PATH + '/.radicale_config'))

    os.system('systemctl --user enable radicale')
    os.system('systemctl --user start radicale')

def show_config():
    with open(RADICALE_CONFIG_PATH + '/.radicale_config', 'r') as config:
        print(config.read())

def stop():
    os.system('systemctl --user disable radicale')

function_map = {'setup': setup, 'config': show_config, 'stop': stop}

if __name__ == '__main__': 
    args = parser.parse_args()
    if args.command:
        try:
            function_map[args.command]()
        except KeyError:
            print("wrong command line parameter")
