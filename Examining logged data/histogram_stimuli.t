
// This script creates CAN messages (defined in histogram.dbc) as stimuli for histogram.t
//
// This script should be loaded on slot 1
// E.g. by issuing the command
// tutil.exe -channel=0 -slot=1 -load histogram_stimuli.txe -start -listen -1

variables {
  const char time_stamp[] = "Time-stamp: <2012-11-19 10:55:57 extmc>\n";

  typedef struct {
    float min;
    float max;
  } range_t;

  typedef struct {
    int   id;
    int   min_delay_in_ms;
    int   max_delay_in_ms;
    int   num_sent;
    Timer timer;
  } tx_ctrl_t;

  typedef struct {
    range_t range;
    tx_ctrl_t tx;
  } stim_ctrl_t;

  stim_ctrl_t ECM_001_ctrl;  // EngineSpeed
  stim_ctrl_t LIM_002_ctrl;  // Load
  stim_ctrl_t ECM_003_ctrl;  // EngineTemp
  stim_ctrl_t ECM_004_ctrl;  // Fuel

  const int can_bitrate = canBITRATE_1M;

  // workaround for compiler restriction
  // const onOff[] = "on\0off";
  char onOff[7] = "on_off";

  const int False = 0;
  const int True  = 1;
}

// Returns a floating point value in the range min - max (inclusive)
float randomFloat (float min, float max, int verbose)
{
  float value = random(1000000001)/1000000000.0 * (max - min) + min;

  if (verbose) {
    printf("randomFloat %f (%f - %f).\n",value, min, max);
  }
  if (value > max || value < min) {
    printf("ERROR: Wrong randomFloat %f < %f < %f not true.\n", min, value, max);
    value = min + max / 2;
  }
  return value;
}

// Returns an integer value in the range min - max (inclusive)
int randomInt (int min, int max, int verbose)
{
  return (int) randomFloat((float)min, (float)max, verbose);
}

// Returns 0 if the transmitter is inactive, otherwise returns the number of
// milliseconds until the transmission is due
int txIsActive(tx_ctrl_t tx)
{
  int ms = timerIsPending(tx.timer);
  printf("%d ms\n", ms);
  return ms;
}

// Activate the transmitter, this will make the transmitter send a single
// value (within the limits setup) within the predefined timedelay.
void txActivate(tx_ctrl_t tx, int verbose)
{
  tx.timer.timeout = randomInt(tx.min_delay_in_ms, tx.max_delay_in_ms, verbose);
  timerStart(tx.timer);
}

// Deactive the transmitter, no further messages will be sent.
void txDeactivate(tx_ctrl_t tx)
{
  timerCancel(tx.timer);
}

// Helper function, get random value within range and reactivate transmit timer
float prepareMsg (stim_ctrl_t ctrl, int verbose)
{
  float value = randomFloat(ctrl.range.min, ctrl.range.max, verbose);
  ctrl.tx.num_sent++;
  txActivate(ctrl.tx, verbose);
  if (verbose) {
    printf("prepareMsg: value %f (%d)\n", value, (int) value);
  }
  return value;
}

// When a timer expires, send the corresponding message with a random value
// and reactivate the message transmitter.
on Timer ECM_001
{
  CanMessage_ECM_001 msg;
  msg.EngineSpeed.Phys = (int) prepareMsg(ECM_001_ctrl, 0);
  printf("send speed ECM_001 %d\n", msg.EngineSpeed.Phys);
  canWrite(msg);
}

on Timer LIM_002
{
  CanMessage_LIM_002 msg;
  msg.Load.Phys = prepareMsg(LIM_002_ctrl, 0);
  printf("send load LIM_002 %f\n", msg.Load.Phys);
  canWrite(msg);
}

on Timer ECM_003
{
  CanMessage_ECM_003 msg;
  msg.EngineTemp.Phys = prepareMsg(ECM_003_ctrl, 0);
  printf("send temp ECM_003 %f\n", msg.EngineTemp.Phys);
  canWrite(msg);
}

on Timer ECM_004
{
  CanMessage_ECM_004 msg;
  msg.Fuel.Phys = prepareMsg(ECM_004_ctrl, 0);
  printf("send Fuel ECM_004 %f\n", msg.Fuel.Phys);
  canWrite(msg);
}

// Initialise by seting min and max values
void rangeInit (range_t range, float min, float max)
{
  range.min = min;
  range.max = max;
}

