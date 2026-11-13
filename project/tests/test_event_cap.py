"""Tests for Event-Cap safeguard and pathological collision handling."""

import time
import pytest
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_pathological_collision_does_not_hang():
    """Verify that extreme chatter (e.g. low restitution, large dt) terminates quickly without hanging."""
    cfg = SimulationConfig(
        initial_height=0.005,  # 5 mm drop
        restitution=0.01,      # very inelastic
        dt=0.05,               # large timestep
        max_sub_events_per_step=10,
        max_time=1.0,
    )
    sim = BouncingBallSimulator(cfg)

    start_time = time.time()
    summary = sim.run()
    elapsed = time.time() - start_time

    # Must complete almost instantaneously (under 1 second)
    assert elapsed < 1.0, f"Simulation took too long ({elapsed}s), possible hang"
    assert summary["settling_status"] == "Settled"
    assert sim.is_settled is True


def test_repeated_chatter_event_cap():
    """Verify event cap prevents infinite loop even when settle velocity is set abnormally low."""
    cfg = SimulationConfig(
        initial_height=0.02,
        restitution=0.5,
        dt=0.01,
        settle_velocity=1e-9,  # artificially near zero
        max_sub_events_per_step=10,
        max_time=0.5,
    )
    sim = BouncingBallSimulator(cfg)

    # Step simulation through 20 steps
    for _ in range(20):
        sim.step()

    # Verify simulator did not crash and simulation time advanced
    assert sim.current_time > 0.0
