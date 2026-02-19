"""Boiler subsystem for converting thermal input into pressurized steam."""

from dataclasses import dataclass
import math


@dataclass
class Boiler:
    """Simple lumped boiler energy and pressure model."""

    water_mass_kg: float
    heat_input_j: float
    boiler_efficiency: float
    initial_temperature_c: float
    tank_volume_m3: float

    cp_water_j_per_kgk: float = 4180.0
    cp_steam_j_per_kgk: float = 2010.0
    latent_heat_vap_j_per_kg: float = 2_257_000.0
    boiling_temp_c: float = 100.0
    steam_gas_constant_j_per_kgk: float = 461.5

    def useful_heat_j(self) -> float:
        return self.heat_input_j * self.boiler_efficiency

    def sensible_heat_needed_j(self) -> float:
        delta_t = max(0.0, self.boiling_temp_c - self.initial_temperature_c)
        return self.water_mass_kg * self.cp_water_j_per_kgk * delta_t

    def phase_change_energy_j(self) -> float:
        return max(0.0, self.useful_heat_j() - self.sensible_heat_needed_j())

    def steam_mass_generated_kg(self) -> float:
        generated = self.phase_change_energy_j() / self.latent_heat_vap_j_per_kg
        return min(self.water_mass_kg, max(0.0, generated))

    def superheat_energy_j(self) -> float:
        evaporating_all = self.water_mass_kg * self.latent_heat_vap_j_per_kg
        return max(0.0, self.phase_change_energy_j() - evaporating_all)

    def steam_temperature_k(self) -> float:
        m_steam = self.steam_mass_generated_kg()
        if m_steam <= 0:
            return self.boiling_temp_c + 273.15
        delta_t_superheat = self.superheat_energy_j() / (m_steam * self.cp_steam_j_per_kgk)
        return self.boiling_temp_c + 273.15 + delta_t_superheat

    def saturation_pressure_pa(self) -> float:
        """Antoine approximation for water saturation pressure (1–100°C region)."""
        temp_c = min(max(self.boiling_temp_c, 1.0), 100.0)
        # Antoine constants for water with pressure in mmHg
        a, b, c = 8.07131, 1730.63, 233.426
        p_mm_hg = 10 ** (a - (b / (c + temp_c)))
        return p_mm_hg * 133.322

    def pressure_pa(self) -> float:
        if self.tank_volume_m3 <= 0:
            return ATM_PRESSURE_PA

        steam_mass = self.steam_mass_generated_kg()
        if steam_mass <= 0:
            return ATM_PRESSURE_PA

        p_abs = (
            steam_mass
            * self.steam_gas_constant_j_per_kgk
            * self.steam_temperature_k()
            / self.tank_volume_m3
        )
        return max(self.saturation_pressure_pa(), p_abs)

    def steam_density_kg_per_m3(self) -> float:
        return self.pressure_pa() / (self.steam_gas_constant_j_per_kgk * self.steam_temperature_k())

    def steam_mass_flow(self, nozzle_area_m2: float, discharge_coefficient: float = 0.9) -> float:
        if nozzle_area_m2 <= 0:
            return 0.0
        delta_p = max(0.0, self.pressure_pa() - ATM_PRESSURE_PA)
        rho = self.steam_density_kg_per_m3()
        return discharge_coefficient * nozzle_area_m2 * math.sqrt(max(0.0, 2.0 * rho * delta_p))


ATM_PRESSURE_PA = 101_325.0
