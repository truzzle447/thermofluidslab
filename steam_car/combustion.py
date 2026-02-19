"""Combustion subsystem for micro steam car digital twin."""

from dataclasses import dataclass


@dataclass
class CombustionChamber:
    """First-principles fuel energy model.

    Parameters
    ----------
    fuel_volume_ml : float
        Fuel volume in milliliters.
    fuel_density_kg_per_m3 : float
        Fuel density in kg/m^3.
    lower_heating_value_j_per_kg : float
        Lower heating value of fuel in J/kg.
    combustion_efficiency : float
        Fraction of ideal energy released into usable thermal energy.
    burn_time_s : float
        Optional burn time for average heat-rate estimate.
    """

    fuel_volume_ml: float
    fuel_density_kg_per_m3: float
    lower_heating_value_j_per_kg: float
    combustion_efficiency: float
    burn_time_s: float = 120.0

    @property
    def fuel_mass_kg(self) -> float:
        """Compute fuel mass from volume and density."""
        fuel_volume_m3 = self.fuel_volume_ml * 1e-6
        return fuel_volume_m3 * self.fuel_density_kg_per_m3

    def available_heat_j(self) -> float:
        """Total useful thermal energy released from combustion."""
        return (
            self.fuel_mass_kg
            * self.lower_heating_value_j_per_kg
            * self.combustion_efficiency
        )

    def average_heat_rate_w(self) -> float:
        """Estimate average heating power over a burn duration."""
        if self.burn_time_s <= 0:
            return 0.0
        return self.available_heat_j() / self.burn_time_s
