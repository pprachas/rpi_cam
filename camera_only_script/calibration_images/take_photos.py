import cv2
import numpy as np 
import os
import utils.camera_controls as cam

cap = cam.init_camera(width = 800, height = 600)
os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=1')
for i in range(30):
    ret, frame = cap.read()

cv2.imwrite('images/8.png',frame)


cap.release()
cv2.destroyAllWindows()
