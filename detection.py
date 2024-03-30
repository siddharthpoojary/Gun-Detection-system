from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import time
import datetime
from datetime import date
from ultralytics import YOLO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from mime import smtp_server,smtp_password,smtp_port,smtp_username,sender_email, send_email
from data_storage import DataStorage
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import glob
from email.message import EmailMessage
import moviepy.editor as mp
import sqlite3

data_storage = DataStorage()



model = YOLO('surveillance_v8n_V3_50.pt')

class Detection(QThread):
    def __init__(self, video_path=None):
        super(Detection, self).__init__()
        self.video_path = video_path
        self.recipient_email = None
        self.subject = None
        self.fetch_recipient_email_and_subject()

    changePixmap = pyqtSignal(QImage)

    def fetch_recipient_email_and_subject(self):
        # Connect to your SQLite database
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # Fetch the recipient email and subject from the database
        cursor.execute("SELECT recipient_email, subject FROM email_data WHERE id = (SELECT MAX(id) FROM email_data)")
        result = cursor.fetchone()
        if result:
            self.recipient_email, self.subject = result

        # Close the database connection
        conn.close()

    def send_email_with_attachment(self, file_path):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self.subject

            attachment = open(file_path, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename=clip.avi")
            msg.attach(part)

            server = smtplib.SMTP(smtp_server, 587)  # Use your SMTP server and port here
            server.starttls()
            server.login(sender_email, smtp_password)
            text = msg.as_string()
            server.sendmail(sender_email, self.recipient_email, text)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print("Email could not be sent. Error:", str(e))

    def run(self):
        starting_time = time.time()
        condition_duration = 2

        self.running = True
        condition_met = False
        email_sent = False
        email_timeout = 5

        # Multi-camera code
        num_cameras = 1
        if self.video_path:
            # Use the video file
            caps = [cv2.VideoCapture(self.video_path)]
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

        frame_width = int(caps[0].get(3))
        frame_height = int(caps[0].get(4))
        size = (frame_width * num_cameras, frame_height)

        # Creating a video writer object with MJPG codec for avi video file output and 10 fps
        video = cv2.VideoWriter('saved_frame/clip.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)

        while self.running:
            frames = [cap.read()[1] for cap in caps]

            if any(frame is None for frame in frames):
                break

            results = [model(frame, conf=0.7, verbose=False) for frame in frames]

            # Visualize the results on each frame
            annotated_frames = [result[0].plot() for result in results]

            # Add a timestamp to each frame
            for annotated_frame in annotated_frames:
                cv2.putText(
                    annotated_frame,
                    datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S %p"),
                    (10, frame_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (0, 0, 255),
                    1,
                )

            # Concatenate all the frames horizontally into one frame
            annotated_frame = cv2.hconcat(annotated_frames)

            # Write the output frame to the video file
            
                
                
            

            height, width, channels = annotated_frame.shape
            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = channels * width
            convert_to_qt_format = QImage(
                rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            p = convert_to_qt_format.scaled(900, 630, Qt.KeepAspectRatio)
            elasped_time = starting_time - time.time()
            self.changePixmap.emit(p)
            


            if any(results[0] for results in results):
                video.write(annotated_frame)
                starting_time = time.time()
                cv2.imwrite("saved_frame/clip.avi", annotated_frame)
                condition_met = True
                
                print("Object Detected")
            
            
        
        # Release resources
        

            # Release video writer
            


        # Send email when conditions are met
            if condition_met and not email_sent and (time.time() - starting_time) >= condition_duration:
                try:
                    print("sending")
                    self.send_email_with_attachment("saved_frame/clip.avi")
                    email_sent = True

                except Exception as e:
                    print("Email could not be sent. Error:", str(e))


        for cap in caps:
            cap.release()

        video.release()

        

        