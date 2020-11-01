# matrix-display-images
Display images and animations on a Raspberry Pi RGB Matrix Display.

This is designed for non-interlaced png images. It can be used to display a single image, or a series of images.
It can also be run in server mode, allowing the configuration file to be updated during run time which will trigger a new series of images.

Also see the subdirectory matrix-messages which includes Python code for updating the configuration file to automatically update the images based on date or time.


## Under development
This code is currently in an early stage and is under active development. It may not work correctly (or at all).
Please check the git log and this README file for details of progress. You may also want to look for official announcements [PenguinTutor on YouTube](https://www.youtube.com/c/PenguinTutor) or [@PenguinTutor on Twitter](https://twitter.com/penguintutor)


## Install

To compile from source first needs the [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix).

Extract the rpi-rgb-led-matrix files
eg.
/home/pi/rpi-rgb-led-matrix
configure and compile the demo programs and check that they are working correctly.

Extract these files into a directory in the home directory
/home/pi/matrix-display-images

change to that directory and run
`make`

If the directories are different from those listed above then you may need to update the Makefile with the path to the matrix libraries

You can now copy the matrix-display-images executable to a convenient place if required.

test using
`sudo ./matrix-display-images -f filename.png`

which will display a single image. Press enter to exit.


## Running in Server mode

The default is for the program to run in server mode. In this mode the configuration file `display-images.cfg` is read which is used to determine the images to display. To change the image then the file should be modified and will be reloaded after displaying each image. By changing the directory then the server can change the images that are displayed. This is similar to the -d (directory) mode, but with the ability to change the directory through the config file whilst the program continues to run.

The file is display-images.cfg. It has the following options which should be each on their own line with = between the parameter and value. There should be no spaces.

Parameter            | Value
:---------------     | :-----------------
display              | true or false (whether to display image - default true)
directory            | Directory containing image files
prefix               | Prefix for image files, followed by ????.png where ???? is a zero padded number starting with 1.
position             | Number of image to display (if not included continue at current image or start at 1).
delay								 | Delay between images in milliseconds


When running in server mode then the following command line options are ignored (-f, -d, -D, -m, -p) and instead should be included in the configuration file.


To start this automatically as a daemon follow the following instructions 

```bash
sudo cp /home/pi/matrix-display-images/matrix-display-images.service /etc/systemd/system
sudo chown root:root /etc/systemd/system/matrix-display-images.service
sudo systemctl enable matrix-display-images.service
sudo systemctl start matrix-display-images.service
```

A common way to run in server mode is using matrix-messages. See the README.md file in that directory for information on setting that up.



## Command line options

By default the program will run in server mode. These are the standard options for the matrix-display-images program.


Flag                  | Description
:---------------      | :-----------------
`-c`                  | Config file for server mode
`-f`                  | Filename for displaying a single image file
`-d`                  | Directory name for displaying series of files (repeat)
`-D`                  | Directory name for displaying series of files (no repeat)
`-p`                  | Prefix for image files (directory listings only)
`-m`                  | Delay between showing each image in directory (milliseconds)
`-v`                  | Basic verbose mode
`-V`                  | Full verbose mode (debug)



In addition to the options listed above the program also supports the standard command line options from [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix) demonstration programs. These will work with all modes.

For example the following can be used to change the number of rows and columns on the display:

Flag                                | Description
:---------------      | :-----------------
`--led-cols`          | Columns in the LED matrix, the 'width'.
`--led-rows`          | Rows in the LED matrix, the 'height'.
`--led-multiplexing`  | In particular bright outdoor panels with small multiplex ratios require this. Often an indicator: if there are fewer address lines than expected: ABC (instead of ABCD) for 32 high panels and ABCD (instead of ABCDE) for 64 high panels.
`--led-row-addr-type` | Adressing of rows; in particular panels with only AB address lines might indicate that this is needed.
`--led-panel-type`    | Chipset of the panel. In particular if it doesn't light up at all, you might need to play with this option because it indicates that the panel requires a particular initialization sequence.


## Limitations / Issues

The program uses significant processing time. If run on a Raspberry Pi Zero or similar then it is recommended that it is run as a headless computer without X running.

The display is designed for 8bpc RGB, non-interlaced images with no transparency. If images have interlacing then it will issue a warning
"libpng warning: Interlace handling should be turned on when using png_read_image". These files should be converted to non-interlaced png images.

The image files can be fixed by using GIMP if neccessary.

In some circumstances the Ctrl-C does not cancel the program. In that case Ctrl-Z can be used and then the program can be stopped using `kill`.

There is limited error handling for the configuration file. It is designed for the configuration file to be created through code (eg. using matrix-message) so that there should be less risk of errors


*** Bug any parameters not specified will retain their previous value - needs to reset to defaults ***

## More Information

For more information see my website at: [PenguinTutor RGB LED Matrix display](http://www.penguintutor.com/projects/rpi-matrix-rgbled)
