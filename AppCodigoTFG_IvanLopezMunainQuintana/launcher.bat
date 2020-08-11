@ECHO OFF
ECHO Starting with the installation of the web application...
SET UserChoice="N"
ECHO If you enter another letter it will be assumed that you have all the libraries installed.
SET /P UserChoice="Do you have all the libraries installed [Y/N]?"
if  "%UserChoice%"=="N" (

ECHO ============================
ECHO  INSTALLING LIBRARIES
ECHO ============================
pip install Flask
pip install beautifulsoup4
pip install mechanize
pip install numpy
pip install xmltodict
pip install requests
pip install openpyxl
)
ECHO Launching the application...
set var_aux= %cd%
cd "C:/Program Files/R/R*/bin"
set var_dir= %cd%
cd %var_aux%
START python app.py  "%var_dir%"
timeout 10
start chrome http://127.0.0.1:5000/
