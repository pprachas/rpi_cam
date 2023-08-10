import cv2
import time
import os
from pathlib import Path

import utils.camera_controls as cam

# Create directory to save folder if it doesn't exist
Path('./images').mkdir(parents=True, exist_ok=True)
# Initize camera
cap = cam.init_camera(width = 1280,height= 720)



# Get frame before focus
ret, frame = cap.read()
cv2.imwrite('images/prefocus.png',frame)

# Run autofocus routine
cam.autofocus(cap)

# Get frame after focus
ret, frame = cap.read()
cv2.imwrite('images/postfocus.png',frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()