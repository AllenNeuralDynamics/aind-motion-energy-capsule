"""top level run script"""
import json
from pathlib import Path

import numpy as np

from aind_motion_energy import compute_motion_energy

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mj2", ".tif", ".tiff"}


def run():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    videos = sorted(
        p for p in DATA_DIR.rglob("*")
        if p.suffix.lower() in VIDEO_EXTENSIONS
    )

    if not videos:
        print(f"No videos found in {DATA_DIR}")
        return

    for video in videos:
        me, avg_map, meta = compute_motion_energy(video)
        stem = video.stem
        np.save(RESULTS_DIR / f"{stem}_motion_energy.npy", me)
        np.save(RESULTS_DIR / f"{stem}_motion_energy_map.npy", avg_map)
        with open(RESULTS_DIR / f"{stem}_me_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
        print(f"{stem}: {len(me)} frames | max={me.max():.4f} | mean={me.mean():.4f}")


if __name__ == "__main__":
    run()
