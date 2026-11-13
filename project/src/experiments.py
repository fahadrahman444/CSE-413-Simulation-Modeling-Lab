"""Experiment runner for parameter sweep studies and CSV generation.

Generates:
- results/simulation_data.csv (default standard run trajectory)
- results/experiment_restitution.csv (variation of restitution e in [0.1, 1.0])
- results/experiment_height.csv (variation of initial height h_0)
- results/experiment_dt_sensitivity.csv (variation of numerical integration dt)

Adheres to V4.0 requirements:
- Single row per tested parameter value in experiment CSVs
- Unsettled runs (e.g., e = 1.0) report 'Did not settle' and '>30 seconds'
"""

import os
from typing import List, Optional
import pandas as pd

from .simulator import BouncingBallSimulator, SimulationConfig


def run_single_simulation(
    config: Optional[SimulationConfig] = None,
    csv_output_path: str = "project/results/simulation_data.csv",
) -> BouncingBallSimulator:
    """Run a standard simulation session and overwrite results/simulation_data.csv."""
    sim = BouncingBallSimulator(config)
    sim.run()
    sim.export_csv(csv_output_path)
    return sim


def run_restitution_experiment(
    restitutions: Optional[List[float]] = None,
    output_path: str = "project/results/experiment_restitution.csv",
) -> pd.DataFrame:
    """Run experiment varying coefficient of restitution e.

    Produces one row per parameter value.
    """
    if restitutions is None:
        restitutions = [0.1, 0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]

    rows = []
    for e in restitutions:
        cfg = SimulationConfig(
            initial_height=10.0,
            restitution=e,
            radius=0.1,
            mass=1.0,
            gravity=9.8,
            dt=0.002,
            max_time=30.0,
        )
        sim = BouncingBallSimulator(cfg)
        summary = sim.run()
        rows.append(summary)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def run_height_experiment(
    heights: Optional[List[float]] = None,
    output_path: str = "project/results/experiment_height.csv",
) -> pd.DataFrame:
    """Run experiment varying drop height h_0."""
    if heights is None:
        heights = [1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0]

    rows = []
    for h in heights:
        cfg = SimulationConfig(
            initial_height=h,
            restitution=0.75,
            radius=0.1,
            mass=1.0,
            gravity=9.8,
            dt=0.002,
            max_time=30.0,
        )
        sim = BouncingBallSimulator(cfg)
        summary = sim.run()
        rows.append(summary)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def run_dt_sensitivity_experiment(
    timesteps: Optional[List[float]] = None,
    output_path: str = "project/results/experiment_dt_sensitivity.csv",
) -> pd.DataFrame:
    """Run experiment analyzing numerical integration error across different timesteps dt."""
    if timesteps is None:
        timesteps = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]

    rows = []
    for dt in timesteps:
        cfg = SimulationConfig(
            initial_height=10.0,
            restitution=0.75,
            radius=0.1,
            mass=1.0,
            gravity=9.8,
            dt=dt,
            max_time=30.0,
        )
        sim = BouncingBallSimulator(cfg)
        summary = sim.run()
        # Calculate maximum energy discrepancy
        df_hist = sim.to_dataframe()
        initial_e = summary["initial_energy"]
        max_energy_drift = float((df_hist["total_energy"] - initial_e).abs().max())
        summary["max_energy_drift_joules"] = max_energy_drift
        summary["relative_energy_error_pct"] = (max_energy_drift / initial_e) * 100.0
        rows.append(summary)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def run_all_experiments() -> None:
    """Execute all parameter sweeps and default simulation data export."""
    print("Executing standard interactive session run -> results/simulation_data.csv")
    run_single_simulation()

    print("Running restitution parameter sweep -> results/experiment_restitution.csv")
    run_restitution_experiment()

    print("Running initial height sweep -> results/experiment_height.csv")
    run_height_experiment()

    print("Running timestep dt sensitivity sweep -> results/experiment_dt_sensitivity.csv")
    run_dt_sensitivity_experiment()
    print("All experiments successfully completed and recorded.")


if __name__ == "__main__":
    run_all_experiments()
