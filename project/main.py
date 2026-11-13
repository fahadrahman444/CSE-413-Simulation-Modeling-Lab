"""Main executable entry point for Bouncing Ball Simulator V4.0.

Usage examples:
    # Run a default simulation and export CSV & plot:
    python project/main.py

    # Run with custom parameters:
    python project/main.py --height 15.0 --restitution 0.8 --dt 0.002

    # Run all parameter sweep experiments and generate all figures:
    python project/main.py --all
"""

import argparse
import os
import sys

# Ensure repository root is on sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from project.src.simulator import BouncingBallSimulator, SimulationConfig
from project.src.experiments import run_all_experiments
from project.src.visualization import generate_validation_plots


def main():
    parser = argparse.ArgumentParser(
        description="Bouncing Ball Simulator V4.0 (Semi-Implicit Euler + TOI Contact)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--height", type=float, default=10.0, help="Initial drop height in meters")
    parser.add_argument("--restitution", type=float, default=0.75, help="Coefficient of restitution e in [0, 1]")
    parser.add_argument("--radius", type=float, default=0.1, help="Ball radius in meters")
    parser.add_argument("--mass", type=float, default=1.0, help="Ball mass in kg")
    parser.add_argument("--gravity", type=float, default=9.8, help="Gravitational acceleration g in m/s^2")
    parser.add_argument("--dt", type=float, default=0.002, help="Physics timestep duration in seconds")
    parser.add_argument("--max-time", type=float, default=30.0, help="Maximum simulation time cap in seconds")
    parser.add_argument("--csv", type=str, default="project/results/simulation_data.csv", help="Output path for simulation trajectory CSV")
    parser.add_argument("--all", action="store_true", help="Run all parameter sweeps and generate all validation figures")

    args = parser.parse_args()

    if args.all:
        print("=" * 60)
        print("Running full experiment suite and generating figures...")
        print("=" * 60)
        run_all_experiments()
        fig_path = generate_validation_plots()
        print(f"\n[SUCCESS] All datasets saved under 'project/results/'")
        print(f"[SUCCESS] Validation figure saved to '{fig_path}'")
        return

    print("=" * 60)
    print("BOUNCING BALL SIMULATOR — V4.0")
    print("=" * 60)
    print(f"Parameters:")
    print(f"  • Initial Height:   {args.height:.2f} m")
    print(f"  • Ball Radius:      {args.radius:.2f} m (Contact at y = {args.radius:.2f} m)")
    print(f"  • Initial Center y: {args.height + args.radius:.2f} m")
    print(f"  • Restitution (e):  {args.restitution:.2f}")
    print(f"  • Timestep (dt):    {args.dt:.4f} s")
    print(f"  • Max Duration:     {args.max_time:.1f} s")
    print("-" * 60)

    cfg = SimulationConfig(
        initial_height=args.height,
        radius=args.radius,
        mass=args.mass,
        restitution=args.restitution,
        gravity=args.gravity,
        dt=args.dt,
        max_time=args.max_time,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()
    csv_file = sim.export_csv(args.csv)

    print("Simulation Results:")
    print(f"  • Status:           {summary['settling_status']}")
    print(f"  • Settling Time:    {summary['settling_time']} s")
    print(f"  • Total Collisions: {summary['total_collisions']}")
    print(f"  • Initial Energy:   {summary['initial_energy']:.4f} J")
    print(f"  • Final Mech. E:    {summary['final_mechanical_energy']:.4f} J")
    print(f"  • Dissipated Energy:{summary['final_dissipated_energy']:.4f} J")
    print(f"  • Final Total E:    {summary['final_total_energy']:.4f} J")
    print(f"\n[SAVED] Trajectory data exported to: {csv_file}")

    fig_file = generate_validation_plots()
    print(f"[SAVED] Validation plot updated at:   {fig_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
