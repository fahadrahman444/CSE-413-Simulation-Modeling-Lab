@echo off
setlocal enabledelayedexpansion
title CSE 413: Bouncing Ball Simulator V4.0 - Launcher
color 0A

:: Move to current directory
cd /d "%~dp0"

:MENU
cls
echo ======================================================================
echo          CSE 413: SIMULATION ^& MODELING LAB - PROJECT RUNNER
echo                Bouncing Ball Simulator V4.0 (Final)
echo ======================================================================
echo.
echo   [1] Launch Live 2D Visual Animation (Recommended)
echo   [2] Run Fast Physics Simulation ^& Terminal Summary
echo   [3] Run All Parameter Sweep Experiments ^& Generate CSVs
echo   [4] Run Full Test Suite (21 Pytest Verification Tests)
echo   [5] Open Technical Report ^& Validation Plot
echo   [6] Open Generated Results Folder
echo   [0] Exit
echo.
echo ======================================================================
set /p choice="Enter your choice [default=1]: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto LIVE_ANIMATION
if "%choice%"=="2" goto SIMULATION
if "%choice%"=="3" goto EXPERIMENTS
if "%choice%"=="4" goto TESTS
if "%choice%"=="5" goto REPORT
if "%choice%"=="6" goto OPEN_FOLDER
if "%choice%"=="0" goto EXIT

echo Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:LIVE_ANIMATION
cls
echo Starting Live 2D Physics Visualizer...
echo (Close the visualizer window to return to this menu)
echo.
python project/src/animation.py
goto MENU

:SIMULATION
cls
echo Running standard physics simulation session...
echo.
python project/main.py
echo.
echo Simulation finished.
pause
goto MENU

:EXPERIMENTS
cls
echo Executing all parameter sweep experiments ^& generating figures...
echo.
python project/main.py --all
echo.
echo Experiments finished. Opening validation figure...
start "" "project\reports\figures\validation.png"
pause
goto MENU

:TESTS
cls
echo Running all 21 verification tests with pytest...
echo.
python -m pytest project/tests -v
echo.
echo Test suite execution complete.
pause
goto MENU

:REPORT
cls
echo Opening Technical Report and Validation Plot...
start "" "project\reports\TECHNICAL_REPORT.md"
start "" "project\reports\figures\validation.png"
timeout /t 2 >nul
goto MENU

:OPEN_FOLDER
explorer "project\results"
goto MENU

:EXIT
echo Exiting...
exit /b 0
