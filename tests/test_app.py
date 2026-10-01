import sys
from pathlib import Path

from sunny_grove import app


def test_asset_root_uses_source_assets_outside_a_bundle(monkeypatch) -> None:
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    assert app._asset_root() == Path(app.__file__).resolve().parents[2] / "assets"


def test_asset_root_uses_pyinstaller_bundle_assets(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert app._asset_root() == tmp_path / "assets"