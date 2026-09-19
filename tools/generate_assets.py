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
    pygame.draw.polygon(gem, (71, 203, 249), ((8, 1), (14, 6), (11, 14), (5, 14), (2, 6)))
    pygame.draw.line(gem, (225, 253, 255), (8, 1), (5, 14), 1)
    pygame.draw.line(gem, (178, 237, 255), (8, 1), (11, 14), 1)
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
    pygame.draw.circle(princess, (255, 205, 171), (8, 6), 4)
    pygame.draw.polygon(princess, (255, 221, 66), ((4, 3), (6, 0), (8, 3), (10, 0), (12, 3)))
    pygame.draw.polygon(princess, (224, 89, 165), ((8, 9), (3, dress_bottom), (13, dress_bottom)))
    eye_positions = {
        "down": ((6, 6), (10, 6)),
        "up": (),
        "left": ((5, 6),),
        "right": ((11, 6),),
    }
    for eye in eye_positions[facing]:
        princess.set_at(eye, (52, 39, 48))
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