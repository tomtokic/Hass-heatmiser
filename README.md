# HA-heatmiser-component
Home Assistant Component (custom) for Heatmiser PRT-N Stats

Upload this custom compenent to your`config/custom_components` folder. Then add to your configuration.yaml as per example below

Notes
My own heatmiser system has 15 stats connected via a single 1 ATC_1000 RS485 adaptor

The timeout in constants.py  is currently set to 0.8 seconds, so it takes c12 seconds to update all stats. This works fine on my own system, but if you have lots of CRC errors reported in the log, then it may be worth increasing this a little to say 1 second or more.

An update is done as part of initialisation, so with this many stats, it will take longer than 10 seconds, so a warning is to be expected, along the lines of 
Setup of climate platform heatmiser_ndc is taking over 10 seconds.

Hass initiates an update to read the stat values after scan_interval seconds. The shorter this interval, the more quickly Hass will detect changes in temperature or heating mode. The fewer stats you have, the smaller this interval can be.

This version has been derived from the original Heatmiser component and the HeatmiserV3 library. The library has been incorporated into the component to add logging and fix a few issues


Example configuration.yaml
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

This version has been derived from the original Heatmiser component and the HeatmiserV3 library
