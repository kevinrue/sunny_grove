from maria_zelda.world import CollectibleKind, Terrain, World


def test_walkability_and_bounds() -> None:
    world = World()

    assert world.is_walkable(1, 1)
    assert world.terrain_at(3, 2) is Terrain.WATER
    assert not world.is_walkable(3, 2)
    assert world.terrain_at(-1, 1) is None
    assert not world.is_walkable(-1, 1)


def test_each_pickup_is_reachable_and_both_types_exist() -> None:
    world = World()
    kinds = {spawn.kind for spawn in world.pickup_spawns}

    assert kinds == {CollectibleKind.GEM, CollectibleKind.FLOWER}
    assert all(world.is_walkable(spawn.tile_x, spawn.tile_y) for spawn in world.pickup_spawns)