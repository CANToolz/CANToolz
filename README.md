# CANToolz

CANToolz is a framework for analysing CAN networks and devices.
This tool based on different modules which can be assembled in pipe together and
can be used by security researchers and automotive/OEM security testers for black-box analysis and etc.

This platform is a try to unify all needed tricks/tools and other things that you can do with CAN bus in one place.
Also it gives a (almost) easy way to add your modules and use "extended" version for your needs
(like custom brutforcers for chosen ECU and etc).

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

- MITM with firewall
- replay discovery
- ping discovery (UDS)

## Example from  The Car Hacker’s Handbook The Car Hacker’s Handbook A Guide for the Penetration Tester
This example just like "Using can-utils to Find the Door-Unlock Control" from great book: "The Car Hacker’s Handbook The Car Hacker’s Handbook A Guide for the Penetration Tester" by Chris Evans

Let's see how it looks like from the console...

    python cantoolz.py -c can_replay_discovery.conf
    hw_USBtin: Init phase started...
    hw_USBtin: Port found: COM14
    hw_USBtin: PORT: COM14
    hw_USBtin: Speed: 500
    hw_USBtin: USBtin device found!
    >> s                            ; start main loop
    >> c gen_replay g               ; collect CAN traffic
    True
    >> c gen_replay g               ; after some time when 'action' finished stop collecting traffic
    False
    >> c gen_replay p               ; see amount of collected packets (you can use mod_stat additional for more info) .. a lot of hings there
    >> 28790
    >> e gen_replay {'pipe':2}      ; switch to pipe 2
    >> c gen_replay 0-14000         ; let's replay firsts half.. does action happen?
    >> True
    >> c gen_replay 14000-28790     ; if not then second half...
    >> True
    >> c gen_replay 14000-20000     ; And continue our 'binary' search
    >> True
    >> c gen_replay 18000-20000     ; And continue our 'binary' search
    >> True
    >> c gen_replay 18000-19000    ; And continue our 'binary' search
    >> True
    .....
    >> c gen_replay 18500-18550    ; here we are...
    >> True
    >> c gen_replay d 18500-18550  ; dump chosen range into a file

    ------------ can_replay_discovery.conf -----------------
    [hw_USBtin]
    port = auto         ; Serial port
    debug = 1           ; debug level (default 0)
    speed = 500         ; bus speed (500, 1000)

    ; load module for replay
    [gen_replay]
    debug = 1

    ; Load stat module. We need it to detect new IDs
    [mod_stat]

    ; Now let's describe the logic of this test and MITM example
    [MITM]

    hw_USBtin = {'action':'read'}    ; Read packets
    gen_replay = {}                  ; module to save and replay
                             ; to additional filter for ID you can use mod_firewall here

    hw_USBtin!1 = {'action':'write','pipe':2}  ; write replays from pipe 2, which is empty now

    ----------------------------------------------------------

That's it for now. Will update this file later with more config, and examples how to use this tool!

# Dev "API" (short version)

Just create file mod_test with same class name insede (extend CANModule class):

 do_effect(msg,args)  - main method, that will be called in the loop.
    msg  - input Message with CAN frame
    args - parameters for this module

 do_start(args)       - this method will be called eah time you activate loop (command start/s)
    args - parameters for this module

 do_stop()            - will be called when main loop has been stoped (ctrl+c or stop in the console)

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

Alexey Sintsov   (@asintsov)
alex.sintsov@gmail.com



