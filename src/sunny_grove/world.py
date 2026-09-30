from dataclasses import dataclass
from enum import Enum
from random import Random


TILE_SIZE = 32
MAP_COLUMNS = 30
MAP_ROWS = 15
WORLD_WIDTH = MAP_COLUMNS * TILE_SIZE
WORLD_HEIGHT = MAP_ROWS * TILE_SIZE


class Terrain(str, Enum):
    GRASS = "grass"
    PATH = "path"
    TREE = "tree"
    MOUNTAIN = "mountain"
    WATER = "water"


class CollectibleKind(str, Enum):
    GEM = "gem"
    FLOWER = "flower"


@dataclass(frozen=True)
class PickupSpawn:
    identifier: str
    kind: CollectibleKind
    tile_x: int
    tile_y: int

    @property
    def center(self) -> tuple[float, float]:
        return (
            self.tile_x * TILE_SIZE + TILE_SIZE / 2,
            self.tile_y * TILE_SIZE + TILE_SIZE / 2,
        )


@dataclass(frozen=True)
class Gate:
    tile_x: int
    tile_y: int
    facing: str

    @property
    def entry_tile(self) -> tuple[int, int]:
        offsets = {
            "up": (0, 1),
            "down": (0, -1),
            "left": (1, 0),
            "right": (-1, 0),
        }
        offset_x, offset_y = offsets[self.facing]
        return self.tile_x + offset_x, self.tile_y + offset_y

    @property
    def center(self) -> tuple[float, float]:
        return (
            self.tile_x * TILE_SIZE + TILE_SIZE / 2,
            self.tile_y * TILE_SIZE + TILE_SIZE / 2,
        )


