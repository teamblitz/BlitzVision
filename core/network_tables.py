import time
from networktables import NetworkTables


NetworkTables.getDefault().initialize(server='10.20.83.2')
NetworkTables.initialize(server='10.20.83.2')
print("NT Client Established")

