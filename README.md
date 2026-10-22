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
| `/root/capsule/data/<mask_asset>/...` | no | ROI annotator mask files (`*_<camera>_masks.npz`), for ROI runs only. Pass the folder with `--roi-masks /root/capsule/data/<mask_asset>`; each video gets the mask file whose name ends in its camera name. Videos without a match get the whole-frame trace only, with a warning. |
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
| `{stem}_motion_energy.npz` | always | All numeric outputs: `me` and `me_clean` (`(T, 1+K)`, column 0 is the whole frame, the rest follow `roi_ids`), `keyframe_mask`, `first_frame`, `roi_ids`, `pixel_counts`, `avg_map`. See the library README's [outputs section](https://github.com/AllenNeuralDynamics/aind-motion-energy#outputs). |
| `{stem}_me_metadata.json` | always | Video properties and processing parameters (fps, codec, dimensions, number of ROIs, frame range, mask file path, `output_version`). |
| `{stem}_roi_masks.npz` | `--roi-masks` passed via `"$@"` | Copy of the input masks, for provenance. |
| `{stem}_motion_energy.png` | always (`--summary-plots` is baked in — see below) | Full-frame trace and, with ROIs, an ROI × time heatmap. |
| `{stem}_motion_energy_map.png` | always (`--summary-plots` is baked in) | Average motion map with ROI outlines. |
| `{stem}_motion_energy.csv` | `--csv` passed via `"$@"` | One row per frame: `frame_index, is_keyframe`, then `<id>, <id>_clean` for `full_frame` and each ROI. |
| `{stem}_motion_energy.mp4` | `--visualize` passed via `"$@"` | Rendered video with ROI outlines and synced, scrolling traces. |

Traces are frame-aligned: they have one row per decoded frame, row `i` is
video frame `first_frame + i`, and row 0 is NaN (it has no preceding frame).
Readers must not add a leading NaN themselves. Results from `v0.3.0` and
earlier wrote four `.npy` files with N−1 values instead; `output_version` in
the metadata is `2` for `v0.4.0` results and absent before.

## The `"$@"` passthrough contract

`code/run` bakes in three fixed arguments:

```bash
aind-motion-energy --input /root/capsule/data --output /root/capsule/results --summary-plots "$@"
```

`--input`, `--output`, and `--summary-plots` are fixed by this capsule and
are not meant to change between runs. Every other CLI flag — `--extensions`, `--roi`,
`--roi-masks`, `--csv`, `--start-frame`, `--end-frame`, `--no-normalize`,
`--no-mask-keyframes`, `--clean-method`, `--visualize`, `--viz-fps`,
`--viz-window-seconds`, `--viz-rois`, `--viz-stride` — arrives per-run via `"$@"`, supplied
by the Code Ocean App Builder's parameter panel or by the batch launcher's
invocation. **Never edit `code/run` to change parameters** — add or override
a flag by passing it at run time instead. See the library README's
[flag reference](https://github.com/AllenNeuralDynamics/aind-motion-energy#flags)
for what's available.

Older flat-layout sessions store each camera as both `.avi` and `.mp4`
(e.g. `bottom_camera.avi` + `bottom_camera.mp4`). Since `v0.3.0` the library
refuses to run when two videos would write the same outputs, so those sessions
need `--extensions .mp4` (the batch launcher passes it). The same check fails the
run if an extra attached data asset shares camera names with the session.

## Related repos

- [`aind-motion-energy`](https://github.com/AllenNeuralDynamics/aind-motion-energy) — the library and CLI this capsule wraps.
- [`aind-motion-energy-batch`](https://github.com/AllenNeuralDynamics/aind-motion-energy-batch) — the launcher that fans out capsule runs across sessions.
