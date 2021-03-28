from PyQt5.QtBluetooth import QBluetoothServiceDiscoveryAgent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class BLE_ServiceAgent(QObject):
    def __init__(self):
        QObject.__init__(self)
        print("Creating service agent\n")

    def scan_services(self, address):
        self.service_agent = QBluetoothServiceDiscoveryAgent(address)

        self.service_agent.serviceDiscovered.connect(self.foundService)
        print("starting agent\n")
        self.service_agent.start()

    def foundService(self, m_service):
        print("Found service" + m_service.serviceName() + '\n')