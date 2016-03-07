import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvaMemoLibXml


def configureSdCard():
    # Our SD card is mounted under E:, so that is where our
    # binary configuration should be placed.
    filename = "E:\\PARAM.LIF"

    xl = kvaMemoLibXml.kvaMemoLibXml()
    print "kvaMemoLibXml version: v%s" % xl.getVersion()

    # Convert the previously validated XML configuration file
    # and write the resulting binary configuration to SD card
    xl.kvaXmlToFile("config.xml", filename)


def downloadConfig():
    import zipfile

    # Our SD card is mounted under E:
    filename = "E:\\config.zip"

    # Creating zip archive
    with zipfile.ZipFile(filename, mode='w',
                         compression=zipfile.ZIP_DEFLATED) as zipf:
        # Adding files to zip archive
        zipf.write("config.xml")
        zipf.write("myCanGenerator.txe")

print "Configure SD card..."
configureSdCard()

print "Download configuration..."
downloadConfig()

print "Done"
