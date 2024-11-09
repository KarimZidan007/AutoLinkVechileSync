import time
import paho.mqtt.client as paho
import base64
from pydbus import SessionBus
from gi.repository import GLib
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from Crypto.Cipher import AES

DBusGMainLoop(set_as_default=True)

# Dictionary to map topics to file names
topic_to_filename = {
    "App": "App.bin",
    "App1": "App1.bin",
    "App2": "App2.bin"
}

# Dictionary to map topics to flags
topic_to_flag = {
    "App": 0x01,
    "App1": 0x02,
    "App2": 0x03
}

# Common flag file path
common_flag_file = "/home/karim/Desktop/Process/MQTT_SERVICE/common_flag.txt"


# Define a D-Bus service for emitting signals

class MessagePublisher(dbus.service.Object):
    def __init__(self, bus_name):
        dbus.service.Object.__init__(self, bus_name, '/org/example/MQTT_SERVICE')

    @dbus.service.signal("org.example.MessageInterface", signature='s')
    def MessageSignal(self, message):
        pass

if __name__ == '__main__':
    # Initialize a D-Bus session
    session_bus = dbus.SessionBus()
    bus_name = dbus.service.BusName("org.example.MQTT_SERVICE", session_bus)
    message_publisher = MessagePublisher(bus_name)

# Function to decrypt binary data using AES
    """
    Decrypt binary data using AES encryption.

    Args:
        key (bytes): The AES encryption key (128-bit).
        binary_data (bytes): The binary data to be decrypted.

    Returns:
        bytes: The decrypted data.
    """
def decrypt_data(key, binary_data):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(binary_data)
    return decrypted_data.rstrip(b'\0')  # Remove null bytes

# Callback function for handling received MQTT messages
    """
    Callback function to handle MQTT connection.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: Userdata (not used in this example).
        flags: Connection flags.
        rc (int): The connection result code.
        properties: Connection properties (not used in this example).
    """
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNECTED %s." % rc)




    """
    Callback function to handle received MQTT messages.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: Userdata (not used in this example).
        msg (paho.mqtt.client.MQTTMessage): The received MQTT message.
    """
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    try:
        binary_data = base64.b64decode(msg.payload)

        # Get the file name based on the received topic
        file_name = topic_to_filename.get(msg.topic, "unknown_topic.hex")

        # Specify the path to save the received binary file
        file_path = f'/home/karim/Desktop/Process/MQTT_SERVICE/{file_name}'

        # Get the flag based on the received topic
        flag = topic_to_flag.get(msg.topic, 0xFF)

        # Decrypt the received binary data
        key = b'0123456789ABCDEF'  # 16-byte (128-bit) AES key
        decrypted_data = decrypt_data(key, binary_data)

        # Save the decrypted binary data as a binary file
        with open(file_path, 'wb') as file:
            file.write(decrypted_data)

        print(f"Saved the received and decrypted binary file as {file_path}")

        # Save the flag to the common flag file
        with open(common_flag_file, 'w') as flag_file:
            flag_file.write(hex(flag))

        print(f"Set common flag to {hex(flag)}")

        # Emit the D-Bus signal to notify other parts of the application
        message_publisher.MessageSignal(hex(flag))
        print(f"Sent flag through D-Bus: {hex(flag)}")
    except Exception as e:
        print(f"Error decoding, decrypting, or saving the binary file: {e}")

# Create an MQTT client
client = paho.Client(client_id="raspberrypi", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# Enable TLS for secure connection
client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
# Set username and password
client.username_pw_set("raspberrypi", "0117011403aA")
# Connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("19275e8da58847238d8dcb7ccd19a24f.s1.eu.hivemq.cloud", 8883)

# Setting callbacks
client.on_message = on_message

# Subscribe to specific topics
for topic in topic_to_filename.keys():
    client.subscribe(topic, qos=2)

# Start the MQTT client loop
client.loop_forever()

