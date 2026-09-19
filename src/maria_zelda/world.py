from dataclasses import dataclass
from enum import Enum


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


class World:
    def __init__(self) -> None:
        self.tiles = [[Terrain.GRASS for _ in range(MAP_COLUMNS)] for _ in range(MAP_ROWS)]
        self._paint_landmarks()
        self.pickup_spawns = (
            PickupSpawn("gem-1", CollectibleKind.GEM, 12, 5),
            PickupSpawn("gem-2", CollectibleKind.GEM, 18, 4),
            PickupSpawn("gem-3", CollectibleKind.GEM, 23, 9),
            PickupSpawn("gem-4", CollectibleKind.GEM, 8, 11),
            PickupSpawn("gem-5", CollectibleKind.GEM, 16, 12),
            PickupSpawn("flower-1", CollectibleKind.FLOWER, 14, 6),
            PickupSpawn("flower-2", CollectibleKind.FLOWER, 6, 5),
            PickupSpawn("flower-3", CollectibleKind.FLOWER, 20, 7),
            PickupSpawn("flower-4", CollectibleKind.FLOWER, 25, 11),
            PickupSpawn("flower-5", CollectibleKind.FLOWER, 5, 12),
        )

    def _paint_landmarks(self) -> None:
        for column in range(MAP_COLUMNS):
            self.tiles[0][column] = Terrain.TREE
            self.tiles[MAP_ROWS - 1][column] = Terrain.TREE
        for row in range(MAP_ROWS):
            self.tiles[row][0] = Terrain.TREE
            self.tiles[row][MAP_COLUMNS - 1] = Terrain.TREE

        for column in range(3, 8):
            for row in range(2, 5):
                self.tiles[row][column] = Terrain.WATER
        for column in range(20, 26):
            for row in range(2, 5):
                self.tiles[row][column] = Terrain.MOUNTAIN
        for column, row in ((3, 8), (4, 8), (5, 8), (4, 9), (25, 7), (26, 7), (26, 8), (10, 12), (11, 12)):
            self.tiles[row][column] = Terrain.TREE

        for column in range(2, 28):
            self.tiles[7][column] = Terrain.PATH
        for row in range(5, 13):
            self.tiles[row][14] = Terrain.PATH

    def terrain_at(self, tile_x: int, tile_y: int) -> Terrain | None:
        if not self.in_bounds(tile_x, tile_y):
            return None
        return self.tiles[tile_y][tile_x]

    def in_bounds(self, tile_x: int, tile_y: int) -> bool:
        return 0 <= tile_x < MAP_COLUMNS and 0 <= tile_y < MAP_ROWS

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        terrain = self.terrain_at(tile_x, tile_y)
        return terrain in {Terrain.GRASS, Terrain.PATH}

    def rect_is_walkable(self, left: float, top: float, width: float, height: float) -> bool:
        if left < 0 or top < 0 or left + width > WORLD_WIDTH or top + height > WORLD_HEIGHT:
            return False
        start_x = int(left // TILE_SIZE)
        end_x = int((left + width - 0.001) // TILE_SIZE)
        start_y = int(top // TILE_SIZE)
        end_y = int((top + height - 0.001) // TILE_SIZE)
        return all(
            self.is_walkable(tile_x, tile_y)
            for tile_y in range(start_y, end_y + 1)
            for tile_x in range(start_x, end_x + 1)
        )