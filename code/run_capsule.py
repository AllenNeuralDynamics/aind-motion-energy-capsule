"""top level run script"""
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from aind_motion_energy import compute_motion_energy

DATA_DIR = Path("/root/capsule/data")
RESULTS_DIR = Path("/root/capsule/results")
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mj2", ".tif", ".tiff"}


def save_plots(stem, me, avg_map, meta):
    fps = meta["fps"]
    t = np.arange(len(me)) / fps

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(t, me, lw=0.5, color="steelblue")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Motion energy")
    ax.set_title(stem)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"{stem}_motion_energy.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(avg_map, cmap="hot", aspect="auto")
    plt.colorbar(im, ax=ax, label="Mean abs diff (per pixel)")
    ax.set_title(f"{stem} — avg motion map")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"{stem}_motion_energy_map.png", dpi=150)
    plt.close(fig)


def run():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Optional parameters via CO environment variables
    video_path_env = '/root/capsule/data/behavior_716325_2024-05-31_10-31-14/behavior-videos/bottom_camera.avi'
    start_frame = 0
    end_frame = 5000

    if video_path_env:
        p = Path(video_path_env)
        videos = [DATA_DIR / p if not p.is_absolute() else p]
    else:
        videos = sorted(
            p for p in DATA_DIR.rglob("*")
            if p.suffix.lower() in VIDEO_EXTENSIONS
        )

    if not videos:
        print(f"No videos found in {DATA_DIR}")
        return

    for video in videos:
        me, avg_map, meta = compute_motion_energy(
            video, start_frame=start_frame, end_frame=end_frame
        )
        stem = video.stem
        np.save(RESULTS_DIR / f"{stem}_motion_energy.npy", me)
        np.save(RESULTS_DIR / f"{stem}_motion_energy_map.npy", avg_map)
        with open(RESULTS_DIR / f"{stem}_me_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
        save_plots(stem, me, avg_map, meta)
        print(f"{stem}: {len(me)} frames | max={me.max():.4f} | mean={me.mean():.4f}")


if __name__ == "__main__":
    run()
