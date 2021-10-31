# HA-heatmiser-component
Custom Home Assistant Component for Heatmiser PRT-N Stats
This component accesses the stats via an IP to RS485 adaptor (I use an ATC_1000)

To use this custom component:
  1. Create a folder `heatmiser_ndc` within `config/custom_components` folder on your HA system
  2. Upload the files climate.py, heatmiser.py, manifest.json and _init_.py to the new `config/custom_components/heatmiser_ndc` folder
  3. and then add the following (edited for your setup) to your configuration.yaml:

```
 climate:
  - platform: heatmiser_ndc
    host: 192.168.0.19
    port: 23
    scan_interval: 20
    tstats:
      - id: 1
        name: Kitchen
      - id: 2
        name: Guest Bath
      - id: 3
        name: Guest Bed
      - id: 4
```

# Notes
This version has been derived from the original Heatmiser component and the HeatmiserV3 library. The library has been incorporated into this custom component (heatmiser.py) to add logging and fix a few issues.

## Update speed
My own heatmiser system has 15 stats connected via a single ATC_1000 RS485 adaptor. 

There is a COM_TIMEOUT in heatmiser.py (currently 0.8 secs), so it takes c12 seconds to update all stats. This works fine on my own system, but if you have lots of CRC errors reported in the log, then it may be worth increasing this a little to say 1 second or more.

Hass includes the first update as part of initialisation, so with this many stats, it will take longer than 10 seconds, so a warning is to be expected, along the lines of 
  "Setup of climate platform heatmiser_ndc is taking over 10 seconds".

The configuration parameter scan_interval determines how frequently Hass reads the stat values after scan_interval seconds. The shorter this interval, the more quickly Hass will detect changes in temperature or heating mode. The fewer stats you have, the smaller this interval can be.

The component now supports HVAC MODES and implements the climate services Turn on, Turn off & Set Hvac Mode
Turn off sets the stat into frost protect mode, Turn on sets it to normal (ie heating if actual temp < target temp))
Set Hvac mode on or off is the same as turn on / turn off
The stat can be turned on/off in the UI, or by calling the relevant services from developer tools

## Logging
The component logs lots of events at debug, error, info & warning levels. Logging levels can be controlled by including something like the following in the configuration.yaml file
```
logger:
  default: warning
  logs:
    custom_components.heatmiser_ndc: debug
```
Logging levels can also be controlled on the fly using the logger.set_level service in Developer Tools in the UI in Yaml mode with 
```
service: logger.set_level
data:
  custom_components.heatmiser_ndc: warning
```