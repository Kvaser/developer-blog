import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvaMemoLibXml
import kvDevice

# Connect to our Kvaser Memorator Pro 5xHS with EAN 00778-9
dev = kvDevice.kvDevice(ean="73-30130-00778-9")
print dev

# Open the device
dev.memoOpen()

# Initialize the SD card with default values
dev.memo.deviceFormatDisk()

# Close the device
dev.memoClose()

xl = kvaMemoLibXml.kvaMemoLibXml()

# Read in the XML configuration file
with open("logall.xml", 'r') as myfile:
    config_xml = myfile.read()

# Convert the XML configuration to a binary configuration
config_lif = xl.kvaXmlToBuffer(config_xml)

# Open the device and write the configuration
dev.memoOpen()
dev.memo.kmfWriteConfig(config_lif)

# Close the device
dev.memoClose()
