# remarkable-file-mover

A few scripts to process an image for a reMarkable tablet sleep screen, and push it to the device via ssh. Currently this only updates the sleep screen.

The functionality is set up to work with the resolution of the reMarkable Paper Pro. I can add the resolutions for the reMarkable 2 if requested.

## Installation

To install the environment needed to run these scripts, follow the directions below. In a terminal, run the commands shown. You will need to have python installed and git.

Linux:
- Will be added soon

Windows:
```bash
git clone https://github.com/rasbot/remarkable-file-mover.git
cd remarkable-file-mover
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Install PuTTY

This specific implementation uses PuTTY to SSH into the reMarkable device. Go to: [https://www.putty.org/](https://www.putty.org/) and download the install file and run it.

### Create a config txt file

In the root directory of the repo, add a new text file and rename it to `remarkable_config.txt`. This file will be hidden (greyed out) since it was added to `.gitignore`, and since this will contain your login info for the reMarkable, keep in mind of this and do not share your PASSWORD.

In the text file, you will need to define some parameters:
```
REMARKABLE_IP=*********
REMARKABLE_PASSWORD=*******
SOURCE_PATH=<path_to_your_image_to_upload>\suspended.png
DESTINATION_DIR=/usr/share/remarkable
PUTTY_PATH=C:\Program Files\PuTTY
DESTINATION_FILE=suspended.png
```
The IP and PASSWORD for your reMarkable can be found by following the directions here [https://remarkable.guide/guide/access/ssh.html](https://remarkable.guide/guide/access/ssh.html)

The `SOURCE_PATH` will be the full path to the final image you want to upload using the bat script. For instance, "C:\Users\ongo\Pictures\suspended.png"

__Note:__ For Windows paths, you need to use "\". For Linux paths, you need to use "/". The `SOURCE_PATH` and `PUTTY_PATH` here are Windows paths, whereas the `DESTINATION_DIR` path is on the reMarkable device, which is Linux.

The `DESTINATION_PATH` and `DESTINATION_FILE` do not need to be updated, as this will only change the sleep screen.

`PUTTY_PATH` is the path to the directory that the PuTTY executable file lives in. The path provided was the default installation path when I installed it.

## Usage

> If you don't want to read all of this, you can run 2 scripts to prepare an image and move it to the reMarkable. `src/process_and_move.py` and `push_to_device.bat`. The information here covers multiple scripts so just read on those 2 mentioned scripts if needed.

There are 3 parts to the scripts. These are:
- Process an image so it is ready to be loaded onto the reMarkable (crop / resize / add optional border)
- Copy / rename the image file to a source destination that will be used to push it to the reMarkable device
- A batch script that pushes the image file to the reMarkable device via SSH

To do the image processing and move the image file, run the `src/process_and_move.py` script. This runs the `src/process_image.py` script that processes the image, and the `src/move_file.py` script that copies / renames the image to a source destination.

### Image processing

Running `src/process_image.py` will do the following:

- crop it to the aspect ratio of the reMarkable tablet
- resize the image to the resolution of the reMarkable tablet
- can add a white border around the image if you want

In the terminal, run
```bash
$ python .\src\process_image.py --help
```
to see the list of command line args you can use.

The args are:
- `--source`, `-s`: The full path to the image. In Windows, you can copy this from Windows explorer by right clicking on an image and selecting "Copy as path", or by using "Ctrl + Shift + c". (ex: `-s "C:\Users\ongo\Pictures\my_image.png"`)
- `--width`, `-w`: Target width of the image (width of the reMarkable screen in pixels, defaults to 1620). (ex: `-w 1200`)
- `--height`, `-h`: Target height of the image (height of the reMarkable screen in pixels, defaults to 2160). (ex: `-h 1920`)
- `--position`, `-p`: Position to anchor to when cropping the image. (ex: `-p left`) Options are:
  - "center": Crops height / width from the center of the image.
  - "left": Crops height / width from the left of the image.
  - "right": Crops height / width from the right of the image.
  - "top": Crops height / width from the top of the image.
  - "bottom": Crops height / width from the bottom of the image.
- `--border`, '`-b`: Add a border to the image. This is a flag and if passed will add a default border of 30 pixels (ex: `-b`) or can pass a border thickness (ex: `-b 50`).

#### Image Comparison

<p align="center">
  <img src="images/ongo.png" alt="Original Image" height="400">
  <br>
  <b>Original Image</b>
</p>

<table>
  <tr>
    <td align="center">
      <img src="images/ongo_processed_center.png" alt="Center Cropped Image" height="400"><br>
      <b>Center Cropped Image</b>
    </td>
    <td align="center">
      <img src="images/ongo_processed_left.png" alt="Left Cropped Image" height="400" width=auto><br>
      <b>Left Cropped Image</b>
    </td>
    <td align="center">
      <img src="images/ongo_processed_right.png" alt="Right Cropped Image" height="400"><br>
      <b>Right Cropped Image</b>
    </td>
  </tr>
</table>

<p align="center">
  <img src="images/ongo_processed_border.png" alt="Cropped Image with Border" height="400">
  <br>
  <b>Cropped Image with Border</b>
</p>

#### Example usage

```bash
$ python .\src\process_image.py -s "C:\Users\ongo\Pictures\my_image.png" -p right -b 45
```
will crop the image with respect to the right of the image and add a 45 pixel border around the image.

### Copy / rename the file / move to specific location

Running `src/move_file.py` will do the following:
- moves / renames the file to a target destination

__Note__: In the config file, you defined a target destination like this:
> SOURCE_PATH=C:\Users\Azathoth\Pictures\suspended.png
An image file you are moving will be copied to this location and renamed to `suspended.png`.

In the terminal, run
```bash
$ python .\src\move_file.py --help
```
to see the list of command line args you can use.

The args are:
- `--source`, `-s`: The full path to the image. In Windows, you can copy this from Windows explorer by right clicking on an image and selecting "Copy as path", or by using "Ctrl + Shift + c".
- `--overwrite`, `-o`: Pass this flag if there is a processed image that you want to overwrite. Without this flag the script will raise an exception and not overwrite the image.

#### Example usage
```bash
$ python .\src\move_file.py -s "C:\Users\ongo\Pictures\my_image_processed.png" -o
```
will move the file at that location to the target destination (defined in the config file) and will overwrite an image if one exists at the destination. Remove `-o` if you do not want to overwrite a file.

### Process image and move

To do the image processing and move the image file, run the `src/process_and_move.py` script. This runs the `src/process_image.py` script that processes the image, and the `src/move_file.py` script that copies / renames the image to a source destination.

__Note__: In the config file, you defined a target destination like this:
> SOURCE_PATH=C:\Users\Azathoth\Pictures\suspended.png
An image file you are moving will be copied to this location and renamed to `suspended.png`.

In the terminal, run
```bash
$ python .\src\process_and_move.py --help
```
to see the list of command line args you can use.

The args are:
- `--source`, `-s`: The full path to the image. In Windows, you can copy this from Windows explorer by right clicking on an image and selecting "Copy as path", or by using "Ctrl + Shift + c".
- `--width`, `-w`: Target width of the image (width of the reMarkable screen in pixels, defaults to 1620)
- `--height`, `-h`: Target height of the image (height of the reMarkable screen in pixels, defaults to 2160)
- `--position`, `-p`: Position to anchor to when cropping the image. Options are:
  - "center": Crops height / width from the center of the image.
  - "left": Crops height / width from the left of the image.
  - "right": Crops height / width from the right of the image.
  - "top": Crops height / width from the top of the image.
  - "bottom": Crops height / width from the bottom of the image.
- `--border`, '`-b`: Add a border with the specified width in pixels (example: 40)
- `--overwrite`, `-o`: Pass this flag if there is a processed image that you want to overwrite. Without this flag the script will raise an exception and not overwrite the image.

#### Example usage

```bash
$ python .\src\process_and_move.py -s "C:\Users\ongo\Pictures\my_image.png" -p left -o
```
will process the source image and crop it with respect to the left of the image, and overwrite an image in the target destination if one exists.

### Pushing the image to the reMarkable

Make sure you have an image in the path defined in the config file

example:

> SOURCE_PATH=C:\Users\Azathoth\Pictures\suspended.png

Connect the reMarkable via a USB cable and make sure it is not sleeping. Now, in the terminal, run:

```bash
$ .\src\push_to_device.bat
```
and if everything is set up correctly, you should see the file being pushed in the terminal, and see "-----PROGRAM FINISHED-----" when it is done.

## Issues

If pushing the file to the reMarkable does not work in the root directory of the repo, you can try navigating to the `src` directory and running it:

```bash
$ cd src
$ push_to_device.bat
```

If you cannot connect to the reMarkable, make sure you have the right IP address. On my device I can see `192.168...` which is not the correct IP address. The `10.11...` or something similar is the correct IP address.

## Next steps

Currently this is set up for the reMarkable Paper Pro. I will add resolutions for the reMarkable 2 soon, or if requested.
