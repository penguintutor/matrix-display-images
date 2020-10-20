#!/usr/bin/python

## Works along with matrix-display-images
## Updates the display-image.cfg file based on seasonal message

from gpiozero import MotionSensor
from time import sleep
from message import message


config_file = "messages.cfg"

current_message = None
future_message = None

def readConfig (config_file):
    fp = fopen(config_file, "r");
    current_entry = {}
    #current_message, new

    while (fp):
        # Read a line at a time
        line = fp.readline().strip()
        # Ignore comments / empty lines
        if (line.startwith ('#') or line == "") :
            continue
        if (line.startswith('[')):
            # If less than 2 entries then only title
            if (len(current_entry) < 2):
                # Save new entry and restart
                current_entry = {}
                line = line.replace ('[', "")
                line = line.replace (']', "")
                current_entry['title'] = line
                continue
            # If not then create an object
            this_message = Message(data)

copy.copy


pir = MotionSensor(26)

def main():
    while (True):1):
        if pir.motion_detected == True:
            print ("Motion detected")
    	sleep (1)



if __name__ == "__main__":
    main()