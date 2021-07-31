import threading
import cv2
import os
import time
from PIL import Image, ImageDraw

import boto3
from pprint import pprint

from firebase_update import update_parking

def detect_parking_block(height, width, left, top,
 floorHeight = 1, floorWidth = 1, floorLeft = 0, floorTop = 0):
    toRight = width+left
    toBottom = height+top

    blockHeight = floorHeight/3
    blockWidth = floorWidth/3

    if (toBottom <= blockHeight) and (toRight <= blockWidth):
        return "a1"
    elif (toBottom <= blockHeight) and (toRight >= blockWidth and toRight <= 2*blockWidth):
        return "a2"
    elif (toBottom <= blockHeight) and (toRight >= 2*blockWidth):
        return "a3"
    
    elif (top >= blockHeight*2) and (toRight <= blockWidth):
        return "a4"
    elif (top >= blockHeight*2) and  (toRight >= blockWidth and toRight <= 2*blockWidth):
        return "a5"
    elif (top >= blockHeight*2) and (toRight >= 2*blockWidth):
        return "a6"
    else:
        return None


def detect_parking_and_save(photo, picture_number):

    model='arn:aws:rekognition:us-east-1:452893641899:project/car_parking/version/car_parking.2021-07-30T13.51.04/1627632366146'
    min_confidence=50
    
    client=boto3.client('rekognition')
    with open(photo, 'rb') as image:
        response = client.detect_custom_labels(Image={'Bytes': image.read()}, 
            MinConfidence=min_confidence,
            ProjectVersionArn=model)

        # pprint (response)

    blocks_with_vehicles = []
    cars = []
    
    
    image = Image.open(photo)
    imgWidth, imgHeight = image.size
    
    draw = ImageDraw.Draw(image)

    blocks = []
    
    for label in response["CustomLabels"]:
        box = label["Geometry"]['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
        
        points = (
        (left,top),
        (left + width, top),
        (left + width, top + height),
        (left , top + height),
        (left, top) )

        block = detect_parking_block(box["Height"], box["Width"], box["Left"], box["Top"])
        blocks.append(block)

        # print ("In the position: ", block)
        # print (f"Height: {box['Height']}, Width: {box['Width']}, Left: {box['Left']}, Top: {box['Top']} ")

        draw.line(points, fill='#00d400', width=5)

        draw.line(((0.33*imgWidth, 0), (0.33*imgWidth, 1*imgHeight)), fill = "#ff0000", width = 5)
        draw.line(((0.66*imgWidth, 0), (0.66*imgWidth, 1*imgHeight)), fill = "#ff0000", width = 5)
        draw.line(((0, 0.33*imgHeight), (imgWidth, 0.33*imgHeight)), fill = "#ffffff", width = 5)
        draw.line(((0, 0.66*imgHeight), (imgWidth, 0.66*imgHeight)), fill = "#ffffff", width = 5)
    
    labels = ["a1", "a2", "a3", "a4", "a5"]
    for label in labels:
        update_parking(label, False)
    
    for block in blocks:
        if block:
]            update_parking(block, True)

    image.save(f"/home/suraj/car_images/1_result_images/{picture_number}.jpg")

RTSP_URL = 'http://192.168.1.200:4747/video'

total_frames = 0
picture_number = 0
 
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
 
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
 
if not cap.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)
 
while True:
    # cap.set(cv2.CAP_PROP_FPS,3) 
    _, frame = cap.read()
    total_frames += 1
    cv2.imshow('RTSP stream', frame)
    if total_frames % 50 == 0:
        picture_number += 1
        cv2.imwrite(f"/home/suraj/car_images/{picture_number}.jpg", frame)

        x = threading.Thread(target=detect_parking_and_save, args=(f"/home/suraj/car_images/{picture_number}.jpg", picture_number))
        x.start()
        # detect_labels_local_file(f"/home/suraj/car_images/{picture_number}.jpg", picture_number)
    
    if cv2.waitKey(1) & 0xFF == ord('q') :
        # break out of the while loop
        break 
cap.release()
cv2.destroyAllWindows()

