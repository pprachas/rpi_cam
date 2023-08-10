import cv2
import time
import utils.camera_controls as cam

import os


# open video0
cap = cam.init_camera()
focus_value=272
os.system(f'v4l2-ctl -d 0 -c focus_absolute={focus_value}')

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows() 