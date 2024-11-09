import base64
import sys
import paho.mqtt.client as paho
from PyQt5 import QtCore, QtGui, QtWidgets
from Crypto.Cipher import AES




import resources_rc
class CombinedApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MQTT File Upload")
        self.setGeometry(100, 100, 800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(170, 300, 351, 25))
        self.lineEdit.setPlaceholderText("Upload the binary file and choose the required ECU")
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(290, 340, 121, 21))
        self.comboBox.addItem("Engine")
        self.comboBox.addItem("Brake")
        self.comboBox.addItem("Environmental")
        self.comboBox.setStyleSheet("background-color: rgb(26, 95, 180); color: white;")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(550, 300, 89, 25))
        self.pushButton.setText("Browse")
        self.pushButton.setStyleSheet("background-color: rgb(26, 95, 180); color: white;")

        self.pushButton.clicked.connect(self.browse_file)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(290, 380, 121, 21))
        self.pushButton_2.setText("UPLOAD")
        self.pushButton_2.setStyleSheet("background-color: rgb(26, 95, 180); color: white;")

        self.pushButton_2.clicked.connect(self.upload_file_mqtt)

        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(290, 10, 171, 201))
        self.graphicsView.setStyleSheet("border-image: url(:/img/iti.png);")

        self.setCentralWidget(self.centralwidget)

    def browse_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Binary File", "", "Binary Files (*.bin);;All Files (*)", options=options
        )

        if file_path:
            self.lineEdit.setText(file_path)

    def encrypt_file_aes(self, key, input_file_path, output_file_path):
        block_size = AES.block_size

        cipher = AES.new(key, AES.MODE_ECB)

        with open(input_file_path, 'rb') as input_file:
            with open(output_file_path, 'wb') as output_file:
                while True:
                    plaintext = input_file.read(block_size)
                    if len(plaintext) == 0:
                        break

                    if len(plaintext) % block_size != 0:
                        plaintext += b'\0' * (block_size - (len(plaintext) % block_size))

                    ciphertext = cipher.encrypt(plaintext)
                    output_file.write(ciphertext)

        print("File encrypted successfully.")

    def upload_file_mqtt(self):
        client = paho.Client(client_id="karimzidanelsayed", userdata=None, protocol=paho.MQTTv5)
        client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
        client.username_pw_set("karimzidanelsayed", "0117011403aA")
        client.connect("19275e8da58847238d8dcb7ccd19a24f.s1.eu.hivemq.cloud", 8883)

        selected_item = self.comboBox.currentText()

        if selected_item == "Engine":
            topic = "App"
        elif selected_item == "Brake":
            topic = "App1"
        elif selected_item == "Environmental":
            topic = "App2"
        else:
            topic = "App"

        file_path = self.lineEdit.text()
        encrypted_file_path = 'encrypted.bin'

        key = b'0123456789ABCDEF'
        self.encrypt_file_aes(key, file_path, encrypted_file_path)

        with open(encrypted_file_path, 'rb') as file:
            binary_data = file.read()

        base64_data = base64.b64encode(binary_data).decode('utf-8')

        client.publish(topic, base64_data, qos=2)
        client.loop_start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = CombinedApp()
    MainWindow.show()
    sys.exit(app.exec_())

