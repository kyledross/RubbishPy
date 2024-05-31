# RubbishPy
A Python implementation of a Von Neumann-architecture computer emulator.  
Refer to LICENSE.txt for license information.
 

## Introduction
RubbishPy is a Python-based emulator of a Von Neumann architecture computer.  It is based on a previous emulator called *RubbishVM*.

## Purpose
This project serves two purposes:
1. To provide an example of emulating a Von Neumann architecture computer in Python, and
2. To provide myself with a project that I am interested in that I can use to learn Python.

This is by no means a perfect design or implementation.  But, it works.

## Requirements
RubbishPy requires the following:
Python 3.11 or later.  
PyGame 2.5.2 or later required (pip install pygame).

RubbishPy was developed with JetBrains PyCharm.  

## Running RubbishPy in terminal
python3 main.py  {options}  

example:  
*cd RubbishPy/src*  
*python3 main.py --compiler address=0 size=1024 program=../Programs/typewriter.txt --processor --console width=80 height=25 address=1024 interrupt=2*

