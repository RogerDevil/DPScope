# DPScope

This is a driver for the 
[DPScope II](http://dpscope.freevar.com/overview_ii.html) oscilloscope. It 
had only Windows software, but a relatively simple serial protocol (see 
[the download page](http://dpscope.freevar.com/downloads.html) for the 
related DPScope).

This software is branched from 
[pepijndevos' code](https://github.com/pepijndevos/DPScope). It has been 
updated to work with Python3, and as of 12/3/2022, this app currently 
captures data in the Datalog mode, but does the measurements do not scale 
accurately.

## Usage

Install [usb serial driver](http://www.ftdichip.com/Drivers/VCP.htm)

    $ python dpscope/gui.py

![screenshot](https://raw.github.com/pepijndevos/DPScope/master/screenshot.png)

## License

Copyright (C) 2012 Pepijn de Vos

Distributed under the Eclipse Public License.
