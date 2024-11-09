#!/bin/bash

# Open a new terminal and run the first Python executable

# Open a new terminal and run the second Python script
gnome-terminal -- /bin/bash -c 'cd /home/karim/Desktop/Process/MQTT_SERVICE && python3 MQ.py; sleep 5; exec /bin/bash'

# Open a new terminal and run the third Python script
gnome-terminal -- /bin/bash -c 'cd /home/karim/Desktop/Process/GUI_SERVICE && python3 final.py; sleep 5; exec /bin/bash'

# Open a new terminal and run the fourth Python script
gnome-terminal -- /bin/bash -c 'cd /home/karim/Desktop/Process/FIRMWARE_UPDATE_SERVICE && python3 FIRM_I2C.py; sleep 5; exec /bin/bash'

