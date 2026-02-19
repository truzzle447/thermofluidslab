"""Nozzle subsystem converting pressure into jet kinetic energy."""

from dataclasses import dataclass
import math


@dataclass
class Nozzle:
    boiler_pressure_pa: float
    atmospheric_pressure_pa: float
    steam_density_kg_per_m3: float
    nozzle_area_m2: float
    discharge_coefficient: float

    def pressure_drop_pa(self) -> float:
        return max(0.0, self.boiler_pressure_pa - self.atmospheric_pressure_pa)

    def exit_velocity_m_per_s(self) -> float:
        """Incompressible Bernoulli approximation for micro-scale design."""
        rho = max(1e-6, self.steam_density_kg_per_m3)
        return math.sqrt(max(0.0, 2.0 * self.pressure_drop_pa() / rho))

    def mass_flow_rate_kg_per_s(self) -> float:
        """Classical orifice relation with discharge coefficient."""
        rho = max(1e-6, self.steam_density_kg_per_m3)
        return (
            self.discharge_coefficient
            * self.nozzle_area_m2
            * math.sqrt(max(0.0, 2.0 * rho * self.pressure_drop_pa()))
        )