class World:
    def __init__(
        self,
        rng: Random | None = None,
        entry_facing: str | None = None,
        return_home: bool = False,
    ) -> None:
        self._rng = rng or Random()
        self.return_home = return_home
        self.entry_gate = self._create_border_gate(entry_facing) if entry_facing else None
        self.spawn_tile = self.entry_gate.entry_tile if self.entry_gate else (14, 9)
        self.gate = None if return_home else self._create_gate()
        self.tower_tile = self._create_tower_tile() if self.entry_gate is None else None
        self.castle_tile: tuple[int, int] | None = None
        self.tiles = [[Terrain.GRASS for _ in range(MAP_COLUMNS)] for _ in range(MAP_ROWS)]
        self._paint_border()
        self._paint_landmarks()
        if self.return_home:
            self.castle_tile = self._create_castle_tile()
            self._paint_path_to(self.castle_tile)
        else:
            self._paint_path_to(self.gate.entry_tile)
        self.pickup_spawns = self._create_pickups()

    def _create_border_gate(self, facing: str) -> Gate:
        if facing not in {"up", "down", "left", "right"}:
            raise ValueError(f"Unknown gate facing: {facing}")
        if facing in {"up", "down"}:
            tile_x = self._rng.randrange(3, MAP_COLUMNS - 3)
            tile_y = 0 if facing == "up" else MAP_ROWS - 1
        else:
            tile_x = 0 if facing == "left" else MAP_COLUMNS - 1
            tile_y = self._rng.randrange(3, MAP_ROWS - 3)
        return Gate(tile_x, tile_y, facing)

    def _create_gate(self) -> Gate:
        gate = self._create_border_gate(self._rng.choice(("up", "down", "left", "right")))
        while self.entry_gate is not None and (gate.tile_x, gate.tile_y) == (self.entry_gate.tile_x, self.entry_gate.tile_y):
            gate = self._create_border_gate(self._rng.choice(("up", "down", "left", "right")))
        return gate

    def _create_castle_tile(self) -> tuple[int, int]:
        candidates = [
            (tile_x, tile_y)
            for tile_y in range(2, MAP_ROWS - 2)
            for tile_x in range(2, MAP_COLUMNS - 2)
            if self.tiles[tile_y][tile_x] in {Terrain.GRASS, Terrain.PATH}
            and (tile_x, tile_y) != self.spawn_tile
        ]
        return self._rng.choice(candidates)

    def _create_tower_tile(self) -> tuple[int, int]:
        spawn_x, spawn_y = self.spawn_tile
        assert self.gate is not None
        entry_x, entry_y = self.gate.entry_tile
        if entry_x != spawn_x:
            direction_x = 1 if entry_x > spawn_x else -1
            return spawn_x - direction_x, spawn_y
        direction_y = 1 if entry_y > spawn_y else -1
        return spawn_x, spawn_y - direction_y

    def _paint_border(self) -> None:
        for column in range(MAP_COLUMNS):
            self.tiles[0][column] = Terrain.TREE
            self.tiles[MAP_ROWS - 1][column] = Terrain.TREE
        for row in range(MAP_ROWS):
            self.tiles[row][0] = Terrain.TREE
            self.tiles[row][MAP_COLUMNS - 1] = Terrain.TREE
        if self.gate is not None:
            self.tiles[self.gate.tile_y][self.gate.tile_x] = Terrain.GRASS
        if self.entry_gate is not None:
            self.tiles[self.entry_gate.tile_y][self.entry_gate.tile_x] = Terrain.GRASS

    def _paint_landmarks(self) -> None:
        for _ in range(6):
            terrain = self._rng.choice((Terrain.TREE, Terrain.MOUNTAIN, Terrain.WATER))
            width = self._rng.randrange(2, 5)
            height = self._rng.randrange(2, 4)
            start_x = self._rng.randrange(2, MAP_COLUMNS - width - 1)
            start_y = self._rng.randrange(2, MAP_ROWS - height - 1)
            for tile_y in range(start_y, start_y + height):
                for tile_x in range(start_x, start_x + width):
                    if abs(tile_x - self.spawn_tile[0]) <= 2 and abs(tile_y - self.spawn_tile[1]) <= 2:
                        continue
                    self.tiles[tile_y][tile_x] = terrain

    def _paint_path_to(self, destination: tuple[int, int]) -> None:
        tile_x, tile_y = self.spawn_tile
        destination_x, destination_y = destination
        while tile_x != destination_x:
            self.tiles[tile_y][tile_x] = Terrain.PATH
            tile_x += 1 if destination_x > tile_x else -1
        while tile_y != destination_y:
            self.tiles[tile_y][tile_x] = Terrain.PATH
            tile_y += 1 if destination_y > tile_y else -1
        self.tiles[destination_y][destination_x] = Terrain.PATH

    def _create_pickups(self) -> tuple[PickupSpawn, ...]:
        reachable = self._reachable_tiles()
        reserved = {self.spawn_tile}
        if self.gate is not None:
            reserved.add(self.gate.entry_tile)
        if self.castle_tile is not None:
            reserved.add(self.castle_tile)
        if self.tower_tile is not None:
            reserved.add(self.tower_tile)
        if self.entry_gate is not None:
            reserved.add(self.entry_gate.entry_tile)
        candidates = [tile for tile in reachable if tile not in reserved]
        positions = self._rng.sample(candidates, 10)
        kinds = (CollectibleKind.GEM,) * 5 + (CollectibleKind.FLOWER,) * 5
        return tuple(
            PickupSpawn(f"{kind.value}-{index + 1}", kind, tile_x, tile_y)
            for index, (kind, (tile_x, tile_y)) in enumerate(zip(kinds, positions, strict=True))
        )

    def _reachable_tiles(self) -> set[tuple[int, int]]:
        reachable = {self.spawn_tile}
        frontier = [self.spawn_tile]
        while frontier:
            tile_x, tile_y = frontier.pop()
            for neighbor in ((tile_x - 1, tile_y), (tile_x + 1, tile_y), (tile_x, tile_y - 1), (tile_x, tile_y + 1)):
                if neighbor in reachable or not self.is_walkable(*neighbor):
                    continue
                reachable.add(neighbor)
                frontier.append(neighbor)
        return reachable

    def terrain_at(self, tile_x: int, tile_y: int) -> Terrain | None:
        if not self.in_bounds(tile_x, tile_y):
            return None
        return self.tiles[tile_y][tile_x]

    def in_bounds(self, tile_x: int, tile_y: int) -> bool:
        return 0 <= tile_x < MAP_COLUMNS and 0 <= tile_y < MAP_ROWS

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        terrain = self.terrain_at(tile_x, tile_y)
        return (
            terrain in {Terrain.GRASS, Terrain.PATH}
            and not self.is_gate(tile_x, tile_y)
            and (tile_x, tile_y) != self.tower_tile
        )

    def is_gate(self, tile_x: int, tile_y: int) -> bool:
        gate_tiles = set()
        if self.gate is not None:
            gate_tiles.add((self.gate.tile_x, self.gate.tile_y))
        if self.entry_gate is not None:
            gate_tiles.add((self.entry_gate.tile_x, self.entry_gate.tile_y))
        return (tile_x, tile_y) in gate_tiles

    def is_exit_gate(self, tile_x: int, tile_y: int) -> bool:
        return self.gate is not None and (tile_x, tile_y) == (self.gate.tile_x, self.gate.tile_y)

    def rect_is_walkable(
        self,
        left: float,
        top: float,
        width: float,
        height: float,
        gate_is_open: bool = False,
    ) -> bool:
        if left < 0 or top < 0 or left + width > WORLD_WIDTH or top + height > WORLD_HEIGHT:
            return False
        start_x = int(left // TILE_SIZE)
        end_x = int((left + width - 0.001) // TILE_SIZE)
        start_y = int(top // TILE_SIZE)
        end_y = int((top + height - 0.001) // TILE_SIZE)
        return all(
            self.is_walkable(tile_x, tile_y) or (gate_is_open and self.is_exit_gate(tile_x, tile_y))
            for tile_y in range(start_y, end_y + 1)
            for tile_x in range(start_x, end_x + 1)
        )