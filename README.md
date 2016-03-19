# CANToolz
###aka YACHT (Yet Another Car Hacking Tool)
CANToolz is a framework for analysing CAN networks and devices.
This tool based on different modules which can be assembled in pipe together and
can be used by security researchers and automotive/OEM security testers for black-box analysis and etc. 
You can use this software for ECU discovery, MITM testing, fuzzing, bruteforcing, scanning and etc

This platform is a try to unify all needed tricks/tools and other things that you can do with CAN bus in one place.
I have found, that there are many tools available, from Charlie Miller and Chris Valasek tools to UDS/CAN tools by Craig Smith.
They all cool and useful, but it is still difficult to use it in every-day work (al least for me) and you need to modify/code 
a lot of thing to get something you want (MITM, scanners with some logic). That's why I have this software. If more people can 
contribute into modules, than more useful this thing can be. It gives (almost) an easy way to add your modules and use "extended" version for your needs
(like custom brutforcers for chosen ECU and etc). Just for fun... finally. No Forbs, Wires  or other big noise needed around this. 
Just want to have a good tool and people around.

"I don't get why everyone releases new "car hacking tools" all the time.  @nudehaberdasher and I released ours in 2013 and they work fine." (c) Charlie Miller (‏@0xcharlie)

"Looking for our car hacking tools / data / scripts? http://illmatics.com/content.zip " (c) Chris Valasek ‏@nudehaberdasher

## Using a Hardware

CANToolz can work with CAN network by using next hardware:

1. [USBtin](http://www.fischl.de/usbtin/)
2. [CANBus Triple](https://canb.us/)

## Modules

- hw_CANBusTriple  - IO module for CANBus Triple HW
- hw_USBtin        - IO module forUSBtin
- mod_firewall     - module for blocking CAN message by ID
- mod_fuzz1        - Simple 'Proxy' fuzzer  (1 byte) Can be combined with gen_ping/gen_replay
- mod_printMessage - printing CAN messages
- mod_stat         - CAN messages statistic (with .csv file output)
                     Analyses option (c mod_stat a) will try to find UDS/ISO TP messages
- gen_ping         - generating CAN messages with chosen IDs (ECU/Service discovery)
- gen_replay       - save and replay packets

P.S. of course we are working on supporting other types of I/O hardware and modules. Please join us!
Main idea that community can produce different modules that can be useful for all of us 8)

## Dependencies

    pip install pyserial


# Usage Examples
See more use-cases inside examples folder:

- CAN Switch filter scanner
    Checking which packets can be passed from diagnostic can to HU and back and etc
- MITM with firewall (ECU ID detection)
    Checking what packets are responsible for chosen "action"
- Replay discovery
    Checking what packets are responsible for chosen "action"
- Ping discovery ( with ISO TP and UDS support)
    UDS detection and etc

And many other options possible. Just use modules in "needed" order.

## Example from  The Car Hacker’s Handbook The Car Hacker’s Handbook A Guide for the Penetration Tester
This example just like "Using can-utils to Find the Door-Unlock Control" from great book: "The Car Hacker’s Handbook The Car Hacker’s Handbook A Guide for the Penetration Tester" by Craig Smith

Let's see how it looks like from the console...

     python canstoolz.py -c can_replay_discovery.py
     hw_USBtin: Init phase started...
     hw_USBtin: Port found: COM14
     hw_USBtin: PORT: COM14
     hw_USBtin: Speed: 500
     hw_USBtin: USBtin device found!
    
    
       _____          _   _ _______          _
      / ____|   /\   | \ | |__   __|        | |
     | |       /  \  |  \| |  | | ___   ___ | |____
     | |      / /\ \ | . ` |  | |/ _ \ / _ \| |_  /
     | |____ / ____ \| |\  |  | | (_) | (_) | |/ /
      \_____/_/    \_\_| \_|  |_|\___/ \___/|_/___|
    
    
    
     >> v
     Loaded queue of modules:
    
     (0)     -       hw_USBtin               {'action': 'read', 'pipe': 1}           Enabled: True
                    ||
                    ||
                    \/
     (1)     -       gen_replay              {'pipe': 1}             Enabled: True
                    ||
                    ||
                    \/
     (2)     -       hw_USBtin               {'action': 'write', 'pipe': 2}          Enabled: True
    
     >> s                            # start main loop
     >> c 1 g               # collect CAN traffic
     True
     >> c 1 g               # after some time when 'action' finished stop collecting traffic
     False
     >> c 1 p               # see amount of collected packets (you can use mod_stat additional for more info) .. a lot of things there
     >> 28790
     >> stop
     >> e 1 {'pipe':2}      # switch to pipe 2
     >> s
     >> c 1 0-14000         # let's replay firsts half.. does action happen?
     >> True
     >> c 1 14000-28790     # if not then second half...
     >> True
     >> c 1 14000-20000     # And continue our 'binary' search
     >> True
     >> c 1 18000-20000     # And continue our 'binary' search
     >> True
     >> c 1 18000-19000    # And continue our 'binary' search
     >> True
     .....
     >> c 1 18500-18550    # here we are...
     >> True
     >> c 1 d 18500-18550  # dump chosen range into a file

    ------------ can_replay_discovery.py -----------------
    load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},  # IO hardware module
    'gen_replay':   {'debug': 1},                             # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
    }

    # Now let's describe the logic of this test
    actions = [
        {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
        {'gen_replay':    {'pipe': 1}},                  # We will sniff first from PIPE 1, then replay to PIPE 2
        {'hw_USBtin':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]

    ----------------------------------------------------------

That's it for now. Will update this file later with more config, and examples how to use this tool!

# Dev "API" (short version)

Just create file mod_test with same class name insede (extend CANModule class):

    do_effect(msg,args)  - main method, that will be called in the loop.
      msg  - input Message with CAN frame
      args - parameters for this module

    do_start(args)       - this method will be called eah time you activate loop (command start/s)
      args - parameters for this module

    do_stop(args)            - will be called when main loop has been stoped (ctrl+c or stop in the console)

    do_init(init_args)   - this nethod will be called when module loaded into a project
      init_args - parameters for initialization



    msg format:
      msg.CANData   - boolean. If true then this message contains CAN Frame
      msg.debugData - boolean. If true then this message contains other data. (can be used for cross-module communication)
      msg.Frame     - CANMessage
      msg.debugText - string



    CANMessage format:
      frame_id        - int, CAN message ID (lower and high bytes together, also can hold extended format)
      frame_length    - int, DATA length (0-8 bytes)
      frame_data      - list, with data

P.S.
 Current version is uber-beta. Not tested enough, code is not clean and ugly and there are bugs that not found yet... working on that, sorry.
 A lot of not-needed IF, and bad code, strange RPINTs and etc...
 Feel free to fix or ignore ;)

With best regards:

Alexey Sintsov   (@asintsov)
alex.sintsov@gmail.com

DC#7812

DEFCON-RUSSIA

http://defcon-russia.ru



