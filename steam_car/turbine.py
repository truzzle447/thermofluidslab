"""Turbine subsystem for jet-to-rotation conversion."""

from dataclasses import dataclass


@dataclass
class Turbine:
    mass_flow_rate_kg_per_s: float
    jet_velocity_in_m_per_s: float
    turbine_radius_m: float
    turbine_efficiency: float
    jet_velocity_out_m_per_s: float = 0.0

    def jet_force_n(self) -> float:
        delta_v = max(0.0, self.jet_velocity_in_m_per_s - self.jet_velocity_out_m_per_s)
        return self.mass_flow_rate_kg_per_s * delta_v * self.turbine_efficiency

    def torque_n_m(self) -> float:
        return self.jet_force_n() * self.turbine_radius_m

    def power_w(self, angular_speed_rad_per_s: float) -> float:
        return self.torque_n_m() * max(0.0, angular_speed_rad_per_s)
