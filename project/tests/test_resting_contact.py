"""Tests for Resting and Grazing Contact handling (Section 4)."""

import pytest
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_resting_contact_settling_and_zero_velocity():
    """Verify ball settles to y=radius and v=0 when velocity drops below SETTLE_VELOCITY."""
    cfg = SimulationConfig(
        initial_height=1.0,
        radius=0.1,
        restitution=0.5,
        settle_velocity=0.1,
        dt=0.002,
        max_time=10.0,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()

    assert summary["settling_status"] == "Settled"
    assert sim.is_settled is True
    # At rest, center is exactly at radius and velocity is 0
    assert pytest.approx(cfg.radius, abs=1e-7) == sim.y
    assert sim.v == 0.0


def test_no_repeated_collisions_after_settling():
    """Verify that once resting, no further collision events are generated."""
    cfg = SimulationConfig(
        initial_height=0.5,
        radius=0.1,
        restitution=0.4,
        settle_velocity=0.1,
        dt=0.002,
        max_time=5.0,
    )
    sim = BouncingBallSimulator(cfg)
    sim.run()

    assert sim.is_settled is True
    collisions_at_rest = sim.collision_count

    # Advance an additional 100 timesteps while resting
    for _ in range(100):
        sim.step()

    # Collision count must NOT increase while resting
    assert sim.collision_count == collisions_at_rest
    assert sim.y == cfg.radius
    assert sim.v == 0.0


def test_settling_dissipates_residual_kinetic_energy():
    """Verify residual kinetic energy at contact is added to cumulative dissipated energy."""
    cfg = SimulationConfig(
        initial_height=0.1,
        radius=0.1,
        restitution=0.2,
        settle_velocity=0.2,
        dt=0.001,
        max_time=5.0,
    )
    sim = BouncingBallSimulator(cfg)
    sim.run()

    assert sim.is_settled is True
    assert sim.dissipated_energy > 0.0
    # Final mechanical energy at rest should be zero relative to contact surface (y = radius)
    final_state = sim.history[-1]
    assert pytest.approx(0.0, abs=1e-6) == final_state.pe
    assert pytest.approx(0.0, abs=1e-6) == final_state.ke
    assert pytest.approx(0.0, abs=1e-6) == final_state.mechanical_energy
