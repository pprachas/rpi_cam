import cv2
import os
import time

'''
This python file contains functions for camera operations using v4l2 and opencv
'''

def init_camera(channel = 0, width = 800, height = 600):
    '''
    This function initializes the camera with specific camera frame size. Note that the
    API backend is v4l2
    Args:
        channel: video channel
        width: width of frame
        height: height of frame
    Returns:
        cap: OpenCV camera object
    
    '''
    cap = cv2.VideoCapture(channel, apiPreference=cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    return cap

def autofocus(cap):
    '''
    Use Arducam autofocus mode to autofocus and freeze the focus value after autofocus routine
    Args:
        cap: OpenCV camera object
    '''
    # Autofocus mode:
    os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=1')
    # Set a 5 seconds timer to autofocus
    t_end = time.time() + 5

    # Image before focus:
    ret, frame = cap.read()

    while time.time() < t_end:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Print focus
        os.system('v4l2-ctl -d 0 -C focus_absolute')

    # Lock in focus value:
    os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=0')
    print('Final Focus value:')
    os.system('v4l2-ctl -d 0 -C focus_absolute')
    print('Camera now focused!')
