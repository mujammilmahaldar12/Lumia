@echo off
title Lumia Investment Advisor - GPU Enabled

echo.
echo ============================================================
echo   LUMIA EXPERT INVESTMENT ADVISOR
echo   GPU-Accelerated AI Analysis
echo ============================================================
echo.
echo  Activating GPU Environment...

cd "c:\Users\mujammil maldar\Desktop\New folder (4)\app"
call .\env\Scripts\activate
cd .\Lumia\

echo.
echo ============================================================
echo   GPU STATUS: NVIDIA GeForce RTX 3060 (12.9 GB VRAM)
echo   PyTorch: 2.7.1+cu118 (CUDA 11.8)
echo   Status: READY
echo ============================================================
echo.
echo  Available Commands:
echo  -------------------
echo   1. streamlit run app/streamlit_app.py    - Web Interface
echo   2. python main.py --top 20               - Quick Analysis
echo   3. python test_gpu.py                    - Test GPU
echo   4. python main.py --type all --top 50    - Full Analysis
echo.
echo ============================================================
echo.

cmd /k
