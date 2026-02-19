"""Drivetrain subsystem for transmitting turbine torque to wheels."""

from dataclasses import dataclass


@dataclass
class Drivetrain:
    turbine_torque_n_m: float
    gear_ratio: float
    mechanical_efficiency: float

    def wheel_torque_n_m(self) -> float:
        return self.turbine_torque_n_m * self.gear_ratio * self.mechanical_efficiency
