"""Tests for Rendering Independence (Physics decoupled from frame rate).

Requirement:
Verify that 10 FPS and 60 FPS rendering loops produce identical physical simulation
results for identical simulation durations when using fixed physics timestep integration.
"""

import math
import pytest
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def run_sim_with_render_fps(fps: float, total_duration: float, physics_dt: float = 0.002):
    """Simulate rendering at a given frame rate while running a fixed physics timestep."""
    cfg = SimulationConfig(
        initial_height=10.0,
        restitution=0.8,
        radius=0.1,
        mass=1.0,
        gravity=9.8,
        dt=physics_dt,
        max_time=total_duration,
    )
    sim = BouncingBallSimulator(cfg)

    frame_dt = 1.0 / fps
    accumulated_time = 0.0
    elapsed_sim_time = 0.0

    # Decoupled game loop / accumulator pattern
    while elapsed_sim_time < (total_duration - 1e-9) and not sim.is_settled:
        accumulated_time += frame_dt
        elapsed_sim_time += frame_dt

        # Consume accumulated time in fixed physics_dt chunks
        while accumulated_time >= physics_dt - 1e-12 and not sim.is_settled:
            sim.step(physics_dt)
            accumulated_time -= physics_dt

    return sim


def test_rendering_rate_independence():
    """Verify that 10 FPS and 60 FPS rendering produce identical physical results."""
    duration = 3.0  # 3 seconds of simulation time
    fixed_dt = 0.002

    sim_10fps = run_sim_with_render_fps(fps=10.0, total_duration=duration, physics_dt=fixed_dt)
    sim_60fps = run_sim_with_render_fps(fps=60.0, total_duration=duration, physics_dt=fixed_dt)

    # 1. Total collisions must be identical
    assert sim_10fps.collision_count == sim_60fps.collision_count, (
        f"Collision count mismatch: 10 FPS={sim_10fps.collision_count}, 60 FPS={sim_60fps.collision_count}"
    )

    # 2. Final position y must be identical
    assert pytest.approx(sim_10fps.y, abs=1e-5) == sim_60fps.y

    # 3. Final velocity v must be identical
    assert pytest.approx(sim_10fps.v, abs=1e-5) == sim_60fps.v

    # 4. Each collision timestamp must match exactly
    for c10, c60 in zip(sim_10fps.collisions, sim_60fps.collisions):
        assert pytest.approx(c10.time, abs=1e-5) == c60.time
        assert pytest.approx(c10.impact_velocity, abs=1e-5) == c60.impact_velocity
        assert pytest.approx(c10.rebound_velocity, abs=1e-5) == c60.rebound_velocity
