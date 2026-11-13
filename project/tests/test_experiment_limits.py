"""Tests for Experiment Reporting, Termination Limits, and File Overwriting (Sections 6 & 8)."""

import os
import pytest
from project.src.experiments import run_single_simulation
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_30_second_limit_unsettled_elastic():
    """Verify that perfectly elastic bouncing (e = 1.0) terminates at 30s with proper reporting."""
    cfg = SimulationConfig(
        initial_height=5.0,
        restitution=1.0,
        dt=0.005,
        max_time=30.0,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()

    # Must hit the 30.0s mark
    assert pytest.approx(30.0, abs=0.05) == summary["final_time"]
    assert summary["settling_status"] == "Did not settle"
    assert summary["settling_time"] == ">30 seconds"
    # Must have recorded multiple collisions
    assert summary["total_collisions"] > 5
    assert len(sim.collisions) == summary["total_collisions"]


def test_settled_simulation_reporting():
    """Verify that dissipative simulation reports 'Settled' and valid numerical time < 30s."""
    cfg = SimulationConfig(
        initial_height=5.0,
        restitution=0.6,
        dt=0.002,
        max_time=30.0,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()

    assert summary["settling_status"] == "Settled"
    settle_time_val = float(summary["settling_time"])
    assert 0.0 < settle_time_val < 30.0


def test_simulation_data_csv_overwritten(tmp_path):
    """Verify results/simulation_data.csv is cleanly overwritten upon new session."""
    csv_file = str(tmp_path / "simulation_data.csv")

    # Run session 1 with 2.0m height
    cfg1 = SimulationConfig(initial_height=2.0, max_time=2.0)
    sim1 = BouncingBallSimulator(cfg1)
    sim1.run()
    sim1.export_csv(csv_file)
    size1 = os.path.getsize(csv_file)

    # Run session 2 with 8.0m height (longer trajectory)
    cfg2 = SimulationConfig(initial_height=8.0, max_time=4.0)
    sim2 = BouncingBallSimulator(cfg2)
    sim2.run()
    sim2.export_csv(csv_file)
    size2 = os.path.getsize(csv_file)

    assert os.path.exists(csv_file)
    # The file should be updated with new run's content
    assert size2 != size1
