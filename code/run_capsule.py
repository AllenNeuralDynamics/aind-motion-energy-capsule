"""top level run script"""
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from aind_motion_energy import clean_trace, compute_motion_energy

DATA_DIR = Path("/root/capsule/data")
RESULTS_DIR = Path("/root/capsule/results")
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mj2", ".tif", ".tiff"}


def save_plots(stem, me, me_clean, keyframe_mask, avg_map, meta):
    fps = meta["fps"]
    t = np.arange(len(me)) / fps

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(t, me_clean, lw=0.5, color="steelblue", label="motion energy (clean)")
    if keyframe_mask.any():
        ax.scatter(t[keyframe_mask], me[keyframe_mask], s=8, color="red",
                   zorder=3, label=f"{meta['n_keyframes_masked']} keyframe diffs (raw)")
        ax.legend(loc="upper right", fontsize=8)
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
    video_path_env = '/root/capsule/data/behavior_854151_2026-06-08_09-39-38/behavior-videos/BottomCamera/video.mp4'
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
        me, keyframe_mask, avg_map, meta = compute_motion_energy(
            video, start_frame=start_frame, end_frame=end_frame
        )
        me_clean = clean_trace(me, keyframe_mask, method="interpolate")
        stem = video.stem
        np.save(RESULTS_DIR / f"{stem}_motion_energy.npy", me)
        np.save(RESULTS_DIR / f"{stem}_motion_energy_clean.npy", me_clean)
        np.save(RESULTS_DIR / f"{stem}_keyframe_mask.npy", keyframe_mask)
        np.save(RESULTS_DIR / f"{stem}_motion_energy_map.npy", avg_map)
        with open(RESULTS_DIR / f"{stem}_me_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
        save_plots(stem, me, me_clean, keyframe_mask, avg_map, meta)
        print(f"{stem}: {len(me)} diffs | {meta['n_keyframes_masked']} keyframes masked | "
              f"max={me.max():.4f} | mean={me.mean():.4f}")


if __name__ == "__main__":
    run()
