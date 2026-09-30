from random import Random

from sunny_grove.world import CollectibleKind, MAP_COLUMNS, MAP_ROWS, TILE_SIZE, Terrain, World


def test_walkability_and_bounds() -> None:
    world = World(Random(1))

    assert world.is_walkable(*world.spawn_tile)
    assert world.terrain_at(-1, 1) is None
    assert not world.is_walkable(-1, 1)
    assert world.gate.tile_x in {0, MAP_COLUMNS - 1} or world.gate.tile_y in {0, MAP_ROWS - 1}
    assert world.is_walkable(*world.gate.entry_tile)
    assert world.terrain_at(*world.gate.entry_tile) is Terrain.PATH
    assert not world.is_walkable(world.gate.tile_x, world.gate.tile_y)
    assert not world.rect_is_walkable(
        world.gate.tile_x * TILE_SIZE,
        world.gate.tile_y * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
    )
    assert world.rect_is_walkable(
        world.gate.tile_x * TILE_SIZE,
        world.gate.tile_y * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
        gate_is_open=True,
    )


def test_each_pickup_is_reachable_and_both_types_exist() -> None:
    world = World(Random(2))
    kinds = {spawn.kind for spawn in world.pickup_spawns}

    assert kinds == {CollectibleKind.GEM, CollectibleKind.FLOWER}
    assert all(world.is_walkable(spawn.tile_x, spawn.tile_y) for spawn in world.pickup_spawns)


def test_random_seeds_generate_different_levels() -> None:
    first = World(Random(7))
    second = World(Random(8))

    first_layout = (first.tiles, first.gate, first.pickup_spawns)
    second_layout = (second.tiles, second.gate, second.pickup_spawns)
    assert first_layout != second_layout


def test_first_world_has_an_enterable_castle() -> None:
    world = World(Random(9))

    assert world.castle_tile is not None
    assert world.is_walkable(*world.castle_tile)
    assert world.castle_tile != world.spawn_tile
    assert world.rect_is_walkable(
        world.castle_tile[0] * TILE_SIZE,
        world.castle_tile[1] * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
    )


def test_entering_world_has_a_permanently_closed_entry_gate() -> None:
    world = World(Random(10), entry_facing="down")

    assert world.entry_gate is not None
    assert world.entry_gate.facing == "down"
    assert world.spawn_tile == world.entry_gate.entry_tile
    assert world.tower_tile is None
    assert not world.rect_is_walkable(
        world.entry_gate.tile_x * TILE_SIZE,
        world.entry_gate.tile_y * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
        gate_is_open=True,
    )


def test_every_world_has_a_reachable_walkable_castle() -> None:
    world = World(Random(11), entry_facing="right")

    assert world.castle_tile is not None
    assert world.is_walkable(*world.castle_tile)
    assert world.castle_tile not in {(pickup.tile_x, pickup.tile_y) for pickup in world.pickup_spawns}
    assert world.terrain_at(*world.castle_entry_tile) is Terrain.PATH
    assert world.castle_entry_facing in {"up", "down", "left", "right"}