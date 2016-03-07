import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvmlib


def verifyLioVersion():
    ml = kvmlib.kvmlib()

    # Our SD card is mounted under E:, so our LOG00000.KMF can
    # be opened from here
    filename = "E:\\LOG00000.KMF"

    try:
        # Open the SD card
        # We have firmware version 3.0 in the device this SD card will
        # be inserted into, this means that the FW is using Lio Data
        # Format v5.0 and we should use kvmDEVICE_MHYDRA_EXT as
        # the deviceType
        lioDataFormat = ml.kmfOpenEx(filename,
                                     deviceType=kvmlib.kvmDEVICE_MHYDRA_EXT)
        print "Lio Data Format v%s" % lioDataFormat

        # Close SD card
        ml.close()

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


def readLogFiles():
    import glob
    import os

    ml = kvmlib.kvmlib()

    # Our SD card is mounted under E:, so our LOG00000.KMF can
    # be opened from here
    filename = "E:\\LOG00000.KMF"

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

    # Open the SD card
    # We have earlier verified that the SD card is using Lio Data Format v5.0
    # and we should use kvmDEVICE_MHYDRA_EXT as the deviceType
    ml.kmfOpen(filename, deviceType=kvmlib.kvmDEVICE_MHYDRA_EXT)

    # Read number of recorded logfiles
    fileCount = ml.logFileGetCount()
    print "Found %d file%s on card:" % (fileCount,
                                        "s" if fileCount > 1 else "")

    # Loop through all logfiles and write their contents to .kme50 files
    for fileIndx in range(fileCount):
        eventCount = ml.logFileMount(fileIndx)
        print "\tFile %3d: %10d events" % (fileIndx, eventCount)
        logEvent = ml.logFileReadEventLogFormat()

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
    import glob
    import os
    import shutil

    # Our SD card is mounted under E:, so our LOG00000.KMF can
    # be opened from here
    filename = "E:\\LOG00000.KMF"

    for file in glob.glob(os.path.join(os.path.dirname(filename), "*")):
        if(os.path.splitext(file)[1].lower() == '.kmf'
           or file.lower() == 'param.lif'
           or file.lower() == 'database.bin'):
            print "Skipping %s" % file
        else:
            print "Copying %s" % file
            shutil.copy(file, ".")


print "Verify Lio data format version..."
verifyLioVersion()

print "Read log files..."
readLogFiles()

print "Get config..."
readConfig()

print "Done"
