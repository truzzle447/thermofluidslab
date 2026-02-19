"""Inventory and materials accounting for mass, cost, and boiler safety."""

from dataclasses import dataclass
import pandas as pd


@dataclass
class Inventory:
    parts_df: pd.DataFrame

    required_columns = [
        "Name",
        "Material",
        "Density_kg_m3",
        "YieldStrength_Pa",
        "Quantity",
        "EstimatedMass_kg",
        "Cost_USD",
    ]

    def validate(self) -> None:
        missing = [c for c in self.required_columns if c not in self.parts_df.columns]
        if missing:
            raise ValueError(f"Missing inventory columns: {missing}")

    def total_mass_kg(self) -> float:
        self.validate()
        return float((self.parts_df["EstimatedMass_kg"] * self.parts_df["Quantity"]).sum())

    def total_cost_usd(self) -> float:
        self.validate()
        return float((self.parts_df["Cost_USD"] * self.parts_df["Quantity"]).sum())

    def boiler_safety_factor(self, pressure_pa: float, inner_radius_m: float, wall_thickness_m: float) -> float:
        """Use highest listed yield strength among boiler-like materials as a proxy."""
        self.validate()
        hoop_stress = (pressure_pa * inner_radius_m) / max(wall_thickness_m, 1e-6)
        yield_strength = float(self.parts_df["YieldStrength_Pa"].max())
        if hoop_stress <= 0:
            return float("inf")
        return yield_strength / hoop_stress
