#!/bin/bash

# remove old portdict.pickle file if it exists
[ -e portdict.pickle ] && rm portdict.pickle

# find empty ports and save them to portdict
python3 -uc 'import portutil; portutil.fill_portdict()'

# activate memeenv
source meme-model-api/memeenv/bin/activate

# kill all current screens and start meme-model api in screen session
for scr in $(screen -ls | grep Detached | awk '{print $1}'); do screen -S $scr -X kill; done
screen -L -S meme-model-api -d -m python3 meme-model-api/main.py

# deactive memeenv
deactivate

# activate venv
source venv/bin/activate

# start all python components in their own screen session
screen -L -S text-api -d -m python3 text-api/main.py
screen -L -S ocr-api -d -m python3 ocr-api/main.py
screen -L -S voice-api -d -m python3 voice-api/main.py
screen -L -S target-api -d -m python3 target-api/main.py
screen -L -S telegram-bot -d -m python3 telegram-bot/main.py

# deactivate venv
deactivate

# print overview
sleep 2
screen -ls
python3 -uc 'import portutil; portutil.print_ports()'

# print useful commands:
echo 'Useful commands:'
echo '  List screen sessions:       screen -ls'
echo '  Attach to screen session:   screen -r ocr-api'
echo '  Detach from screen session: Ctrl + A, D'
echo '  Scrolling in screen:        Ctrl + A, esc -> up/down -> esc'

# start tests

#echo "Starting all tests in test_endpoints.py..."
#sleep 30
#py.test --ignore=meme-model-api/vilio