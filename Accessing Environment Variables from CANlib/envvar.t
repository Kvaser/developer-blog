
envvar {
  char Message[128];
  int Severity;
  int HostIdRequest;
  int HostIdConnected;
}

variables {
  Timer delay_timer;
  // We hold the connected host id in a local variable so only we can change the value.
  int hostIdConnected;
}

void setHostIdConnected (int value)
{
  hostIdConnected = value;
  envvarSetValue(HostIdConnected, value);
}

on Timer delay_timer {
  printf("Signal that we are ready to accept connections.\n");
  setHostIdConnected(0);
}

on start {
    // Host id 1 signals that the device is busy
    setHostIdConnected(1);
    // Our device is not accepting any connections during a simulated 3 second boot
    delay_timer.timeout = (3000);  // Milliseconds
    timerStart(delay_timer);
  }

on stop {
    // Signal that we do not accept any new connections
    setHostIdConnected(1);
  }

// Print incoming messages
on envvar Message {
  char msg[128];
  int severity;
  envvarGetValue(Message, msg);
  envvarGetValue(Severity, &severity);
  printf("Severity: %d - %s\n", severity, msg);
}

// Someone wanted to connect
on envvar HostIdRequest {
  int hostId;
  envvarGetValue(HostIdRequest, &hostId);
  if (hostId == 0) {
    // When host id is zero, this is actually a disconnect request
    setHostIdConnected(0);
  } else if (hostIdConnected == 0) {
    // We are free to take this connection request.
    // Accept it by setting hostIdConnected to the id of the requesting host
    setHostIdConnected(hostId);
  }
}

// Make sure that no one else changes the HostIdConnected variable
on envvar HostIdConnected {
  int hostId;
  envvarGetValue(HostIdConnected, &hostId);
  if (hostId != hostIdConnected) {
    // Update the envionment variable to reflect current state
    envvarSetValue(HostIdConnected, hostIdConnected);
  }
}
