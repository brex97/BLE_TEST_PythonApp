import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtBluetooth import QBluetoothUuid
from package.gui import Ui_MainWindow
from package.ble_utils.Scan import BLE_Scanner
from package.ble_utils.Controller import BLE_Controller
from package.ble_utils.ServiceDiscovery import BLE_ServiceAgent

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.ble_scanner = BLE_Scanner()
        self.ble_controller = BLE_Controller()
        #self.ble_serviceAgent = BLE_ServiceAgent()

    #Event signals
        self.listWidget.itemClicked.connect(self.selectedFromList)
        self.pushButton_clearOut.clicked.connect(self.clearOutput)
        self.pushButton_clearOut_2.clicked.connect(self.clearOutput2)
        self.pushButton_Disconnect.clicked.connect(self.handleButtonDisconnect)
        self.pushButtonService.clicked.connect(self.handleButtonService)
        #BLE Scanner events
        self.pushButtonScan.clicked.connect(self.handleButtonScan)
        self.ble_scanner.discoveryAgent.finished.connect(self.updateList)
        self.ble_scanner.discoveryAgent.error.connect(self.errorHandle)
        self.ble_scanner.scannerOutputMessage.connect(self.updateOutput)
        #BLE Controller events
        self.ble_controller.controllerOutputMessage.connect(self.updateOutput2)
        self.pushButton_Conn.clicked.connect(self.handleButtonConn)
        self.ble_controller.controllerConnected.connect(self.handleDeviceConnected)
        self.ble_controller.serviceFound.connect(self.handleServicesFound)
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
        self.textBrowser_4.clear()  #page 2 char browser
        self.pushButton_Conn.setEnabled(False)

    def handleDeviceConnected(self):
        print("Changing page\n")
        self.stackedWidget.setCurrentIndex(1)  #switch to "services page"
        self.textBrowser_3.append(">>Connected to device\n")
        #self.ble_serviceAgent.scan_services(self.ble_controller.ble_device.address())

    def handleServicesFound(self, service):
        self.ble_service_uuid = QBluetoothUuid(service)
        self.itemService = QtWidgets.QListWidgetItem()
        self.itemService.setText(self.ble_service_uuid.toString())
        self.itemService.setData(QtCore.Qt.UserRole, self.ble_service_uuid)
        self.listWidget_2.addItem(self.itemService)

    def handleButtonService(self):
       #self.listWidget_characteristics.clear()
        self.ble_controller.readService(self.listWidget_2.currentItem().data(QtCore.Qt.UserRole))

    def handleCharacteristics(self):
        self.listWidget_characteristics.clear()
        
        for obj in self.ble_controller.openedService.characteristics():
            self.itemChar = QtWidgets.QListWidgetItem()
            self.itemChar.setText(obj.name())
            self.itemChar.setData(QtCore.Qt.UserRole, obj)
            self.listWidget_characteristics.addItem(self.itemChar)

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