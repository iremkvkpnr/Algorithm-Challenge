# VRP API — Vehicle Routing Problem Solver

A straightforward HTTP service that solves Vehicle Routing Problems using Google OR-Tools. I built this to handle real-world delivery optimization scenarios with a clean, extensible architecture.

## What It Does

**Input:** Vehicles, jobs, and travel time matrix

**Output:** Optimized delivery routes that minimize total time

**Stack:** FastAPI + OR-Tools + Pydantic (with optional MongoDB)

**Philosophy:** Keep it simple, make it work, then make it better

## Core Features

This service takes your delivery problem and figures out the best routes:

- **Handles any scale:** Works with 5 jobs or 500 jobs per request
- **Real service times:** Accounts for both travel time and time spent at each stop
- **Capacity aware:** Respects vehicle capacity limits when provided
- **Flexible endings:** Vehicles don't have to return to depot (useful for real operations)
- **Reproducible:** Set a seed to get the same solution every time
- **Optional persistence:** Can save solutions to MongoDB for later analysis

## Why I Built It This Way

- **Fresh optimization:** Every request gets a custom solution (no cached approximations)
- **Configurable:** Tune solver behavior via environment variables
- **Clean code:** Proper separation of concerns, easy to understand and modify
- **Room to grow:** Architecture supports adding new features without major rewrites

## How It Works

1. Convert incoming JSON → domain objects
2. Build OR-Tools model (RoutingIndexManager + RoutingModel) with sink node for flexible endings
3. Register transit callbacks: distance (travel time) + time (travel + service)
4. Add dimensions (Time, Capacity) when applicable
5. Solve with configurable search parameters
6. Extract routes via NextVar traversal, compute metrics, return JSON

## Run Locally

```bash
git clone <repo>
cd Algorithm-Challenge
pip install -r requirements.txt
python -m src.main
# docs: http://localhost:8000/docs
```

## Environment Variables

```bash
VRP_TIME_LIMIT=30          # Maximum solve time in seconds
VRP_SOLUTION_LIMIT=100     # Maximum number of solutions to explore
VRP_RANDOM_SEED=42         # Random seed for deterministic results
MONGO_URI=mongodb://localhost:27017/vrp
```

## API Usage

**Endpoint:** `POST /solve`

**Request Format:**
```json
{
  "vehicles": [...],
  "jobs": [...], 
  "matrix": [...]
}
```

**Example Response:**
```json
{
  "total_delivery_duration": 8547,
  "routes": {
    "1": {
      "jobs": [3, 7, 12],
      "delivery_duration": 4231,
      "capacity_used": 8,
      "total_service_time": 900,
      "total_distance": 3331,
      "start_location": 0,
      "end_location": 15
    },
    "2": {
      "jobs": [1, 5, 9, 14],
      "delivery_duration": 4316,
      "capacity_used": 12,
      "total_service_time": 1200,
      "total_distance": 3116,
      "start_location": 0,
      "end_location": 8
    }
  },
  "metadata": {
    "solve_time_seconds": 0.087,
    "algorithm": "OR-Tools",
    "objective_value": 8547,
    "random_seed": 999,
    "jobs_count": 7,
    "vehicles_used": 2
  }
}
```

## Current Limitations & Trade-offs

- **Synchronous processing:** Solver runs on the request thread, so large problems might timeout
- **Fresh solve every time:** No warm-starting from previous solutions (keeps things simple for now)
- **Basic observability:** Minimal logging and no metrics yet
- **No auth/rate limiting:** Focused on the core algorithm, not production hardening

## Benchmarks (Summary)

Tested several OR-Tools strategies on sample instances:

| Configuration | Total Duration | Solve Time | Notes |
|---------------|----------------|------------|-------|
| **Default** (PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH) | 6345 | 0.039s | Best speed/quality balance |
| **SAVINGS** strategy | 6345 | 0.039s | Same result |
| **TABU_SEARCH** | 6345 | 0.041s | Same result |
| **SIMULATED_ANNEALING** | 6345 | 0.100s | Same result, slower |
| **Global Span Cost** (100) | 6345 | 1.691s | Same result, much slower |

**Key findings:** Default configuration optimal for tested sizes. Global-span balancing increases runtime significantly.

## What's Next

I kept this focused on the core problem, but here's where it could go:

### Quick Wins
- **Async processing:** Move big solves to background tasks
- **Better baselines:** Add simple greedy algorithm for comparison
- **More solver options:** Expose time limits and strategies in the API

### Bigger Ideas
- **Event-driven optimization:** Auto-reoptimize when new jobs come in
- **Incremental solving:** Use previous solutions as starting points
- **Multi-objective:** Balance time, distance, and operational costs
- **Production hardening:** Auth, rate limiting, proper monitoring

## Want to Experiment?

- Bump `VRP_TIME_LIMIT` to 60+ seconds for better solutions on large problems
- Try different strategies in `src/services/vrp_service.py` (SAVINGS, TABU_SEARCH, etc.)
- Use `VRP_RANDOM_SEED` to get consistent results when testing
- Check the benchmark table above to see what works best

## Testing

```bash
# Run tests
PYTHONPATH=. pytest tests/ -v

# Experiment with algorithms
# Modify solver parameters in src/services/vrp_service.py
# Test with: VRP_TIME_LIMIT=60 python -m src.main
```