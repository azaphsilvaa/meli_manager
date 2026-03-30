@echo off

echo ================================
echo   INSTALANDO SOFTWARE ML
echo ================================
echo.

echo Criando ambiente virtual...
python -m venv .venv

echo.
echo Ativando ambiente virtual...
call .venv\Scripts\activate

echo.
echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================
echo INSTALACAO CONCLUIDA
echo ================================
pause