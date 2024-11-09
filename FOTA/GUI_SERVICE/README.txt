FUNCTIONALITY 

This script is a PyQt5 application that creates a GUI window for displaying firmware update notifications and progress. It also communicates with MQTT_SERVICE && FIRMWARE_UPDATESERVICE via D-Bus signals.


Prerequisites:

1-Python 3.x installed on your system.

2-Required Python packages can be installed using pip:

pip install PyQt5 dbus-python

You need to have the following D-Bus services set up in your project:

org.example.MQTT_SERVICE for MQTT message reception and signal emission.
org.example.Sender for sending progress signals.
org.example.GUI_SERVICE for sending messages to the GUI.
Instructions:

Clone or download the script to your local project directory.

Open the script (final.py) in a text editor to customize the following parameters according to your project:

Replace the path in tesla_pixmap = QPixmap("/path/to/your/image.jpg") with the path to the image you want to display in the GUI.
Customize the firmware update unit types and signal flags in the handle_firmware_update_signal function according to your project.

Save the script after making the necessary modifications.

In your project, set the unit_type variable somewhere before running the script.

Run the script to start the GUI and connect to the D-Bus services. You can do this by executing the following command in your terminal:

bash
python3 final.py
The script will create a GUI window that displays firmware update notifications and progress. It will also communicate with other parts of the application through D-Bus signals.

Note:

Ensure that your project has the required D-Bus services and interfaces set up to work with this script. You should have org.example.MQTT_SERVICE, org.example.Sender, and org.example.GUI_SERVICE services configured to handle MQTT messages, progress signals, and message notifications, respectively.
