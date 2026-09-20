# Sunny Grove

## Product Goal

Create a calm, polished 2D exploration game that a three-year-old can play independently with the arrow keys. The child guides an original princess through cheerful generated outdoor maps, discovers gems and flowers, and watches separate large counters increase to practice early counting.

The game should feel like a gentle toy, not a challenge: no failure state, no time limit, no enemies, no combat, no score pressure, and no required reading to play. Terrain blocks the princess only to make the world understandable and fun to explore.

## First Playable Experience

1. `python main.py` opens a full-screen game on Windows, Ubuntu, and macOS.
2. The princess explores a bright grassland with randomly generated paths, trees, mountains, water, gems, flowers, and a border gate.
3. Holding arrow keys moves smoothly; diagonal movement has the same overall speed as straight movement.
4. Trees, mountains, water, and map edges block movement.
5. Walking onto a gem or flower collects it automatically, plays a gentle chime when sound is available, and increments its matching counter.
6. Collecting every item opens the wooden border gate and displays an arrow pointing to it. Walking through the open gate starts a fresh generated map and resets counters.
7. Escape and window close may quit. No other control is needed during play.

## Design Principles

- Make objects large, colorful, well-spaced, and forgiving for a toddler.
- Keep exploration calm: no hazards, enemies, timers, health, competition, or failure states.
- Show large, persistent, icon-paired counters for gems and flowers so collection directly supports counting practice.
- Create original art and sound. Do not copy protected characters, maps, sprites, music, UI, or other source material.
- Run fully offline with Python and pygame; bundled assets must resolve independently of the launch directory.

## World

Build one generated, one-screen top-down outdoor map with a central grassy clearing, optional dirt paths, tree clusters, mountain barriers, water, several open collectible pockets, and one border gate. Every pickup must be reachable without a precision puzzle. Spawn the princess near one visible pickup for immediate feedback.

| Terrain | Walkable |
| --- | --- |
| Grass | Yes |
| Path | Yes |
| Tree | No |
| Mountain | No |
| Water | No |

Keep terrain data, bounds, walkability, generated collectible positions, and gate placement independent of pygame so they are unit-testable.

## Character, Collectibles, and Counters

The protagonist is an original pixel-art princess with an easily legible crown, hair, dress, and outline. Do not resemble a known copyrighted character.

There are two explicit collectible types: `GEM` and `FLOWER`.

- Use strongly distinct original sprites.
- Start each level with a small, countable number of each type, initially five gems and five flowers.
- Space collectibles generously on walkable terrain.
- Use forgiving overlap detection and allow each item to be collected only once per round.
- Render a compact, high-contrast top HUD with a gem icon and large gem number plus a flower icon and large flower number.
- Update only the matching counter when collected. Both counters start at zero and reset on the next level.

## Movement

- Arrow keys are the sole play control.
- Sample held keys every frame and use delta-time-based continuous movement.
- Normalize diagonal vectors.
- Resolve each movement axis independently so the princess slides gently along obstacles.
- Track four-direction facing and render a subtle walk animation while moving.

## Art and Sound

Use small, original pixel assets, such as 16 x 16 tiles rendered with integer nearest-neighbor scaling. Provide grass, grass variation, path, water, tree, mountain, wooden gate, exit arrow, princess frames, gem, flower, a pickup chime, and a short completion flourish.

Use a bright, varied palette. Sound must be optional: initialize the mixer once, continue silently when unavailable, and never show an error dialog for audio failure. Do not add music or sound settings in this milestone.

## Architecture

```text
main.py
	-> sunny_grove.app.run()
			-> GameState: movement, collision, pickup, counters, gate unlock, level transition
			-> World: generated map, terrain, bounds, pickup and gate data
			-> pygame: input, asset loading, optional sound, rendering
```

```text
AGENTS.md
README.md
requirements.txt
.gitignore
main.py
assets/
	tiles/
	sprites/
	sounds/
src/sunny_grove/
	__init__.py
	app.py
	game_state.py
	world.py
tests/
	test_world.py
	test_game_state.py
```

- `world.py` owns generated terrain, bounds, pickup placement, and gate placement.
- `game_state.py` owns all pygame-free rules, gate unlocking, and level transitions.
- `app.py` owns pygame lifecycle, input, assets, sound, renderer, HUD, and exit arrow.
- Tests run without a pygame display or audio device.

## Development and CI

- Use Python 3.13.5, as pinned in `.python-version`.
- Install dependencies with `python -m pip install -r requirements.txt` in the active virtual environment.
- Run tests with `python -m pytest` in the active virtual environment.
- GitHub Actions repeats those install and test commands on `ubuntu-latest`, `windows-latest`, and `macos-latest`.

## Delivery Sequence

1. Add setup files, package layout, entry point, and README.
2. Implement and test the independent world model.
3. Implement and test movement, collision, typed collection, counters, gate unlocking, and level transitions.
4. Create original assets.
5. Build the pygame loop and renderer.
6. Run tests and manually tune map layout, collision forgiveness, sprite scale, and counter contrast.

## Required Tests

- Generated terrain walkability, bounds, valid typed spawns, and gate placement.
- Equal straight and diagonal distance for equal delta time.
- Blocking by each solid terrain type and map edges.
- Gem collection increments only the gem counter; flower collection increments only the flower counter.
- Duplicate pickup processing cannot increment a counter twice.
- Gate opens only after all pickups are collected.
- Entering the open gate creates a new level with typed pickups and reset counters.

## Acceptance Checklist

1. Install with `python -m pip install -r requirements.txt`; `python -m pytest` succeeds.
2. `python main.py` opens the full-screen game from the repository root on Windows, Ubuntu, and macOS.
3. The rendered scene includes the princess, terrain, gems, flowers, and two readable counters.
4. Arrow keys and diagonals move smoothly without crossing solid terrain or map bounds.
5. Each collectible updates only its matching counter.
6. A completed level opens its gate; exiting through it creates a new map, restores items, resets counters, and keeps movement responsive.
7. The game remains playable with unavailable audio.

## Out of Scope

No inventory, quests, saves, enemies, combat, damage, health, timers, leaderboards, tactics, mouse or controller support, menus, tutorials, settings, music, dialogue, online services, analytics, ads, asset packs, or executable packaging.
