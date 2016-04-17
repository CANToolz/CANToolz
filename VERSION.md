## Version 1.4-1
### CHANGES
 - new web design/logo (thx my wife Sevtalana Sintcova!)

## Version 1.4-0
### CHANGES
 - mod_stat diff mode added: now we can compare "new" traffic and "old" to fins new ID/frames
 -- details: http://asintsov.blogspot.de/2016/04/cantoolz-modstat-diff-mode.html
 - now commands can be disabled (in Diff mod of mod_stat you can't use some commands)

## Version 1.3-3
### CHANGES
 - USBTin default bitrates calc added. Any speed/rate supported! (forgot that rate can be float... now it is fixed)
 
## Version 1.3-2
### CHANGES
 - USBTin default bitrates calc added. Any speed/rate supported!
 
## Version 1.3-1
### CHANGES
 - USBTin default bitrates added to the list 

## Version 1.3-0
### CHANGES
 - CAN module change: now we do not store additional raw data. We have saved up to 50% memory! But now "write" operation a little bit longer...
 - BUS name as any string now (except CBT, should be num 1, 2 or 3)
 - mod_ping/ gen_replay - delay added. This could be helpful when USBtin is overflowed with "write requests"
 - WEB API: Status bar added
 - FrontEnd status bar done
 
## Version 1.2-5
### CHANGES
 - FrontEnd fix: now parameters and options showing actual status (by Sergey Kononenko)
 
## Version 1.2-4
### CHANGES
 - libs/module.py workaround feature added: Now we can get current status of the module. This is needed because you need to know when ping/fuzz finished. Later we will think about proper status-bar 
 
## Version 1.2-3
### CHANGES
 - mod_stat design change: now Analysis function is parametrized, if you do not want to see all output
 - gen_ping fix: uds scan for non sub-commands fixed, new subbcomands added
 - example uds_scan changed

## Version 1.2-2
### CHANGES
 - WEB interface fix: dependences from Intrnet connection (d3 external web) 

## Version 1.2-1
### CHANGES
 - mod_stat fix: table print format 

## Version 1.2-0
### CHANGES
 - mod_stat feature added: ASCII detection (print ASCII if found in the traffic)
 - mod_stat feature added: Marking CAN frames via metafile/metadata (COMMENTS for ID)
 - mod_stat feature added: Marking control bytes via metafile/metada  to re-assemble fragmented frames 
 - mod_stat feature added: experimental chain detection (re-assemble fragmented frames that are sent in LOOP)
 - mod_stat fix: UDS/ISO tp detection bug fixed (when you scan more)
 - mod_stat change: now it stores ALL packets, not just table, and save in REPLAY save all these frames (WARNINING: Now  this module stores all frames, which can affect memory and speed. Let's see how it works...)
 - mod_stat feature removed: alert feature removed
 

## Version 1.1-1
### CHANGES
 - mod_stat fixes: better output, simple dump functions

## V1.1b
### CHANGES
 - Fixed mod_stat analysis option bug, when CAN Frame has 1 byte size
 - Default sniff config added


## V1.0b
### CHANGES
First Beta

