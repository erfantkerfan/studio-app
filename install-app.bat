@ECHO OFF

color 3f

ECHO ============== INSTALLING ==============
pip install -r requirements.txt
copy .env.example .env
ECHO.
ECHO.
ECHO ================== DONE ==================
pause