# aind-motion-energy-capsule

![support](https://img.shields.io/badge/support-supported-brightgreen)

Code Ocean capsule that runs [`aind-motion-energy`](https://github.com/AllenNeuralDynamics/aind-motion-energy)
on behavior videos. `code/run` is a thin shell: it forwards its arguments to
the library's `aind-motion-energy` CLI and does no compute of its own.

## Input assets and mount layout

The capsule reads from `/root/capsule/data`:

| Path | Required | Contents |
|---|---|---|
| `/root/capsule/data/<asset_name>/...` | yes | One behavior-video data asset, attached by whatever triggers the run (see below). Searched recursively for video files (`.mp4`, `.avi`, `.mkv`, `.mov`, `.mj2`, `.tif`, `.tiff`) plus each video's companion CSV in the same folder. |
| `/root/capsule/data/foraging_nwb_bonsai/...` | no | An NWB asset used only by `examples/example_motion_energy.ipynb` for trial-time alignment. Not read by `code/run`; irrelevant to a normal capsule run. |

The video asset is attached one of two ways:

- **Code Ocean App Builder** — a manual run with one asset attached directly.
- **[`aind-motion-energy-batch`](https://github.com/AllenNeuralDynamics/aind-motion-energy-batch)** — the launcher that fans out one capsule run per session, attaching one asset per run, mounted under its own asset name.

## Outputs

Written to `/root/capsule/results`, one set per discovered video, keyed on
`{stem}` — the video's parent folder name if the file stem is literally
`"video"` (AIND's `<CameraName>/video.mp4` layout), otherwise the file's own
stem. See the library README's
[camera-keying heuristic](https://github.com/AllenNeuralDynamics/aind-motion-energy#camera-keying-heuristic)
for why.

| File | Written when | Contents |
|---|---|---|
| `{stem}_motion_energy.npy` | always | Raw motion-energy trace. |
| `{stem}_motion_energy_clean.npy` | always | Cleaned trace with keyframe-contaminated diffs handled. |
| `{stem}_keyframe_mask.npy` | always | Bool mask flagging keyframe-contaminated diffs. |
| `{stem}_motion_energy_map.npy` | always | Per-pixel average absolute frame difference. |
| `{stem}_me_metadata.json` | always | Video properties and processing parameters (fps, codec, dimensions, ROI, frame range, etc.). |
| `{stem}_motion_energy.png` | always (`--summary-plots` is baked in — see below) | Motion-energy timeseries plot. |
| `{stem}_motion_energy_map.png` | always (`--summary-plots` is baked in) | Heatmap of `{stem}_motion_energy_map.npy`. |
| `{stem}_motion_energy.csv` | `--format csv` or `both` passed via `"$@"` | Per-frame `frame_index, motion_energy, motion_energy_clean, is_keyframe`. |
| `{stem}_motion_energy.mp4` | `--visualize` passed via `"$@"` | Rendered video with a synced, scrolling motion-energy plot. |

## The `"$@"` passthrough contract

`code/run` bakes in three fixed arguments:

```bash
aind-motion-energy --input /root/capsule/data --output /root/capsule/results --summary-plots "$@"
```

`--input`, `--output`, and `--summary-plots` are fixed by this capsule and
are not meant to change between runs. Every other CLI flag — `--roi`,
`--format`, `--start-frame`, `--end-frame`, `--no-normalize`,
`--no-mask-keyframes`, `--clean-method`, `--visualize`, `--viz-fps`,
`--viz-window-seconds`, `--viz-stride` — arrives per-run via `"$@"`, supplied
by the Code Ocean App Builder's parameter panel or by the batch launcher's
invocation. **Never edit `code/run` to change parameters** — add or override
a flag by passing it at run time instead. See the library README's
[flag reference](https://github.com/AllenNeuralDynamics/aind-motion-energy#flags)
for what's available.

## Related repos

- [`aind-motion-energy`](https://github.com/AllenNeuralDynamics/aind-motion-energy) — the library and CLI this capsule wraps.
- [`aind-motion-energy-batch`](https://github.com/AllenNeuralDynamics/aind-motion-energy-batch) — the launcher that fans out capsule runs across sessions.
