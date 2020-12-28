"""Support for the PRT Heatmiser themostats using the V3 protocol."""
""" Dec 2020 NDC version"""

import logging
from typing import List

from . import connection, heatmiser
import voluptuous as vol

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PORT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    PRECISION_WHOLE,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "heatmiser_ndc"
CONF_THERMOSTATS = "tstats"

TSTAT_SCHEMA = vol.Schema(
    {vol.Required(CONF_ID): vol.Range(1, 32), vol.Required(CONF_NAME): cv.string,}
)

TSTATS_SCHEMA = vol.All(cv.ensure_list, [TSTAT_SCHEMA])

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_THERMOSTATS, default=[]): TSTATS_SCHEMA,
    }
)

COMPONENT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_THERMOSTATS): TSTATS_SCHEMA,
    }
)
CONFIG_SCHEMA = vol.Schema({DOMAIN: COMPONENT_SCHEMA}, extra=vol.ALLOW_EXTRA)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the heatmiser thermostat."""
    _LOGGER.debug("Setting up platform")
    heatmiser_v3_thermostat = heatmiser.HeatmiserThermostat

    host = config[CONF_HOST]
    port = str(config.get(CONF_PORT))

    thermostats = config[CONF_THERMOSTATS]

    uh1_hub = connection.HeatmiserUH1(host, port)

    add_entities(
        [
            HeatmiserV3Thermostat(heatmiser_v3_thermostat, thermostat, uh1_hub)
            for thermostat in thermostats
        ],
        True,
    )


class HeatmiserV3Thermostat(ClimateEntity):
    """Representation of a HeatmiserV3 thermostat."""

    def __init__(self, therm, device, uh1):
        """Initialize the thermostat."""
        _LOGGER.debug(f'Initialising thermostat {device}')
        self.therm = therm(device[CONF_ID], "prt", uh1)
        self.uh1 = uh1
        self._name = device[CONF_NAME]
        self._current_temperature = None
        self._target_temperature = None
        self._id = device
        self.dcb = None
        self._hvac_mode = HVAC_MODE_OFF
        self._temperature_unit = None

    @property
    def supported_features(self):
        _LOGGER.debug(f'supported features returning {SUPPORT_TARGET_TEMPERATURE}')
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def name(self):
        _LOGGER.debug(f'name returning {self._name}')
        return self._name

    @property
    def temperature_unit(self):
        value = TEMP_CELSIUS if (int(self.dcb[5]["value"]) == 0) else TEMP_FAHRENHEIT
        _LOGGER.debug(f'temperature unit returning {value}')
        return value

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        
        if (int(self.dcb[23]["value"]) == 1):
            value = HVAC_MODE_OFF
        elif (int(self.dcb[35]["value"]) == 0):
            value = HVAC_MODE_AUTO
        else:
            value = HVAC_MODE_HEAT
        _LOGGER.debug(f'hvac mode returning {value}')
        return value

    def set_hvac_mode(self, hvac_mode):
        _LOGGER.debug(f'set hvac mode to {hvac_mode}')
        if hvac_mode == HVAC_MODE_OFF:
            self.therm.set_frost_protect_mode(1)
        else:
            self.therm.set_frost_protect_mode(0)

    def turn_off(self):
        """Turn. off the zone."""
        _LOGGER.debug(f'turn off called')
        self.therm.set_frost_protect_temp(7)
        self.set_hvac_mode(HVAC_MODE_OFF)

    def turn_on(self):
        """Turn. on the zone."""
        _LOGGER.debug(f'turn off called')
        self.set_hvac_mode(HVAC_MODE_AUTO)

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        _LOGGER.debug(f'target temp step returning {PRECISION_WHOLE}')
        return PRECISION_WHOLE

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        _LOGGER.debug(f'min temp returning 5')
        return 5

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        _LOGGER.debug(f'max temp returning 35')
        return 35

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.
           Need to be a subset of HVAC_MODES.
        """
        _LOGGER.debug(f'hvac modes called')
        return []

    @property
    def current_temperature(self):
        """Return the current temperature depending on sensor select"""
        senselect = self.dcb[13]["value"]
        if senselect in [0,3]:    # Built In sensor
            index = 32
        elif senselect in [1,4]:    # remote  air sensor
            index = 28
        else:
            index = 30    # assume floor sensor

        temperature = (self.dcb[index]["value"] * 256 + self.dcb[index +1]["value"])/10
        _LOGGER.debug(f'Current temp returned {temperature}')
        return (temperature)

    @property
    def target_temperature(self):
        _LOGGER.debug(f'Get target temp')
        temperature = self.therm.get_target_temp()
        _LOGGER.debug(f'Target temp returned {temperature}')
        return temperature

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        _LOGGER.debug(f'Set target temp: {temperature}')
        self._target_temperature = int(temperature)
        self.therm.set_target_temp(self._target_temperature)
        

    def update(self):
        """Get the latest data."""
        _LOGGER.debug(f'**** Update started')
        self.dcb = self.therm.read_dcb()
        self._current_temperature = int(self.current_temperature)
        self._target_temperature = int(self.target_temperature)
        self._hvac_mode = self.hvac_mode
        _LOGGER.debug(f'**** Update done- current T: {self._current_temperature}, target T: {self._target_temperature}, hvac mode: {self._hvac_mode}')
       
