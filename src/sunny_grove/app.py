from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pygame

from .game_state import GameState
from .world import CollectibleKind, MAP_COLUMNS, MAP_ROWS, TILE_SIZE, Terrain, World


WINDOW_WIDTH: Final = 960
WINDOW_HEIGHT: Final = 540
HUD_HEIGHT: Final = 60
BACKGROUND: Final = (29, 61, 72)
ASSET_ROOT: Final = Path(__file__).resolve().parents[2] / "assets"


@dataclass(frozen=True)
class Assets:
    tiles: dict[Terrain, pygame.Surface]
    gem: pygame.Surface
    flower: pygame.Surface
    gate_closed: pygame.Surface
    gate_open: pygame.Surface
    exit_arrow: pygame.Surface
    princess: dict[tuple[str, int], pygame.Surface]


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sunny Grove")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 34)
    assets = _load_images()
    pickup_sound, celebration_sound = _load_sounds()
    state = GameState(World())
    running = True

    while running:
        delta_seconds = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        direction = (
            int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]),
            int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]),
        )
        gate_was_open = state.gate_open
        collected = state.update(direction, delta_seconds)
        if collected and pickup_sound is not None:
            pickup_sound.play()
        if not gate_was_open and state.gate_open and celebration_sound is not None:
            celebration_sound.play()

        _draw_scene(game_surface, state, assets, font)
        _present_scene(screen, game_surface)
        pygame.display.flip()

    pygame.quit()


def _load_sounds() -> tuple[pygame.mixer.Sound | None, pygame.mixer.Sound | None]:
    try:
        pygame.mixer.init()
        return (
            pygame.mixer.Sound(ASSET_ROOT / "sounds" / "pickup.wav"),
            pygame.mixer.Sound(ASSET_ROOT / "sounds" / "celebrate.wav"),
        )
    except (FileNotFoundError, pygame.error):
        return None, None


def _load_images() -> Assets:
    tile_names = {
        Terrain.GRASS: "grass.png",
        Terrain.PATH: "path.png",
        Terrain.TREE: "tree.png",
        Terrain.MOUNTAIN: "mountain.png",
        Terrain.WATER: "water.png",
    }
    tiles = {
        terrain: _load_scaled(ASSET_ROOT / "tiles" / filename)
        for terrain, filename in tile_names.items()
    }
    princess = {
        (facing, frame): _load_scaled(ASSET_ROOT / "sprites" / f"princess_{facing}_{frame}.png")
        for facing in ("down", "up", "left", "right")
        for frame in range(2)
    }
    return Assets(
        tiles=tiles,
        gem=_load_scaled(ASSET_ROOT / "sprites" / "gem.png"),
        flower=_load_scaled(ASSET_ROOT / "sprites" / "flower.png"),
        gate_closed=_load_scaled(ASSET_ROOT / "sprites" / "gate_closed.png"),
        gate_open=_load_scaled(ASSET_ROOT / "sprites" / "gate_open.png"),
        exit_arrow=_load_scaled(ASSET_ROOT / "sprites" / "exit_arrow.png"),
        princess=princess,
    )


def _load_scaled(path: Path) -> pygame.Surface:
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))


def _present_scene(screen: pygame.Surface, game_surface: pygame.Surface) -> None:
    display_width, display_height = screen.get_size()
    scale = min(display_width / WINDOW_WIDTH, display_height / WINDOW_HEIGHT)
    scene_size = (round(WINDOW_WIDTH * scale), round(WINDOW_HEIGHT * scale))
    scene = pygame.transform.scale(game_surface, scene_size)
    position = (
        (display_width - scene_size[0]) // 2,
        (display_height - scene_size[1]) // 2,
    )
    screen.fill(BACKGROUND)
    screen.blit(scene, position)


def _draw_scene(
    screen: pygame.Surface,
    state: GameState,
    assets: Assets,
    font: pygame.font.Font,
) -> None:
    screen.fill(BACKGROUND)
    _draw_world(screen, state.world, assets)
    _draw_gate(screen, state, assets)
    for pickup in state.active_pickups.values():
        _draw_pickup(screen, assets, pickup.kind, int(pickup.x), int(pickup.y + HUD_HEIGHT))
    _draw_princess(screen, assets, state)
    _draw_hud(screen, state, assets, font)


def _draw_world(screen: pygame.Surface, world: World, assets: Assets) -> None:
    for row in range(MAP_ROWS):
        for column in range(MAP_COLUMNS):
            terrain = world.tiles[row][column]
            tile = assets.tiles[terrain]
            screen.blit(tile, (column * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT))


def _draw_pickup(
    screen: pygame.Surface,
    assets: Assets,
    kind: CollectibleKind,
    center_x: int,
    center_y: int,
) -> None:
    image = assets.gem if kind is CollectibleKind.GEM else assets.flower
    screen.blit(image, image.get_rect(center=(center_x, center_y)))


def _draw_gate(screen: pygame.Surface, state: GameState, assets: Assets) -> None:
    gate = state.world.gate
    gate_image = assets.gate_open if state.gate_open else assets.gate_closed
    gate_center = (int(gate.center[0]), int(gate.center[1] + HUD_HEIGHT))
    screen.blit(gate_image, gate_image.get_rect(center=gate_center))
    if not state.gate_open:
        return

    rotations = {"up": 0, "right": -90, "down": 180, "left": 90}
    arrow = pygame.transform.rotate(assets.exit_arrow, rotations[gate.facing])
    entry_x, entry_y = gate.entry_tile
    entry_center = (entry_x * TILE_SIZE + TILE_SIZE // 2, entry_y * TILE_SIZE + TILE_SIZE // 2 + HUD_HEIGHT)
    screen.blit(arrow, arrow.get_rect(center=entry_center))


def _draw_princess(screen: pygame.Surface, assets: Assets, state: GameState) -> None:
    image = assets.princess[(state.facing, state.walk_frame)]
    screen.blit(image, image.get_rect(center=(int(state.x), int(state.y + HUD_HEIGHT))))


def _draw_hud(screen: pygame.Surface, state: GameState, assets: Assets, font: pygame.font.Font) -> None:
    pygame.draw.rect(screen, (255, 239, 193), (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, (146, 100, 92), (0, HUD_HEIGHT - 2), (WINDOW_WIDTH, HUD_HEIGHT - 2), 2)
    _draw_pickup(screen, assets, CollectibleKind.GEM, 34, 30)
    _draw_pickup(screen, assets, CollectibleKind.FLOWER, 250, 30)
    gem_text = font.render(f"Gems: {state.gem_count}", True, (55, 47, 76))
    flower_text = font.render(f"Flowers: {state.flower_count}", True, (55, 47, 76))
    screen.blit(gem_text, (55, 17))
    screen.blit(flower_text, (273, 17))