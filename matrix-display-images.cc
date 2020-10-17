/* Image display for the LED Matrix display */
/* See http://www.penguintutor.com */

#include "led-matrix.h"

#include <unistd.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/stat.h>
#include <stdbool.h>
#include <png.h>
#include <zlib.h>

#define PNG_ERROR -2
#define NOT_PNG -1
#define PNG_OK 0


/* Can show single file and wait for key press
 * Show a directory one and wait for key press
 * Show a directory on repeat (Ctrl-C to exit)
 * Run server mode looking for config file for which
 * files to display
*/
#define DEFAULT_MODE	0 		// becomes server mode
#define SINGLE_IMG 1
#define DIRECTORY_ONCE 2
#define DIRECTORY_RPT 3
#define SERVER_MODE 4


using rgb_matrix::GPIO;
using rgb_matrix::RGBMatrix;
using rgb_matrix::Canvas;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}


/* Loads a png image and displays on canvas */
// Image should be at least size of display. If oversized then just displays top left of image
int displayPng(Canvas *canvas, const char *file_name) /* We need to open the file */
{
   png_structp png_ptr;
   png_infop info_ptr;
   png_uint_32 width, height;
   int bit_depth, color_type, interlace_type;
	 unsigned int row;
   FILE *fp;

   if ((fp = fopen(file_name, "rb")) == NULL)
      return (PNG_ERROR);

	// Fill if background needed
  //canvas->Fill(0, 0, 255);


	 png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

   if (png_ptr == NULL)
   {
      fclose(fp);
      return (PNG_ERROR);
   }

   /* Allocate/initialize the memory for image information.  REQUIRED. */
   info_ptr = png_create_info_struct(png_ptr);
   if (info_ptr == NULL)
   {
      fclose(fp);
      png_destroy_read_struct(&png_ptr, NULL, NULL);
      return (PNG_ERROR);
   }

   /* Set error handling if you are using the setjmp/longjmp method (this is
    * the normal method of doing things with libpng).  REQUIRED unless you
    * set up your own error handlers in the png_create_read_struct() earlier.
    */
   if (setjmp(png_jmpbuf(png_ptr)))
   {
      /* Free all of the memory associated with the png_ptr and info_ptr. */
      png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
      fclose(fp);
      /* If we get here, we had a problem reading the file. */
      return (PNG_ERROR);
   }

   /* Set up the input control if you are using standard C streams. */
   png_init_io(png_ptr, fp);


   /* The call to png_read_info() gives us all of the information from the
    * PNG file before the first IDAT (image data chunk).  REQUIRED.
    */
   png_read_info(png_ptr, info_ptr);

   png_get_IHDR(png_ptr, info_ptr, &width, &height, &bit_depth, &color_type,
       &interlace_type, NULL, NULL);

   /* Tell libpng to strip 16 bits/color files down to 8 bits/color.
    * Use accurate scaling if it's available, otherwise just chop off the
    * low byte.
    */
   png_set_scale_16(png_ptr);
	 png_set_packing(png_ptr);

	 /* Expand paletted colors into true RGB triplets. */
   if (color_type == PNG_COLOR_TYPE_PALETTE)
      png_set_palette_to_rgb(png_ptr);
   if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
      png_set_expand_gray_1_2_4_to_8(png_ptr);


   png_read_update_info(png_ptr, info_ptr);

   /* Allocate the memory to hold the image using the fields of info_ptr. */
   png_bytep row_pointers[height];
   for (row = 0; row < height; row++)
      row_pointers[row] = NULL; /* Clear the pointer array */
   for (row = 0; row < height; row++)
      row_pointers[row] = (png_bytep) png_malloc(png_ptr, png_get_rowbytes(png_ptr,
          info_ptr));

		/* Read the entire image in one go */
   png_read_image(png_ptr, row_pointers);

	 /* Read rest of file, and get additional chunks in info_ptr.  REQUIRED. */
   png_read_end(png_ptr, info_ptr);

/* Display Image Here */

// Return if width or height is less than canvas
int num_rows = canvas->height();
int num_cols = canvas->width();
if (height < (unsigned int)num_rows) num_rows = height;
if (width < (unsigned int)num_cols) num_cols = width;

 for (int i = 0; i < num_rows; i++) {
        for (int j = 0; j < num_cols; j ++ ) {
						canvas->SetPixel(j, i, row_pointers[i][j*3], row_pointers[i][j*3+1], row_pointers[i][j*3+2]);
        }
    }

   /* Clean up after the read, and free any memory allocated.  REQUIRED. */
   png_destroy_read_struct(&png_ptr, &info_ptr, NULL);

   /* Close the file. */
   fclose(fp);

   return (PNG_OK);
}

