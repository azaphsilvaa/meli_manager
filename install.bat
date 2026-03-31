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
echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias...
python -m pip install -r requirements.txt

echo.
echo Gerando sons padrao do sistema...
python app\scripts\generate_default_sounds.py

echo.
echo ================================
echo INSTALACAO CONCLUIDA
echo ================================
pause