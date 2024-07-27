# helmet_detection_and_e-challan_system
This project uses YOLO (You Only Look Once) object detection models to identify individuals riding motorcycles who are not wearing helmets. It automates the issuance of electronic challans (fines) by recognizing license plates from detected images and sending notifications via email.

##**Features**

Person and Motorcycle Detection: Identifies individuals riding motorcycles. 

Helmet Detection: Determines if the rider is wearing a helmet. 

License Plate Recognition: Extracts and recognizes license plate numbers using OCR (Optical Character Recognition). 

Automated Email Notifications: Sends e-challans to registered vehicle owners via email. 

GUI Interface: Provides an easy-to-use graphical interface for image selection and processing. 



Prerequisites
Python 3.x
Tesseract OCR: Optical Character Recognition tool.


Installation
1. Clone the Repository
bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2. Set Up a Virtual Environment (Optional but Recommended)
Create a virtual environment to manage dependencies:
bash

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install Required Packages
Install the necessary Python packages:
bash

pip install -r requirements.txt


4. Configure Tesseract OCR
Ensure that Tesseract OCR is installed on your system. Set the path to the Tesseract executable in the man.py script:

python

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
Replace the path with the actual path to Tesseract OCR on your machine.


Usage

1. Run the Application
Start the application by running the man.py script:

bash

python man.py

2. Select an Image
The GUI will open. Click the "Select Image" button to choose an image file for processing. The application will analyze the image, detect persons on motorcycles, check for helmets, and extract license plates.

3. Review Results
Detected objects and their labels will be displayed in the GUI.
If a rider without a helmet is detected, an email notification will be sent to the registered owner of the vehicle based on the license plate.


Configuration

Email Settings: Update the sender_email and sender_password in the man.py file with your email credentials.
Model Paths: Ensure the paths to the YOLO model files in the man.py script are correct.


Example CSV Files
license_plate_info.csv: Contains the extracted license plate information and corresponding image file locations.
license_plate_owners.csv: Maps license plates to email addresses for notification purposes. (This file is personal and should be managed securely.)


License

This project is licensed under the MIT License. See the LICENSE file for details.
