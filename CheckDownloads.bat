@echo off
setlocal

rem Set the path to your Python executable
set python_executable=C:\Users\camst\AppData\Local\Programs\Python\Python311\python.exe

rem Set the paths to your Python scripts
set script1=C:\Python JW News\JWDownload.py
set script2=C:\Python JW News\JWKids Songs.py
set script3=C:\Python JW News\JWKids.py

rem Run the Python scripts one after the other
"%python_executable%" "%script1%"
"%python_executable%" "%script2%"
"%python_executable%" "%script3%"

endlocal
