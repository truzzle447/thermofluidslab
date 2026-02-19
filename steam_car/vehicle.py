"""Vehicle subsystem for traction and rolling resistance checks."""

from dataclasses import dataclass


@dataclass
class Vehicle:
    mass_kg: float
    wheel_radius_m: float
    mu_static: float
    c_rr: float
    gravity_m_per_s2: float = 9.81

    def rolling_resistance_force_n(self) -> float:
        return self.c_rr * self.mass_kg * self.gravity_m_per_s2

    def required_traction_torque_n_m(self) -> float:
        return self.rolling_resistance_force_n() * self.wheel_radius_m

    def max_friction_torque_n_m(self) -> float:
        return self.mu_static * self.mass_kg * self.gravity_m_per_s2 * self.wheel_radius_m

    def evaluate_go_no_go(self, available_wheel_torque_n_m: float) -> dict:
        required = self.required_traction_torque_n_m()
        max_traction = self.max_friction_torque_n_m()
        traction_limited_available = min(available_wheel_torque_n_m, max_traction)
        go = traction_limited_available > required

        if required <= 0:
            margin = 0.0
        else:
            margin = (traction_limited_available - required) / required * 100.0

        return {
            "go": go,
            "required_torque_n_m": required,
            "max_friction_torque_n_m": max_traction,
            "effective_available_torque_n_m": traction_limited_available,
            "safety_margin_percent": margin,
        }
