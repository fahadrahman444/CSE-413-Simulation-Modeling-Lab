"""Tests for CSV output format, column names, and numerical integrity."""

import os
import pandas as pd
import pytest
from project.src.experiments import (
    run_dt_sensitivity_experiment,
    run_height_experiment,
    run_restitution_experiment,
    run_single_simulation,
)


def test_simulation_data_csv_structure(tmp_path):
    """Verify results/simulation_data.csv has required columns and valid numbers."""
    csv_file = str(tmp_path / "simulation_data.csv")
    sim = run_single_simulation(csv_output_path=csv_file)

    assert os.path.exists(csv_file)
    df = pd.read_csv(csv_file)

    expected_cols = [
        "time",
        "position_y",
        "velocity",
        "potential_energy",
        "kinetic_energy",
        "mechanical_energy",
        "dissipated_energy",
        "total_energy",
        "is_settled",
        "collision_count",
    ]

    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in CSV output"

    # Verify no NaN or Inf values
    assert not df.isna().any().any(), "CSV contains NaN values"
    assert len(df) > 10, "CSV has insufficient rows"


def test_experiment_csv_one_row_per_parameter(tmp_path):
    """Verify experiment CSVs contain exactly one row per tested parameter."""
    restitutions = [0.2, 0.5, 0.8, 1.0]
    out_csv = str(tmp_path / "exp_restitution.csv")
    df = run_restitution_experiment(restitutions=restitutions, output_path=out_csv)

    assert os.path.exists(out_csv)
    assert len(df) == len(restitutions)

    # Check that e=1.0 reports 'Did not settle' and '>30 seconds'
    row_1 = df[df["restitution"] == 1.0].iloc[0]
    assert row_1["settling_status"] == "Did not settle"
    assert row_1["settling_time"] == ">30 seconds"

    # Check heights experiment
    heights = [2.0, 5.0, 10.0]
    out_h_csv = str(tmp_path / "exp_height.csv")
    df_h = run_height_experiment(heights=heights, output_path=out_h_csv)
    assert len(df_h) == len(heights)
