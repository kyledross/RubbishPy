# Rubbish Real-Time Clock Device

### Purpose

The real-time clock device serves two purposes.

The first purpose is to provide a real-time count of seconds since Thursday 1 January 1970 00:00:00 UT (the Unix
epoch). This is a single value at a single address in memory space. The second purpose is to provide an
interrupt at half-second intervals that software can subscribe to in order to do time-specific operations.

### Usage

Create the device by adding it to the Rubbish command-line as follows:
`--rtc address={address} interrupt={interrupt} interval={milliseconds}`

This will create the device, and once the machine is running, the number of seconds in since the Unix epoch began
will be available at {address}. Every {milliseconds} (approximately), an interrupt of number {interrupt} will
be generated for software to respond to.

**Note**: The Rubbish processor gives lower interrupt numbers the highest priority, so choose the interrupt
number accordingly. Systems where timing is not as critical should use higher interrupt numbers so that
more important interrupts are handled firstly.


