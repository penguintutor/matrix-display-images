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
log_file = "/home/pi/matrix-display-images/matrix-messages/log.txt"

# how long to wait between checking for pir setting in sec
time_between_pir = 1

active_message = None
# Aim of future_message_start is just to determine when next to re-read
# config file - so set at maximum 24 hours (minutes)
# if config gives a sooner value then change later
future_message_change = 1440

pir = MotionSensor(26)

# Debug setting - increase value to print status messages whilst running
# debug=0 will only display errors
debug = 0
# What level to log to file (1 = less noisy than debug 1)
# Level 3+ is going to be very noisy
log_level = 1

def readConfig (config_file):
    global active_message, future_message_change
    # Reset active_message and future_message_change
    active_message = None
    future_message_change = 1440
    
    if (debug > 0):
        print ("Reading config file")
        
    if (log_level > 0):
        logMessage ("Reading config file")
    
    fp = open(config_file, "r")
    current_entry = {}

    while (fp):
        lastline = False
        # Read a line at a time
        line = fp.readline()
        # lastline indicates lastline of file read in, but if we've already reached end
        # indicated by not line - then treat the same as though it's the last line
        if (not line):
            lastline = True
            line = ''
        if (line == '') :
            lastline = True
        # strip off any new line etc (must do after checking for lastline)
        line = line.strip()
        # Ignore comments / empty lines
        if ((line.startswith ('#') or line == "") and lastline == False) :
            continue
        if (line.startswith('[') or lastline == True):
            # If less than 2 entries in current entry then only title so ignore
            if (len(current_entry) < 2):
                # if there is title, but nothing else then issue warning
                if ('title' in current_entry.keys()):
                    print ("Warning last entry incomplete - %s", current_entry['title'])
                if (lastline == True):
                    #Debug show all objects as created
                    print ("Warning last entry incomplete %s and last line read", current_entry['title'])
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
            if (debug > 0):
                print (this_message.to_string())
            
            # Should this be current active one (if so then don't read anymore entries)
            if (this_message.date_time_valid()):
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
            
            # Exit if lastline read - no more entries
            if (lastline == True):
                break
            
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

    

def logMessage (message):
    fp = open(log_file, "a")
    fp.write (datetime.now().isoformat()+": "+message+"\n")
    fp.close()
    
    
def startLog ():
    # Allows it to change the log_level if unable to log
    global log_level
    if (log_level == 0):
        return
    if (log_file == ""):
        log_level = 0
        return
    # Write to log 
    logMessage ("Application started")
        
        

def writeConfig (pir_status):
    if (debug > 0):
        print ("Writing config")
    if (log_level > 0):
        logMessage("Writing config "+active_message.title)
    fp = open(display_image_config_file, "w")
    fp.write ("directory="+active_message.directory+"\n")
    if (active_message.pir_enable and pir_status):
        fp.write ("prefix="+active_message.pir_prefix+"\n")
    else:
        fp.write ("prefix="+active_message.prefix+"\n")
    if (active_message.delay != ""):
        fp.write ("delay="+active_message.delay+"\n")
    if (active_message.display == "false") :
        fp.write ("display=false\n")
    ## Need to add position handling
    fp.close()
    
def writeDisableConfig ():
    if (debug > 0):
        print ("Writing null config")
    if (log_level > 0):
        logMessage("Writing null config")
    fp = open(display_image_config_file, "w")
    fp.write ("display=false\n")
    fp.close()

def main():
    startLog()
    time_read = datetime.min
    while True:
        
        # read the config file
        # reread if time has expired
        if (time_read + timedelta(minutes=future_message_change) < datetime.now()):
            #print ("Reading config file")
            # reset active_message - readConfig will replace if there is an active message
            active_message == None
            readConfig (config_file)
            time_read = datetime.now()
        
        if (active_message == None):
            if (debug > 0):
                print ("No active message")
            writeDisableConfig()
            # log sleep time
            if (log_level > 2):
                logMessage ("Sleeping for "+str(future_message_change*60)+ "seconds (not active)")
            # set sleep time to next config check time
            sleep (future_message_change * 60)
        else:
            if (debug > 0) :
                print ("Active message is "+active_message.title)
        
            if active_message.pir_enable:
                if (debug > 1):
                    print ("Checking pir")
                if pir.motion_detected == True:
                    writeConfig (True)
                    if (debug > 1):
                        print ("Motion detected")
                    if (active_message.pir_ontime != 0):
                        # log sleep time
                        if (log_level > 2):
                            logMessage ("Sleeping for "+str(active_message.pir_ontime/1000)+ "seconds (motion detected")
                        sleep(active_message.pir_ontime/1000)
                else:
                    writeConfig (False)
                    # log sleep time
                    if (log_level > 2):
                        logMessage ("Sleeping for "+str(time_between_pir)+ "seconds (pir delay)")
                    sleep (time_between_pir)
            else:
                writeConfig (False)
                # log sleep time
                if (log_level > 2):
                    logMessage ("Sleeping for "+str(future_message_change*60)+ "seconds (not pir)")
                sleep (future_message_change * 60)
                



if __name__ == "__main__":
    main()