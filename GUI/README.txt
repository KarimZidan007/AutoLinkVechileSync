MQTT File Upload Application

This application allows you to upload binary files to an MQTT broker with the option to choose the target ECU (Engine, Brake, or Environmental). The application encrypts the file using AES and then publishes it to the MQTT broker using the Paho MQTT client.

Usage:

1. Browse for a Binary File: Click the "Browse" button to select the binary file you want to upload.

2. Choose the Target ECU: Use the drop-down menu to select the target ECU for the upload (Engine, Brake, or Environmental).

3. Upload the File: Click the "UPLOAD" button to start the upload process. The file will be encrypted and published to the MQTT broker.

Requirements:

- Python 3.x
- PyQt5
- Paho MQTT
- Crypto library (for AES encryption)

Building the Standalone .exe:

1. Ensure you have Python, PyQt5, Paho MQTT, and the Crypto library installed on your system.

2. Install PyInstaller if you haven't already:


3. Open a command prompt or terminal.

4. Navigate to the directory containing your script.

5-open dist directory 

1. Double-click the . .exe file to launch the application.

2. Use the application to upload binary files to the MQTT broker.

That's it! You now have a standalone .exe application for uploading files to an MQTT broker with AES encryption.

