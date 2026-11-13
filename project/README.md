# Bouncing Ball Simulator (V4.0)

A physics-based discrete-time numerical simulation of a bouncing ball using semi-implicit Euler integration, sub-timestep Time-of-Impact (TOI) collision detection, coefficient of restitution energy loss, resting contact mechanics, and decoupled rendering.

---

## 📁 Project Architecture

```text
project/
├── src/
│   ├── __init__.py
│   ├── physics.py          # Semi-implicit Euler integration & TOI quadratic solver
│   ├── simulator.py        # Simulation engine, state management, energy accounting
│   ├── experiments.py      # Automated parameter sweep experiments
│   └── visualization.py    # Matplotlib plots, figures, and validation graphs
├── tests/
│   ├── __init__.py
│   ├── test_toi.py                 # Time-of-Impact analytical & boundary validation
│   ├── test_event_cap.py           # Pathological collision handling
│   ├── test_csv_output.py          # CSV format and column consistency
│   ├── test_rendering_indep.py     # 10 FPS vs 60 FPS physics decoupling
│   └── test_benchmark.py           # 30-second simulation performance benchmark
├── results/                # Output datasets (simulation_data.csv & experiment CSVs)
├── reports/
│   ├── TECHNICAL_REPORT.md # Full technical report with theory, equations, & validation
│   └── figures/            # Output graphs (validation.png, etc.)
└── docs/
    └── SPECIFICATION_V4.md # Consolidated V4.0 Project Specification
```

---

## ⚡ Reference Benchmark Result
As required by Section 7 of the V4.0 specification, benchmarking was performed on the reference test system:
* **System CPU:** Intel64 GenuineIntel
* **Simulated Physical Duration:** 30.0 seconds (15,002 integration steps, $e = 1.0$)
* **Wall-Clock Time:** **0.0460 s** (~46 ms)
* **Speedup Factor:** **652.0x faster than real-time**

---

## 🚀 Running the Project

### 1. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 2. Run Test Suite
```bash
python -m pytest tests/ -v
```

### 3. Run Experiments & Generate CSVs
```bash
python -m project.src.experiments
```
Outputs generated under `results/`:
- `results/simulation_data.csv`
- `results/experiment_restitution.csv`
- `results/experiment_height.csv`
- `results/experiment_dt_sensitivity.csv`

### 4. Generate Validation Plots
```bash
python -m project.src.visualization
```
Generated figure:
- `reports/figures/validation.png`

---

## 📖 Documentation
* Technical Report: [reports/TECHNICAL_REPORT.md](reports/TECHNICAL_REPORT.md)
* Consolidated V4.0 Specification: [docs/SPECIFICATION_V4.md](docs/SPECIFICATION_V4.md)
