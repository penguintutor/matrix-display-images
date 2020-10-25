#Matrix Messages

This is a program to be used in conjunction with the matrix-display-images program.

This program can be used to show different images on an RGB LED Matrix on a Raspberry Pi by instructing the matrix-display-images to load the current image from a different folder. Additional functionality is included to allow the program to respond to external events such as a PIR motion sensor.



##messages.cfg file

Format of each entry


[Title - human readable reference]
start_date=<mm:dd>      (can add yyyy:mm:dd for year specific) - start-date and end-date must use same format (mm:dd or yyyy:mm:dd)
end-date=<mm:dd>
start_time=<hh:mm:ss>   (if start-time need end-time - if not then on all day) - handle time in same day or from night to morning
end_time=<hh:mm:ss>     (if endtime < starttime and time > startime and time < endtime then on - if endtime > start time and time >starttime and starttime < endtime then on)
directory=<path>
prefix=<normal-prefix>
pir_enable=true
pir_prefix=<prefix>
count=<number>


Order of entries is important - first match that applies is used - sleeps until end-date or reasonable time passed
Also need to save next nearest start time above as another potential trigger for re-reading.

When any of those times are reached then re-read config to see which applies


## Todo

Add more checking to message.py for parsing config file


## More Information

For more information see my website at: [PenguinTutor RGB LED Matrix display](http://www.penguintutor.com/projects/rpi-matrix-rgbled)