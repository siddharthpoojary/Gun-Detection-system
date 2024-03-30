import cv2
import datetime
from datetime import date
from ultralytics import YOLO

model = YOLO('surveillance_v8n_V3_50.pt')

current_date = date.today()

output_dir = "yolov8_output"
output_name = current_date.strftime("%b-%d-%Y-")

video_path = input("Enter Filename or press Enter to use Webcam : ")
if video_path:
    cap = cv2.VideoCapture(video_path)
else:
    cap = cv2.VideoCapture(0)

frame_width = int(cap.get(3)) 
frame_height = int(cap.get(4)) 
   
size = (frame_width, frame_height) 
video = cv2.VideoWriter('{}.avi'.format(output_name), cv2.VideoWriter_fourcc(*'MJPG'), 10, size) 

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model(frame,conf=0.7,verbose=False)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        cv2.putText(annotated_frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S %p"),(10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.50, (0, 0, 255), 1)

        if results[0]:
            video.write(annotated_frame)

        # cv2.namedWindow('Security',cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Security', (800,500))
        cv2.imshow("Security", annotated_frame)
        

        if results[0]: 
            print("Weapon Detected")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

video.release()
cap.release()
cv2.destroyAllWindows()