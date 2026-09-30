from dataclasses import dataclass
from math import cos, pi, sin
from pathlib import Path
from typing import Final

import pygame

from .game_state import GameState
from .world import CollectibleKind, MAP_COLUMNS, MAP_ROWS, TILE_SIZE, Terrain, World


WINDOW_WIDTH: Final = 960
WINDOW_HEIGHT: Final = 540
HUD_HEIGHT: Final = 60
BACKGROUND: Final = (29, 61, 72)
CELEBRATION_DURATION: Final = 1.8
COLLECTION_COMPLETION_DURATION: Final = 5.0
COLLECTIBLE_TARGET: Final = 5
ASSET_ROOT: Final = Path(__file__).resolve().parents[2] / "assets"


@dataclass(frozen=True)
class Assets:
    tiles: dict[Terrain, pygame.Surface]
    gem: pygame.Surface
    flower: pygame.Surface
    gate_closed: pygame.Surface
    gate_open: pygame.Surface
    exit_arrow: pygame.Surface
    tower: pygame.Surface
    princess: dict[tuple[str, int], pygame.Surface]


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sunny Grove")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 34)
    celebration_font = pygame.font.Font(None, 76)
    assets = _load_images()
    pickup_sound, celebration_sound = _load_sounds()
    state = GameState(World())
    celebration_elapsed: float | None = None
    collection_completion_kind: CollectibleKind | None = None
    collection_completion_elapsed = 0.0
    collection_completion_queue: list[CollectibleKind] = []
    running = True

    while running:
        delta_seconds = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if celebration_elapsed is None and collection_completion_kind is None:
            keys = pygame.key.get_pressed()
            direction = (
                int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]),
                int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]),
            )
            gate_was_open = state.gate_open
            counts_before_update = {
                CollectibleKind.GEM: state.gem_count,
                CollectibleKind.FLOWER: state.flower_count,
            }
            collected = state.update(direction, delta_seconds)
            if collected and pickup_sound is not None:
                pickup_sound.play()
            if not gate_was_open and state.gate_open and celebration_sound is not None:
                celebration_sound.play()
            collection_completion_queue.extend(
                kind
                for kind, count in (
                    (CollectibleKind.GEM, state.gem_count),
                    (CollectibleKind.FLOWER, state.flower_count),
                )
                if counts_before_update[kind] < COLLECTIBLE_TARGET <= count
            )
            if collection_completion_queue:
                collection_completion_kind = collection_completion_queue.pop(0)
                collection_completion_elapsed = 0.0
            elif state.transition_pending:
                celebration_elapsed = 0.0
        elif collection_completion_kind is not None:
            collection_completion_elapsed += delta_seconds
            if collection_completion_elapsed >= COLLECTION_COMPLETION_DURATION:
                collection_completion_kind = None
                if collection_completion_queue:
                    collection_completion_kind = collection_completion_queue.pop(0)
                    collection_completion_elapsed = 0.0
        else:
            celebration_elapsed += delta_seconds
            if celebration_elapsed >= CELEBRATION_DURATION:
                state.advance_level()
                celebration_elapsed = None

        _draw_scene(game_surface, state, assets, font)
        if collection_completion_kind is not None:
            _draw_collection_completion(
                game_surface,
                celebration_font,
                collection_completion_kind,
                collection_completion_elapsed,
            )
        elif celebration_elapsed is not None:
            _draw_celebration(game_surface, celebration_font, celebration_elapsed)
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
        tower=_load_scaled(ASSET_ROOT / "sprites" / "tower.png"),
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
    _draw_tower(screen, state.world, assets)
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


def _draw_tower(screen: pygame.Surface, world: World, assets: Assets) -> None:
    if world.tower_tile is None:
        return
    tile_x, tile_y = world.tower_tile
    center = (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2 + HUD_HEIGHT)
    screen.blit(assets.tower, assets.tower.get_rect(center=center))


def _draw_gate(screen: pygame.Surface, state: GameState, assets: Assets) -> None:
    gate = state.world.gate
    gate_image = assets.gate_open if state.gate_open else assets.gate_closed
    gate_center = (int(gate.center[0]), int(gate.center[1] + HUD_HEIGHT))
    screen.blit(gate_image, gate_image.get_rect(center=gate_center))
    if state.world.entry_gate is not None:
        entry_gate = state.world.entry_gate
        entry_center = (int(entry_gate.center[0]), int(entry_gate.center[1] + HUD_HEIGHT))
        screen.blit(assets.gate_closed, assets.gate_closed.get_rect(center=entry_center))
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


