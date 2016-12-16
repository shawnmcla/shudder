"""Various methods to facilitate time-triggered events."""

import time
import threading
_events = {}

class _TimedEvent:
    _nextId = 0
    def __init__(self, call, interval, once=False):
        _TimedEvent._nextId += 1
        self.eventId = _TimedEvent._nextId
        self.call = call
        self.interval = interval
        self.once = once
        self.expired = False
        self.lastCalled = time.time()
    
    def _call(self):
        self.call()
    
    def call_if_due(self):
        if (time.time() - self.lastCalled) >= self.interval:
            if self.once:
                self.expired = True
            self.lastCalled = time.time()
            self._call()

def register_event(call: "method to call",
                interval: "time between calls in seconds",
                once: "if True, only call once and then discard" = False):
    """Register a method to be called at the specified interval (or after x seconds if once)."""
    event = _TimedEvent(call, interval, once)
    _events[event.eventId] = event
    return event.eventId

def deregister_event(eventId: "Event Id returned from register_event()"):
    """Remove a method from the list of timed events."""
    if eventId in _events:
        del _events[eventId]
        return True
    return False

def _timerLoop():
    """Loop every second, calling TimedEvents which are due."""
    while True:
        keysToDelete = []
        for key in _events.keys():
            _events[key].call_if_due()
            if _events[key].expired:
                keysToDelete.append(key)
        for key in keysToDelete:
            del _events[key]
        time.sleep(1)

def initialize_timed_event_manager():
    """Initialize the Thread for timed event handling."""
    timedEventThread = threading.Thread(target = _timerLoop)
    timedEventThread.start()
    print("Timed event manager started")