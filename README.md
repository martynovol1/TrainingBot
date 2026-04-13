# TrainingBot

TrainingBot is a personal tracker with two frontends on a shared backend:
- Telegram bot for tasks, calories, day tracking, and statistics.
- FastAPI website with the same data and functionality.

Both apps use the same SQLite database and the same business logic from `core/`.

## Features

- Start and finish a day.
- Add food and exercise entries.
- Add tasks and mark them as completed for the active day.
- View pending tasks for the current day with inline `Выполнить` buttons in Telegram.
- View statistics by day.
- Log in to the website using a one-time code from the Telegram bot.
- Keep user data isolated per Telegram account.

## Project Structure

- `core/` shared models, database, settings, and services.
- `bot/` Telegram bot app, handlers, keyboards, and helpers.
- `web/` FastAPI app, templates, and static files.
- `tokens/` bot token fallback.
- `start_bot.py` Telegram bot entry point.
- `start_web.py` FastAPI entry point.
- `tasks.db` SQLite database.

## Requirements

- Python 3.14+ recommended.
- Dependencies from `requirements.txt`.

Install them with:

```powershell
venv\Scripts\pip install -r requirements.txt
```

Run tests with:

```powershell
venv\Scripts\pytest
```

## Configuration

The project can read these environment variables:

- `BOT_API_TOKEN` - Telegram bot token. If not set, the bot falls back to `tokens/bot_token.py`.
- `DATABASE_URL` - database URL, default `sqlite:///tasks.db`.
- `APP_SECRET_KEY` - FastAPI session secret, default is a development value.
- `WEB_BASE_URL` - public website URL used in the bot login message, default `http://127.0.0.1:8000`.
- `BASE_METABOLISM_CALORIES` - default `1800`.
- `LOGIN_CODE_TTL_MINUTES` - web login code lifetime, default `10`.

Example:

```powershell
$env:BOT_API_TOKEN="123456:ABC..."
$env:APP_SECRET_KEY="change-me"
$env:WEB_BASE_URL="http://127.0.0.1:8000"
```

## Run

Start the bot:

```powershell
venv\Scripts\python start_bot.py
```

Start the website:

```powershell
venv\Scripts\uvicorn start_web:app --reload
```

Open the website at `http://127.0.0.1:8000`.

## Website Login

1. Open Telegram bot.
2. Go to `Веб-доступ`.
3. Get a one-time code.
4. Paste it into `/login` on the website.

The code is short-lived and bound to your Telegram user.

## Notes

- The first run creates the database schema automatically.
- The website and bot use the same data and authorization model.
- Tests use an isolated SQLite database and do not touch the main `tasks.db`.
- If you want to reset the local database, remove `tasks.db` before starting the apps again.
