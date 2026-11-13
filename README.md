# CSE-413-Simulation-Modeling-Lab
Official repository for CSE 413: Simulation &amp; Modeling Lab. Contains all lab work, class assignments, and course projects.
Course Code: CSE 413
Course Teacher: Audity Ghosh, Lecturer, Department of Computer Science and Engineering, University of Information Technology and Sciences (UITS)
Welcome to the **CSE 413: Simulation & Modeling Lab** repository. This repository contains class work, lab assignments, statistical testing scripts, and project submissions for the course.
---
## 📌 Course Overview

### What is Simulation & Modeling?

Imagine you are designing a new traffic light system for a busy city. You wouldn't test it directly on real streets—that could disrupt traffic, cost money, and cause accidents. Instead, you create a virtual version of the system and test it digitally.

* **Modeling:** Creating a simplified representation of a system (e.g., mathematical equations or algorithms that represent traffic flow, car speeds, and signal timing).
* **Simulation:** Running experiments on that model over time to observe its behavior under various conditions (e.g., simulating rush-hour bottlenecks or road closures).

By combining modeling and simulation, we can predict system behavior, optimize performance, and solve complex engineering problems without real-world risks or costs.

---

## 🎯 Why Take This Course?

* **Practical Skillset:** Build hands-on proficiency in **Python** (`numpy`, `scipy.stats`, `matplotlib`), the industry standard for modeling and data analysis.
* **Problem Solving:** Learn to model real-world systems, ranging from network traffic and distributed systems to financial markets and queueing mechanics.
* **Research & Career Ready:** Acquire statistical and simulation tools essential for academic research, thesis projects, and roles in AI, Data Science, and Systems Engineering.

---

## 📚 Course Breakdown & Applications

Below is the structured course outline along with real-world scenarios and Python implementations covered in this course:

| Topic | Real-World Scenario | Python Implementation / Libraries |
| :--- | :--- | :--- |
| **1. Intro to Python & Basic Operations** | Robotic control systems calculating angles and managing sensor inputs. | Basic operations, matrix manipulations. |
| **2. Random Number Generation** | Gaming apps generating random events (dice rolls, card shuffles). | `numpy.random` |
| **3. One-Sample t-Test** | Analyzing customer engagement before and after a marketing campaign. | `scipy.stats.ttest_1samp` |
| **4. Two-Sample t-Test** | Comparing the performance of two distinct Machine Learning algorithms. | `scipy.stats.ttest_ind` |
| **5. Chi-Square Goodness-of-Fit Test** | Checking if customer purchase distributions match a theoretical model. | `scipy.stats.chisquare` |
| **6. Performing Chi-Square Test** | Healthcare analytics testing disease distribution patterns across regions. | `scipy.stats.chisquare` |
| **7. One-Sample Kolmogorov-Smirnov Test** | Verifying if financial market returns follow a normal distribution. | `scipy.stats.kstest` |
| **8. Two-Sample Kolmogorov-Smirnov Test** | Comparing web server response rates under identical traffic loads. | `scipy.stats.ks_2samp` |
| **9. Testing Normality** | Validating sensor noise distributions in robotics before applying models. | `scipy.stats.normaltest` |
| **10. Implementation of Monte Carlo Simulation** | Simulating future stock prices to evaluate investment portfolio risk. | Custom sampling with `numpy.random` |
| **11. Single Server Queuing System** | Optimizing agent allocation and wait times in a customer support queue. | Queuing models / Discrete-event logic |
| **12. Complex Engineering Problem** | Designing an industrial robotic arm (motor behavior, efficiency, reach). | Multi-variable dynamic simulations |

---

## 📁 Repository Structure

```text
CSE-413-Simulation-Modeling-Lab/
├── labs/
│   ├── Lab-01/
│   │   └── SIM_Lab1_Md_Fahad_Rahman_0432320005101071(B1).ipynb
│   └── Lab-02/
│       └── SIM_Lab2_Md_Fahad_Rahman_0432320005101071(B1).ipynb
├── project/
│   ├── main.py              # CLI entry point for custom parameter simulations
│   ├── src/                 # Physics engine, state manager, live GUI visualizer
│   ├── tests/               # 21 automated unit tests (TOI, energy, benchmark, etc.)
│   ├── results/             # Datasets (simulation_data.csv & experiment CSVs)
│   ├── reports/             # Technical report & generated figures (validation.png)
│   ├── docs/                # V4.0 specification & presentation defense guide
│   └── README.md            # Project technical overview
├── run.bat                  # One-click Windows interactive launcher
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🎯 Lab Assignments

| Lab | Topic | Notebook Link |
| :--- | :--- | :--- |
| **Lab 01** | NumPy Scalar, Matrix, and Vector Operations | [Lab-01 Notebook](labs/Lab-01/SIM_Lab1_Md_Fahad_Rahman_0432320005101071(B1).ipynb) |
| **Lab 02** | Unique Matrix Value Investigation | [Lab-02 Notebook](labs/Lab-02/SIM_Lab2_Md_Fahad_Rahman_0432320005101071(B1).ipynb) |

---

## 🚀 Course Project: Bouncing Ball Simulator (V4.0)

A physically accurate discrete-time bouncing ball simulator implementing:
* **Upward-positive coordinates**: Ground at $y = 0$, contact at $y = r$, upward velocity positive, $-g$ gravity.
* **Semi-implicit Euler integration**: Symplectic scheme ensuring phase-space stability without energy explosion.
* **Exact Time-of-Impact (TOI)**: Analytical quadratic root solver detecting collisions at sub-millisecond precision without floor tunneling.
* **Resting contact mechanics**: Settling velocity threshold ($0.08\text{ m/s}$) preventing Zeno paradox infinite chatter.
* **Decoupled rendering**: Bitwise physics invariance across different visual frame rates (10 vs 60 FPS).
* **21 Automated Verification Tests**: All passing covering TOI, energy conservation, event cap, benchmarks, and CSV integrity.
* **One-Click Windows Launcher**: Double-click [run.bat](run.bat) to launch the live 2D GUI, run simulations, or execute tests.

### 📚 Documentation & Guides
* **Oral Defense & Viva Guide:** [PRESENTATION_DEFENSE_GUIDE.md](project/docs/PRESENTATION_DEFENSE_GUIDE.md)
* **Technical Report:** [TECHNICAL_REPORT.md](project/reports/TECHNICAL_REPORT.md)
* **Validation Plot:** [validation.png](project/reports/figures/validation.png)
* **Consolidated V4.0 Specification:** [SPECIFICATION_V4.md](project/docs/SPECIFICATION_V4.md)
* **Project README:** [project/README.md](project/README.md)


