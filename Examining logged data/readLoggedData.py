
  import os
  import sys
  sys.path.append("C:/temp/Canlib_SDK_v5.11/Samples/Python")
  os.environ["KVDLLPATH"] = "C:/dev/canlib/Lib/bin_x64"

  import datetime
  import glob
  import kvDevice
  import kvmlib
  import ctypes

  def raw2float(data):
      # This function interprets the raw value as a float and converts it into a Python integer
      # The data is defined in the database as:
      # type: float, format: Intel, start bit: 0, length: 32, factor: 1, offset: 0
      data_hex_str = "0x%02x%02x%02x%02x" % (data[3], data[2], data[1], data[0])
      i = int(data_hex_str, 0)
      cp = ctypes.pointer(ctypes.c_int(i))
      fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_float))
      return fp.contents.value

  def getEventTime(startTime, event):
      # The event timestamp is given in nanoseconds. This function converts it to
      # seconds, and returns the sum of startTime and event time (as a Python
      # datetime object).
      offsetInSeconds = event.timeStamp/1000000000.0
      return startTime + datetime.timedelta(seconds=offsetInSeconds)

  def readEventsFromDevice(ean, channel, msgId):
      # Read all events from device matching ean, channel and msgId
      print "Open device..."
      # Create a device with the selected EAN number
      dev = kvDevice.kvDevice(ean=ean)
      # Open a device that matches our criteria (EAN)
      dev.memoOpen()
      # Mount the log files so we can acces them
      dev.memo.deviceMountKmf()
      # Read out how many log files that are availible on the card
      fileCount = dev.memo.logFileGetCount()
      print "Found %d file%s on card:" % (fileCount, "s" if fileCount > 1 else "")

      # Now we read all events from each file found on the card.
      for fileIndx in range (fileCount):
          # When mounting the logfile, we get an aproximate value back
          eventCount = dev.memo.logFileMount(fileIndx)
          print "File %3d: Contains less than %d events" % (fileIndx, eventCount)
          # We read out when the logging was started
          startTime = dev.memo.logFileGetStartTime()
          print "Logging started at %s\n" % startTime

          while True:
              # Read events from the log file, when no more events are availible,
              # 'None' will be returned
              event = dev.memo.logReadEventEx()
              if event is None:
                  break

              # We are only interested in events that are log messages
              if type(event) is kvmlib.logMsg:
                  # Also filter on message id and channel number
                  if event.id == msgId and event.channel == channel:
                      # We know the message data is a float, so convert it to a
                      # more usable format
                      value = raw2float(event.data)
                      # Now filter on the value
                      if value > 159 and value < 163:
                          # Get the time of the event
                          eventTime = getEventTime(startTime, event)
                          print "%s, Msg id %d value %f on channel %d:" % (eventTime, msgId, value, channel)
                          #print event

          print "\n"
          # Dismount to free up resources
          dev.memo.logFileDismount()
      # We are done, close the kvmlib handle to device
      dev.memoClose()

  def readTimedEventsFromDevice(ean, channel, msgId, firstTime, lastTime):
      # Read all events from device matching ean, channel, msgId and have a
      # timestamp between firstTime and lastTime (inclusive)
      print "Open device..."
      # Create a device with the selected EAN number
      dev = kvDevice.kvDevice(ean=ean)
      # Open a device that matches our criteria (EAN)
      dev.memoOpen()
      # Mount the log files so we can acces them
      dev.memo.deviceMountKmf()
      # Read out how many log files that are availible on the card
      fileCount = dev.memo.logFileGetCount()
      print "Found %d file%s on card:" % (fileCount, "s" if fileCount > 1 else "")
      # Now we read all events from each file found on the card.
      for fileIndx in range (fileCount):
          # When mounting the logfile, we get an aproximate value back
          eventCount = dev.memo.logFileMount(fileIndx)
          print "File %3d: Contains less than %d events" % (fileIndx, eventCount)
          # We read out when the logging was started
          startTime = dev.memo.logFileGetStartTime()
          print "Logging started at %s\n" % startTime
          while True:
              # Read events from the log file, when no more events are availible,
              # 'None' will be returned
              event = dev.memo.logReadEvent()
              if event is None:
                  break
              # We are only interested in events that are log messages
              if type(event) is kvmlib.logMsg:
                  # Also filter on message id and channel number
                  if event.id == msgId and event.channel == channel:
                      # Filter out log messages that are outside of our time range
                      time = startTime + datetime.timedelta(seconds=event.timeStamp/1000000000.0)
                      if time >= firstTime and time <= lastTime:       #
                          msgId = event.id
                          # We know the message data is a float, so convert it to a
                          # more usable format
                          value = raw2float(event.data)
                          # Get the time of the event
                          eventTime = getEventTime(startTime, event)
                          print "%s, Msg id %d value %f on channel %d:" % (eventTime, msgId, value, channel)
          print "\n"
          # Dismount to free up resources
          dev.memo.logFileDismount()
      # We are done, close the kvmlib handle to device
      dev.memoClose()

  # Read all events with message id 503, on the first channel, from the first
  # device with EAN 73-30130-00567-9.
  readEventsFromDevice(ean="73-30130-00567-9", channel=0, msgId=503)

  # Read all events with message id 503, on the first channel, from the first
  # device with EAN 73-30130-00567-9 that was recorded between 2015-05-17 12:49:10
  # and 2015-05-17 12:49:20.
  startTime = datetime.datetime.strptime("2015-05-17 12:49:10", "%Y-%m-%d %H:%M:%S")
  endTime = datetime.datetime.strptime("2015-05-17 12:49:20", "%Y-%m-%d %H:%M:%S")
  print "\nLooking at %s - %s" % (startTime,endTime)
  readTimedEventsFromDevice(ean="73-30130-00567-9", channel=0, msgId=503, firstTime=startTime, lastTime=endTime)
