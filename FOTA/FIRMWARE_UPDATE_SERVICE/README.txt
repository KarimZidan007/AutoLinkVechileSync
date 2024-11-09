Functionality:
This Python script is designed to communicate with an embedded system's bootloader over I2C and perform various operations, including firmware updates. It listens for D-Bus signals to initiate bootloader actions, such as requesting the bootloader version, erasing flash memory sectors, and writing firmware to memory.

Usage Instructions:
1-Prerequisites:

Python 3.x is installed on your machine.
Ensure the required Python libraries are installed: serial, struct, os, time, dbus, RPi.GPIO, smbus.
2-Code Customization:

Open the Python script.
Adjust the I2C_ADDRESS variable to match the I2C device address of your hardware setup.
Define the GetBinaryFilePath(signal) function to specify the paths to the firmware binary files for different signals (e.g., "0x1", "0x2", "0x3"). Replace the paths with your own firmware files.
3-Run the Script:

Open a terminal or command prompt.
Navigate to the directory where the Python script is located.
Execute the script using the following command:
shell
Copy code
python FIRM_I2C.py
4-Signal Transmission:

Ensure that the D-Bus service, responsible for sending signals to the bootloader, is running on the target device.
The service should send signals with appropriate signal values (e.g., "0x1", "0x2", "0x3") to trigger bootloader operations.
5-Monitor Progress:

The script reports progress updates during firmware writing. The progress value is sent over D-Bus to be consumed by other services or interfaces.
6-Adapt to Your Setup:

Adapt the script to your specific hardware and communication setup if needed.
Modify any other parameters or constants to match your embedded system's requirements.
By following these steps, you can use this Python script on another machine to communicate with your embedded system's bootloader and perform bootloader operations, including firmware updates. Make sure to adapt the script to your specific hardware and D-Bus service setup.
