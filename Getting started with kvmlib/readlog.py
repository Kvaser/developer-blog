import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvDevice

# Connect to our Kvaser Memorator Pro 5xHS with EAN 00778-9
dev = kvDevice.kvDevice(ean="73-30130-00778-9")
dev.open()
dev.memoOpen()
fileCount = dev.memo.logFileGetCount()
print "Found %d file%s on card:" % (fileCount,
                                    "s" if fileCount > 1 else "")

# Loop through all logfiles and write their contents to stdout
for fileIndx in range(fileCount):
    myEvents = dev.memoReadEvents(fileIndx)
    for event in myEvents:
        print event
    print "\n"

# Delete all logfiles
dev.memo.logFileDeleteAll()

# Close device
dev.memoClose()
dev.close()
