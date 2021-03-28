from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class BLE_Scanner(QObject):  
    scannerOutputMessage = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        self.discoveryAgent = QBluetoothDeviceDiscoveryAgent()
        self.discoveryAgent.setLowEnergyDiscoveryTimeout(5000)

    def scanDevices(self):
        print("Scanning\n")                             #debug
        self.scannerOutputMessage.emit(">>Scanning\n")
        self.discoveryAgent.start()







