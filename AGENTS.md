# Maria Zelda

## Product Goal

Create a calm, polished 2D exploration game that a three-year-old can play independently with the arrow keys. The child guides an original princess through one cheerful outdoor map, discovers gems and flowers, and watches separate large counters increase to practice early counting.

The game should feel like a gentle toy, not a challenge: no failure state, no time limit, no enemies, no combat, no score pressure, and no required reading to play. Terrain blocks the princess only to make the world understandable and fun to explore.

## First Playable Experience

1. `python main.py` opens a fixed 960 x 540 game window on Windows.
2. The princess explores a bright grassland with paths, trees, mountains, water, gems, and flowers.
3. Holding arrow keys moves smoothly; diagonal movement has the same overall speed as straight movement.
4. Trees, mountains, water, and map edges block movement.
5. Walking onto a gem or flower collects it automatically, plays a gentle chime when sound is available, and increments its matching counter.
6. Collecting every item triggers a short, non-blocking celebration. The game restores a fresh round of items, resets counters, and keeps exploration active.
7. Escape and window close may quit. No other control is needed during play.

## Design Principles

- Make objects large, colorful, well-spaced, and forgiving for a toddler.
- Keep exploration calm: no hazards, enemies, timers, health, competition, or failure states.
- Show large, persistent, icon-paired counters for gems and flowers so collection directly supports counting practice.
- Create original art and sound. It may evoke broad classic top-down pixel-adventure conventions, but must not copy Zelda or other protected characters, maps, sprites, music, or UI.
- Run fully offline with Python and pygame; bundled assets must resolve independently of the launch directory.

## World

Build one authored, one-screen top-down outdoor map with a central grassy clearing, optional dirt paths, tree clusters, mountain barriers, a small pond or stream, and several open collectible pockets. Every pickup must be reachable without a precision puzzle. Spawn the princess near one visible pickup for immediate feedback.

| Terrain | Walkable |
| --- | --- |
| Grass | Yes |
| Path | Yes |
| Tree | No |
| Mountain | No |
| Water | No |

Keep terrain data, bounds, walkability, and deterministic collectible spawn positions independent of pygame so they are unit-testable.

## Character, Collectibles, and Counters

The protagonist is an original pixel-art princess with an easily legible crown, hair, dress, and outline. Do not resemble a known copyrighted princess or Zelda character.

There are two explicit collectible types: `GEM` and `FLOWER`.

- Use strongly distinct original sprites.
- Start each round with a small, countable number of each type, initially five gems and five flowers.
- Space collectibles generously on walkable terrain.
- Use forgiving overlap detection and allow each item to be collected only once per round.
- Render a compact, high-contrast top HUD with a gem icon and large gem number plus a flower icon and large flower number.
- Update only the matching counter when collected. Both counters start at zero and reset with the next round.

## Movement

- Arrow keys are the sole play control.
- Sample held keys every frame and use delta-time-based continuous movement.
- Normalize diagonal vectors.
- Resolve each movement axis independently so the princess slides gently along obstacles.
- Track four-direction facing and render a subtle walk animation while moving.

## Art and Sound

Use small, original pixel assets, such as 16 x 16 tiles rendered with integer nearest-neighbor scaling. Provide grass, grass variation, path, water, tree, mountain, princess frames, gem, flower, a pickup chime, and a short completion flourish.

Use a bright, varied palette. Sound must be optional: initialize the mixer once, continue silently when unavailable, and never show an error dialog for audio failure. Do not add music or sound settings in this milestone.

## Architecture

```text
main.py
	-> maria_zelda.app.run()
			-> GameState: movement, collision, pickup, counters, celebration, reset
			-> World: map, terrain, bounds, spawn data
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
src/maria_zelda/
	__init__.py
	app.py
	game_state.py
	world.py
tests/
	test_world.py
	test_game_state.py
```

- `world.py` owns terrain, map layout, bounds, and spawn definitions.
- `game_state.py` owns all pygame-free rules and state.
- `app.py` owns pygame lifecycle, input, assets, sound, renderer, HUD, and celebration effect.
- Tests run without a pygame display or audio device.

## Delivery Sequence

1. Add setup files, package layout, entry point, and README.
2. Implement and test the independent world model.
3. Implement and test movement, collision, typed collection, counters, celebration, and reset.
4. Create original assets.
5. Build the pygame loop and renderer.
6. Run tests and manually tune map layout, collision forgiveness, sprite scale, and counter contrast.

## Required Tests

- Terrain walkability, bounds, and valid typed spawns.
- Equal straight and diagonal distance for equal delta time.
- Blocking by each solid terrain type and map edges.
- Gem collection increments only the gem counter; flower collection increments only the flower counter.
- Duplicate pickup processing cannot increment a counter twice.
- Celebration starts only after all pickups are collected.
- Round reset restores all typed pickups and resets both counters.

## Acceptance Checklist

1. Install with `pip install -r requirements.txt`; `pytest` succeeds.
2. `python main.py` opens the 960 x 540 game from the repository root and another working directory.
3. The rendered scene includes the princess, terrain, gems, flowers, and two readable counters.
4. Arrow keys and diagonals move smoothly without crossing solid terrain or map bounds.
5. Each collectible updates only its matching counter.
6. A completed round celebrates, restores items, resets counters, and keeps movement responsive.
7. The game remains playable with unavailable audio.

## Out of Scope

No additional maps, doors, inventory, quests, saves, progression, enemies, combat, damage, health, timers, leaderboards, tactics, mouse or controller support, menus, tutorials, settings, music, dialogue, online services, analytics, ads, asset packs, or executable packaging.
