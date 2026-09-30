from random import Random

import pytest

from sunny_grove.game_state import GameState
from sunny_grove.world import CollectibleKind, TILE_SIZE, Terrain, World


def test_diagonal_input_moves_along_one_axis() -> None:
    world = World(Random(1))
    world.tiles[8][10] = Terrain.PATH
    world.tiles[8][11] = Terrain.PATH
    world.tiles[9][10] = Terrain.PATH
    state = GameState(world)
    state.x, state.y = (10 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)

    state.update((1, 1), 1.0)

    assert (state.x, state.y) == (11 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)


def test_released_movement_finishes_at_the_next_tile_center() -> None:
    world = World(Random(7))
    spawn_x, spawn_y = world.spawn_tile
    direction_x = -1 if (spawn_x + 1, spawn_y) == world.tower_tile else 1
    world.tiles[spawn_y][spawn_x] = Terrain.PATH
    world.tiles[spawn_y][spawn_x + direction_x] = Terrain.PATH
    state = GameState(world)
    start_x, start_y = state.x, state.y

    state.update((direction_x, 0), 0.04)

    assert min(start_x, start_x + direction_x * TILE_SIZE) < state.x < max(start_x, start_x + direction_x * TILE_SIZE)
    state.update((0, 0), 1.0)

    assert (state.x, state.y) == (start_x + direction_x * TILE_SIZE, start_y)


def test_pickups_increment_only_their_matching_counter() -> None:
    state = GameState(World(Random(2)))
    gem = next(pickup for pickup in state.active_pickups.values() if pickup.kind is CollectibleKind.GEM)
    state.x, state.y = gem.x, gem.y

    collected = state.update((0, 0), 0)

    assert collected == [CollectibleKind.GEM]
    assert state.gem_count == 1
    assert state.flower_count == 0
    assert gem.identifier not in state.active_pickups
    assert state.update((0, 0), 0) == []
    assert state.gem_count == 1


@pytest.mark.parametrize(
    "terrain",
    [Terrain.TREE, Terrain.MOUNTAIN, Terrain.WATER],
)
def test_solid_terrain_blocks_the_princess(terrain: Terrain) -> None:
    world = World(Random(3))
    world.tiles[8][11] = terrain
    world.tiles[8][10] = Terrain.PATH
    state = GameState(world)
    state.x, state.y = (10 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)

    state.update((1, 0), 0.2)

    assert (state.x, state.y) == (10 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)


def test_diagonal_movement_cannot_cut_through_a_single_blocked_tile() -> None:
    world = World(Random(8))
    world.tiles[8][10] = Terrain.PATH
    world.tiles[8][11] = Terrain.PATH
    world.tiles[9][10] = Terrain.TREE
    world.tiles[9][11] = Terrain.PATH
    state = GameState(world)
    state.x, state.y = (10 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)

    state.update((1, 1), 1.0)

    assert (state.x, state.y) == (11 * TILE_SIZE + TILE_SIZE / 2, 8 * TILE_SIZE + TILE_SIZE / 2)


def test_map_edge_blocks_the_princess() -> None:
    state = GameState(World(Random(4)))
    state.x, state.y = (16, 16)

    state.update((0, -1), 0.2)

    assert (state.x, state.y) == (16, 16)


def test_completion_opens_gate_and_entering_it_starts_a_new_level() -> None:
    state = GameState(World(Random(5)), rng=Random(6))
    previous_world = state.world
    for pickup in tuple(state.active_pickups.values()):
        state.x, state.y = pickup.x, pickup.y
        state.update((0, 0), 0)

    assert state.gate_open
    assert state.gem_count == 5
    assert state.flower_count == 5

    state.x, state.y = state.world.gate.center
    state.update((0, 0), 0)

    assert state.transition_pending
    assert state.level == 1
    assert state.world is previous_world

    state.advance_level()

    assert state.level == 2
    assert state.world is not previous_world
    assert state.world.entry_gate is not None
    opposite_facing = {"up": "down", "down": "up", "left": "right", "right": "left"}
    assert state.world.entry_gate.facing == opposite_facing[previous_world.gate.facing]
    assert (state.x, state.y) == (
        state.world.spawn_tile[0] * TILE_SIZE + TILE_SIZE / 2,
        state.world.spawn_tile[1] * TILE_SIZE + TILE_SIZE / 2,
    )
    assert not state.gate_open
    assert state.gem_count == 0
    assert state.flower_count == 0
    assert len(state.active_pickups) == 10