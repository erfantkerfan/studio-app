@ECHO OFF

color 3f
ECHO.
ECHO.
set /p branch=Enter Branch name:
ECHO ============== CLONING ==============
git clone https://github.com/alaatv/studio-app -b %branch% && cd studio-app
git remote rename origin production
ECHO.
ECHO.
ECHO ============== INITIALIZING ==============
pip install -r requirements.txt
ECHO.
ECHO.
ECHO ================== DONE ==================
pause