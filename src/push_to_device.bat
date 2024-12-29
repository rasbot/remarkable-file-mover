@echo off
setlocal EnableDelayedExpansion

rem Get the root directory of the batch file
set "ROOT_DIR=%~dp0.."

rem Path to the configuration file in the config directory
set "CONFIG_FILE=%ROOT_DIR%\config\remarkable_config.txt"

rem Verify that the configuration file exists
if not exist "%CONFIG_FILE%" (
    echo Configuration file "%CONFIG_FILE%" not found!
    exit /b 1
)

rem Read and set variables from config file
for /f "usebackq tokens=1,* delims==" %%a in ("%CONFIG_FILE%") do (
    set "%%a=%%b"
)

rem Set destination path based on directory
set "DESTINATION_PATH=%DESTINATION_DIR%/%DESTINATION_FILE%"

rem Validate required variables
if not defined REMARKABLE_IP (
    echo REMARKABLE_IP not set in config file
    exit /b 1
)
if not defined REMARKABLE_PASSWORD (
    echo REMARKABLE_PASSWORD not set in config file
    exit /b 1
)
if not defined SOURCE_PATH (
    echo SOURCE_PATH not set in config file
    exit /b 1
)
if not defined DESTINATION_DIR (
    echo DESTINATION_DIR not set in config file
    exit /b 1
)
if not defined PUTTY_PATH (
    echo PUTTY_PATH not set in config file
    exit /b 1
)