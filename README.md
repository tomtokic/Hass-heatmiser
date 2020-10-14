# HA-heatmiser-component
Home Assistant Component for Heatmiser PRT-N Stats

Upload this to `config/custom_components` folder and then see the example config to add to the configuration.yaml:

```
 - platform: heatmiser_brett
    host: 192.168.1.81
    scan_interval: 30
    port: 9999
    tstats:
      - id: 1
        name: Living Room
      - id: 2
        name: Hallway
      - id: 3
        name: Dining Room
      - id: 4
        name: Cinema Room
      - id: 5
        name: Kitchen
      - id: 6
        name: Washroom

```