static int usage(const char *progname) {
  fprintf(stderr, "usage: %s <options> [optional parameter]\n",
          progname);
  fprintf(stderr, "Options:\n");

  rgb_matrix::PrintMatrixFlags(stderr);

  fprintf(stderr, "Display images\n");
  fprintf(stderr, "\t-f filename - display individual file\n"
          "\t-d directory - display directory images (-p prefix) (-m ms-delay)\n"
          "\t-D directory - display directory only once\n"
          "\t-c configfile - server mode\n");
  fprintf(stderr, "Example:\n\t%s -f image01.png\n"
          "Shows one image until enter pressed\n", progname);
  return 1;
}


// works out filename from parts and updates path, then return -1 if not exist
// 1 if file exists
bool checkFileExist (char *full_path, char *directory, char *prefix, int count) {
	// if already got / on end of directory don't add another one, otherwise add one
	char slash[2] = "/";
	struct stat buffer;
	// If already ends with / then set to an empty string
	if (directory[strlen(directory)-1] == '/'){
	 slash[0] = '\0';
	 }
	sprintf (full_path, "%s%s%s%04d.png",directory, slash, prefix, count);

  return (stat (full_path, &buffer) == 0);
	}


int main(int argc, char *argv[]) {
  RGBMatrix::Options defaults;
  defaults.hardware_mapping = "regular";  // or e.g. "adafruit-hat"
	defaults.cols = 64;
  defaults.rows = 32;
  defaults.chain_length = 1;
  defaults.parallel = 1;
  defaults.show_refresh_rate = false;
	rgb_matrix::RuntimeOptions runtime_opt;
	char full_path[200];
  //Canvas *canvas = rgb_matrix::CreateMatrixFromFlags(&argc, &argv, &defaults);
	int mode = DEFAULT_MODE;
	char prefix[20] = "";
	char directory [150] = "";
	char *configfile, *filename;
	// Default = 1sec delay between images
	int ms_delay = 1000;
	// position of image to show
	int img_number = 1;
	int success;


  // Extract the command line flags that contain
  // relevant matrix options.
  if (!ParseOptionsFromFlags(&argc, &argv, &defaults, &runtime_opt)) {
    return usage(argv[0]);
  }


  // It is always good to set up a signal handler to cleanly exit when we
  // receive a CTRL-C for instance. The DrawOnCanvas() routine is looking
  // for that.
  signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);


  int opt;
	// Only one of these can be used at a time
	// c = config file, d = directory_rpt, -D = directory_one, f = filename
	// -p = prefix (directory and server only)
	// config = servermode
	// -m = ms delay between images
	while ((opt = getopt(argc, argv, "c:d:D:f:m:p:")) != -1){
    switch (opt) {
			case 'c':
				mode = SERVER_MODE;
				configfile = optarg;
				break;
			case 'f':
				if (mode != SERVER_MODE) mode = SINGLE_IMG;
				filename = optarg;
				break;
			case 'd':
			  if (mode != SERVER_MODE) mode = DIRECTORY_RPT;
				strcpy (directory, optarg);
				break;
			case 'D':
			  if (mode != SERVER_MODE) mode = DIRECTORY_ONCE;
				strcpy (directory, optarg);
				break;
			case 'p':
				strcpy (prefix, optarg);
				break;
			case 'm':
				ms_delay = atoi(optarg);
				break;

		}
	}

  RGBMatrix *matrix = CreateMatrixFromOptions(defaults, runtime_opt);
  if (matrix == NULL)
    return 1;

	Canvas *canvas = matrix;
  if (canvas == NULL)
    return 1;


  // Default is server mode
	if (mode == DEFAULT_MODE) mode = SERVER_MODE;


	// Single file
	if (mode == SINGLE_IMG) {

		printf ("Displaying single image %s\n", filename);

	  success = displayPng(canvas, filename);
		if (success != PNG_OK) printf ("Error displaying file %s\n", filename);
		// Allow press any key
		getchar();
	}

	// Directory is the same, but breaks out if once
	if (mode == DIRECTORY_RPT || mode == DIRECTORY_ONCE){

	while (1) {

		// If no file then go back to zero and try again
		if (!checkFileExist (full_path, directory, prefix, img_number)) {
			// Unless this is one time only in which case exit here
			if (mode == DIRECTORY_ONCE) {exit(0);}
			img_number = 1;
			// generate filename - if initial file doesn't exist then exit
			if (!checkFileExist (full_path, directory, prefix, img_number)) {
				printf ("File %s not found\n", full_path);
				exit(0);
			}
		}
		// Display the file
		success = displayPng(canvas, full_path);
		// This error is a warning - only exit on file 0 not found
		if (success != PNG_OK) printf ("Error displaying file %s\n", full_path);

		// Increment the count
		img_number ++;
		// Wait for delay ms before showing next image
		usleep (ms_delay * 1000);

	}
	}

  // Animation finished. Shut down the RGB matrix.
  delete canvas;

  return 0;
}