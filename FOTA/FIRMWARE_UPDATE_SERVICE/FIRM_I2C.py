import serial
import struct
import os
import sys
import time
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from pydbus import SessionBus
import dbus.service
import RPi.GPIO as GPIO 
import smbus

# Initialize I2C1 bus

i2cbus = smbus.SMBus(1)

time.sleep(1)

# Global I2C address variable

global I2C_ADDRESS

# Set up D-Bus main loop

DBusGMainLoop(set_as_default=True)
# Initialize the GLib main loop

mainloop = GLib.MainLoop()
# Bootloader command constants

CBL_GET_VER_CMD = 0x10
CBL_FLASH_ERASE_CMD = 0x15
CBL_MEM_WRITE_CMD = 0x16
# Constants for bootloader responses

INVALID_SECTOR_NUMBER = 0x00
VALID_SECTOR_NUMBER = 0x01
UNSUCCESSFUL_ERASE = 0x02
SUCCESSFUL_ERASE = 0x03

FLASH_PAYLOAD_WRITE_FAILED = 0x00
FLASH_PAYLOAD_WRITE_PASSED = 0x01

verbose_mode = 1
Memory_Write_Active = 0
Memory_Write_All = 1
# Global progress variable

progress=0
# Global firmware_flasher variable

global firmware_flasher

# Create a D-Bus object for progress signal

class ProgressSender(dbus.service.Object):
    def __init__(self, bus):
        bus_name = dbus.service.BusName("org.example.Sender", bus)
        dbus.service.Object.__init__(self, bus_name, '/org/example/ProgressSender')

    @dbus.service.signal("org.example.ProgressInterface", signature='i')
    def ProgressSignal(self, value):
        pass
        
        
# Variable to store the received signal value
signal_val='0'

def StartBootloader(signal):
    global firmware_flasher
    global I2C_ADDRESS
    
    if signal_val == "0x1":
        I2C_ADDRESS = 0x49
    elif signal_val == "0x2":
        I2C_ADDRESS = 0x51
    elif signal_val == "0x3":
        I2C_ADDRESS = 0x53
    else:
        print("Invalid signal value")
        return


    print(f"BOOTLOADER STARTED {signal}")
    BinaryFilePath = GetBinaryFilePath(signal)

    if BinaryFilePath:
        #send dummy data to force stm to system reset
        dummy=0x01
        

        i2cbus.write_byte(I2C_ADDRESS, dummy)

        time.sleep(1)
        print("ERASE")

        Decode_CBL_Command(6)


        Decode_CBL_Command(7)


        Decode_CBL_Command(1)
        BinFile.close()

# Function to write data to the I2C device with error handling

