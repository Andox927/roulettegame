# Roulette

A Django app for running weighted prize roulette draws. It includes a public frontend spin page and a login-protected backend to manage prize configurations and review draw history.

## Features
- Weighted roulette wheel with animated spins
- Multiple prize configurations per event
- Draw history and activity snapshots
- Backend UI to edit prizes and probabilities
- JSON endpoints for draw and activity actions

## Tech Stack
- Django 6.0.2
- SQLite (db.sqlite3)

## Setup
1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`

Then visit `http://127.0.0.1:8000/` for the roulette wheel and `http://127.0.0.1:8000/backend/` for the admin UI (login required).

## Usage
1. Log in to `/backend/` and create a configuration with prize names and probabilities, then save.
2. Go to `/` to spin the wheel, enter a nickname, and draw.
3. Use the "新增抽獎" button on the frontend to archive current draw history into an activity record.
4. View or delete past activities from `/backend/` under "讀取抽獎歷史".

## API
- `POST /api/draw/` (fields: `config_id`, `nickname`)
- `POST /api/new-activity/` (fields: `activity_name`, `config_id`)
- `POST /api/delete-activity/` (fields: `activity_name`)

## Project Layout
- `roulette_app/` core app logic (models, views)
- `roulette_project/` Django settings and URLs
- `templates/` frontend/backend templates
- `static/` JS/CSS assets
