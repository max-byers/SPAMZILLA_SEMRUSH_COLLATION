@echo off
echo GoDaddy Domain Extractor
echo ======================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Running domain extractor...
python advanced_godaddy_extractor.py
echo.
echo Press any key to exit...
pause >nul 