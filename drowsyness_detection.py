import cv2
import cvzone
import pandas as pd
import numpy as np
import dlib
from picamera2 import Picamera2
from ultralytics import YOLO
from imutils import face_utils

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#status marking for currrent state
sleep = 0
drowsy = 0
active = 0
status=""
color=(0,0,0)
count=0
def compute(ptA,ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a,b,c,d,e,f):
    up = compute(b,d) + compute(c,e)
    down = compute(a,f)
    ratio = up/(2.0*down)
	
    #Checking if it is blinked
    if(ratio>0.25):
        return 2
    elif(ratio>0.21 and ratio<=0.25):
        return 1
    else:
        return 0

while True:
    frame= picam2.capture_array()

    count += 1
    if count % 3 != 0:
        continue
    #im=cv2.flip(frame,-1)
 
	
    faces = detector(frame)
    #detected face in faces array 
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        print("insice for face")
        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1,y1) , (x2,y2), (0,255,0) ,2)
        landmarks = predictor(frame,face)
        landmarks = face_utils.shape_to_np(landmarks)
        #The number are actually the landmarks which will show eye
        left_blink = blinked(landmarks[36],landmarks[37],landmarks[38],landmarks[41],landmarks[40],landmarks[39])
        right_blink = blinked(landmarks[42],landmarks[43],landmarks[44],landmarks[47],landmarks[46],landmarks[45])
        print(type(left_blink))
        print("left blink",left_blink)
        print("right blink",right_blink)
         #Now judge what to do for the eye blinks
        if(left_blink ==0 or right_blink ==0):
            sleep += 1
            drowsy = 0
            active = 0
            if(sleep>6):
                print("SLeeping....")
                status = "SLEEPING !!!"
                color = (255,0,0)
        elif(left_blink ==1 or right_blink ==1):
            sleep = 0
            active = 0
            drowsy += 1
            if(drowsy>6):
                print("DRowsy....")
                status = "Drowsy !" 
                color=(0,0,255)
        else:
            drowsy = 0
            sleep = 0
            active += 1
            if(active>6):
                print("Active .......")
                status = "Active :"
                color = (0,255,0)
    
        cv2.putText(frame,status,(100,100),cv2.FONT_HERSHEY_SIMPLEX,1.2,color,3)
	
        for n in range(0,68):
            print("inside for")
            (x,y) = landmarks[n]
            cv2.circle(face_frame,(x,y),1,(255,255,255),-1)
        cv2.imshow("Frame",frame)
        cv2.imshow("Result off detection", face_frame)
        if cv2.waitKey(1)==ord('q'):
            break
cv2.destroyAllWindows() 
