import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enables debug mode.
DEBUG = True




# DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
