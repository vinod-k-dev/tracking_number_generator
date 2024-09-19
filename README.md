# Tracking Number Generator Software

The objective of this assignment is to develop a Tracking Number Generator system for the organization. This system will be responsible for efficiently generating and managing unique tracking numbers for orders. A typical workflow for the organization using this system will include the creation, retrieval, and management of tracking numbers to streamline logistics and order processing.

## Clone the project
Clone the project from Github:

    Project Root Directory: `/var/www`
    
    git clone remote url

## Create Environment file

    Go to the settings folder then create .env file

    Note : Like see the .example_env file in project root folder, same veriable copy and paste in .env file on settings folder then update env varible .

## Virtual Environment Setup
Create Virtualenv Folder

    virtualenv --python=python3.12 Project_dir/.venv


Activate Environment:

    source project_venv/bin/activate


## Install dependencies:

    pip install -r requirements.txt


## Apply database migrations

    python3 manage.py makemigrations
    python3 manage.py migrate

## Create super user

    python3 manage.py createsuperuser

## Load base data

Load fixtures:

