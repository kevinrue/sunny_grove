from dataclasses import dataclass
from math import hypot
from random import Random

from .world import CollectibleKind, PickupSpawn, TILE_SIZE, World


PLAYER_SIZE = 22
PLAYER_SPEED = 145.0
PICKUP_RADIUS = 20.0


@dataclass(frozen=True)
class ActivePickup:
    identifier: str
    kind: CollectibleKind
    x: float
    y: float

    @classmethod
    def from_spawn(cls, spawn: PickupSpawn) -> "ActivePickup":
        x, y = spawn.center
        return cls(spawn.identifier, spawn.kind, x, y)


class GameState:
    def __init__(self, world: World | None = None, rng: Random | None = None) -> None:
        self._rng = rng or Random()
        self.world = world or World(self._rng)
        self.level = 1
        self.x = 0.0
        self.y = 0.0
        self.facing = "down"
        self.walk_frame = 0
        self.walk_elapsed = 0.0
        self.gem_count = 0
        self.flower_count = 0
        self.gate_open = False
        self._move_target: tuple[float, float] | None = None
        self.transition_pending = False
        self.finale_pending = False
        self.active_pickups: dict[str, ActivePickup] = {}
        self._start_level()

    def update(self, direction: tuple[float, float], delta_seconds: float) -> list[CollectibleKind]:
        if self.transition_pending:
            return []

        direction_x, direction_y = direction
        if direction_x and direction_y:
            direction_y = 0
        length = hypot(direction_x, direction_y)
        elapsed = max(delta_seconds, 0)
        if length:
            direction_x /= length
            direction_y /= length
            if self._move_target is None:
                self._update_facing(direction_x, direction_y)
                self._begin_move(direction_x, direction_y)

        if self._move_target is not None:
            self.walk_elapsed += elapsed
            self.walk_frame = int(self.walk_elapsed / 0.18) % 2
            self._advance_move(PLAYER_SPEED * elapsed)
        else:
            self.walk_frame = 0

        collected = self._collect_overlapping_pickups()
        if self.gate_open and self._is_at_destination():
            self.transition_pending = True
            self.finale_pending = self.world.return_home
        return collected

    def _update_facing(self, direction_x: float, direction_y: float) -> None:
        if abs(direction_x) > abs(direction_y):
            self.facing = "right" if direction_x > 0 else "left"
        else:
            self.facing = "down" if direction_y > 0 else "up"

    def _begin_move(self, direction_x: float, direction_y: float) -> None:
        step_x = TILE_SIZE if direction_x > 0 else -TILE_SIZE if direction_x < 0 else 0
        step_y = TILE_SIZE if direction_y > 0 else -TILE_SIZE if direction_y < 0 else 0
        half_size = PLAYER_SIZE / 2
        target_x = self.x
        target_y = self.y
        if step_x:
            candidate_x = self.x + step_x
            if self.world.rect_is_walkable(
                candidate_x - half_size,
                self.y - half_size,
                PLAYER_SIZE,
                PLAYER_SIZE,
                self.gate_open,
            ):
                target_x = candidate_x
        if step_y:
            candidate_y = self.y + step_y
            if self.world.rect_is_walkable(
                self.x - half_size,
                candidate_y - half_size,
                PLAYER_SIZE,
                PLAYER_SIZE,
                self.gate_open,
            ):
                target_y = candidate_y
        if (target_x, target_y) != (self.x, self.y):
            self._move_target = (target_x, target_y)

    def _advance_move(self, distance: float) -> None:
        if self._move_target is None:
            return
        target_x, target_y = self._move_target
        remaining_x = target_x - self.x
        remaining_y = target_y - self.y
        remaining_distance = hypot(remaining_x, remaining_y)
        if distance >= remaining_distance:
            self.x, self.y = self._move_target
            self._move_target = None
            return
        progress = distance / remaining_distance
        self.x += remaining_x * progress
        self.y += remaining_y * progress

    def _collect_overlapping_pickups(self) -> list[CollectibleKind]:
        collected: list[CollectibleKind] = []
        for identifier, pickup in tuple(self.active_pickups.items()):
            if hypot(self.x - pickup.x, self.y - pickup.y) > PICKUP_RADIUS:
                continue
            del self.active_pickups[identifier]
            if pickup.kind is CollectibleKind.GEM:
                self.gem_count += 1
            else:
                self.flower_count += 1
            collected.append(pickup.kind)

        if collected and not self.active_pickups:
            self.gate_open = True
        return collected

    def _is_at_destination(self) -> bool:
        tile = (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))
        if self.world.return_home:
            return tile == self.world.castle_tile
        return self.world.is_gate(*tile)

    def advance_level(self) -> None:
        if not self.transition_pending or self.finale_pending:
            return
        opposite_facing = {"up": "down", "down": "up", "left": "right", "right": "left"}
        self.level += 1
        assert self.world.gate is not None
        self.world = World(
            self._rng,
            entry_facing=opposite_facing[self.world.gate.facing],
            return_home=self.level == 3,
        )
        self._start_level()

    def restart(self) -> None:
        self.level = 1
        self.world = World(self._rng)
        self._start_level()

    def _start_level(self) -> None:
        spawn_x, spawn_y = self.world.spawn_tile
        self.x = spawn_x * TILE_SIZE + TILE_SIZE / 2
        self.y = spawn_y * TILE_SIZE + TILE_SIZE / 2
        self.gem_count = 0
        self.flower_count = 0
        self.gate_open = False
        self._move_target = None
        self.transition_pending = False
        self.finale_pending = False
        self.active_pickups = {
            spawn.identifier: ActivePickup.from_spawn(spawn) for spawn in self.world.pickup_spawns
        }