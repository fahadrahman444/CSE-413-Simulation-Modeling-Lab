"""Visualization tools and analytical validation graph generation.

Outputs:
- project/reports/figures/validation.png
- project/reports/figures/energy_conservation.png
- project/reports/figures/parameter_sweeps.png
"""

import os
import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .physics import calculate_analytical_first_impact_time
from .simulator import BouncingBallSimulator, SimulationConfig


def generate_validation_plots(
    output_dir: str = "project/reports/figures",
    show_plot: bool = False,
) -> str:
    """Generate comprehensive analytical validation graphs saved as validation.png."""
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "validation.png")

    cfg = SimulationConfig(
        initial_height=10.0,
        radius=0.1,
        mass=1.0,
        restitution=0.75,
        gravity=9.8,
        dt=0.001,
        max_time=15.0,
    )
    sim = BouncingBallSimulator(cfg)
    sim.run()
    df = sim.to_dataframe()

    # Analytical trajectory for the first free-fall phase:
    t_analytical_1 = calculate_analytical_first_impact_time(cfg.initial_height, cfg.gravity)
    t_analytical = np.linspace(0, t_analytical_1, 200)
    y_analytical = (cfg.initial_height + cfg.radius) - 0.5 * cfg.gravity * (t_analytical**2)
    v_analytical = -cfg.gravity * t_analytical

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Bouncing Ball Simulator V4.0 — Physical & Analytical Validation",
        fontsize=14,
        fontweight="bold",
    )

    # 1. Position Trajectory vs Analytical
    axs[0, 0].plot(df["time"], df["position_y"], label="Numerical (Semi-Implicit Euler + TOI)", color="royalblue", lw=2)
    axs[0, 0].plot(t_analytical, y_analytical, "--", color="crimson", lw=2, label="Analytical Fall 1 ($y = y_0 - \\frac{1}{2}gt^2$)")
    axs[0, 0].axhline(y=cfg.radius, color="black", linestyle=":", label="Ground Surface Contact ($y=r$)")
    axs[0, 0].set_title("Ball Center Position vs. Time ($y(t)$)")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Vertical Position $y$ (m)")
    axs[0, 0].grid(True, linestyle="--", alpha=0.6)
    axs[0, 0].legend(loc="upper right")

    # 2. Velocity Profile
    axs[0, 1].plot(df["time"], df["velocity"], label="Numerical Velocity $v(t)$", color="darkorange", lw=1.5)
    axs[0, 1].plot(t_analytical, v_analytical, "--", color="black", lw=1.5, label="Analytical Velocity 1 ($-gt$)")
    axs[0, 1].axhline(y=0, color="gray", linestyle="-", alpha=0.5)
    axs[0, 1].set_title("Velocity Profile ($v(t)$)")
    axs[0, 1].set_xlabel("Time (s)")
    axs[0, 1].set_ylabel("Vertical Velocity (m/s)")
    axs[0, 1].grid(True, linestyle="--", alpha=0.6)
    axs[0, 1].legend(loc="lower right")

    # 3. Energy Conservation & Dissipation Breakdown
    axs[1, 0].plot(df["time"], df["potential_energy"], label="Potential Energy (PE)", color="forestgreen", lw=1.5)
    axs[1, 0].plot(df["time"], df["kinetic_energy"], label="Kinetic Energy (KE)", color="goldenrod", lw=1.5)
    axs[1, 0].plot(df["time"], df["mechanical_energy"], label="Mechanical Energy (PE + KE)", color="purple", lw=1.8)
    axs[1, 0].plot(df["time"], df["dissipated_energy"], label="Cumulative Dissipated", color="firebrick", linestyle="--", lw=1.8)
    axs[1, 0].plot(df["time"], df["total_energy"], label="Total Accounting ($E_{mech} + E_{diss}$)", color="black", lw=2.0)
    axs[1, 0].set_title("Energy Accounting & Conservation Budget")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Energy (Joules)")
    axs[1, 0].grid(True, linestyle="--", alpha=0.6)
    axs[1, 0].legend(loc="right")

    # 4. Phase Portrait (y vs v)
    axs[1, 1].plot(df["position_y"], df["velocity"], color="teal", lw=1.2, alpha=0.85)
    axs[1, 1].plot(df["position_y"].iloc[0], df["velocity"].iloc[0], "go", label="Start")
    axs[1, 1].plot(df["position_y"].iloc[-1], df["velocity"].iloc[-1], "ro", label="Settled")
    axs[1, 1].set_title("Phase Portrait ($y$ vs. $v$)")
    axs[1, 1].set_xlabel("Position $y$ (m)")
    axs[1, 1].set_ylabel("Velocity $v$ (m/s)")
    axs[1, 1].grid(True, linestyle="--", alpha=0.6)
    axs[1, 1].legend()

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()

    if show_plot:
        plt.show()

    return out_file


def generate_all_figures() -> None:
    """Generate all figures for reporting."""
    print("Generating validation.png -> project/reports/figures/validation.png")
    generate_validation_plots()
    print("Validation figure generated successfully.")


if __name__ == "__main__":
    generate_all_figures()