// Initialise by seting min and max intermessage delays and set up timer handler
void txInit(tx_ctrl_t tx, const char timer_hook[], int min_delay_in_ms, int max_delay_in_ms)
{
  tx.num_sent        = 0;
  tx.min_delay_in_ms = min_delay_in_ms;
  tx.max_delay_in_ms = max_delay_in_ms;
  timerSetHandler(tx.timer, timer_hook);
}

// Initialise our message transmitters
void init_stimuli_ctrl (void)
{
  rangeInit(ECM_001_ctrl.range, 0.0, 6000.0);
  txInit(ECM_001_ctrl.tx, "ECM_001", 10, 2000);

  rangeInit(LIM_002_ctrl.range, 0.0, 100.0);
  txInit(LIM_002_ctrl.tx, "LIM_002", 1000, 10000);

  rangeInit(ECM_003_ctrl.range, -60.0, 200.0);
  txInit(ECM_003_ctrl.tx, "ECM_003", 10, 500);

  rangeInit(ECM_004_ctrl.range, 0.0, 300.0);
  txInit(ECM_004_ctrl.tx, "ECM_004", 500, 1000);
}


on start {
  printf("Starting histogram stimuli program in slot.\n");
  init_stimuli_ctrl();

  // set up can bus and go buson
  canSetBitrate(can_bitrate);
  canSetBusOutputControl(canDRIVER_NORMAL);
  canBusOn();

  // workaround for compiler restriction
  onOff[2] = '\0';

  txActivate(ECM_001_ctrl.tx, 1);
  txActivate(LIM_002_ctrl.tx, 0);
  txActivate(ECM_003_ctrl.tx, 0);
  txActivate(ECM_004_ctrl.tx, 0);
  printf("All sending is now enabled\n");
}

on stop {
  printf("Stopping histogram stimuli program.\n");
  printf("Number of messages sent, ECM_001:%d, LIM_002:%d, ECM_003:%d, ECM_004:%d.\n",
         ECM_001_ctrl.tx.num_sent,
         LIM_002_ctrl.tx.num_sent,
         ECM_003_ctrl.tx.num_sent,
         ECM_004_ctrl.tx.num_sent);
  canBusOff();
}

// helper function to toggle activation of message sending.
int txToggle(tx_ctrl_t tx, int verbose)
{
  if (txIsActive(tx)) {
    txDeactivate(tx);
    return 3;  // pointing at off in onoff string
  } else {
    txActivate(tx, verbose);
    return 0;
  }
}

// keys to toggle message sending
on key 's' {
  printf("Speed sending is now %s.\n", onOff + txToggle(ECM_001_ctrl.tx, 1));
}

on key 'l' {
  printf("Load sending is now %s.\n", onOff + txToggle(LIM_002_ctrl.tx, 0));
}

on key 't' {
  printf("EngineTemp sending is now %s.\n", onOff + txToggle(ECM_003_ctrl.tx, 0));
}

on key 'f' {
  printf("Fuel sending is now %s.\n", onOff + txToggle(ECM_004_ctrl.tx, 0));
}

on key 'a' {
  static int all_on = True;

  if (all_on) {
    txDeactivate(ECM_001_ctrl.tx);
    txDeactivate(LIM_002_ctrl.tx);
    txDeactivate(ECM_003_ctrl.tx);
    txDeactivate(ECM_004_ctrl.tx);
    printf("All sending is now disabled\n");
    all_on = False;
  } else {
    txActivate(ECM_001_ctrl.tx, 1);
    txActivate(LIM_002_ctrl.tx, 0);
    txActivate(ECM_003_ctrl.tx, 0);
    txActivate(ECM_004_ctrl.tx, 0);
    printf("All sending is now enabled\n");
    all_on = True;
  }
}

on key 'q' {
  printf("Stopping slot 0 (histogram.t).\n");
  scriptStop(0); // slot 0
  printf("Stopping slot 1 (this program, histogram_stimuli.t).\n");
  scriptStop(1); // slot 1
}


on key '?' {
  printf("\n Histogram stimuli program\n");
  printf("=============================\n");
  printf("%s", time_stamp);
  printf(" ? - Print this help\n");
  printf(" a - Toggle all sending\n");
  printf(" s - Toggle Speed sending (current %d)\n",
         timerIsPending(ECM_001_ctrl.tx.timer));
  printf(" l - Toggle Load sending (current %d)\n",
         timerIsPending(LIM_002_ctrl.tx.timer));
  printf(" t - Toggle Temperature sending (current %d)\n",
         timerIsPending(ECM_003_ctrl.tx.timer));
  printf(" f - Toggle Fuel sending (current %d)\n",
         timerIsPending(ECM_004_ctrl.tx.timer));
  printf(" q - Quit\n");
}
