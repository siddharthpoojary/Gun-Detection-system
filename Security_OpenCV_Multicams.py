import os
import cv2
import datetime
from datetime import date
from ultralytics import YOLO

# Load the pretrained model from a file
model = YOLO('surveillance_v8n_V3.pt')

# Get the current date.
current_date = date.today()

# Define the output directory and file name
output_dir = "saved_frame"
output_name = current_date.strftime("%b-%d-%Y-")

# Ask the user for a video file name or press enter to use the webcam
video_file = input("Enter a video file name or press enter to use the webcam: ")

# Set num_cameras to 1 by default
num_cameras = 1

if video_file:
    # Use the video file
    caps = [cv2.VideoCapture(video_file)]
else:
    # Try to open each camera until it fails, then get the number of cameras
    num_cameras = 0
    while True:
        cap = cv2.VideoCapture(num_cameras)
        if not cap.isOpened():
            cap.release()
            break
        cap.release()
        num_cameras += 1

    # If no cameras are found, fall back to the webcam
    if num_cameras == 1:
        print("No cameras found. Falling back to webcam.")

    # Create a list of video capture objects for each camera
    caps = [cv2.VideoCapture(i) for i in range(num_cameras)]

# Get the frame width and height of the first camera
frame_width = int(caps[0].get(3)) 
frame_height = int(caps[0].get(4)) 

# Define the size of the output frame as the total width and height of all cameras
size = (frame_width * num_cameras, frame_height) 

# Changing the path to current date folder for saving video
if not os.path.exists(output_dir+"/"+output_name):
    os.chdir(output_dir)
    os.makedirs(output_name)
    os.chdir(output_name)
else :
    os.chdir(output_dir)
    os.chdir(output_name)

# Creating a video writer object with mp4v codec for mp4 video file output and 20 fps
# Use MJPG codec for avi video format
video = cv2.VideoWriter('{}.mp4'.format(output_name), cv2.VideoWriter_fourcc(*'mp4v'), 10, size) 

while True:
    # Read a frame from each camera
    frames = [cap.read()[1] for cap in caps]

    # Check if any camera failed to read a frame
    if any(frame is None for frame in frames):
        break

    # Apply the model to each frame and get the results
    results = [model(frame, conf=0.6, verbose=False) for frame in frames]

    # Visualize the results on each frame
    annotated_frames = [result[0].plot() for result in results]

    # Add a timestamp to each frame
    for annotated_frame in annotated_frames:
        cv2.putText(annotated_frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S %p"),(10, frame_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.50, (0, 0, 255), 1)

    # Concatenate all the frames horizontally into one frame
    annotated_frame = cv2.hconcat(annotated_frames)

    # Write the output frame to the video file
    if any(results[0] for results in results):
        print("Weapon Detected")
        video.write(annotated_frame)

    # Show the output frame on the screen
    cv2.imshow("Security", annotated_frame)

    # Exit the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release all the resources
video.release()
for cap in caps:
    cap.release()
cv2.destroyAllWindows()