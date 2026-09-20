from __future__ import annotations

from array import array
from math import sin, tau
from pathlib import Path
import wave

import pygame


ROOT = Path(__file__).resolve().parents[1]
TILES = ROOT / "assets" / "tiles"
SPRITES = ROOT / "assets" / "sprites"
SOUNDS = ROOT / "assets" / "sounds"
SIZE = 16


def main() -> None:
    pygame.init()
    for directory in (TILES, SPRITES, SOUNDS):
        directory.mkdir(parents=True, exist_ok=True)

    _save_tiles()
    _save_sprites()
    _write_tone(SOUNDS / "pickup.wav", (880, 1175), 0.16)
    _write_tone(SOUNDS / "celebrate.wav", (659, 784, 988, 1319), 0.38)
    pygame.quit()


def _surface() -> pygame.Surface:
    return pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)


def _save(surface: pygame.Surface, path: Path) -> None:
    pygame.image.save(surface, path)


def _save_tiles() -> None:
    grass = _surface()
    grass.fill((92, 174, 79))
    for position in ((2, 3), (11, 5), (6, 12), (13, 13)):
        pygame.draw.rect(grass, (132, 203, 91), (*position, 1, 2))
    _save(grass, TILES / "grass.png")

    grass_variant = grass.copy()
    pygame.draw.line(grass_variant, (60, 142, 69), (3, 9), (5, 7))
    pygame.draw.line(grass_variant, (60, 142, 69), (10, 3), (12, 1))
    _save(grass_variant, TILES / "grass_variant.png")

    path = _surface()
    path.fill((221, 185, 117))
    pygame.draw.circle(path, (192, 145, 87), (4, 4), 1)
    pygame.draw.circle(path, (239, 210, 145), (12, 11), 1)
    _save(path, TILES / "path.png")

    water = _surface()
    water.fill((61, 145, 205))
    for y in (4, 11):
        pygame.draw.line(water, (159, 220, 235), (2, y), (6, y - 1))
        pygame.draw.line(water, (159, 220, 235), (9, y), (14, y - 1))
    _save(water, TILES / "water.png")

    tree = grass.copy()
    pygame.draw.rect(tree, (110, 72, 45), (7, 9, 3, 7))
    pygame.draw.circle(tree, (35, 107, 60), (8, 7), 6)
    pygame.draw.circle(tree, (55, 140, 68), (6, 5), 3)
    _save(tree, TILES / "tree.png")

    mountain = grass.copy()
    pygame.draw.polygon(mountain, (81, 82, 112), ((1, 14), (8, 1), (15, 14)))
    pygame.draw.polygon(mountain, (211, 224, 232), ((8, 1), (5, 7), (8, 6), (10, 8)))
    _save(mountain, TILES / "mountain.png")


def _save_sprites() -> None:
    for facing in ("down", "up", "left", "right"):
        for frame in range(2):
            princess = _princess(facing, frame)
            _save(princess, SPRITES / f"princess_{facing}_{frame}.png")

    gem = _surface()
    dark_blue = (20, 101, 158)
    blue = (24, 167, 215)
    cyan = (59, 203, 233)
    pale_cyan = (160, 239, 249)
    pygame.draw.polygon(gem, dark_blue, ((5, 1), (10, 1), (15, 6), (8, 15), (1, 6)))
    pygame.draw.polygon(gem, blue, ((5, 2), (10, 2), (13, 6), (8, 13), (3, 6)))
    pygame.draw.polygon(gem, cyan, ((5, 2), (9, 2), (12, 6), (8, 7), (4, 6)))
    pygame.draw.polygon(gem, pale_cyan, ((6, 2), (9, 2), (8, 6), (5, 6)))
    pygame.draw.polygon(gem, dark_blue, ((2, 6), (4, 6), (8, 10), (8, 13)))
    pygame.draw.polygon(gem, cyan, ((8, 7), (12, 6), (8, 13)))
    _save(gem, SPRITES / "gem.png")

    flower = _surface()
    for center in ((8, 3), (13, 8), (8, 13), (3, 8)):
        pygame.draw.circle(flower, (248, 104, 154), center, 4)
    pygame.draw.circle(flower, (255, 219, 59), (8, 8), 3)
    _save(flower, SPRITES / "flower.png")


def _princess(facing: str, frame: int) -> pygame.Surface:
    princess = _surface()
    dress_bottom = 14 if frame == 0 else 15
    pygame.draw.ellipse(princess, (77, 48, 66), (3, 2, 10, 11))
    pygame.draw.polygon(princess, (255, 221, 66), ((4, 3), (6, 0), (8, 3), (10, 0), (12, 3)))
    pygame.draw.polygon(princess, (224, 89, 165), ((8, 9), (3, dress_bottom), (13, dress_bottom)))
    if facing == "down":
        pygame.draw.circle(princess, (255, 205, 171), (8, 6), 4)
        for eye in ((6, 6), (10, 6)):
            princess.set_at(eye, (52, 39, 48))
        princess.set_at((8, 7), (211, 132, 112))
        pygame.draw.line(princess, (178, 67, 99), (7, 9), (9, 9))
    elif facing == "up":
        pygame.draw.ellipse(princess, (77, 48, 66), (3, 2, 10, 10))
        pygame.draw.line(princess, (123, 75, 87), (5, 5), (5, 9))
        pygame.draw.line(princess, (123, 75, 87), (8, 4), (8, 10))
        pygame.draw.line(princess, (123, 75, 87), (11, 5), (11, 9))
    else:
        is_left = facing == "left"
        profile = (
            ((7, 3), (5, 3), (4, 5), (3, 6), (4, 7), (5, 8), (7, 9), (9, 8), (9, 4))
            if is_left
            else ((9, 3), (11, 3), (12, 5), (13, 6), (12, 7), (11, 8), (9, 9), (7, 8), (7, 4))
        )
        pygame.draw.polygon(princess, (255, 205, 171), profile)
        eye = (5, 5) if is_left else (11, 5)
        nose = (3, 6) if is_left else (13, 6)
        mouth_start = (4, 8) if is_left else (11, 8)
        mouth_end = (5, 8) if is_left else (12, 8)
        ear = (8, 6) if is_left else (8, 6)
        princess.set_at(eye, (52, 39, 48))
        princess.set_at(nose, (211, 132, 112))
        princess.set_at(ear, (211, 132, 112))
        pygame.draw.line(princess, (178, 67, 99), mouth_start, mouth_end)
        hair_x = 8 if is_left else 7
        pygame.draw.line(princess, (123, 75, 87), (hair_x, 3), (hair_x, 8))
    return princess


def _write_tone(path: Path, notes: tuple[int, ...], duration: float) -> None:
    sample_rate = 22_050
    samples_per_note = int(sample_rate * duration / len(notes))
    audio = array("h")
    for frequency in notes:
        for index in range(samples_per_note):
            progress = index / samples_per_note
            envelope = min(1.0, progress * 18) * max(0.0, 1.0 - progress) ** 1.8
            sample = int(9_000 * envelope * sin(tau * frequency * index / sample_rate))
            audio.append(sample)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(audio.tobytes())


if __name__ == "__main__":
    main()