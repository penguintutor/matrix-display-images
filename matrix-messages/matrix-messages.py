#!/usr/bin/python

## Works along with matrix-display-images
## Updates the display-image.cfg file based on seasonal message

from gpiozero import MotionSensor
from time import sleep
from message import Message
import copy


config_file = "messages.cfg"

active_message = None
# Aim of future_message_start is just to determine when next to re-read
# config file - so set at maximum 24 hours
future_message_change = 1440

pir = MotionSensor(26)


def readConfig (config_file):
    # Reset active_message and future_message_change
    active_message = None
    future_message_change = 1440
    
    fp = open(config_file, "r");
    current_entry = {}

    while (fp):
    #for line in fp:
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
    


def main():
    
    # read the config file
    readConfig (config_file)
    
    if (active_message == None):
        print ("No active message")
    else:
        print (active_message.title)
    
    print ("Config File read")
    
    
    
#    while (True):
#        if pir.motion_detected == True:
#            print ("Motion detected")
#    	sleep (1)



if __name__ == "__main__":
    main()