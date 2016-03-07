import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import datetime

import kvaMemoLibXml
import kvmlib


def setDeviceTime():
    ml = kvmlib.kvmlib()

    # Since our firmware is v3.0 we should be using kvmDEVICE_MHYDRA_EXT
    # as the device type.
    deviceType = kvmlib.kvmDEVICE_MHYDRA_EXT

    # We know that our device is connected to Card channel number 0
    cardChannel = 0

    # We have firmware version 3.0 in our device, this means that
    # the FW is using Lio Data Format v5.0 and we should use
    # kvmDEVICE_MHYDRA_EXT as the deviceType
    ml.deviceOpen(memoNr=cardChannel, devicetype=deviceType)

    # Having obtained a kvmHandle, we can now e.g. check the
    # device serial number
    print "Serial number:%d" % ml.deviceGetSerialNumber()

    # Set the real time clock of the device
    ml.deviceSetRTC(datetime.datetime.now())

    # Read the device time
    print "Current device time is %s" % ml.deviceGetRTC()

    # Close device
    ml.close()


def initDevice():
    ml = kvmlib.kvmlib()

    # Since our firmware is v3.0 we should be using kvmDEVICE_MHYDRA_EXT
    # as the device type.
    deviceType = kvmlib.kvmDEVICE_MHYDRA_EXT

    # We saw earlier that our device is connected to Card channel number 0
    cardChannel = 0

    # Open the device
    ml.deviceOpen(memoNr=cardChannel, devicetype=deviceType)

    try:
        # Mount the log area
        lioDataFormat = ml.deviceMountKmf()
        print "Lio Data Format v%s" % lioDataFormat
        # Verify that the LIO data format of the card corresponds to
        # the device type we used when opening the device
        if lioDataFormat != '5.0':
            print "Unexpected Lio Data Format:", lioDataFormat
            if lioDataFormat == '3.0':
                print("This log file can be read if you reopen the"
                      " device as kvmDEVICE_MHYDRA.")
            exit(1)
    except kvmlib.kvmDiskNotFormated:
        print "SD card is not initialized..."
        exit(1)

    # Format the SD Card and reserve 10 MB for configuration files
    # (i.e. DATABASE.BIN) and 1000 MB for our own files.
    print "Initializing SD card..."
    ml.deviceFormatDisk(reserveSpace=10000, dbaseSpace=10)

    # Report info about the disk area allocated for logging
    (diskSize, usedDiskSize) = ml.kmfGetUsage()
    print "Log size: %d MB\nUsed: %d MB" % (diskSize, usedDiskSize)

    # Close the device
    ml.close()


def saveConfig():
    ml = kvmlib.kvmlib()
    xl = kvaMemoLibXml.kvaMemoLibXml()

    # Since our firmware is v3.0 we should be using kvmDEVICE_MHYDRA_EXT
    # as the device type.
    deviceType = kvmlib.kvmDEVICE_MHYDRA_EXT

    # We saw earlier that our device is connected to Card channel number 0
    cardChannel = 0

    # Read in the XML configuration file
    with open("config.xml", 'r') as myfile:
        config_xml = myfile.read()

    # Convert the XML configuration to a binary configuration
    config_lif = xl.kvaXmlToBuffer(config_xml)

    # Open the device and write the configuration
    ml.deviceOpen(memoNr=cardChannel, devicetype=deviceType)
    ml.kmfWriteConfig(config_lif)

    # Close the device
    ml.close()


def copyFiles():
    import zipfile
    import canlib

    # Create Zip archive
    with zipfile.ZipFile("config.zip", mode='w',
                         compression=zipfile.ZIP_DEFLATED) as zipf:
        # Adding files to zip archive
        zipf.write("config.xml")
        zipf.write("myCanGenerator.txe")

    cl = canlib.canlib()

    # We know that our device was connected to CANlib channel number 0
    canlibChannel = 0

    # Open the device and write the zip archive
    ch = cl.openChannel(channel=canlibChannel)
    # Since the SD card is formated using FAT, we should use
    # a 8.3 filename as the target filename
    ch.fileCopyToDevice("config.zip", "config.zip")

    ch.close()

print "Setting device time..."
setDeviceTime()

print "Initialize device..."
initDevice()

print "Save configuration to device..."
saveConfig()

print "Copy files to device..."
copyFiles()

print "Done"
