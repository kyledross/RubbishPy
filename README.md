# RubbishPy
A Python implementation of RubbishVM
For licensing information, see LICENSE.txt
 

## Introduction

RubbishPy is a Python-based emulator of a Von Neumann architecture computer.  It is based on a previous emulator called *RubbishVM*.

## Requirements
RubbishPy requires Python 3.11 or later.  
RubbishPy requires tkinter for window support in console (apt install python3-tk).  
RubbishPy was developed with JetBrains PyCharm.  

## Running RubbishPy in terminal
python3 ./src/main.py  {options}  

example:  
*cd RubbishPy/src*  
*ex: python3 main.py --compiler address=0 size=1024 program=../Programs/typewriter.txt --processor --consolev2 address=1024 interrupt=2

## History of RubbishPy

### RSA Emulator

Language: Visual Basic 6.0

This was the first attempt at writing an emulator of a computing machine. The name was derived from "Ross System A". It was never really finished, but was an exercise in what NOT to do. Architecturally, it was a single Windows form and devices were coded as methods.  This did not work well.

### RSB Emulator

Language: Visual Basic 6.0

This was the second attempt at writing an emulator and it, too, remained unfinished. The name was derived from "Ross System B". It was the first iteration that incorporated the backplane model, but I had still not really designed it properly (I couldn't decide where the clock tick source should be... directly in the backplane or as a device on the bus?)  It did open up my thinking on how to construct a proper emulation with a backplane with common buses and a clock tick source.

### RSC2000 Emulator

Language: Visual Basic 6.0

This was the third attempt at writing an emulator and was the first to be fully operational. The name was derived from "Ross System C" originally, but upon completion in 2000, the name was changed to "RSC2000".
> "...which was the style at the time"  
> -- Abe Simpson  

This emulator featured the DP2000 processor (_which was the style..._).  It featured no interrupts, so every program had to "poll" memory locations routinely for information.  This kept the system very busy.  A cached DP2000 processor was written that inherited the original and provided an L2 cache, but the L2 cache was blind to memory changes that occurred outside of processor I/O.  This sped up the system considerably, but wasn't very feasible because memory values *do* change (keyboard input, for example).  A bigger performance improvement was made when additional logic was added to the backplane in the form of device controller that would detect the destination of a read or write request on the bus and give the very next emulator clock-tick to that device, followed by an additional clock-tick on the original requesting device. This, in essence, created a DMA-type behavior in the emulator and provided a very big performance boost.

### RSC2008 VM / RubbishVM

Language: Visual Basic.NET

This was the fourth rewrite and was the first to be labelled as a "virtual machine" (albeit an improper name, as it was an emulator).  It started with the name RSC2008, but was renamed to "RubbishVM" in 2012 after being influenced by a clock that my then-girlfriend proclaimed as being "rubbish". It was a complete rewrite with a brand-new processor that was compatible with most DP2000 instructions, but expanded upon them with support for interrupt vectors, stacks, and more registers. It also featured, for the first time, IEEE floating point math instructions. As with the DP2000 processor, a cached version of the Rubbish processor was written that behaves identically to the cache logic of the DP2000 cached processor (which isn't that useful).

The backplane was simplified when it was rewritten, eliminating the device controller logic that enabled the DMA-type behavior. Doing this kept the system simple and makes overall system behavior more predictable.

The VM also included a new interrupt-driven I/O device that combined both the keyboard and console display (the RSC2000 virtual machine had individual keyboard and console devices that were not interrupt-driven and had to be polled).

The RubbishVM project also included an experimental and proof-of-concept BASIC compiler (which was sparsely functional with only rudimentary functionality... mostly PRINT and GOTO).  The compiler would compile to RSC assembly language, which was then compiled to RubbishVM machine code.

### RubbishPy

Language: Python

This is the current incarnation of the Rubbish emulator.  It has been completely rewritten in Python.  It is code-compatible with RubbishVM programs, and offers compatible devices.  With this edition of the emulator, there will be no further development of the prior emulator.  Going forward, new features and functionality will be added to this emulator.
