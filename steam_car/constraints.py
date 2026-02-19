"""Constraint checker for competition rules and pressure vessel limits."""

from dataclasses import dataclass


@dataclass
class Constraints:
    total_mass_kg: float
    length_cm: float
    fuel_volume_ml: float
    pressure_pa: float
    boiler_inner_radius_m: float
    boiler_wall_thickness_m: float
    boiler_yield_strength_pa: float

    mass_limit_kg: float = 1.0
    length_limit_cm: float = 30.0
    fuel_limit_ml: float = 20.0
    min_safety_factor: float = 2.0

    def hoop_stress_pa(self) -> float:
        return self.pressure_pa * self.boiler_inner_radius_m / max(self.boiler_wall_thickness_m, 1e-6)

    def boiler_safety_factor(self) -> float:
        stress = self.hoop_stress_pa()
        if stress <= 0:
            return float("inf")
        return self.boiler_yield_strength_pa / stress

    def allowable_pressure_pa(self) -> float:
        """Pressure giving exactly minimum required safety factor."""
        return (
            self.boiler_yield_strength_pa
            * self.boiler_wall_thickness_m
            / (self.min_safety_factor * self.boiler_inner_radius_m)
        )

    def check_all(self) -> dict:
        sf = self.boiler_safety_factor()
        allowable_p = self.allowable_pressure_pa()
        return {
            "mass_ok": self.total_mass_kg <= self.mass_limit_kg,
            "length_ok": self.length_cm <= self.length_limit_cm,
            "fuel_ok": self.fuel_volume_ml <= self.fuel_limit_ml,
            "safety_factor_ok": sf >= self.min_safety_factor,
            "pressure_ok": self.pressure_pa <= allowable_p,
            "hoop_stress_pa": self.hoop_stress_pa(),
            "boiler_safety_factor": sf,
            "allowable_pressure_pa": allowable_p,
        }
