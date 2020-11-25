"""Support for the PRT Heatmiser themostats using the V3 protocol."""
import math
import logging
from typing import List

from heatmiserV3 import connection, heatmiser
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

DOMAIN = "heatmiser_brett"
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
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        return TEMP_CELSIUS if (int(self.dcb[5]["value"]) == 0) else TEMP_FAHRENHEIT

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        if (int(self.dcb[23]["value"]) == 1):
            return HVAC_MODE_OFF
        elif (int(self.dcb[35]["value"]) == 0):
            return HVAC_MODE_AUTO
        else:
            return HVAC_MODE_HEAT

    def set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVAC_MODE_OFF:
            self.therm.set_frost_protect_mode(1)
        else:
            self.therm.set_frost_protect_mode(0)

    def turn_off(self):
        """Turn. off the zone."""
        self.therm.set_frost_protect_temp(7)
        self.set_hvac_mode(HVAC_MODE_OFF)

    def turn_on(self):
        """Turn. on the zone."""
        self.set_hvac_mode(HVAC_MODE_AUTO)

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_WHOLE

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 5

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 35

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.

        Need to be a subset of HVAC_MODES.
        """
        return []
    
    @property
    def current_temperature(self):
        """Return the current temperature depending on sensor select"""
        senselect = self.dcb[13]["value"]
        if senselect in [0,3]:    # Built In sensor
            index = 32
        elif senselect in [1,4]:  # remote air sensor
            index = 28
        else:                     # assume floor sensor
            index = 30   
        return (self.dcb[index]["value"] * 256 + self.dcb[index +1]["value"])/10
    
    @property
    def current_temperature_old(self):
        """Return the current temperature."""
        return (
            (self.dcb[31]["value"] / 10)
            if (int(self.dcb[13]["value"]) > 1)
            else (self.dcb[33]["value"]/10)
        )

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.therm.get_target_temp()

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        self._target_temperature = int(temperature)
        self.therm.set_target_temp(self._target_temperature)

    def update(self):
        """Get the latest data."""
        self.dcb = self.therm.read_dcb()
        self._current_temperature = int(self.current_temperature)
        self._target_temperature = int(self.target_temperature)
        self._hvac_mode = self.hvac_mode
