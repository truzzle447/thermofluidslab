"""Streamlit dashboard for Micro Steam Car Design – Energy-Centric Digital Twin."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from steam_car.boiler import Boiler
from steam_car.combustion import CombustionChamber
from steam_car.constraints import Constraints
from steam_car.drivetrain import Drivetrain
from steam_car.inventory import Inventory
from steam_car.nozzle import Nozzle
from steam_car.turbine import Turbine
from steam_car.vehicle import Vehicle

ATM_PRESSURE_PA = 101_325.0


def default_inventory_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Boiler Shell", "Copper", 8960, 70e6, 1, 0.18, 12.0],
            ["Turbine Wheel", "Aluminum", 2700, 95e6, 1, 0.08, 10.0],
            ["Axle + Bearings", "Steel", 7850, 250e6, 1, 0.06, 9.0],
            ["Chassis", "Composite", 1600, 120e6, 1, 0.22, 15.0],
            ["Wheels", "Polymer", 1200, 45e6, 4, 0.03, 3.0],
        ],
        columns=[
            "Name",
            "Material",
            "Density_kg_m3",
            "YieldStrength_Pa",
            "Quantity",
            "EstimatedMass_kg",
            "Cost_USD",
        ],
    )


def run_dashboard() -> None:
    st.set_page_config(page_title="Micro Steam Car Digital Twin", layout="wide")
    st.title("Micro Steam Car Design – Energy-Centric Digital Twin")
    st.caption(
        "Chemical → Thermal → Internal (water) → Pressure → Jet kinetic → "
        "Turbine rotation → Wheel torque → Vehicle motion"
    )

    with st.sidebar:
        st.header("Global Inputs")
        fuel_volume_ml = st.slider("Fuel volume (ml)", 1.0, 20.0, 20.0, 0.5)
        fuel_density = st.number_input("Fuel density (kg/m³)", 600.0, 900.0, 790.0, 10.0)
        lhv = st.number_input("Fuel LHV (J/kg)", 10e6, 40e6, 22.7e6, 0.1e6)
        comb_eff = st.slider("Combustion efficiency", 0.1, 1.0, 0.72, 0.01)
        boiler_eff = st.slider("Boiler efficiency", 0.1, 1.0, 0.65, 0.01)
        water_mass_kg = st.slider("Water mass (kg)", 0.02, 0.30, 0.12, 0.005)
        initial_temp_c = st.slider("Initial water temperature (°C)", 10.0, 40.0, 25.0, 1.0)

        st.subheader("Mechanical Inputs")
        turbine_radius = st.slider("Turbine radius (m)", 0.005, 0.05, 0.018, 0.001)
        gear_ratio = st.slider("Gear ratio", 1.0, 30.0, 9.0, 0.5)
        wheel_radius = st.slider("Wheel radius (m)", 0.01, 0.08, 0.03, 0.001)
        vehicle_mass = st.slider("Vehicle mass (kg)", 0.2, 1.2, 0.75, 0.01)
        nozzle_area = st.slider("Nozzle area (m²)", 1e-7, 8e-6, 2e-6, 1e-7, format="%.1e")

        st.subheader("Structure Inputs")
        car_length_cm = st.slider("Vehicle length (cm)", 10.0, 50.0, 27.0, 0.5)
        boiler_radius_m = st.slider("Boiler inner radius (m)", 0.005, 0.03, 0.012, 0.001)
        boiler_thickness_m = st.slider("Boiler wall thickness (m)", 0.0005, 0.005, 0.0012, 0.0001)
        tank_volume_m3 = st.slider("Boiler free steam volume (m³)", 1e-5, 5e-4, 1.2e-4, 1e-5, format="%.1e")

        cd_nozzle = st.slider("Nozzle discharge coefficient", 0.4, 1.0, 0.85, 0.01)
        turbine_eff = st.slider("Turbine efficiency", 0.1, 1.0, 0.55, 0.01)
        drive_eff = st.slider("Drivetrain efficiency", 0.1, 1.0, 0.85, 0.01)
        mu_s = st.slider("Static friction coefficient", 0.2, 1.2, 0.65, 0.01)
        c_rr = st.slider("Rolling resistance coefficient", 0.005, 0.08, 0.02, 0.001)

    combustion = CombustionChamber(fuel_volume_ml, fuel_density, lhv, comb_eff)
    boiler = Boiler(
        water_mass_kg=water_mass_kg,
        heat_input_j=combustion.available_heat_j(),
        boiler_efficiency=boiler_eff,
        initial_temperature_c=initial_temp_c,
        tank_volume_m3=tank_volume_m3,
    )
    nozzle = Nozzle(
        boiler_pressure_pa=boiler.pressure_pa(),
        atmospheric_pressure_pa=ATM_PRESSURE_PA,
        steam_density_kg_per_m3=boiler.steam_density_kg_per_m3(),
        nozzle_area_m2=nozzle_area,
        discharge_coefficient=cd_nozzle,
    )
    turbine = Turbine(
        mass_flow_rate_kg_per_s=nozzle.mass_flow_rate_kg_per_s(),
        jet_velocity_in_m_per_s=nozzle.exit_velocity_m_per_s(),
        turbine_radius_m=turbine_radius,
        turbine_efficiency=turbine_eff,
    )
    drivetrain = Drivetrain(turbine.torque_n_m(), gear_ratio, drive_eff)
    vehicle = Vehicle(vehicle_mass, wheel_radius, mu_s, c_rr)
    motion = vehicle.evaluate_go_no_go(drivetrain.wheel_torque_n_m())

    tabs = st.tabs([
        "1️⃣ Energy Flow",
        "2️⃣ Mechanical Design",
        "3️⃣ Inventory & Materials",
        "4️⃣ Constraints & Validation",
    ])

    with tabs[0]:
        st.subheader("Energy Transformation Blocks")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Combustion Heat (kJ)", f"{combustion.available_heat_j()/1000:.1f}")
        c2.metric("Boiler Pressure (kPa)", f"{boiler.pressure_pa()/1000:.1f}")
        c3.metric("Jet Velocity (m/s)", f"{nozzle.exit_velocity_m_per_s():.1f}")
        c4.metric("Wheel Torque (N·m)", f"{drivetrain.wheel_torque_n_m():.3f}")

        with st.expander("Combustion Stage"):
            st.latex(r"Q = m_{fuel}\,LHV\,\eta_{comb}")
            st.write(
                "Fuel chemical energy is converted to thermal energy. The usable heat "
                "depends on the fuel mass, lower heating value, and combustion efficiency. "
                "This neglects radiative losses and transient flame dynamics."
            )

        with st.expander("Boiler Stage"):
            st.latex(r"Q_{useful}=\eta_b Q,\quad m_{steam}=\frac{Q_{useful}-m_wc_p\Delta T}{h_{fg}}")
            st.write(
                "The boiler first heats liquid water to saturation and then vaporizes part of it. "
                "Pressure is estimated with an ideal-gas relation for steam in free volume. "
                "Real two-phase effects and nonuniform temperature are simplified."
            )

        with st.expander("Nozzle Stage"):
            st.latex(r"V_{exit}\approx\sqrt{\frac{2\Delta P}{\rho}},\quad \dot{m}=C_dA\sqrt{2\rho\Delta P}")
            st.write(
                "Pressure potential is converted into kinetic energy in the nozzle. "
                "The model assumes quasi-steady incompressible behavior for tractability. "
                "At high pressure ratios, compressibility/choking can reduce accuracy."
            )

        with st.expander("Turbine + Drivetrain + Vehicle Stage"):
            st.latex(r"F=\dot{m}(V_{in}-V_{out}),\;\tau_t=Fr_t,\;\tau_w=\tau_t G\eta_m")
            st.latex(r"\tau_{req}=C_{rr}mgr_w,\quad \tau_{max}=\mu_smgr_w")
            st.write(
                "Jet momentum transfer produces turbine torque, amplified by gearing and reduced by "
                "mechanical losses. The vehicle moves only if effective wheel torque exceeds rolling "
                "resistance demand while staying below traction limits."
            )

        if motion["go"]:
            st.success(f"🟢 GO – Safety margin: {motion['safety_margin_percent']:.1f}%")
        else:
            st.error(f"🔴 NO GO – Torque deficit: {abs(motion['safety_margin_percent']):.1f}%")

    with tabs[1]:
        st.subheader("Mechanical Design Sensitivity")
        pressure_range = np.linspace(ATM_PRESSURE_PA + 5_000, ATM_PRESSURE_PA + 220_000, 40)
        torque_vals = []
        gear_req_vals = []

        required_torque = vehicle.required_traction_torque_n_m()
        for p in pressure_range:
            n = Nozzle(
                boiler_pressure_pa=float(p),
                atmospheric_pressure_pa=ATM_PRESSURE_PA,
                steam_density_kg_per_m3=boiler.steam_density_kg_per_m3(),
                nozzle_area_m2=nozzle_area,
                discharge_coefficient=cd_nozzle,
            )
            t = Turbine(
                mass_flow_rate_kg_per_s=n.mass_flow_rate_kg_per_s(),
                jet_velocity_in_m_per_s=n.exit_velocity_m_per_s(),
                turbine_radius_m=turbine_radius,
                turbine_efficiency=turbine_eff,
            )
            base_wheel_torque = t.torque_n_m() * drive_eff
            torque_vals.append(base_wheel_torque)
            gear_req_vals.append(required_torque / max(base_wheel_torque, 1e-9))

        fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
        ax[0].plot(pressure_range / 1000.0, torque_vals, color="tab:blue")
        ax[0].set_title("Wheel Torque vs Boiler Pressure")
        ax[0].set_xlabel("Boiler Pressure (kPa abs)")
        ax[0].set_ylabel("Wheel Torque Before Gear Ratio (N·m)")
        ax[0].grid(alpha=0.3)

        ax[1].plot(pressure_range / 1000.0, gear_req_vals, color="tab:green")
        ax[1].set_title("Required Gear Ratio vs Pressure")
        ax[1].set_xlabel("Boiler Pressure (kPa abs)")
        ax[1].set_ylabel("Required Gear Ratio")
        ax[1].grid(alpha=0.3)
        st.pyplot(fig)

        mass_breakdown = {
            "Fuel": combustion.fuel_mass_kg,
            "Water": water_mass_kg,
            "Structure+Hardware": max(0.0, vehicle_mass - (water_mass_kg + combustion.fuel_mass_kg)),
        }
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        ax2.pie(mass_breakdown.values(), labels=mass_breakdown.keys(), autopct="%1.1f%%")
        ax2.set_title("Current Mass Breakdown")
        st.pyplot(fig2)

    with tabs[2]:
        st.subheader("Editable Parts and Materials Inventory")
        if "parts_df" not in st.session_state:
            st.session_state["parts_df"] = default_inventory_df()

        edited_df = st.data_editor(st.session_state["parts_df"], num_rows="dynamic", use_container_width=True)
        st.session_state["parts_df"] = edited_df

        inventory = Inventory(edited_df)
        total_mass = inventory.total_mass_kg()
        total_cost = inventory.total_cost_usd()
        inventory_sf = inventory.boiler_safety_factor(boiler.pressure_pa(), boiler_radius_m, boiler_thickness_m)

        c1, c2, c3 = st.columns(3)
        c1.metric("Inventory mass (kg)", f"{total_mass:.3f}")
        c2.metric("Inventory cost (USD)", f"{total_cost:.2f}")
        c3.metric("Boiler SF from inventory", f"{inventory_sf:.2f}")

    with tabs[3]:
        st.subheader("Constraint Compliance and Validation")
        inventory_df = st.session_state.get("parts_df", default_inventory_df())
        yield_strength = float(pd.to_numeric(inventory_df["YieldStrength_Pa"], errors="coerce").fillna(0).max())

        constraints = Constraints(
            total_mass_kg=vehicle_mass,
            length_cm=car_length_cm,
            fuel_volume_ml=fuel_volume_ml,
            pressure_pa=boiler.pressure_pa(),
            boiler_inner_radius_m=boiler_radius_m,
            boiler_wall_thickness_m=boiler_thickness_m,
            boiler_yield_strength_pa=yield_strength,
        )
        check = constraints.check_all()

        st.latex(r"\sigma_{hoop}=\frac{Pr}{t}")
        st.write(
            "The boiler wall is checked using thin-walled pressure vessel hoop stress. "
            "A minimum safety factor of 2 is enforced against material yield stress. "
            "The model assumes uniform wall thickness and neglects stress concentrations."
        )

        def mark(ok: bool) -> str:
            return "✅ PASS" if ok else "❌ FAIL"

        st.write(f"Mass limit (≤1 kg): **{mark(check['mass_ok'])}**")
        st.write(f"Length limit (≤30 cm): **{mark(check['length_ok'])}**")
        st.write(f"Fuel volume limit (≤20 ml): **{mark(check['fuel_ok'])}**")
        st.write(f"Boiler SF ≥2: **{mark(check['safety_factor_ok'])}**")
        st.write(f"Pressure ≤ allowable: **{mark(check['pressure_ok'])}**")

        st.metric("Hoop stress (MPa)", f"{check['hoop_stress_pa']/1e6:.2f}")
        st.metric("Computed safety factor", f"{check['boiler_safety_factor']:.2f}")
        st.metric("Allowable pressure (kPa abs)", f"{check['allowable_pressure_pa']/1000:.1f}")

        all_ok = all([check["mass_ok"], check["length_ok"], check["fuel_ok"], check["safety_factor_ok"], check["pressure_ok"], motion["go"]])
        if all_ok:
            st.success("Design summary: Feasible under current assumptions and constraints.")
        else:
            st.warning("Design summary: Not yet feasible. Adjust pressure, mass, gearing, or structure.")


if __name__ == "__main__":
    run_dashboard()
