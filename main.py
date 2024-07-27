import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import csv
import re
from ultralytics import YOLO
import cv2
import os
import datetime
import pytesseract
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog
import sys

class ImageSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Selector')
        self.setGeometry(100, 100, 400, 300)

        self.select_button = QPushButton('Select Image', self)
        self.select_button.clicked.connect(self.selectImage)
        self.select_button.setGeometry(150, 100, 100, 30)

    def selectImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)", options=options)
        if image_path:
            self.processImage(image_path)

    def processImage(self, image_path):
        # Initialize YOLO models
        person_bike_model = YOLO(r"C:\Users\Admin\Desktop\helmett\person_with_motorcycle\best.pt")
        helmet_model = YOLO(r"C:\Users\Admin\Desktop\helmett\newhelmet\best.pt")
        number_plate_model = YOLO(r"C:\Users\Admin\Desktop\helmett\number_plate\best.pt")

        output_dir = r""  # Directory to save the output images
        csv_output_file = "license_plate_info.csv"  # CSV file to store license plate information
        email_owner_file = "license_plate_owners.csv"  # CSV file containing email addresses of license plate owners

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        # Read the input image
        frame = cv2.imread(image_path)

        # Process frame
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect person on a bike
        person_bike_results = person_bike_model.predict(img)

        # Initialize CSV file and writer for license plate info
        with open(csv_output_file, mode='w', newline='') as plate_file:
            plate_writer = csv.writer(plate_file)
            plate_writer.writerow(['License Plate', 'Image Location'])  # Write header with Image Location

            # Process each detection result
            for r in person_bike_results:
                boxes = r.boxes
                # Filter detections for person with a motorcycle
                for box in boxes:
                    cls = box.cls
                    if person_bike_model.names[int(cls)] == "Person_Bike":
                        # Crop person with motorcycle image
                        x1, y1, x2, y2 = box.xyxy[0]
                        person_with_motorcycle_image = frame[int(y1):int(y2), int(x1):int(x2)]

                        # Draw boundary box and label for person with motorcycle
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(frame, "Person with Motorcycle", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0), 2)

                        # Detect helmet on the person
                        helmet_results = helmet_model.predict(person_with_motorcycle_image)

                        # Flag to check if helmet is detected
                        helmet_detected = False

                        # Process each helmet detection result
                        for hr in helmet_results:
                            h_boxes = hr.boxes
                            # Filter detections for helmet
                            for h_bo in h_boxes:
                                h_cls = h_bo.cls
                                if helmet_model.names[int(h_cls)] == "helmet on":
                                    # Set the flag to True if a helmet is detected
                                    helmet_detected = True
                                    # Draw boundary box for helmet
                                    cv2.rectangle(person_with_motorcycle_image, (int(h_bo.xyxy[0][0]), int(h_bo.xyxy[0][1])),
                                                (int(h_bo.xyxy[0][2]), int(h_bo.xyxy[0][3])), (0, 255, 0), 2)
                                    # Add label for helmet
                                    cv2.putText(person_with_motorcycle_image, "Helmet", (int(h_bo.xyxy[0][0]), int(h_bo.xyxy[0][1]) - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        if not helmet_detected:
                            # Draw boundary box for no helmet
                            cv2.rectangle(person_with_motorcycle_image, (int(h_bo.xyxy[0][0]), int(h_bo.xyxy[0][1])),
                                            (int(h_bo.xyxy[0][2]), int(h_bo.xyxy[0][3])), (0, 0, 255), 2)
                            # Add label for no helmet
                            cv2.putText(person_with_motorcycle_image, "helmet off", (int(h_bo.xyxy[0][0]), int(h_bo.xyxy[0][1]) - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            # Detect number plate on the person with motorcycle
                            number_plate_results = number_plate_model.predict(person_with_motorcycle_image)

                            # Flag to check if number plate is detected
                            plate_detected = False

                            # Save the cropped person with motorcycle image
                            timestamp = datetime.datetime.now().strftime("%d%Y%m%H%M%S")
                            output_file = f"person_with_motorcycle_no_helmet_{timestamp}.jpg"
                            output_path = os.path.join(output_dir, output_file)
                            cv2.imwrite(output_path, person_with_motorcycle_image)

                            # Process each number plate detection result
                            for nr in number_plate_results:
                                np_boxes = nr.boxes
                                # Filter detections for number plates
                                for np_bo in np_boxes:
                                    np_cls = np_bo.cls
                                    if number_plate_model.names[int(np_cls)] == "License_Plate":
                                        plate_detected = True

                                        # Draw boundary box for number plate
                                        cv2.rectangle(person_with_motorcycle_image, (int(np_bo.xyxy[0][0]), int(np_bo.xyxy[0][1])),
                                                    (int(np_bo.xyxy[0][2]), int(np_bo.xyxy[0][3])), (255, 0, 0), 2)
                                        # Add label for number plate
                                        cv2.putText(person_with_motorcycle_image, "Number Plate", (int(np_bo.xyxy[0][0]), int(np_bo.xyxy[0][1]) - 10),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                                        # Crop the license plate region
                                        plate_image = person_with_motorcycle_image[int(np_bo.xyxy[0][1]):int(np_bo.xyxy[0][3]),
                                                                                        int(np_bo.xyxy[0][0]):int(np_bo.xyxy[0][2])]

                                        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

                                        # Perform OCR on the license plate image
                                        plate_text = pytesseract.image_to_string(gray, config='--psm 6')
                                        plate_text = re.sub(r'[^a-zA-Z0-9]', '', plate_text)
                                        plate_text = plate_text.upper()
                                        print("Detected Number Plate:", plate_text)

                                        # Write license plate text to CSV
                                        plate_writer.writerow([plate_text, f"Image Cropped: {output_file}"])  # Include image location in CSV

                                        # Read email addresses from license_plate_owners.csv
                                        with open(email_owner_file, mode='r') as owner_file:
                                            owner_reader = csv.reader(owner_file)
                                            next(owner_reader)  # Skip header

                                            # Create a dictionary to map license plates to email addresses
                                            plate_to_email = {row[0]: row[1] for row in owner_reader}

                                            # Get the email address for the detected license plate
                                            receiver_email = plate_to_email.get(plate_text, None)

                                            # Send email if email address is found
                                            if receiver_email:
                                                sender_email = ""  # Update with your email address
                                                sender_password = ""  # Update with your email password

                                                # Create message container
                                                msg = MIMEMultipart()
                                                msg['From'] = sender_email
                                                msg['To'] = receiver_email
                                                msg['Subject'] = "E-Challan Notification"

                                                # Email body
                                                body = f"Dear License Plate Owner,\n\nYou have been issued an e-challan for not wearing a helmet and violating traffic rules.\n\nDetected License Plate: {plate_text}\n\nPlease pay the fine of Rs.1000 as soon as possible.\n\nRegards,\nTraffic Police Department"

                                                # Attach the cropped image to the email
                                                with open(output_path, 'rb') as image_file:
                                                    image_data = image_file.read()
                                                    image = MIMEImage(image_data, name=os.path.basename(output_path))
                                                    msg.attach(MIMEText(body, 'plain'))
                                                    msg.attach(image)

                                                # Connect to SMTP server and send email
                                                try:
                                                    server = smtplib.SMTP('smtp.gmail.com', 587)
                                                    server.starttls()
                                                    server.login(sender_email, sender_password)
                                                    text = msg.as_string()
                                                    server.sendmail(sender_email, receiver_email, text)
                                                    server.quit()
                                                    print("Email sent successfully!")
                                                except Exception as e:
                                                    print("Error sending email:", str(e))
                                            else:
                                                print(f"No email found for license plate: {plate_text}")

                            if not plate_detected:
                                # Save the cropped person with motorcycle image
                                timestamp = datetime.datetime.now().strftime("%d%Y%m%H%M%S")
                                output_file = f"person_with_motorcycle_{timestamp}.jpg"
                                output_path = os.path.join(output_dir, output_file)
                                cv2.imwrite(output_path, person_with_motorcycle_image)

        # Display the frame with detected objects and their labels
        cv2.imshow('Frame', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageSelector()
    window.show()
    sys.exit(app.exec_())
