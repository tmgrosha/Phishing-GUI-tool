import subprocess
import requests
import os
from time import sleep
from platform import system as systemos, architecture
from subprocess import check_output

RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW, YELLOW2, GREEN2 = '\033[91m', '\033[46m', '\033[36m', '\033[1;32m', '\033[0m', '\033[1;33m', '\033[1;93m', '\033[1;92m'

def net():
    print("{0}[{2}#{0}] {2}Checking for internet connection{2}....".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
    sleep(3)
    m = subprocess.run(['wget', '-q', '--spider', 'http://google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if m.returncode == 0:
        print("\n{0}[{2}#{0}] {3}INTERNET {0}- {3}[{2}CONNECTED{3}]".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
        sleep(3)
    else:
        print("\n{0}[{2}#{0}] {3}INTERNET {0}- {3}[{2}NOT-CONNECTED{3}]".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
        print("{0}[{2}#{0}] {2}Turn on your internet connection\n\n".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
        exit()

def checkjp2a():
    if subprocess.run(['which', 'jp2a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        print("{0}[{2}*{0}] {2}JP2A NOT FOUND\n {0}[{2}*{0}] {2}Installing JP2A... ".format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        subprocess.run(['apt-get', 'install', 'jp2a', '-y', '>', '/dev/null'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit()

def checkwget():
    if subprocess.run(['which', 'wget'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        print("{0}[{2}*{0}] {2}WGET NOT FOUND\n {0}[{2}*{0}] {2}Installing WGET... ".format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        subprocess.run(['apt-get', 'install', 'wget', '-y', '>', '/dev/null'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit()

def checkPHP():
    if subprocess.run(['which', 'php'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        print("{0}[{2}*{0}] {2}PHP NOT FOUND\n {0}[{2}*{0}] {2}Installing PHP... ".format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        subprocess.run(['apt-get', 'install', 'php', '-y', '>', '/dev/null'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit()

def checkNgrok():
    if not os.path.isfile('Server/ngrok'):
        print('{0}[{2}*{0}]{2} Ngrok Not Found {0}!!'.format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        print(' {0}[{2}*{0}]{2} Downloading Ngrok...{5}'.format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        filename = 'ngrok-v3-stable-linux-amd64.tgz'
        url = 'https://bin.equinox.io/c/bNyj1mQVY4c/' + filename
        subprocess.run(['wget', '-4', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['tar', '-zxvf', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['mv', 'ngrok', 'Server/ngrok'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['rm', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['chmod', '+x', 'ngrok'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit()
    else:
        print(" {0}[{2}*{0}] {2}NGROK INSTALLATION FOUND......".format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        sleep(1)

def checkLocalxpose():
    if not os.path.isfile('Server/loclx'):
        print(' {0}[{2}*{0}]{2} Localxpose Not Found {0}!!'.format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        print(' {0}[{2}*{0}]{2} Downloading Localxpose...{5}'.format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        filename = 'loclx-linux-amd64.zip'
        url = 'https://api.localxpose.io/api/v2/downloads/'+filename
        subprocess.run(['wget', '-4', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['unzip', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['rm', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['mv', 'loclx-linux-*', 'loclx'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['chmod', '+x', 'loclx'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['mv', 'loclx', 'Server/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit()
    else:
        print(" {0}[{2}*{0}] {2}LOCALXPOSE INSTALLATION FOUND.....".format(RED, WHITE, CYAN, GREEN, DEFAULT ,YELLOW))
        sleep(1)

def first_run_setup():
    if not os.path.exists("first_run_flag.txt"):
        print("{0}[{2}*{0}] {2}First time running the program, setting up dependencies...".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
        net()
        checkjp2a()
        checkwget()
        checkPHP()
        checkNgrok()
        checkLocalxpose()
        with open("first_run_flag.txt", "w") as f:
            f.write("Setup completed\n")
        print("{0}[{2}*{0}] {2}Setup complete. You can now run the program.".format(RED, WHITE, CYAN, GREEN, DEFAULT , YELLOW))
        exit()
