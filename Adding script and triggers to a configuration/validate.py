import sys
sys.path.append("D:/temp/CanlibSDK_5.14/Samples/Python")


import kvaMemoLibXml

xl = kvaMemoLibXml.kvaMemoLibXml()
print "kvaMemoLibXml version: v" + xl.getVersion()

# Read in the XML configuration file
with open("config.xml", 'r') as myfile:
    config_xml = myfile.read()

# Validate the XML configuration
xl.kvaXmlValidate(config_xml)

# Get number of validation messages
(countErr, countWarn) = xl.xmlGetValidationStatusCount()
print "Errors: %d, Warnings: %d" % (countErr, countWarn)

# If we have any validation errors, print those
if countErr != 0:
    code = -1
    while code != 0:
        (code, text) = xl.xmlGetValidationError()
        print "%d: %s" % (code, text)

# If we have any validation warnings, print those
if countWarn != 0:
    code = -1
    while code != 0:
        (code, text) = xl.xmlGetValidationWarning()
        print "%d: %s" % (code, text)

# Exit if we had any validation errors or warnings
if countErr != 0 or countWarn != 0:
    raise Exception('Please fix validation Errors/Warnings.')
