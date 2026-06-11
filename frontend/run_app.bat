@echo off
REM Script de démarrage rapide pour Windows

echo ==================================
echo 🚀 Demarrage de l'Application
echo ==================================
echo.

REM Verification de Streamlit
streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Streamlit n'est pas installe.
    echo Installation...
    pip install streamlit pandas plotly
)

echo ✅ Tous les elements sont prets!
echo.
echo Lancement de l'application...
echo.
echo 💡 Tips:
echo    - L'application s'ouvrira automatiquement dans votre navigateur
echo    - Acces a http://localhost:8501 si ce n'est pas le cas
echo    - Appuyez sur Ctrl+C pour arreter l'application
echo    - Appuyez sur 'R' dans l'interface pour redemarrer
echo.

cd /d "%~dp0"
streamlit run frontend/app.py

pause
