@echo off
REM Set the path to your virtual environment's activation script
set VIRTUAL_ENV_PATH=C:\Users\User\Documents\Github\Beauty-Salon\.venv\Scripts\activate

REM Activate the virtual environment
call %VIRTUAL_ENV_PATH%

REM Run the Django management command
python C:\Users\User\Documents\Github\Beauty-Salon\manage.py send_appointment_reminders
