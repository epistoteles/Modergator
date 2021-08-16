import random
import subprocess
import pickle


def get_unused_port(name):
    port_suggestion = 0
    netstat_output = ':0'
    while f"{':'}{port_suggestion}" in str(netstat_output):
        port_suggestion = random.randint(1000, 60000)
        netstat_output, _ = subprocess.Popen(['netstat', '-lat'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT).communicate()
    return port_suggestion


def print_ports():
    response = []
    try:
        portdict = pickle.load(open("portdict.pickle", "rb"))
    except (OSError, IOError) as e:
        print('portdict.pickle does not exist')
    for key, value in portdict.items():
        response += [f'  Using port {value} for service {key}']
    print('\n'.join(response))


def fill_portdict():
    print('Filling portdict and starting services ...')
    portdict = {}
    for api in ['text-api', 'voice-api', 'ocr-api', 'meme-model-api', 'target-api']:
        port = get_unused_port(api)
        portdict[api] = port
    pickle.dump(portdict, open("portdict.pickle", "wb"))
