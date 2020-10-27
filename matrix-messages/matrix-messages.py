#!/usr/bin/python3

## Works along with matrix-display-images
## Updates the display-image.cfg file based on seasonal message

from gpiozero import MotionSensor
from time import sleep
from message import Message
from datetime import datetime, timedelta
import copy


config_file = "/home/pi/matrix-display-images/matrix-messages/messages.cfg"
display_image_config_file = "/home/pi/matrix-display-images/display-image.cfg"

# how long to wait between checking for pir setting in sec
time_between_pir = 1

active_message = None
# Aim of future_message_start is just to determine when next to re-read
# config file - so set at maximum 24 hours (minutes)
# if config gives a sooner value then change later
future_message_change = 1440

pir = MotionSensor(26)


def readConfig (config_file):
    global active_message
    # Reset active_message and future_message_change
    active_message = None
    future_message_change = 1440
    
    fp = open(config_file, "r")
    current_entry = {}

    while (fp):
        lastline = False
        # Read a line at a time
        line = fp.readline()
        if (line == '') :
            lastline = True
        # strip off any new line etc (must do after checking for lastline)
        line = line.strip()
        # Ignore comments / empty lines
        if (line.startswith ('#') or line == "") :
            continue
        if (line.startswith('[') or lastline == True):
            # If less than 2 entries in current entry then only title so ignore
            if (len(current_entry) < 2):
                # if there is title, but nothing else then issue warning
                if ('title' in current_entry.keys()):
                    print ("Warning ast entry incomplete - %s", current_entry['title'])
                if (lastline == True):
                    #Debug show all objects as created
                    print ("Last line read")
                    break
                # get rid of current entry - and start new with title
                current_entry = {}
                line = line.replace ('[', "")
                line = line.replace (']', "")
                current_entry['title'] = line
                continue

            # Current_entry has values in it so create a new instance
            this_message = Message(current_entry)
            
            # Test to see if this new entry is to be new entry or potential next
            # If so save it as the new entry
            #Debug show all objects as created
            print (this_message.to_string())
            
            # Should this be current active one (if so then don't read anymore entries)
            if (this_message.date_time_valid):
                #print ("Found active entry")
                # Make this active
                active_message = copy.copy(this_message)
                # update time next check if less then next message
                if (active_message.minutes_to_end() < future_message_change):
                    future_message_change = active_message.minutes_to_end()
                # stop reading file
                break
            # or is this likely to be the next one - ie shortest time to active
            elif (this_message.minutes_to_start() < future_message_change):
                future_message_change = this_message.minutes_to_start()
                
                
            # Now stored previous entry and if not already got active
            # save new entry in temporary dictionary
            current_entry = {}
            line = line.replace ('[', "")
            line = line.replace (']', "")
            current_entry['title'] = line

            
        # Otherwise this is next line - store in data
        else:
            (key, value) = line.split('=')
            current_entry[key] = value
            
            
    # End of while loop
    # close file
    fp.close()
    

def writeConfig (pir_status):
    fp = open(display_image_config_file, "w")
    fp.write ("directory="+active_message.directory+"\n")
    if (active_message.pir_enable and pir_status):
        fp.write ("prefix="+active_message.pir_prefix+"\n")
    else:
        fp.write ("prefix="+active_message.prefix+"\n")
    ## Need to add delay and position handling
    fp.close()

def main():
    time_read = datetime.min
    while True:
        
        # read the config file
        # reread if it's changed or when time has expired
        if (time_read + timedelta(minutes=future_message_change) < datetime.now()):
            #print ("Reading config file")
            readConfig (config_file)
            time_read = datetime.now()
        
        if (active_message == None):
            #print ("No active message")
            pass
        else:
            print (active_message.title)
        
            if active_message.pir_enable:
                #print ("Checking pir")
                if pir.motion_detected == True:
                    writeConfig (True)
                    #print ("Motion detected")
                else:
                    writeConfig (False)
                    sleep (time_between_pir)
            else:
                writeConfig (False)
                sleep (future_message_change * 60)
                



if __name__ == "__main__":
    main()