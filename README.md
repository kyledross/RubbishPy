# RubbishPy
A Python implementation of a Von Neumann-architecture computer emulator.  
Refer to LICENSE.txt for license information.
 

## Introduction
RubbishPy is a Python-based emulator of a Von Neumann architecture computer.

## Purpose
This project serves two purposes:
1. To provide an example of emulating a Von Neumann architecture computer in Python, and
2. To provide myself with a project that I am interested in that I can use to learn Python.

This is by no means a perfect design or implementation. You're bound to see things that are less-than-stellar. Maybe even hideous.

But, it works.

## Requirements
RubbishPy requires the following:
Python 3.11 or later.  
Python package PyGame 2.5.2 or later required (pip install pygame).
Python package Numpy 1.26 or later required (pip install numpy).

RubbishPy was developed with JetBrains PyCharm.  

## Running RubbishPy in terminal
python3 main.py  {options}  

example:  

```commandline
cd RubbishPy/src
```
```commandline
python3 main.py --compiler address=0 size=1024 program=../Programs/typewriter.txt --processor --console width=80 height=25 address=1024 interrupt=2
```
## Adding a new device

... more to come here.

## Why "RubbishPy"?
The "Rubbish" part of the name is inspired by an alarm clock that my Cornish wife had, which she claimed was "rubbish" because it couldn't keep time properly.  Considering this project is primarily a learning exercise for me, and that it is not a perfect implementation, I thought the name was fitting.

The "Py" suffix is to distinguish it as the Python version of the Rubbish emulator, as there were previous unpublished versions that I had written in Visual Basic 6 and VB.Net.
