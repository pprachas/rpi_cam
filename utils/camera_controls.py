import cv2
import os
import time
import numpy as np


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
    cap = cv2.VideoCapture(channel, cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap
     
def calibrate(rows =8, columns =6):
    pattern_size = (rows,columns)
    # Define object points (3D cords)
    objp = np.zeros((np.prod(pattern_size),3), np.float32)
    objp[:,:2] = np.mgrid[0:pattern_size[0],0:pattern_size[1]].T.reshape(-1,2)

    #Images used for calibration
    images = os.listdir('/home/pi/Desktop/rpi_cam/camera_only_script/calibration_images')

    #Create empty arrays to store results
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    for fname in images:
        img = cv2.imread(f'/home/pi/Desktop/rpi_cam/camera_only_script/calibration_images/{fname}')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #Find corners for each image
        found, corners = cv2.findChessboardCorners(gray, pattern_size, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)

        #If corners  are found then add to array
        if found:
            #Sub Pixel corners
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
            corners2 = cv2.cornerSubPix(gray, corners, (13, 13), (-1, -1), criteria)

            imgpoints.append(corners2)
            objpoints.append(objp)

        
    #Use results to find camerea_matrix and distorion_coefficents   
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


    return objp, mtx, dist

def find_angles(image,objp,mtx,dist,rows =8, columns =6):
    # Define the dimensions of the checkerboard
    pattern_size = (rows, columns)
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    # Find the corners of the checkerboard
    ret, corners = cv2.findChessboardCorners(image, pattern_size)
    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
        cv2.cornerSubPix(gray, corners, (13, 13), (-1, -1), criteria)
        # Estimate the pose of the checkerboard
        _, rvec, tvec = cv2.solvePnP(objp, corners, mtx, dist)

        # Convert the rotation vector to a rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rvec)

        yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        pitch = np.arctan2(-rotation_matrix[2, 0], np.sqrt(rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))
        roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])

        # Convert the angles from radians to degrees
        yaw_deg = np.degrees(yaw)
        pitch_deg = np.degrees(pitch)
        roll_deg = np.degrees(roll)

        # Print the rotation angles (in degrees)
        print('Rotation angles (degrees):')
        print('Yaw:', yaw_deg)
        print('Pitch:', pitch_deg)
        print('Roll:', roll_deg)

def is_blurry(img):

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply Laplacian operator
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    return laplacian_var

def auto_sqaure(img):
    #blur image
    blur = cv2.GaussianBlur(img, (5, 5), 0)

    #find edges
    edges = cv2.Canny(blur,100,200)

    #find coords for edges
    white = np.where(edges != [0])

    #find leftmost and rightmost edge coords
    x1 = np.min(white[1]) - 50
    x2 = np.max(white[1]) + 50

    return x1, x2

def mask_img(img, num_holes = 0):

    # Create blank image to draw mask
    blank = np.zeros_like(img)


    #Apply filters to image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #blur = cv2.GaussianBlur(gray,(19,19),0)
    blur = cv2.bilateralFilter(gray,17,75,75)
    ret, thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Close small holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # If there are no inner holes in specimen
    if num_holes == 0:
        # Find all outer contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Ensure that conours exist within image
        if contours:
            # Take largest contour and fill in on blank image
            outer_contour = max(contours, key=cv2.contourArea)
            cv2.fillPoly(blank, pts=[outer_contour], color=(255, 255, 255))
            largest_area = cv2.contourArea(outer_contour)

    # If there are any inner holes 
    else:

        #Find contours and obtain hierarchy information
        contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        areas = []

        #Esnure that contours exist within image
        if contours:
            
            #loop through contours and hierarchy 
            for i, h in enumerate(hierarchy[0]):
                contour = contours[i]
                
                #Check to see if is outer contour
                if h[3] ==  -1:
                    #if has children than draw on blank image in white
                    if h[2] != -1:
                        cv2.fillPoly(blank, pts=[contour], color=(255, 255, 255))

                    #Do not want outer contours in list
                    continue

                #Find area and append to list
                area = cv2.contourArea(contour)
                areas.append([i,area])

            # Esnure that given holes does not exceed number of holes found
            if num_holes > len(areas):
                num_holes = len(areas)

            # Sort by size in descending order
            areas = np.array(areas)
            sorted = np.argsort(areas[:, 1])[::-1]
            sorted_areas = areas[sorted]

            #Loop through sorted array based on number of given holes
            for i in range(num_holes):
                #Fill holes with black on blank image
                idx = int(sorted_areas[i][0])
                contour = contours[idx]
                cv2.fillPoly(blank, pts=[contour], color=(0, 0, 0))
        
    #Return final mask image    
    return blank

