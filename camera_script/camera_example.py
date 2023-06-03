import cv2
import time
import os

# open video0
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

# cap.grab()

# cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
# time.sleep(2)
# cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
# time.sleep(2)
# cap.set(cv2.CAP_PROP_FOCUS, 7)


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

# Autofocus mode:
os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=1')
# Time to perform autofocus
t_end = time.time() + 10

# Image before focus:
ret, frame = cap.read()

cv2.imwrite('pre_focus.tiff',frame)

while time.time() < t_end:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Print focus
    os.system('v4l2-ctl -d 0 -C focus_absolute')
    # Display the resulting frame
    cv2.imshow('frame', frame)

# Lock in focus value:
os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=0')

print('Final Focus value:')
os.system('v4l2-ctl -d 0 -C focus_absolute')

ret, frame = cap.read()
# Image after focus and lock
cv2.imwrite('focus.tiff',frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()