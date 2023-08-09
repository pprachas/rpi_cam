<!--Hello -->

# DIC Pipleine

This repository contains code that is able to control an Arducam camera with the Raspberry Pi as well as GPIO output signals on start the Instron and camera at the same time. The Raspberry Pi can be thought as its own small computer with a Linux based OS. One of the methods to access the Raspberry Pi itself after setup is through ssh. Note that the code in the raspberry pi can be committed to this repository.

### More information on DIC can be found here:
1. [Good Practices Guide For DIC](https://idics.org/guide/)
2. [NCORR - Open Source 2D DIC Software](http://www.ncorr.com/)
3. [DuoDIC: 3D Digital Image Correlation in MATLAB](https://joss.theoj.org/papers/10.21105/joss.04279)
4. [Evaluating Spekle Quality using Glare](https://www.sciencedirect.com/science/article/pii/S0143816621002360)

## Table of Contents
- [DIC Pipleine](#dic-pipleine)
    - [More information on DIC can be found here:](#more-information-on-dic-can-be-found-here)
  - [Table of Contents](#table-of-contents)
  - [Contents in This Repository](#contents-in-this-repository)
  - [Dependencies](#dependencies)
  - [Project Summary](#project-summary)
    - [Checkerboard Calibration](#checkerboard-calibration)
    - [Minimum Area Rectangle](#minimum-area-rectangle)
    - [Masking](#masking)
  - [V4L2](#v4l2)


## Contents in This Repository

| Folder| Contents of the folder|
|-------|--------|
|[camera_only_script](camera_only_script)| scripts in this folder only run manipulate the camera.|
|[gpio_only_script](gpio_only_script)| scripts in this folder only sends GPIO outputs |
|[utils](utils) | All the functions that are used in this repo. | 

## Dependencies 
The code in this repository is written using python and relies on the OpenCV library. 

## Project Summary

This pipeline is designed to calibrate the camera before DIC and take images durning the defomration of the specimen. It will also create a mask of the intial image which can then be used in a software like Ncorr to run DIC. 

### Checkerboard Calibration

Running the file will start by alloywing you to aligning the camera to the subject by placing a cherckerboard pattern in the Instron. The number of rows and columns in the checkerboard should be specifed when calling the function (the defualt is 8x6 but any number will work). 

The function displays the video and also prints out the rotation vector labeled as roll, pitch, and yaw. Rotation around the front-to-back axis is called roll. Rotation around the side-to-side axis is called pitch. Rotation around the vertical axis is called yaw. See the diagram below for further clarifcation.

**In order to get accurate results, you need to have calibration images of the checkboard taken using the same camera. These images should be stored on the pi so that they can be used to obtain distortion coefficents and the camera matrix.**

Ideally, the angles for row, pitch, and yaw should be zero or as close to zero as possible in order to reduce out of plane motion during DIC. Once the camera is alligned, it should be locked in place in order to prevent any more movement. 

![alt text](https://automaticaddison.com/wp-content/uploads/2020/03/yaw_pitch_rollJPG.jpg)

### Minimum Area Rectangle

After aligned the camera, replace the checkerboard with the acutal DIC subject in the instron. In order to esnure the that the subject is perfectly vertical, the script will find the orientation of the subject and print out the angle. 

### Masking 

The inital image captured by the camera before the instrong begins streching the subject will be automacially masked and saved to the pi. Images will be taken overy the period of 10 seconds which can be modifyied within the code and also saved to the pi. 

It is best to use a black background and to ensure that there no other objects in the final image other than the DIC specimen itself and the instron to ensure the highest quality mask. 


## V4L2

The code uses v4l2 to control the camera. List of useful controls can be foud [here](https://manpages.ubuntu.com/manpages/bionic/man1/v4l2-ctl.1.html):
https://manpages.ubuntu.com/manpages/bionic/man1/v4l2-ctl.1.html

