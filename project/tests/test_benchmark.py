"""Performance benchmark test for Bouncing Ball Simulator V4.0.

Benchmarks a full 30-second simulation at 30 FPS (or equivalent physics steps)
and records execution wall-clock time and speedup factor.
"""

import time
import pytest
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def benchmark_30s_simulation(dt: float = 0.002, restitution: float = 1.0) -> dict:
    """Run a 30-second simulation (e.g. perfectly elastic e=1.0 for continuous calculation)."""
    cfg = SimulationConfig(
        initial_height=10.0,
        restitution=restitution,
        dt=dt,
        max_time=30.0,
    )
    sim = BouncingBallSimulator(cfg)

    t_start = time.perf_counter()
    summary = sim.run()
    elapsed_wall_time = time.perf_counter() - t_start

    simulated_duration = summary["final_time"]
    speedup = simulated_duration / elapsed_wall_time if elapsed_wall_time > 0 else float("inf")

    return {
        "simulated_time_sec": simulated_duration,
        "wall_clock_time_sec": elapsed_wall_time,
        "speedup_factor": speedup,
        "steps_computed": len(sim.history),
        "total_collisions": summary["total_collisions"],
    }


def test_benchmark_performance_smoke():
    """Verify 30-second simulation benchmark runs and finishes smoothly."""
    results = benchmark_30s_simulation(dt=0.002, restitution=1.0)

    assert results["simulated_time_sec"] >= 29.9
    assert results["wall_clock_time_sec"] > 0
    # Must run faster than real time (speedup > 1.0x) on modern machines
    assert results["speedup_factor"] > 1.0, f"Benchmark was slower than real-time: {results['speedup_factor']:.2f}x"
    print(f"\n[BENCHMARK RESULT]: 30s sim took {results['wall_clock_time_sec']:.4f}s ({results['speedup_factor']:.1f}x real-time)")


if __name__ == "__main__":
    res = benchmark_30s_simulation()
    print("Benchmark Result:", res)
