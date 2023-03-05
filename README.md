# Inels HACS integration
Temporary repository of iNELS to mqtt Home Assistant Community Store integration.

![iNELS_icon][iNELS_icon]

## Features
Allows the integration of both wireless and bus based [iNELS] devices.

Platforms used:
Platform | Description
-- | --
`binary_sensor` | Mostly used to show binary input sensors, motion sensors, proximity sensors...
`button` | Used to trigger HA automations as if the physical buttons were pressed themselves
`climate` | Used to control thermovalves and thermostat behaviour
`cover` | Used to control shutters
`light` | Used to control various types of lights (dimmable lights, RGB, DALI...)
`sensor` | Used to show a wide array of sensors and their values (temperature, voltage, humidity, light...)
`select` | Used to display and select from a given number of options (used only to control fan speed)
`switch` | Used to control relays in the devices

## Supported devices
### Wireless
- Switches (01, 02)
- Shutters (03, 21)
- Light dimmers (04, 05)
- Switches with external temperature sensors (07)
- Wireless thermovalves (09)
- Temperature sensors (10)
- Thermostats (12)
- Flood detectors (15)
- Generic detector (16)
- Motion detector (17)
- Controllers/buttons (18, 19)
- Temperature and humidity sensors (29)

### Bus

- SA3-01B (100)
- DA3-22M (101)
- GRT3-50 (102)
- GSB3-90Sx (103)
- SA3-02B (104)
- SA3-02M (105)
- SA3-04M (106)
- SA3-06M (107)
- SA3-012M (108)
- SA3-022M (109)
- FA3-612M (111)
- IOU3-108M (112)
- RC3-610DALI (114)
- IM3_20B (115)
- IM3_40B (116)
- IM3_80B (117)
- DMD3-1 (120)
- IM3-140M (121)
- WSB3-20 (122)
- WSB3-40 (123)
- WSB3-20H (124)
- WSB3-40H (125)
- GCR3-11 (128)
- GCH3-31 (129)
- GSP3-100 (136)
- GDB3-10 (137)
- GSB3-40SX (138)
- GSB3-60SX (139)
- GSB3-20SX (140)
- GBP3-60 (141)
- DAC3_04B (147)
- DAC3_04M (148)
- DCDA-33M (150)
- DA3-66M (151)
- ADC3-60M (156)
- TI3-10B (157)
- TI3-40B (158)
- TI3-60M (159)
- IDRT3-1 (160)


[iNELS_icon]: https://www.inels.com/media/img/logo.png
[iNELS]: https://www.inels.com/
