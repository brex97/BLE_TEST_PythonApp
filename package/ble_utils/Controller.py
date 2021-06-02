from PyQt5.QtBluetooth import QLowEnergyController, QLowEnergyService, QBluetoothUuid
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class BLE_Controller(QObject):
    controllerOutputMessage = pyqtSignal(str)
    controllerConnected = pyqtSignal()
    servicesFound = pyqtSignal()
    serviceOpened = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)

    def connectDevice(self, dev):
        self.ble_device = dev
        print("Connnecting to {0}".format(self.ble_device.name()))      #debug
        self.controllerOutputMessage.emit(">>Connecting to " + self.ble_device.name())
        
        self.controller = QLowEnergyController.createCentral(self.ble_device)    
        
        self.controller.connected.connect(self.deviceConnected)
        self.controller.disconnected.connect(self.deviceDisconnected)
        self.controller.error.connect(self.errorReceived)
        self.controller.serviceDiscovered.connect(self.addLEservice)
        self.controller.discoveryFinished.connect(self.serviceScanDone)

        self.controller.setRemoteAddressType(QLowEnergyController.PublicAddress)
        self.controller.connectToDevice()

    def disconnect(self):
        self.controller.disconnectFromDevice()
        #del self.controller

    def deviceConnected(self):
        print("Device connected\n")             #debug
        self.controllerConnected.emit()
        self.controller.discoverServices()

    def addLEservice(self, servUid):        #debugging purpose function, can delete later
        self.serviceUid = servUid
        print("Found service {0}\n".format(self.serviceUid.toString()))

    def errorReceived(self, errMessage):
        print("error ")
        print("{0}\n".format(errMessage.toString()))
        self.controllerOutputMessage.emit(">>ERROR\n")

    def deviceDisconnected(self):
        print("device disconnected\n")
        self.controllerOutputMessage.emit(">>Device disconnected - Press Disconnect?\n")

    def serviceScanDone(self):
        print("Service scan done\n")
        self.servicesFound.emit()
        self.controllerOutputMessage.emit(">>Services scan done\n")

    def readService(self, ble_service_UID):
        self.openedService = self.controller.createServiceObject(ble_service_UID)
        if self.openedService == None:
            print("ERR: Cannot open service\n")
        print(self.openedService.serviceName() + '\n')

        if (self.openedService.state() == QLowEnergyService.ServiceDiscovered):
            self.handleServiceOpened()
            
        elif (self.openedService.state() == QLowEnergyService.DiscoveryRequired):
            self.openedService.stateChanged.connect(self.handleServiceOpened)
            self.openedService.discoverDetails()
        else:
            print("Cannot discover service\n")

    def handleServiceOpened(self):
        if (self.openedService.state() == QLowEnergyService.ServiceDiscovered):
            self.serviceOpened.emit()

    
