import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSignal  # Add this import
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus
import dbus.service
import time 
from time import sleep

# Set up the D-Bus main loop for handling signals
DBusGMainLoop(set_as_default=True)
# Initialize global variables

global session_bus
global bus_name
session_bus = dbus.SessionBus()

global progress
global mqtt_service_proxy
global progress_bar
global signal_flag

flag=0
global unit_type
global receiver

# Create a global variable to track whether a window is open
window_open = False

app = QApplication(sys.argv)
# D-Bus Service for Receiving Progress Signals

class ProgressReceiver(dbus.service.Object):
    def __init__(self, bus):
        bus_name = dbus.service.BusName("org.example.Sender", bus)
        dbus.service.Object.__init__(self, bus_name, '/org/example/ProgressSender')

    @dbus.service.signal("org.example.ProgressInterface", signature='i')
    def ProgressSignal(self, value):
        pass
# D-Bus Service for Sending Messages

class MessagePublisher(dbus.service.Object):
    def __init__(self, bus_name):
        dbus.service.Object.__init__(self, bus_name, '/org/example/GUI_SERVICE')

    @dbus.service.signal("org.example.MessageInterface", signature='s')
    def MessageSignal(self, message):
        pass

# Define a custom signal for updating the progress bar
class MyWindow(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self,unit_type):
        super(MyWindow, self).__init__()

        self.setWindowTitle("Firmware Update Notification")
        self.setGeometry(100, 100, 600, 400)  # Reduced the height by 30%

        layout = QVBoxLayout()

        # Load the Tesla image
        tesla_image = QLabel()
        tesla_pixmap = QPixmap("/home/karim/Desktop/Process/GUI_SERVICE/0x0-Roadster_02_2_600x400.jpg")
        tesla_image.setPixmap(tesla_pixmap)
        layout.addWidget(tesla_image)

        # Define a QFont for bigger and bold text
        font = QFont()
        font.setPointSize(18)  # Set the font size
        font.setBold(True)  # Make the font bold



        message_label = QLabel(f"Firmware Update Available for: {unit_type}")
        message_label.setFont(font)
        layout.addWidget(message_label)

        install_button = QPushButton("Install")
        not_now_button = QPushButton("Not Now")

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()  # Initially, hide the progress bar

        def close_window():
            global window_open
            window_open = False  # Mark that the window is closed
            self.close()

        def install_firmware():
            install_button.hide()
            not_now_button.hide()
            self.progress_bar.show()  # Show the progress bar
            #send a messege to FIRMWARE_SERVICE THROUGH DBUS
            message_publisher.MessageSignal(str(signal_flag))
            print(f"Sent flag through D-Bus: {signal_flag}")

        install_button.clicked.connect(install_firmware)
        not_now_button.clicked.connect(close_window)

        layout.addWidget(install_button)
        layout.addWidget(not_now_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.close()




# Connect to the signal from the MQTT service
def connect_to_mqtt_service():
    while True:
        try:
            mqtt_service_proxy = session_bus.get_object("org.example.MQTT_SERVICE", "/org/example/MQTT_SERVICE")
            mqtt_service_proxy.connect_to_signal("MessageSignal", handle_firmware_update_signal)
            print("Connected to MQTT service.")
            return  # Exit the retry loop if successful
        except dbus.exceptions.DBusException:
            time.sleep(3)  # Wait for 5 seconds before retrying
            
#call back function used to force gui to pop on when receiving a dbus signal from MQTT
def handle_firmware_update_signal(unit_type):
    global signal_flag
    global message_publisher
    global bus_name
    global window
    if unit_type == "0x1":
       signal_flag="0x1";  
       unit_type = "Engine Control Unit"
    elif unit_type == "0x2":
         signal_flag="0x2";  
         unit_type = "Brake Control Unit"
    elif unit_type == "0x3":
         signal_flag="0x3";  
         unit_type = "HVAC Control Unit"
    #create aservice of the dbus (with the following bus name )
    bus_name = dbus.service.BusName("org.example.GUI_SERVICE", session_bus)
    #create an object of MessagePublisher class
    message_publisher = MessagePublisher(bus_name)
    #create object from QTWindow class
    window = MyWindow(unit_type)
    #create object from Progress Receiver class
    receiver = ProgressReceiver(session_bus)
    #start to listen to signal called Progress Signal from ProgeressInterface 
    session_bus.add_signal_receiver(window.update_progress, dbus_interface="org.example.ProgressInterface", signal_name="ProgressSignal")
    #start the gui
    window.show()

if __name__ == '__main__':

    #start to listen to dbus service called mqtt_service
    connect_to_mqtt_service()  # Use the correct function name here

    # Set unit_type somewhere

    sys.exit(app.exec_())
