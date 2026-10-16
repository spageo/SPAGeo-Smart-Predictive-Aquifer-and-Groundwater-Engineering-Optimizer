# SPAGeo Browser Demo

A lightweight browser interface for exploring a previously saved SPAGeo / MODFLOW head-output file.

## Scope

- Displays saved head snapshots and basic statistics.
- Allows selection among the saved simulation times.
- Does not run MODFLOW, access QGIS, generate AI workflows, or submit cloud simulations.
- Results are demonstration data and have not been independently validated.

## Run locally on Windows

From the repository root, create an isolated environment outside the repository:

```powershell
$envDir = Join-Path $env:LOCALAPPDATA "SPAGeo-WebDemo\.venv"
py -3.13 -m venv $envDir
& "$envDir\Scripts\python.exe" -m pip install --upgrade pip
& "$envDir\Scripts\python.exe" -m pip install -r .\demo_web\requirements.txt
& "$envDir\Scripts\python.exe" -m streamlit run .\demo_web\app.py
```

Streamlit normally opens the app in a browser at `http://localhost:8501`.

## Data

The file `data/spageo_demo_heads.npz` contains exported snapshots from a previously saved local simulation. It is not a new simulation run.

## Deployment

This folder is the intended entry point for a future hosted demo. Hosting is not configured by these files alone. Test locally before publishing, and review the repository's licensing, data, and access requirements before making it public.
