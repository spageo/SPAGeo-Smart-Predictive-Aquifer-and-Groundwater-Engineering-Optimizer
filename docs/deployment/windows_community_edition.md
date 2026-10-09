# SPAGeo Community Edition — Windows Deployment

## 1. Deployment Model

SPAGeo Community Edition is currently deployed as a Windows standalone desktop application using the QGIS/PyQGIS runtime as its GIS engine.

The QGIS runtime is installed separately rather than bundled into the SPAGeo repository.

The deployment flow is:

Windows
  |
  +-- QGIS 3.44.x runtime
  |
  +-- SPAGeo launcher
        |
        +-- PyQGIS
        +-- SPAGeo standalone application
        +-- MODFLOW 6

## 2. System Requirements

### Operating System

- Windows 10 or later
- 64-bit Windows recommended

### QGIS

SPAGeo requires a compatible QGIS installation providing the PyQGIS runtime.

The current validated environment uses:

- QGIS 3.44.12
- QGIS Python 3.12.13
- QGIS/PyQGIS runtime
- QGIS runtime initialized through o4w_env.bat

The current launcher expects:

C:\Program Files\QGIS 3.44.12

Future releases should support automatic or configurable QGIS discovery.

### MODFLOW 6

SPAGeo uses MODFLOW 6 through FloPy.

mf6.exe must be available through the Windows PATH.

The current validated installation is:

C:\MODFLOW6\mf6.7.0_win64\mf6.7.0_win64\bin\mf6.exe

The launcher does not hard-code this path.

## 3. Python Runtime

The standalone application uses the Python runtime supplied by QGIS.

The validated Python executable is:

C:\Program Files\QGIS 3.44.12\apps\Python312\python.exe

SPAGeo requires PyQGIS and the QGIS-provided Qt/PyQt components.

A separate system Python installation is not required by the current launcher.

## 4. Python Application Dependencies

The current application uses packages including:

- NumPy
- FloPy
- boto3
- PyQGIS/QGIS Python bindings
- QGIS-provided Qt/PyQt bindings

PyQGIS and QGIS-provided components are supplied by QGIS and should not be treated as ordinary standalone pip dependencies.

## 5. SPAGeo Repository

The Community Edition repository contains the application code, UI, GIS integration, model engine, tests, documentation, and deployment scripts.

The standalone application entry point is:

standalone_app.py

The deployment launcher is:

scripts\run_spageo.bat

## 6. One-Click Launcher

From the repository root, start SPAGeo with:

.\scripts\run_spageo.bat

The launcher:

1. Establishes the SPAGeo repository root.
2. Initializes the QGIS runtime.
3. Configures the PyQGIS Python path.
4. Configures the QGIS prefix path.
5. Starts standalone_app.py.
6. Returns the application exit status.

## 7. Validated Startup and Shutdown

The current Windows launcher has been tested successfully in the validated QGIS 3.44.12 development environment.

The validated sequence includes:

- Preparing the QGIS runtime.
- Starting `standalone_app.py`.
- Successful QGIS initialization.
- A visible SPAGeo standalone window.
- Successful Qt event-loop exit.
- Releasing the standalone window before QGIS shutdown.
- Successful QGIS shutdown.

The standalone application was launched and closed three consecutive times through the official QGIS Python launcher. All three runs returned process exit code `0`.

The one-click launcher, `scripts\run_spageo.bat`, was also tested successfully and returned process exit code `0`.

These results validate the current development environment. Testing on a clean Windows environment is still required before release.

## 8. Current Installation Procedure

The current Community Edition deployment procedure is:

1. Install a compatible QGIS version.
2. Install/configure MODFLOW 6.
3. Ensure mf6.exe is available through PATH.
4. Obtain the SPAGeo Community Edition repository.
5. Open a terminal in the repository root.
6. Run:

.\scripts\run_spageo.bat

The current standalone launcher does not require pip install -e ..

## 9. Current Deployment Limitation

The current launcher uses the fixed QGIS installation path:

C:\Program Files\QGIS 3.44.12

This is suitable for the currently validated environment but is not yet a general-purpose installer mechanism.

A future Windows installer should:

- detect the installed QGIS runtime;
- validate the required PyQGIS components;
- validate MODFLOW 6;
- configure runtime paths automatically;
- provide a desktop shortcut;
- provide an uninstall mechanism;
- avoid requiring PowerShell for normal users.

## 10. Future Windows Packaging

The current launcher is the foundation for the Windows Community Edition package.

The intended progression is:

Current
  |
  +-- run_spageo.bat
  |
  v
Windows launcher/package
  |
  +-- QGIS runtime detection
  +-- MODFLOW 6 validation
  +-- Desktop shortcut
  |
  v
Community Edition installer

Bundling the complete QGIS runtime is not part of the current deployment stage.

## 11. Troubleshooting

### Verify QGIS Python

Test-Path "C:\Program Files\QGIS 3.44.12\apps\Python312\python.exe"

Expected:

True

### Verify QGIS environment

Test-Path "C:\Program Files\QGIS 3.44.12\bin\o4w_env.bat"

Expected:

True

### Verify MODFLOW 6

where.exe mf6

The command should return the location of mf6.exe.

## 12. Deployment Status

Current Windows Community Edition deployment status:

- Runtime bootstrap: Validated in the current development environment
- One-click launcher: Created and tested
- Launcher startup and shutdown: Passed
- Standalone application process exit: Passed repeated tests
- Runtime/dependency documentation: In progress
- Windows installer/package: Not yet implemented
- Fresh-environment validation: Pending