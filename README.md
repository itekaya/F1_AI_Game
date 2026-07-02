# F1 AI Racing

A top-down F1 racing simulation where cars learn to drive around a track using **NEAT** (NeuroEvolution of Augmenting Topologies). Instead of scripting driving behavior, each car is controlled by a small neural network evolved over successive generations until it learns to take corners, avoid walls, and complete laps on its own.

## How it works

- Each car is equipped with 5 forward-facing distance sensors (raycasts at -60°, -30°, 0°, 30°, 60°) plus its current speed, giving 6 inputs to a neural network.
- The network outputs 2 values controlling throttle and steering.
- Every generation, a population of cars is spawned simultaneously on the track. Cars are rewarded for staying alive, moving fast, passing checkpoints, and completing laps, and penalized for colliding with track walls or sitting idle.
- Cars that crash too many times or stall out are removed from the simulation early.
- NEAT evolves the population's neural networks (topology and weights) across generations based on fitness, gradually producing better drivers.

## Project structure

```
main.py                  Entry point — runs the NEAT training loop and simulation
car.py                   Car physics, collision detection, sensors, and rendering
track.py                 Track loading, collision mask, checkpoints, start/finish line
config-feedforward.txt   NEAT hyperparameters (population size, mutation rates, etc.)
assets/                  Track images, collision masks, car sprite, and checkpoint data
```

## Requirements

- Python 3.10+
- [pygame](https://www.pygame.org/)
- [neat-python](https://neat-python.readthedocs.io/)

Install dependencies:

```bash
pip install pygame neat-python
```

## Running

```bash
python main.py
```

A window will open showing the track and the current generation of cars racing simultaneously. On-screen text shows the number of cars still alive, the current generation, and lap count.

## Controls

The simulation also doubles as a checkpoint editor for the track:

| Key | Action |
|---|---|
| `Left Click` | Place a checkpoint at the mouse position |
| `Backspace` | Remove the last placed checkpoint |
| `H` | Switch new checkpoints to horizontal orientation |
| `V` | Switch new checkpoints to vertical orientation |
| `P` | Print all checkpoints to the console as Python code |
| `F` | Free the camera (stop following the lead car) |
| `G` | Re-enable camera follow |
| `Z` / `Q` / `S` / `D` | Move the camera manually (when not following) |

Checkpoints are saved automatically to `assets/checkpoints.json` whenever they're added or removed.

## Configuration

NEAT's behavior (population size, mutation rates, fitness threshold, network topology constraints, etc.) is controlled entirely through `config-feedforward.txt`. Tweak this file to change how quickly and aggressively the population evolves.
