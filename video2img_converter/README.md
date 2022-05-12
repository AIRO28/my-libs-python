# Module name
video2img_converter

# Overview
Cuts out video files stored in the input folder in specified frame units.

# Dependency libraries and packages
```
opencv-python
natsort
```

# How to use
Install dependencies libraries and packages in the execution environment.  

Please store the video files to be converted in the input folder beforehand.  
Video files to be converted should be stored in file units. Do not recurse directories.  


### Convertible Video File Extensions
- mp4, MP4
- mov, MOV

## ・Shell

```shell
# Default 1 fps
$ chmod +x ./convert.sh
$ sh ./convert.sh
```

## ・Python

```python
# python video2img.py <Output FPS>
$ python video2img.py 30
```
