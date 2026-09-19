from math import hypot, isclose

import pytest

from maria_zelda.game_state import CELEBRATION_SECONDS, GameState
from maria_zelda.world import CollectibleKind, World


def test_diagonal_and_straight_movement_cover_equal_distance() -> None:
    straight = GameState(World())
    diagonal = GameState(World())
    start_straight = (straight.x, straight.y)
    start_diagonal = (diagonal.x, diagonal.y)

    straight.update((1, 0), 0.1)
    diagonal.update((1, 1), 0.1)

    straight_distance = hypot(straight.x - start_straight[0], straight.y - start_straight[1])
    diagonal_distance = hypot(diagonal.x - start_diagonal[0], diagonal.y - start_diagonal[1])
    assert isclose(straight_distance, diagonal_distance, rel_tol=1e-9)


def test_pickups_increment_only_their_matching_counter() -> None:
    state = GameState(World())
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
    ("start", "direction"),
    [
        ((2 * 32 + 16, 3 * 32 + 16), (1, 0)),
        ((19 * 32 + 16, 3 * 32 + 16), (1, 0)),
        ((2 * 32 + 16, 8 * 32 + 16), (1, 0)),
    ],
)
def test_solid_terrain_blocks_the_princess(
    start: tuple[int, int], direction: tuple[int, int]
) -> None:
    state = GameState(World())
    state.x, state.y = start

    state.update(direction, 0.2)

    assert (state.x, state.y) == start


def test_map_edge_blocks_the_princess() -> None:
    state = GameState(World())
    state.x, state.y = (16, 16)

    state.update((0, -1), 0.2)

    assert (state.x, state.y) == (16, 16)


def test_completion_resets_the_round_after_celebration() -> None:
    state = GameState(World())
    for pickup in tuple(state.active_pickups.values()):
        state.x, state.y = pickup.x, pickup.y
        state.update((0, 0), 0)

    assert state.is_celebrating
    assert state.gem_count == 5
    assert state.flower_count == 5

    state.update((0, 0), CELEBRATION_SECONDS)

    assert not state.is_celebrating
    assert state.gem_count == 0
    assert state.flower_count == 0
    assert len(state.active_pickups) == 10