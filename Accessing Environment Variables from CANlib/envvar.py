
## This code is part of a Kvaser blog article located at  
## http://www.kvaser.com/developer-blog/accessing-environment-variables-from-canlib-2-of-3/

import os
import sys
sys.path.append("C:/temp/Canlib_SDK_2015-08-17/Samples/Python")

## If the Python code cannot find the correct dll (32 vs 64 bit) for your system, 
## (e.g. kvmlib.dll) you can point KVDLLPATH to the correct location with the following:
# os.environ["KVDLLPATH"] = "C:/dev/canlib/Lib/bin"

import time
import kvDevice

# Define some values and messages to send to our device
# In order to hide these secret messages, we write them encoded ;-)
messages = [(1, "-Jung unccraf gb n sebt'f pne jura vg oernxf qbja?"),
            (2, "-Vg trgf gbnq njnl."),
            (3, "-Jul jnf fvk fpnerq bs frira?"),
            (4, "-Orpnhfr frira 'ngr' avar."),
            (5, "-Jung vf gur qvssrerapr orgjrra fabjzra naq fabjjbzra?"),
            (6, "-Fabjonyyf."),
            (7, "-Jurer qvq lbh svaq gurfr?"),
            (8, "-uggc://jjj.ynhtusnpgbel.pbz/wbxrf/jbeq-cynl-wbxrf")]


# We will be using the first Eagle device found connected to the PC
# For an introduction to the kvDevice object, see
# http://www.kvaser.com/developer-blog/object-oriented-approach-accessing-kvaser-device-python-3-3/
eagle_ean = "73-30130-00567-9"
dev = kvDevice.kvDevice(ean=eagle_ean)

# Open a handle to the device
dev.open()

# Load the t program into slot 0
dev.channel.scriptLoadFile(0, "envvar.txe")

# Start the program in slot 0
dev.channel.scriptStart(0)

# Our protocol states that we should wait until HostIdConnected is zero before trying to connect
print "Waiting for device to be free..."
# All calls to the kvScriptEnvarOpen() and kvScriptEnvvarGetXXX() functions are hidden in the
# envvar class inside canlib.py. Here we can access it directly with dev.channel.envvar.YYY
while dev.channel.envvar.HostIdConnected != 0:
    time.sleep(0.2)

# Now we try to connect by writing our unique id into the environment variable HostIdRequest.
# We wait until our connection was accepted, i.e. HostIdConnected contains our id.
print "Requesting connection..."
myHostId = 42
print "Waiting for device to connect..."
while dev.channel.envvar.HostIdConnected != myHostId:
    if dev.channel.envvar.HostIdConnected == 0:
        print "Requesting connection..."
        if dev.channel.envvar.HostIdRequest != myHostId:
            dev.channel.envvar.HostIdRequest = myHostId
        time.sleep(0.2)
print "Connected!"

# Start sending our messages to the device
for (severity, message) in messages:
    print "Sending message %d" % severity
    dev.channel.envvar.Severity = severity
    dev.channel.envvar.Message = message.encode('rot13')
    time.sleep(4)

print "Disconnect..."
dev.channel.envvar.HostIdRequest = 0

# Stop the script running in slot 0.
dev.channel.scriptStop(0)
