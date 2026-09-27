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
        self.active_pickups: dict[str, ActivePickup] = {}
        self._start_level()

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
        if self.gate_open and self._is_at_gate():
            self._advance_level()
        return collected

    def _update_facing(self, direction_x: float, direction_y: float) -> None:
        if abs(direction_x) > abs(direction_y):
            self.facing = "right" if direction_x > 0 else "left"
        else:
            self.facing = "down" if direction_y > 0 else "up"

    def _move(self, distance_x: float, distance_y: float) -> None:
        half_size = PLAYER_SIZE / 2
        candidate_x = self.x + distance_x
        if self.world.rect_is_walkable(
            candidate_x - half_size,
            self.y - half_size,
            PLAYER_SIZE,
            PLAYER_SIZE,
            self.gate_open,
        ):
            self.x = candidate_x
        candidate_y = self.y + distance_y
        if self.world.rect_is_walkable(
            self.x - half_size,
            candidate_y - half_size,
            PLAYER_SIZE,
            PLAYER_SIZE,
            self.gate_open,
        ):
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
            self.gate_open = True
        return collected

    def _is_at_gate(self) -> bool:
        return self.world.is_gate(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def _advance_level(self) -> None:
        opposite_facing = {"up": "down", "down": "up", "left": "right", "right": "left"}
        self.level += 1
        self.world = World(self._rng, entry_facing=opposite_facing[self.world.gate.facing])
        self._start_level()

    def _start_level(self) -> None:
        spawn_x, spawn_y = self.world.spawn_tile
        self.x = spawn_x * TILE_SIZE + TILE_SIZE / 2
        self.y = spawn_y * TILE_SIZE + TILE_SIZE / 2
        self.gem_count = 0
        self.flower_count = 0
        self.gate_open = False
        self.active_pickups = {
            spawn.identifier: ActivePickup.from_spawn(spawn) for spawn in self.world.pickup_spawns
        }