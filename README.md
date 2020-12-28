# HA-heatmiser-component
Home Assistant Component (custom) for Heatmiser PRT-N Stats

Upload this to `config/custom_components` folder and then see the example config to add to the configuration.yaml:

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