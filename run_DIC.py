import cv2
import numpy as numpy
import os 
import utils.camera_controls as cam
import time
import utils.gpio_control as sig
import time

# Intialize Camera
cap = cam.init_camera(width = 800, height = 600)

# Position properly using checkerboard 
os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=1')

#Calibrate camera using images
objp, mtx, dist = cam.calibrate()
print(f'The distortion coefficents are {dist}')

#Ensure in plane using checkerboard calibration
while True:
    # Capture frame from camera
    ret, frame = cap.read()

    #Calculate orientation of chekcerboard
    cam.find_angles(frame,objp,mtx,dist)
    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


#  Switch to DIC sample in Instron now from checkerboard
while True:
    # Capture frame from camera
    ret, frame = cap.read()

    #Calculate angle of DIC sample
    frame  = cam.rectangle(frame)
    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()


# Initilize Camera again at better resolution
cap = cam.init_camera(width = 1920, height = 1080)

for i in range(5):
    ret, frame = cap.read()
# Find best foucs value
focus = cam.find_focus(cap)


#Set focus value and allow camera to stabilize
os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=0')
os.system(f'v4l2-ctl -d 0 -c focus_absolute={focus}')

for i in range(10):
    ret, frame = cap.read()

# Save image and create mask
cv2.imwrite('DIC_imgs/img0.png',frame)
mask = cam.mask_img(frame, num_holes = 0)
cv2.imwrite('DIC_imgs/mask.png',mask)

imgs = []

init_time = time.time()
current_time = time.time()
# send signal
gpio_pin = sig.init_pin(17)
print('Sending Signal:')
sig.send_sig(gpio_pin)

while current_time-init_time < 10:
    ret, frame = cap.read()
    imgs.append(frame)
    current_time = time.time()

for count,img in enumerate(imgs):
    cv2.imwrite(f'DIC_imgs/img{count+1}.png',img)
