@ECHO OFF

color 3f
ECHO.
ECHO.
ECHO ============== CLONING ==============
git clone https://github.com/erfantkerfan/studio-app.git && cd studio-app
ECHO.
ECHO.
ECHO ============== INITIALIZING ==============
pip install -r requirements.txt
copy .env.example .env
ECHO.
ECHO.
ECHO ================== DONE ==================
pause