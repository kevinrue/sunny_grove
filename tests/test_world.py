from random import Random

from sunny_grove.world import CollectibleKind, MAP_COLUMNS, MAP_ROWS, TILE_SIZE, World


def test_walkability_and_bounds() -> None:
    world = World(Random(1))

    assert world.is_walkable(*world.spawn_tile)
    assert world.terrain_at(-1, 1) is None
    assert not world.is_walkable(-1, 1)
    assert world.gate.tile_x in {0, MAP_COLUMNS - 1} or world.gate.tile_y in {0, MAP_ROWS - 1}
    assert world.is_walkable(*world.gate.entry_tile)
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