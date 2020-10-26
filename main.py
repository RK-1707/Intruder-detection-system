# Import the required libraries
import numpy as np
import cv2
import time
import datetime
from collections import deque
from twilio.rest import Client

#Function for sending message via Twilio
def send_message(body, info_dict):

    # Your Account ROHAN from twilio.com/console
    account_rohan = info_dict['account_rohan']

    # Your Auth Token from twilio.com/console
    auth_token  = info_dict['auth_token']


    client = Client(account_rohan, auth_token)

    message = client.messages.create( to = info_dict['99228606##'], from_ = info_dict['Application'], body= body)
    
#Function for detecting if a person is present
def is_person_present(frame, thresh=1100):
    global foog
    
    # Apply background subtraction
    fgmask = foog.apply(frame)

    # Removing shadows
    ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)

    # Apply dilation to increase the area of moving object
    fgmask = cv2.dilate(fgmask,kernel,iterations = 4)

    # Detect contours in the frame
    contours, hierarchy = cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
     
    # Check if there was a person and not noise
    if contours and cv2.contourArea(max(contours, key = cv2.contourArea)) > thresh:
            
            # Get the max contour
            cnt = max(contours, key = cv2.contourArea)

            # Draw a bounding box around the person and label it as person detected
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame,(x ,y),(x+w,y+h),(0,0,255),2)
            cv2.putText(frame,'Intruder Detected',(x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1, cv2.LINE_AA)
            
            return True, frame
        
    else:
        return False, frame

# Set Window normal so we can resize it
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

# Capture video and input it to application
cap = cv2.VideoCapture('http://192.168.18.4:6067/video')

# Get width and height of the frame
width = int(cap.get(3))
height = int(cap.get(4))

# Read and store the credentials information in a dict
with open('credentials.txt', 'r') as myfile:
  data = myfile.read()

info_dict = eval(data)

# Initialize the background Subtractor
foog = cv2.createBackgroundSubtractorMOG2( detectShadows = True, varThreshold = 100, history = 2000)
status = False
patience = 7
detection_thresh = 15
initial_time = None
de = deque([False] * detection_thresh, maxlen=detection_thresh)
fps = 0 
frame_counter = 0
start_time = time.time()

while(True):
    ret, frame = cap.read()
    if not ret:
        break 
            
    # This function will return a boolean variable telling if someone was present or not, it will also draw boxes if it finds someone
    detected, annotated_image = is_person_present(frame)  
    
    # Register the current detection status on our object
    de.appendleft(detected)
     
    # If we have consecutively detected a person 15 times then we are sure that someone is present
    if sum(de) == detection_thresh and not status:                       
            status = True
            entry_time = datetime.datetime.now().strftime("%A, %I-%M-%S %p %d %B %Y")
            out = cv2.VideoWriter('outputs/{}.mp4'.format(entry_time), cv2.VideoWriter_fourcc(*'XVID'), 15.0, (width, height))

    # If status is True but the person is not in the current frame
    if status and not detected:
        
        # Restart the patience timer only if the person has not been detected for a few frames so we are sure it wasn't a False positive
        if sum(de) > (detection_thresh/2): 
            
            if initial_time is None:
                initial_time = time.time()
            
        elif initial_time is not None:        
            
            # If the patience has run out and the person is still not detected then set the status to False
            # Also save the video by releasing the video writer and send a text message.
            if  time.time() - initial_time >= patience:
                status = False
                exit_time = datetime.datetime.now().strftime("%A, %I:%M:%S %p %d %B %Y")
                out.release()
                initial_time = None
            
                body = "Alert: \n A Person Entered the Room at {} \n Left the room at {}".format(entry_time, exit_time)
                send_message(body, info_dict)
    
    # If significant amount of detections (more than half of detection_thresh) has occured then we reset the Initial Time.
    elif status and sum(de) > (detection_thresh/2):
        initial_time = None
    
    # Get the current time in the required format
    current_time = datetime.datetime.now().strftime("%A, %I:%M:%S %p %d %B %Y")

    # Show the Frame
    cv2.imshow('frame',frame)
    
    # Calculate the Average FPS
    frame_counter += 1
    fps = (frame_counter / (time.time() - start_time))
    
    # Exit if q is pressed.
    if cv2.waitKey(30) == ord('q'):
        break

# Release Capture and destroy windows
cap.release()
cv2.destroyAllWindows()
out.release()    