def find_focus(cap): 

    os.system('v4l2-ctl -d 0 -c white_balance_automatic=1')
    os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=1')
    os.system('v4l2-ctl -d 0 -c focus_automatic_continuous=0')
    #Capture image and select area of subject
    ret, frame = cap.read()

    x1, x2 = auto_sqaure(frame)
    y1 = 400
    y2 = 800

    #Define area of object trtying to focus
    new_frame  = frame[y1:y2,x1:x2]

    #Define starting focus value
    focus_value = 0
    best_blur = 0

    # Cycle through foucs values going by 10s
    while focus_value < 500:

        for i in range(3):
            ret, frame = cap.read()
            new_frame  = frame[y1:y2,x1:x2]
            blur_value = is_blurry(new_frame)

        #Set focus to specifc value and print
        os.system(f'v4l2-ctl -d 0 -c focus_absolute={focus_value}')

        #Capture frame at focus value
        ret, frame = cap.read()
        new_frame  = frame[y1:y2,x1:x2]

        #Determine blur and print
        blur_value = is_blurry(new_frame)
        print(focus_value, blur_value)

        if blur_value > best_blur:
            best_blur = blur_value
            best_focus = focus_value

        if blur_value < best_blur - 1000:
            break
        #Increase focus value
        focus_value += 10

        
    #Set focus value to 10 below best focus 
    focus_value = best_focus -10
    upper_focus = best_focus + 10

    # Set focus to focus value
    os.system(f'v4l2-ctl -d 0 -c focus_absolute={focus_value}')

    #Allow camera adjust by grabbbing images
    for i in range(5):

        ret, frame = cap.read()
        new_frame  = frame[y1:y2,x1:x2]
        blur_value = is_blurry(new_frame)

    best_blur = 0
    #Cycle through focus values 10 above and below best focus value by 1s
    while focus_value <= upper_focus:

        #Set focus value and print
        os.system(f'v4l2-ctl -d 0 -c focus_absolute={focus_value}')

        #Capture frame at focus value
        ret, frame = cap.read()
        new_frame  = frame[y1:y2,x1:x2]

        # Determine blur and print
        blur_value = is_blurry(new_frame)
        print(focus_value, blur_value)

        # Check to see if blur is better 
        if  blur_value > best_blur:
            best_blur = blur_value
            best_focus = focus_value

            
        # Increase focus value
        focus_value += 1


    print(f'The best focus is: {best_focus}')
    print(f'Laplacian Varaince is: {best_blur}')

    return best_focus

def rectangle(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray,9,75,75)
    ret, thresh = cv2.threshold(blur,30,255,cv2.THRESH_BINARY)

    # Close small holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find all outer contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contour_parents = []
    # Ensure that conours exist within image
    if contours:
        for i, contour in enumerate(contours):
            if hierarchy[0][i][2] != -1:
                contour_parents.append(contour) 
        if contour_parents:
            outer_contour = max(contour_parents, key=cv2.contourArea)
            min_area_rect = cv2.minAreaRect(outer_contour)
            box = cv2.boxPoints(min_area_rect)
            box = box.astype(int)
            cv2.drawContours(img, [box], 0, (255, 0, 0), 2)

            angle = min_area_rect[2]
            print(angle)
    
            x, y, w, h = cv2.boundingRect(outer_contour)

            # Draw the non-rotated bounding box around the contour
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            area_non_rotated= w*h
            area_rotated = cv2.contourArea(box)
            cv2.putText(img,str(area_non_rotated),(60,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            cv2.putText(img,str(area_rotated),(60,80),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)

    return img
