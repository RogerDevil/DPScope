# DPScope

This is a driver for the 
[DPScope I](http://dpscope.freevar.com/overview.html) oscilloscope. It 
had only Windows software, but a relatively simple serial protocol (see 
[the download page](http://dpscope.freevar.com/downloads.html) for the 
scope).

This software is branched from 
[pepijndevos' code](https://github.com/pepijndevos/DPScope). It has been 
updated to work with Python3, and the long term goal of the project is to 
provide full functionalities as per the windows software. Review the 
release notes to see which features are currently working/not working.

## Usage

Install [usb serial driver](http://www.ftdichip.com/Drivers/VCP.htm)

    $ python dpscope/gui.py

![screenshot](https://raw.github.com/pepijndevos/DPScope/master/screenshot.png)

## License

Copyright (C) 2012 Pepijn de Vos

Distributed under the Eclipse Public License.
