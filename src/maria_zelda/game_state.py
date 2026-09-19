from dataclasses import dataclass
from math import hypot

from .world import CollectibleKind, PickupSpawn, World


PLAYER_SIZE = 22
PLAYER_SPEED = 145.0
PICKUP_RADIUS = 20.0
CELEBRATION_SECONDS = 1.25


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
    def __init__(self, world: World) -> None:
        self.world = world
        self.x = 14 * 32 + 16
        self.y = 9 * 32 + 16
        self.facing = "down"
        self.walk_frame = 0
        self.walk_elapsed = 0.0
        self.gem_count = 0
        self.flower_count = 0
        self.celebration_remaining = 0.0
        self.active_pickups: dict[str, ActivePickup] = {}
        self._reset_round()

    @property
    def is_celebrating(self) -> bool:
        return self.celebration_remaining > 0

    def update(self, direction: tuple[float, float], delta_seconds: float) -> list[CollectibleKind]:
        direction_x, direction_y = direction
        length = hypot(direction_x, direction_y)
        if length:
            direction_x /= length
            direction_y /= length
            self._update_facing(direction_x, direction_y)
            elapsed = max(delta_seconds, 0)
            self.walk_elapsed += elapsed
            self.walk_frame = int(self.walk_elapsed / 0.18) % 2
            distance = PLAYER_SPEED * elapsed
            self._move(direction_x * distance, direction_y * distance)
        else:
            self.walk_frame = 0

        collected = self._collect_overlapping_pickups()
        if self.is_celebrating:
            self.celebration_remaining -= max(delta_seconds, 0)
            if self.celebration_remaining <= 0:
                self._reset_round()
        return collected

    def _update_facing(self, direction_x: float, direction_y: float) -> None:
        if abs(direction_x) > abs(direction_y):
            self.facing = "right" if direction_x > 0 else "left"
        else:
            self.facing = "down" if direction_y > 0 else "up"

    def _move(self, distance_x: float, distance_y: float) -> None:
        half_size = PLAYER_SIZE / 2
        candidate_x = self.x + distance_x
        if self.world.rect_is_walkable(candidate_x - half_size, self.y - half_size, PLAYER_SIZE, PLAYER_SIZE):
            self.x = candidate_x
        candidate_y = self.y + distance_y
        if self.world.rect_is_walkable(self.x - half_size, candidate_y - half_size, PLAYER_SIZE, PLAYER_SIZE):
            self.y = candidate_y

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
            self.celebration_remaining = CELEBRATION_SECONDS
        return collected

    def _reset_round(self) -> None:
        self.gem_count = 0
        self.flower_count = 0
        self.celebration_remaining = 0.0
        self.active_pickups = {
            spawn.identifier: ActivePickup.from_spawn(spawn) for spawn in self.world.pickup_spawns
        }