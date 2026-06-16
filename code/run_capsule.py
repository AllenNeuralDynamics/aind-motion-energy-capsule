"""top level run script"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from aind_motion_energy import (
    clean_trace,
    compute_motion_energy,
    render_motion_energy_video,
)

DATA_DIR = Path("/root/capsule/data")
RESULTS_DIR = Path("/root/capsule/results")
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mj2", ".tif", ".tiff"}


def save_plots(stem, me, me_clean, keyframe_mask, avg_map, meta):
    fps = meta["fps"]
    t = np.arange(len(me)) / fps

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(t, me, lw=0.4, color="0.78", alpha=0.8)
    ax.plot(t, me_clean, lw=0.6, color="steelblue")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Motion energy")
    ax.set_title(stem)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to a specific video file (absolute, or relative to /root/capsule/data). "
             "If omitted, all videos under /root/capsule/data are processed.",
    )
    parser.add_argument("--start-frame", type=int, default=0)
    parser.add_argument("--end-frame", type=int, default=5000)
    args = parser.parse_args()

    start_frame = args.start_frame
    end_frame = args.end_frame

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.video:
        p = Path(args.video)
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
        render_motion_energy_video(
            video, me_clean, fps_source=meta["fps"],
            output_path=RESULTS_DIR / f"{stem}_motion_energy.mp4",
            raw_trace=me,
            start_frame=start_frame, end_frame=end_frame,
            window_seconds=3.0, out_fps=60.0,
        )
        print(f"{stem}: {len(me)} diffs | {meta['n_keyframes_masked']} keyframes masked | "
              f"max={me.max():.4f} | mean={me.mean():.4f}")


if __name__ == "__main__":
    run()

