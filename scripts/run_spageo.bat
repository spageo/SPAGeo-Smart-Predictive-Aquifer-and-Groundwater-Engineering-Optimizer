@echo off
setlocal

echo ==========================================
echo SPAGeo Community Edition
echo ==========================================
echo.

set "SPAGEO_ROOT=%~dp0.."
set "QGIS_ROOT=C:\Program Files\QGIS 3.44.12"
set "QGIS_PREFIX=%QGIS_ROOT%\apps\qgis-ltr"
set "QGIS_PYTHON=%QGIS_PREFIX%\python"

echo Preparing QGIS runtime...

call "%QGIS_ROOT%\bin\o4w_env.bat"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to initialize the QGIS runtime.
    pause
    exit /b 1
)

set "PYTHONPATH=%QGIS_PYTHON%"
set "QGIS_PREFIX_PATH=%QGIS_PREFIX%"

cd /d "%SPAGEO_ROOT%"

echo Starting SPAGeo...
echo.

python "%SPAGEO_ROOT%\standalone_app.py"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo SPAGeo closed successfully.
) else (
    echo SPAGeo exited with code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