def Write_Data_To_I2C(I2C_ADDRESS, Value):
    max_retries = 10
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            i2cbus.write_byte(I2C_ADDRESS, Value)
            print(f"Data {Value} sent to address {I2C_ADDRESS}.")
            time.sleep(1)
            break  # Exit the loop if the write operation is successful
        except IOError:
            print(f"Failed to send data to address {I2C_ADDRESS}. (Attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    else:
        print(f"Maximum retry attempts reached. Data not sent to address {I2C_ADDRESS}.")



# Function to read data from the I2C device and ensure the expected data length

def Read_I2C_Data_Length(device_address,Data_Len):
    print("CHECK FOR ACK")
  
    data = []
    for j in range(Data_Len):
        try:
            val=i2cbus.read_byte(I2C_ADDRESS)
            print(f"RECEIVED {val} ")
            data.append(val)
        #time.sleep(1)
        except IOError:
            print("ERROR IN RECEIVING")
    I2C_Value_len = len(data)
    time.sleep(1)
    while  I2C_Value_len!= Data_Len:
        for j in range(Data_Len):
                try:
                    val=i2cbus.read_byte(I2C_ADDRESS)
                    print(f"RECEIVED {val}")
                    I2C_Value_len=I2C_Value_len+1
                    data.append(val)

                #time.sleep(1)
                except IOError:
                    print("ERROR IN RECEIVING")
                print("Waiting Reply from the Bootloader")
    return data



def Read_Data_From_I2C():
    return i2cbus.read_byte(I2C_ADDRESS)
# Function to read data from the serial port as a response to a bootloader command

def Read_Data_From_Serial_Port(Command_Code):
    Length_To_Follow = 0
    BL_ACK= Read_I2C_Data_Length(I2C_ADDRESS,2)
    if len(BL_ACK):
        BL_ACK_Array = bytearray(BL_ACK)
        if BL_ACK_Array[0] == 0xCD:
            print("Received Acknowledgement from Bootloader")
            Length_To_Follow = BL_ACK_Array[1]
            print(f"Preparing to receive ({int(Length_To_Follow)}) bytes from the bootloader")
            if Command_Code == CBL_GET_VER_CMD:
                Process_CBL_GET_VER_CMD(Length_To_Follow)
            elif Command_Code == CBL_FLASH_ERASE_CMD:
                Process_CBL_FLASH_ERASE_CMD(Length_To_Follow)
            elif Command_Code == CBL_MEM_WRITE_CMD:
                Process_CBL_MEM_WRITE_CMD(Length_To_Follow)
        else:
            print("Received Not-Acknowledgement from Bootloader")
            sys.exit()


#Function to get version of the current boot_loader
def Process_CBL_GET_VER_CMD(Data_Len):

    Serial_Data = Read_I2C_Data_Length(I2C_ADDRESS,Data_Len)
    _value_ = bytearray(Serial_Data)
    print(f"Bootloader Vendor ID: {_value_[0]}")
    print(f"Bootloader Version: {_value_[1]}.{_value_[2]}.{_value_[3]}")


#Function to force boot_loader to erase the current application
def Process_CBL_FLASH_ERASE_CMD(Data_Len):
    BL_Erase_Status = 0

    Serial_Data = Read_I2C_Data_Length(I2C_ADDRESS,Data_Len)
    if len(Serial_Data):
        BL_Erase_Status = bytearray(Serial_Data)
        if BL_Erase_Status[0] == INVALID_SECTOR_NUMBER:
            print("Erase Status -> Invalid Sector Number")
        elif BL_Erase_Status[0] == UNSUCCESSFUL_ERASE:
            print("Erase Status -> Unsuccessful Erase")
        elif BL_Erase_Status[0] == SUCCESSFUL_ERASE:
            print("Erase Status -> Successful Erase")
        else:
            print("Erase Status -> Unknown Error")
    else:
        print("Timeout! Bootloader is not responding")


#function used to force bootloader to write data on flash
def Process_CBL_MEM_WRITE_CMD(Data_Len):
    global Memory_Write_All
    BL_Write_Status = 0

    Serial_Data = Read_I2C_Data_Length(I2C_ADDRESS,Data_Len)
    BL_Write_Status = bytearray(Serial_Data)
    if BL_Write_Status[0] == FLASH_PAYLOAD_WRITE_FAILED:
        print("Write Status -> Write Failed or Invalid Address")
    elif BL_Write_Status[0] == FLASH_PAYLOAD_WRITE_PASSED:
        print("Write Status -> Write Successful")
        Memory_Write_All = Memory_Write_All and FLASH_PAYLOAD_WRITE_PASSED
    else:
        print("Timeout! Bootloader is not responding")

def Calculate_CRC32(Buffer, Buffer_Length):
    CRC_Value = 0xFFFFFFFF
    for DataElem in Buffer[0:Buffer_Length]:
        CRC_Value = CRC_Value ^ DataElem
        for DataElemBitLen in range(32):
            if CRC_Value & 0x80000000:
                CRC_Value = (CRC_Value << 1) ^ 0x04C11DB7
            else:
                CRC_Value = (CRC_Value << 1)
    return CRC_Value

#function convert word to byte
def Word_Value_To_Byte_Value(Word_Value, Byte_Index, Byte_Lower_First):
    Byte_Value = (Word_Value >> (8 * (Byte_Index - 1)) & 0x000000FF)
    return Byte_Value


#function to detect which ecu application iam gonna fetch and send to bootloader
def GetBinaryFilePath(signal):
    if signal == "0x1":
        return "/home/karim/Desktop/Process/MQTT_SERVICE/App.bin"
    elif signal == "0x2":
        return "/home/karim/Desktop/Process/MQTT_SERVICE/App1.bin"
    elif signal == "0x3":
        return "/home/karim/Desktop/Process/MQTT_SERVICE/App2.bin"
    else:
        return None

#function to detect which command i want to send to bootloader init the frame and send it to bootloader
def Decode_CBL_Command(Command):
    BL_Host_Buffer = [0] * 255
    BL_Return_Value = 0

    if (Command == 1):
        print("Request the bootloader version")
        CBL_GET_VER_CMD_Len = 6
        BL_Host_Buffer[0] = CBL_GET_VER_CMD_Len - 1
        BL_Host_Buffer[1] = CBL_GET_VER_CMD
        CRC32_Value = Calculate_CRC32(BL_Host_Buffer, CBL_GET_VER_CMD_Len - 4)
        CRC32_Value = CRC32_Value & 0xFFFFFFFF
        print(f"Host CRC = {hex(CRC32_Value)}")
        BL_Host_Buffer[2] = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[3] = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[4] = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[5] = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_I2C(I2C_ADDRESS,BL_Host_Buffer[0])
        time.sleep(1)
        i2cbus.write_i2c_block_data(I2C_ADDRESS, BL_Host_Buffer[1],BL_Host_Buffer[2:CBL_GET_VER_CMD_Len])
        time.sleep(1)
        Read_Data_From_Serial_Port(CBL_GET_VER_CMD)
    elif (Command == 6):
        print("Mass erase or sector erase of the user flash command")
        CBL_FLASH_ERASE_CMD_Len = 8
        SectorNumber = 0
        NumberOfSectors = 0
        BL_Host_Buffer[0] = CBL_FLASH_ERASE_CMD_Len - 1
        BL_Host_Buffer[1] = CBL_FLASH_ERASE_CMD
        SectorNumber = 1  # Set the sector number (you can modify this)
        if SectorNumber != 0xFF:
            NumberOfSectors = 4  # Set the number of sectors to erase (you can modify this)
        BL_Host_Buffer[2] = SectorNumber
        BL_Host_Buffer[3] = NumberOfSectors
        CRC32_Value = Calculate_CRC32(BL_Host_Buffer, CBL_FLASH_ERASE_CMD_Len - 4)
        CRC32_Value = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[4] = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[5] = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[6] = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[7] = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)

        Write_Data_To_I2C(I2C_ADDRESS,BL_Host_Buffer[0])
        time.sleep(1)
        i2cbus.write_i2c_block_data(I2C_ADDRESS, BL_Host_Buffer[1],BL_Host_Buffer[2:8])
        Read_Data_From_Serial_Port(CBL_FLASH_ERASE_CMD)
        print("\nErase Done Successfully")
    elif (Command == 7):
        print("Write data into different memories of the MCU command")
        File_Total_Len = 0
        BinFileRemainingBytes = 0
        BinFileSentBytes = 0
        BaseMemoryAddress = 0
        BinFileReadLength = 0
        Memory_Write_All = 1

       

        File_Total_Len = CalculateBinFileLength(signal_val)  # Pass the integer to the function
        print(f"Preparing writing a binary file with length ({File_Total_Len}) Bytes")
        OpenBinFile()
        BinFileRemainingBytes = File_Total_Len - BinFileSentBytes
        BaseMemoryAddress = 0x08008000  # Set the start address (you can modify this)
        while BinFileRemainingBytes:
            Memory_Write_Is_Active = 1
            if BinFileRemainingBytes >= 21:
                BinFileReadLength = 21
            else:
                BinFileReadLength = BinFileRemainingBytes
            for BinFileByte in range(BinFileReadLength):
                BinFileByteValue = BinFile.read(1)
                BinFileByteValue = bytearray(BinFileByteValue)
                BL_Host_Buffer[7 + BinFileByte] = int(BinFileByteValue[0])
            BL_Host_Buffer[1] = CBL_MEM_WRITE_CMD
            BL_Host_Buffer[2] = Word_Value_To_Byte_Value(BaseMemoryAddress, 1, 1)
            BL_Host_Buffer[3] = Word_Value_To_Byte_Value(BaseMemoryAddress, 2, 1)
            BL_Host_Buffer[4] = Word_Value_To_Byte_Value(BaseMemoryAddress, 3, 1)
            BL_Host_Buffer[5] = Word_Value_To_Byte_Value(BaseMemoryAddress, 4, 1)
            BL_Host_Buffer[6] = BinFileReadLength
            CBL_MEM_WRITE_CMD_Len = (BinFileReadLength + 11)
            BL_Host_Buffer[0] = CBL_MEM_WRITE_CMD_Len - 1
            CRC32_Value = Calculate_CRC32(BL_Host_Buffer, CBL_MEM_WRITE_CMD_Len - 4)
            CRC32_Value = CRC32_Value & 0xFFFFFFFF
            BL_Host_Buffer[7 + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
            BL_Host_Buffer[8 + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
            BL_Host_Buffer[9 + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
            BL_Host_Buffer[10 + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
            BaseMemoryAddress = BaseMemoryAddress + BinFileReadLength
            Write_Data_To_I2C(I2C_ADDRESS,BL_Host_Buffer[0])
            time.sleep(0.1)
            i2cbus.write_i2c_block_data(I2C_ADDRESS, BL_Host_Buffer[1],BL_Host_Buffer[2:CBL_MEM_WRITE_CMD_Len])
            
            BinFileSentBytes = BinFileSentBytes + BinFileReadLength
            BinFileRemainingBytes = File_Total_Len - BinFileSentBytes
            print(f"Bytes sent to the bootloader: {BinFileSentBytes}")
            progress = int((BinFileSentBytes / File_Total_Len) * 100)

            sender.ProgressSignal(progress)



            print(f"Progress is %{progress}")
            BL_Return_Value = Read_Data_From_Serial_Port(CBL_MEM_WRITE_CMD)
            time.sleep(0.1)
        Memory_Write_Is_Active = 0
        if Memory_Write_All == 1:
            print("\nPayload Written Successfully")


#function to detect the binary file size iam gonna to send to bootloader
def CalculateBinFileLength(signal_val):
    binary_file_path = GetBinaryFilePath(signal_val)
    if binary_file_path is not None:
        if os.path.exists(binary_file_path):
            return os.path.getsize(binary_file_path)
        else:
            print(f"Binary file not found at: {binary_file_path}")
            return 0  # or handle the error as appropriate
    else:
        print("Invalid signal value")
        return 0  # or handle the error as appropriate

def OpenBinFile():
    global BinFile
    binary_file_path = GetBinaryFilePath(signal_val)
    BinFile = open(binary_file_path, 'rb')



#connect to gui dbus and start to init the callback function to specific signal
def ConnectToGUIService():
    try:
        session_bus = dbus.SessionBus()
        firmware_flash_proxy = session_bus.get_object("org.example.GUI_SERVICE", "/org/example/GUI_SERVICE")
        print("CONNECTED")

        def handle_signal(signal):
            global signal_val
            signal_val = signal
            print("Received signal:", signal)
            StartBootloader(signal)
        firmware_flash_proxy.connect_to_signal("MessageSignal", handle_signal)

    except dbus.exceptions.DBusException as e:
        GLib.timeout_add_seconds(0.1, ConnectToGUIService)  # Retry after 5 seconds

#function that create a bus object to send progress bar info to GUI through it
def ConnectToFirmwareFlasher():
    global sender
    try:
        print("Connected to MainLoop.")
        global bus_name
        session_bus = dbus.SessionBus()
        sender = ProgressSender(session_bus)

        print("Connected to FIRMWARE service.")
    except dbus.exceptions.DBusException as e:
        print(f"Error connecting to FIRMWARE service: {e}")
        time.sleep(1)  # Wait for 1 second before retrying

if __name__ == "__main__":

    ConnectToFirmwareFlasher()
    ConnectToGUIService()
    mainloop.run()


