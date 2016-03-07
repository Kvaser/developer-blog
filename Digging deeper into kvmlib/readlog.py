import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvmlib


def readLogFiles():
    import glob
    import os

    ml = kvmlib.kvmlib()

    # Since our firmware is v3.0 we should be using kvmDEVICE_MHYDRA_EXT
    # as the device type.
    deviceType = kvmlib.kvmDEVICE_MHYDRA_EXT

    # We saw earlier that our device is connected to Card channel number 0
    cardChannel = 0

    # Directory to put the resulting files in
    resultDir = "result"

    # Make sure the result directory exists and is empty
    if os.path.isdir(resultDir):
        files = glob.glob(os.path.join(resultDir, "*"))
        for f in files:
            os.remove(f)
    else:
        os.mkdir(resultDir)
    os.chdir(resultDir)

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

    # Read number of recorded logfiles
    fileCount = ml.logFileGetCount()
    print "Found %d file%s on card:" % (fileCount,
                                        "s" if fileCount > 1 else "")

    # Loop through all logfiles and write their contents to .kme50 files
    for fileIndx in range(fileCount):
        eventCount = ml.logFileMount(fileIndx)
        print "\tFile %3d: %10d events" % (fileIndx, eventCount)
        logEvent = ml.logFileReadEventLogFormat()
        #
        # The first logEvent contains device information
        memoEvent = logEvent.createMemoEvent()
        sn = memoEvent.serialNumber
        ean_lo = memoEvent.eanLo
        ean_sn = "%05x-%x_%d" % ((ean_lo >> 4) & 0xfffff, ean_lo & 0xf, sn)
        # Add EAN and serial number info to filename
        logfileName = "log_%s_%d.kme50" % (ean_sn, fileIndx)
        ml.kmeCreateFile(logfileName, kvmlib.kvmFILE_KME50)
        while logEvent is not None:
            # Write event to stdout
            print logEvent
            ml.kmeWriteEvent(logEvent)
            # Read next event
            logEvent = ml.logFileReadEventLogFormat()
        ml.kmeCloseFile()

    # Delete all logfiles
    ml.logFileDeleteAll()

    # Close device
    ml.close()


def readConfig():
    import os

    import canlib

    cl = canlib.canlib()

    # We already knew that our device was connected to CANlib channel number 0
    canlibChannel = 0

    # Open the device
    ch = cl.openChannel(channel=canlibChannel)

    # List files on device
    numFiles = ch.fileGetCount()

    if numFiles:
        for i in range(numFiles):
            name = ch.fileGetName(i)
            # Skip known system files
            if (os.path.splitext(name)[1].lower() == '.kmf'
                    or name.lower() == 'param.lif'
                    or name.lower() == 'database.bin'):
                print "Skipping %s" % name
            else:
                # Copy user files to PC
                print "Copying %s" % name
                ch.fileCopyFromDevice(name, name)

    ch.close()

print "Read log files..."
readLogFiles()

print "Get config..."
readConfig()

print "Done"
