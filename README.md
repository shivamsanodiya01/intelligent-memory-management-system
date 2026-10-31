# Intelligent Memory Management System Using Predictive Page Replacement

A local Operating Systems simulation that compares **FIFO**, **LRU**, and **Optimal** page replacement with a **rule-based predictive** algorithm. The dashboard is built with **Python 3.13** and **Streamlit**.

This is a teaching/simulation project. It does not modify a real operating system kernel.

## Project objective

Show how limited main memory is managed when programs generate a sequence of page requests (a **reference string**), and compare classical replacement policies with a predictive policy that estimates which loaded page is least likely to be needed soon.

## Problem statement

When a CPU references a page that is not in a memory frame, a **page fault** occurs. If every frame is occupied, the OS must **replace** one resident page. Different victim choices produce different fault counts. Students usually study FIFO, LRU, and Optimal. This project adds a deterministic predictor based on:

- how often each page has appeared (**frequency**)
- how recently it was used (**recency**)
- how often one page is followed by another (**transition probability**)

## Features

- Manual reference-string input and sample strings
- Configurable number of frames
- FIFO, LRU, Optimal, and Predictive algorithms
- Page faults, hits, hit ratio, and fault ratio
- Step-by-step frame snapshots with Hit / Fault on every reference
- Comparison table and charts
- Predictive scores shown when a victim is chosen
- Input checks for empty strings and frame count ≤ 0
- Automated unit tests
- Graphite Green dashboard with per-algorithm summary metrics, memory utilization, and a replacement timeline

The Streamlit theme is configured in `.streamlit/config.toml` and uses a dark graphite
palette with emerald accents. The overview metrics summarize the first selected
algorithm; the comparison cards and charts show every selected algorithm.

## Algorithms

| Algorithm | Victim choice | Uses the future? |
|-----------|---------------|------------------|
| FIFO | Page that entered memory first | No |
| LRU | Page unused for the longest time | No |
| Optimal | Page whose next use is farthest (or never) | Yes (benchmark only) |
| Predictive | Resident page with the lowest prediction score | No |

**Optimal** is treated as a theoretical benchmark. A real OS cannot see future references. The predictive algorithm is **not** guaranteed to beat Optimal, FIFO, or LRU on every string.

## Predictive methodology

History is updated **after** each decision, so the current request and any future requests are not used when choosing a victim.

1. Count how many times each page has appeared so far.
2. Record the last step index at which each page was used.
3. Count observed pairs `(previous page → next page)`.
4. On a fault with full memory, score every resident page *p*:

### Formula

```
Prediction Score S(p) =
    alpha * Frequency Score F(p)
  + beta  * Recency Score R(p)
  + gamma * Transition Probability T(p)
```

- **F(p)** — count(*p*) divided by the maximum count among resident pages (range 0–1)
- **R(p)** — normalized recency among resident pages (newer → closer to 1)
- **T(p)** — P(*p* | previous page) from the transition counts
- **alpha, beta, gamma** — sidebar weights, then normalized so they sum to 1

The resident page with the **lowest** S(p) is replaced (least likely to be needed soon). Equal scores are broken by choosing the left-most frame, which keeps the simulation **deterministic and reproducible**.

This is a **rule-based** method, not machine learning and not random.

## Project structure

```
Intelligent-Memory-Management/
├── app.py
├── requirements.txt
├── README.md
├── algorithms/
│   ├── __init__.py
│   ├── common.py
│   ├── fifo.py
│   ├── lru.py
│   ├── optimal.py
│   └── predictive.py
├── prediction/
│   ├── __init__.py
│   ├── frequency.py
│   ├── recency.py
│   └── transition.py
├── visualization/
│   ├── __init__.py
│   └── graphs.py
└── tests/
    ├── __init__.py
    └── test_algorithms.py
```

`algorithms/common.py` only holds shared result formatting so every algorithm returns the same fields.

## Installation (Windows)

Use the existing virtual environment in this folder if it is already present.

```powershell
cd C:\Intelligent-Memory-Management
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If `Activate.ps1` is blocked, run:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## How to run

```powershell
cd C:\Intelligent-Memory-Management
.\venv\Scripts\python.exe -m streamlit run app.py
```

The app opens in the browser (usually `http://localhost:8501`).

### Run tests

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_algorithms -v
```

The project theme is loaded automatically when running Streamlit from the project
directory, as in the command above.

## Example input

- Reference string: `7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1`
- Frames: `3`

### Expected type of output

You should see a table of faults/hits/ratios, two bar charts, and a step-by-step trace. For this well-known string with 3 frames, the classical algorithms match the usual textbook counts:

- FIFO: **15** faults, **5** hits
- LRU: **12** faults, **8** hits
- Optimal: **9** faults, **11** hits

Predictive fault count depends on the weights. It will be a real simulated number for that run, not a hardcoded value. Optimal remaining lowest (or tied) on many strings is normal.

## Limitations

- Simulation only: no real virtual-memory hardware, TLB, or disk I/O
- Transition model is first-order (looks at one previous page)
- Predictive quality depends on locality in the reference string and on weights
- Optimal uses future knowledge; it is not a practical OS policy
- Page identifiers must be integers

## Future scope

- Second-order transitions or working-set windows
- Belady's anomaly demonstration for FIFO
- Export of traces to CSV
- Comparison against Clock / Second-Chance
- Longer traces generated from simple program models

## Viva notes (short)

1. A **page fault** means the page is not in any frame.
2. **Hit ratio** = hits / total references.
3. **FIFO** = oldest in; **LRU** = least recently used; **Optimal** = used farthest in the future.
4. **Predictive** scores resident pages from past frequency, recency, and P(next | previous), then drops the lowest score.
5. Do not claim Predictive always wins. Optimal is the theoretical benchmark.
