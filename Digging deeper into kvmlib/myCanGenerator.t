// This script is intended to be used to check a configuration set as:
//
// [ ] Log everything
// [ ] FIFO mode
// Power settings: 5 Time to live after CAN power disconnected, in seconds
//
// CAN 1 should be connected to CAN 2
//
// Triggers:
// CAN1 Trigger1 Timer [4s] : Start logging, post-trigger=0
// CAN1 Trigger2 Timer [7s] : Stop logging,  post-trigger=3000
//
// Script sends msg id:
// Id 1 at 0.5s
// Id 2 at 1.5s
// Id 3 at 2.5s
// Id 4 at 3.5s
// Id 5 at 4.5s
// ... and so on until
// Id 11 at 10.5s

variables {
  // Base channel. CAN messages will be sent on channel ch and received on
  // channel ch + 1
  const int ch = 0;

  // The singleshot timer is used to get a delay before the first CAN message
  // is sent.
  Timer singleshot;

  // The periodic timer is then used between each CAN message
  Timer periodic;

  // The message id of the sent CAN messages, will be incremented
  int msgId = 1;

  // The CAN message to be sent
  CanMessage msg;
}

on Timer singleshot {
  // Start the periodic timer to send 10 more CAN messages
  timerStart(periodic, 10);

  // After using the current CAN message id, increment before next use
  msg.id    = msgId++;
  msg.flags = 0;
  msg.dlc   = 8;
  msg.data  = "\x12\x21\x13\x31\x22\x34\x41\x15";

  // Send CAN message
  canWrite(ch, msg);
  printf("Single shot MsgId: %d\n", msg.id);
}

on Timer periodic {
  // After using the current CAN message id, increment before next use
  msg.id = msgId++;

  // Send CAN message
  canWrite(ch, msg);
  printf("Periodic MsgId: %d\n", msg.id);
  if (!timerIsPending(periodic)) {
    printf("Timer done!");
  }
}

on start {
  printf("Starting testlogger companion script\n");

  // Setup the two CAN channels and go bus on.
  // This will override the settings in the binary configuration,
  // most notably the channels will no longer be in silent mode.
  canBusOff(ch);
  canBusOff(ch + 1);
  canSetBitrate(ch, canBITRATE_1M);
  canSetBitrate(ch + 1, canBITRATE_1M);
  canSetBusOutputControl(ch, canDRIVER_NORMAL);
  canSetBusOutputControl(ch + 1, canDRIVER_NORMAL);
  canBusOn(ch);
  canBusOn(ch + 1);

  singleshot.timeout = 500;   // Wait half a second
  periodic.timeout   = 1000;  // One second period

  // Start the singleshot timer to send the first CAN message
  timerStart(singleshot);
  printf("Start periodic transmission\n");
}

on stop {
  printf("Stopping script\n");
  canBusOff(ch);
  canBusOff(ch + 1);
}
