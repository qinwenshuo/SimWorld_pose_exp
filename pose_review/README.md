# Pose Review

`01_generate_videos.ipynb` records a dataset of short two-agent "discussion" video clips across varied camera/agent positions and facing angles, for reviewing how pose affects 2D framing. Output (`.mp4` clips + `metadata.csv`) goes to `output_pose_review/`.

## Prerequisites

- **OS**: Windows (required for OBS window capture of the UE server).
- **SimWorld** — install and start the UE server per the root [Setup](../README.md#setup) guide. The notebook connects via UnrealCV on `localhost:9000` using the `demo_city_1` scene.
- **Extra packages**: `pip install obsws-python tqdm`
- **OBS Studio** — [install it](https://obsproject.com/), add a **Window Capture** source named `Window Capture` targeting the UE window, and enable **Tools → WebSocket Server Settings**. Set the password via env var before launching:
  ```bash
  export OBS_PASSWORD='your-obs-websocket-password'
  jupyter notebook
  ```

## Usage

With the UE server and OBS running, run the notebook top to bottom. It builds a pool of 10 distinct characters, then records 3 repetitions per condition (skipping any clips that already exist, so it's safe to resume). Use the **Regenerate a Specific Video** cell to re-record a single clip by filename.
