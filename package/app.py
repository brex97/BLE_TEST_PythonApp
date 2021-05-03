import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QByteArray
from PyQt5.QtBluetooth import QBluetoothUuid, QLowEnergyService
from package.gui import Ui_MainWindow
from package.ble_utils.Scan import BLE_Scanner
from package.ble_utils.Controller import BLE_Controller

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.ble_scanner = BLE_Scanner()
        self.ble_controller = BLE_Controller()

        self.pushButton_Conn.setEnabled(False)  ##initially not enabled, only after device selection
        self.pushButtonService.setEnabled(False) ## initialy not enabled, only after service selection
        self.pushButton_Characteristic.setEnabled(False)   #same

    #Event signals
        self.listWidget.itemClicked.connect(self.selectedFromList)
        self.listWidget_2.itemClicked.connect(self.serviceClicked)
        self.listWidget_characteristics.itemClicked.connect(self.characteristicClicked)
        self.pushButton_clearOut.clicked.connect(self.clearOutput)
        self.pushButton_clearOut_2.clicked.connect(self.clearOutput2)
        self.pushButton_Disconnect.clicked.connect(self.handleButtonDisconnect)
        self.pushButtonService.clicked.connect(self.handleButtonService)
        self.pushButton_Characteristic.clicked.connect(self.handleButtonChar)
        #BLE Scanner events
        self.pushButtonScan.clicked.connect(self.handleButtonScan)
        self.ble_scanner.discoveryAgent.finished.connect(self.updateList)
        self.ble_scanner.discoveryAgent.error.connect(self.errorHandle)
        self.ble_scanner.scannerOutputMessage.connect(self.updateOutput)
        #BLE Controller events
        self.ble_controller.controllerOutputMessage.connect(self.updateOutput2)
        self.pushButton_Conn.clicked.connect(self.handleButtonConn)
        self.ble_controller.controllerConnected.connect(self.handleDeviceConnected)
        self.ble_controller.servicesFound.connect(self.handleServicesFound)
        #BLE Service events
        self.ble_controller.serviceOpened.connect(self.handleCharacteristics)
    
    def handleButtonScan(self):
        self.pushButton_Conn.setEnabled(False)
        self.textBrowser.clear()
        self.ble_scanner.scanDevices()

    def updateList(self):
        self.listWidget.clear()
        
        for obj in self.ble_scanner.discoveryAgent.discoveredDevices():
            self.item2add = QtWidgets.QListWidgetItem()
            self.item2add.setText(obj.name())
            self.item2add.setData(QtCore.Qt.UserRole, obj)
            self.listWidget.addItem(self.item2add)
        
        self.textBrowser_2.append(">>Scan finished\n")

    def selectedFromList(self, itemC):
        self.pushButton_Conn.setEnabled(True)
        self.deviceInfo = itemC.data(QtCore.Qt.UserRole)
        if(self.deviceInfo.coreConfigurations() == 1):
            self.devType = "Bluetooth low energy device"
        elif (self.deviceInfo.coreConfigurations() == 2):
            self.devType = "Bluetooth standard device"
        else:
            self.devType = "Bluetooth standard and low energy device"
        #print("{0}\n".format(self.deviceInfo.address().toString()))
        self.textBrowser.setText("Device name: " + self.deviceInfo.name() +
                                 "\nDevice type: " + self.devType +
                                 "\nMAC address: " + self.deviceInfo.address().toString() +
                                 "\nDevice UUID: " + self.deviceInfo.deviceUuid().toString() + '\n')

    def handleButtonConn(self):
        self.ble_controller.connectDevice(self.listWidget.currentItem().data(QtCore.Qt.UserRole))
    
    def handleButtonDisconnect(self):
        self.stackedWidget.setCurrentIndex(0)
        self.ble_controller.disconnect()
        self.textBrowser_2.append(">>Disconnected from device\n")   #output page 1
        self.listWidget.clear()     #found devices on page 1
        self.textBrowser.clear()    #device info on page 1
        self.listWidget_2.clear()   #services list on page 2
        self.listWidget_characteristics.clear()  #page 2 char browser
        self.textBrowser_3.clear()  ##output on page 2
        self.pushButton_Conn.setEnabled(False)
        self.pushButtonService.setEnabled(False)
        self.pushButton_Characteristic.setEnabled(False)

    def handleDeviceConnected(self):
        print("Changing page\n")
        self.stackedWidget.setCurrentIndex(1)  #switch to "services page"
        self.textBrowser_3.append(">>Connected to device\n")
        #self.ble_serviceAgent.scan_services(self.ble_controller.ble_device.address())

    def handleServicesFound(self):
        for servicesUids in self.ble_controller.controller.services():
            self.ble_service_uuid = QBluetoothUuid(servicesUids)
            print(self.ble_service_uuid.toString())
            self.foundService = self.ble_controller.controller.createServiceObject(self.ble_service_uuid)
            if self.foundService == None:
                print("Not created")
            self.itemService = QtWidgets.QListWidgetItem()
            self.itemService.setText(self.foundService.serviceName())
            self.itemService.setData(QtCore.Qt.UserRole, self.ble_service_uuid)
            self.listWidget_2.addItem(self.itemService)

    def serviceClicked(self):
        self.pushButtonService.setEnabled(True)

    def handleButtonService(self):
       #self.listWidget_characteristics.clear()
        self.pushButton_Characteristic.setEnabled(False)
        self.ble_controller.readService(self.listWidget_2.currentItem().data(QtCore.Qt.UserRole))

    def handleCharacteristics(self):
        self.listWidget_characteristics.clear()
        
        for obj in self.ble_controller.openedService.characteristics():
            self.itemChar = QtWidgets.QListWidgetItem()
            self.itemChar.setText(obj.uuid().toString())
            self.itemChar.setData(QtCore.Qt.UserRole, obj)
            self.listWidget_characteristics.addItem(self.itemChar)

    def characteristicClicked(self):
        self.pushButton_Characteristic.setEnabled(True)

    def handleButtonChar(self):
        self.karakteristika = self.listWidget_characteristics.currentItem().data(QtCore.Qt.UserRole)

        self.tekst = self.karakteristika.value().data().decode()                #Ispis prve vrijednosti karakteristike odabrane
        self.textBrowser_3.append("Received: {0}".format(self.tekst))

        self.type = QBluetoothUuid(QBluetoothUuid.ClientCharacteristicConfiguration)
        self.descript = self.karakteristika.descriptor(self.type)

        self.array = QByteArray(b'\x01\x00')        #turn on NOTIFY for characteristic

        self.ble_controller.openedService.characteristicChanged.connect(self.updateVal)
        self.ble_controller.openedService.writeDescriptor(self.descript, self.array)    #turon on NOTIFY
    
    def updateVal(self, Charac, newVal):
        self.HRVAL = QByteArray()
        self.HRVAL = newVal
        self.strng = int(self.HRVAL[1].hex(), 16)
        #print(self.strng)
        self.textBrowser_3.append("Heart rate : {0}".format(self.strng))
        
    def updateOutput(self, message):
        self.textBrowser_2.append(message)

    def clearOutput(self):
        self.textBrowser_2.clear()

    def updateOutput2(self, message):
        self.textBrowser_3.append(message)

    def clearOutput2(self):
        self.textBrowser_3.clear()

    def errorHandle(self, errMessage):
        print("Error handle\n")                 #debug
        print("{0}".format(errMessage.toString()))  #debug
        self.textBrowser_2.append(">>ERROR\n")

def run():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()