WHAT THIS SCRIPT DO ?

1-Subscribes to specific MQTT topics.
2-Receives messages on those topics.
3-Decrypts the received binary data using AES encryption.
4-Saves the decrypted data as binary files with corresponding filenames.
5-Updates a common flag file with a specific value based on the topic.
6-Sends a D-Bus signal to notify other parts of the application with the flag value.



To use this script in another project, you can follow these steps:
Prerequisites:

Python 3.x installed on your system.
Required Python packages can be installed using pip:
Copy code
pip install paho-mqtt pydbus pycrypto


   ```

**Instructions:**

1. Clone or download the script to your local project directory.

2. Open the script (`MQ.py`) in a text editor to customize the following parameters according to your project:

   - Modify the `topic_to_filename` and `topic_to_flag` dictionaries to match the MQTT topics you want to subscribe to and their corresponding filenames and flags. line( 14 &21)

   - Update the `common_flag_file` variable with the path to your common flag file. (line28)

3. Make sure you have the necessary encryption key (`key` variable) configured for decrypting the received data. Update it as needed for your specific application.  line (104)

4. Ensure that you have your MQTT broker details, such as the broker address, port, and authentication (username and password) configured in the script. Modify the following lines accordingly: line (132&134)

   ```python
   client.username_pw_set("raspberrypi", "0117011403aA")
   client.connect("19275e8da58847238d8dcb7ccd19a24f.s1.eu.hivemq.cloud", 8883)
   ```

5. Customize the D-Bus service and signals to suit your application's requirements. You can modify the `MessagePublisher` class and its signal definitions.

6. Save the script after making the necessary modifications.

7. Run the script to start the MQTT message reception and processing. You can do this by executing the following command in your terminal:

   ```bash
   python MQ.py
   ```

   The script will continuously listen for MQTT messages on the specified topics and perform the defined actions.

8. Monitor the output and check the specified file paths to access the received and decrypted binary files.

**Note:**
- Ensure that your project has the required D-Bus service and interface set up to receive signals emitted by this script. The D-Bus signal is sent to notify other parts of the application.

You can now integrate this script into your project, following the steps and customizations provided in this README.
