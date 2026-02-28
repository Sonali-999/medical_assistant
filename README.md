need to install mysql community server

#pip install speechrecognition pyaudio pydub ffmpeg-python python-dotenv groq elevenlabs gradio
#python -m pip install mysql-connector-python
python -m venv .venv
#.\.venv\Scripts\activate
python brain_of_the_doctor.py
python gradio_app.py

in mysql community->command prompt
#Get-Content schema.sql | mysql -u root -p
#mysql -u root -p

# -- create database if it doesn’t exist
# CREATE DATABASE IF NOT EXISTS medical_assistant
#   CHARACTER SET utf8mb4
#   COLLATE utf8mb4_unicode_ci;

# -- create user (or reset password if exists)
# CREATE USER IF NOT EXISTS 'aim_user'@'localhost' IDENTIFIED BY 'Sonali@2005';
# ALTER USER 'aim_user'@'localhost' IDENTIFIED BY 'Sonali@2005';

# -- grant permissions
# GRANT ALL PRIVILEGES ON medical_assistant.* TO 'aim_user'@'localhost';
# FLUSH PRIVILEGES;


# exit;
# mysql -u aim_user -p medical_assistant
# USE medical_assistant;
# queries