def _draw_celebration(screen: pygame.Surface, font: pygame.font.Font, elapsed: float) -> None:
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((30, 47, 90, 128))
    screen.blit(overlay, (0, 0))

    for center_x, center_y, color, offset in (
        (230, 190, (255, 104, 135), 0.0),
        (480, 145, (255, 220, 88), 0.7),
        (725, 215, (101, 225, 186), 1.4),
    ):
        radius = 22 + ((elapsed + offset) % 0.9) / 0.9 * 88
        for ray in range(12):
            angle = ray * pi / 6 + elapsed * 2
            start = (center_x + cos(angle) * (radius - 16), center_y + sin(angle) * (radius - 16))
            end = (center_x + cos(angle) * radius, center_y + sin(angle) * radius)
            pygame.draw.line(screen, color, start, end, 5)
        pygame.draw.circle(screen, (255, 248, 207), (center_x, center_y), 9)

    message = font.render("Well done!", True, (255, 255, 255))
    shadow = font.render("Well done!", True, (91, 57, 92))
    center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    screen.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 4)))
    screen.blit(message, message.get_rect(center=center))


def _draw_hud(screen: pygame.Surface, state: GameState, assets: Assets, font: pygame.font.Font) -> None:
    pygame.draw.rect(screen, (255, 239, 193), (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, (146, 100, 92), (0, HUD_HEIGHT - 2), (WINDOW_WIDTH, HUD_HEIGHT - 2), 2)
    _draw_tiara(screen, (58, 32), 0.9, state.gem_count)
    _draw_bouquet(screen, (280, 34), 0.82, state.flower_count)
    gem_text = font.render(f"{state.gem_count}/{COLLECTIBLE_TARGET}", True, (55, 47, 76))
    flower_text = font.render(f"{state.flower_count}/{COLLECTIBLE_TARGET}", True, (55, 47, 76))
    screen.blit(gem_text, (111, 17))
    screen.blit(flower_text, (336, 17))


def _draw_tiara(
    screen: pygame.Surface,
    center: tuple[int, int],
    scale: float,
    diamond_count: int,
) -> None:
    center_x, center_y = center
    points = ((-36, 14), (-31, -4), (-18, 5), (-9, -15), (0, 4), (9, -20), (18, 5), (31, -4), (36, 14))
    scaled_points = [_scaled_point(center_x, center_y, scale, x, y) for x, y in points]
    pygame.draw.polygon(screen, (205, 143, 45), scaled_points)
    pygame.draw.polygon(
        screen,
        (255, 217, 91),
        [_scaled_point(center_x, center_y, scale, x, y) for x, y in ((-31, 12), (-27, 2), (-18, 9), (-9, -10), (0, 8), (9, -15), (18, 9), (27, 2), (31, 12))],
    )
    pygame.draw.line(
        screen,
        (134, 82, 47),
        _scaled_point(center_x, center_y, scale, -34, 15),
        _scaled_point(center_x, center_y, scale, 34, 15),
        max(1, round(3 * scale)),
    )
    for index, (socket_x, socket_y) in enumerate(((-25, 3), (-12, -5), (0, -10), (12, -5), (25, 3))):
        position = _scaled_point(center_x, center_y, scale, socket_x, socket_y)
        if index < diamond_count:
            _draw_diamond(screen, position, 5 * scale)
        else:
            pygame.draw.circle(screen, (151, 101, 69), position, max(2, round(4 * scale)))
            pygame.draw.circle(screen, (255, 239, 171), position, max(1, round(2 * scale)))


def _draw_bouquet(
    screen: pygame.Surface,
    center: tuple[int, int],
    scale: float,
    flower_count: int,
) -> None:
    center_x, center_y = center
    stem_base = _scaled_point(center_x, center_y, scale, 0, 19)
    flower_positions = ((0, -17), (-17, -10), (17, -10), (-25, 1), (25, 1))
    flower_colors = ((248, 104, 154), (255, 132, 92), (177, 110, 221), (255, 190, 65), (103, 180, 222))
    for index, (flower_x, flower_y) in enumerate(flower_positions[:flower_count]):
        flower_center = _scaled_point(center_x, center_y, scale, flower_x, flower_y)
        pygame.draw.line(screen, (55, 132, 67), stem_base, flower_center, max(1, round(3 * scale)))
        leaf_center = _scaled_point(center_x, center_y, scale, flower_x * 0.45 + (-4 if index % 2 else 4), flower_y * 0.45 + 5)
        pygame.draw.ellipse(screen, (82, 166, 74), (*leaf_center, max(2, round(8 * scale)), max(2, round(4 * scale))))
        _draw_flower(screen, flower_center, 6 * scale, flower_colors[index])
    pygame.draw.polygon(
        screen,
        (232, 104, 144),
        [_scaled_point(center_x, center_y, scale, x, y) for x, y in ((-10, 14), (0, 19), (-9, 24), (-4, 19))],
    )
    pygame.draw.polygon(
        screen,
        (232, 104, 144),
        [_scaled_point(center_x, center_y, scale, x, y) for x, y in ((10, 14), (0, 19), (9, 24), (4, 19))],
    )
    pygame.draw.circle(screen, (255, 193, 211), stem_base, max(2, round(3 * scale)))


def _draw_diamond(screen: pygame.Surface, center: tuple[int, int], radius: float) -> None:
    center_x, center_y = center
    size = max(2, round(radius))
    pygame.draw.polygon(screen, (17, 96, 156), ((center_x, center_y - size), (center_x + size, center_y), (center_x, center_y + size), (center_x - size, center_y)))
    pygame.draw.polygon(screen, (73, 207, 239), ((center_x, center_y - size + 1), (center_x + size - 1, center_y), (center_x, center_y + size - 1), (center_x - size + 1, center_y)))
    pygame.draw.polygon(screen, (190, 246, 252), ((center_x, center_y - size + 1), (center_x, center_y), (center_x - size + 1, center_y)))


def _draw_flower(screen: pygame.Surface, center: tuple[int, int], radius: float, color: tuple[int, int, int]) -> None:
    center_x, center_y = center
    petal_radius = max(2, round(radius * 0.62))
    offset = max(2, round(radius * 0.68))
    for offset_x, offset_y in ((0, -offset), (offset, 0), (0, offset), (-offset, 0)):
        pygame.draw.circle(screen, color, (center_x + offset_x, center_y + offset_y), petal_radius)
    pygame.draw.circle(screen, (255, 222, 78), center, max(2, round(radius * 0.48)))


def _scaled_point(center_x: int, center_y: int, scale: float, offset_x: float, offset_y: float) -> tuple[int, int]:
    return (round(center_x + offset_x * scale), round(center_y + offset_y * scale))


def _draw_collection_completion(
    screen: pygame.Surface,
    font: pygame.font.Font,
    kind: CollectibleKind,
    elapsed: float,
) -> None:
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((37, 48, 92, 142))
    screen.blit(overlay, (0, 0))

    pulse = 1.0 + sin(elapsed * pi * 2.3) * 0.08
    center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    for ray in range(18):
        angle = ray * pi / 9 + elapsed * 1.6
        inner_radius = 122 * pulse
        outer_radius = 152 * pulse
        start = (center[0] + cos(angle) * inner_radius, center[1] + sin(angle) * inner_radius)
        end = (center[0] + cos(angle) * outer_radius, center[1] + sin(angle) * outer_radius)
        pygame.draw.line(screen, (255, 229, 111), start, end, 5)

    if kind is CollectibleKind.GEM:
        _draw_tiara(screen, center, 4.1 * pulse, COLLECTIBLE_TARGET)
        message = "Tiara complete!"
    else:
        _draw_bouquet(screen, center, 4.0 * pulse, COLLECTIBLE_TARGET)
        message = "Bouquet complete!"
    text = font.render(message, True, (255, 255, 255))
    shadow = font.render(message, True, (91, 57, 92))
    text_center = (center[0], center[1] + 168)
    screen.blit(shadow, shadow.get_rect(center=(text_center[0] + 3, text_center[1] + 4)))
    screen.blit(text, text.get_rect(center=text_center))