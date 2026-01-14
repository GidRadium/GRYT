# GRYT
**GRYT** - Telegram bot, maded by **G**id**R**adium, which can download **Y**ou**T**ube, or other site's media. It is written on Python, and uses yt-dlp and other APIs to download streaming media.

## Download
```bash
git clone https://github.com/GidRadium/GRYT.git
```

## Install
Create python enviroment and load libs.
```bash
cd GRYT
uv venv
source .venv/bin/activate
uv sync
```

## Setup
Configure .env file
```bash
nano .env
```
Fill with your secrets
```bash
TG_API_ID=123456
TG_API_HASH=abcdef123456
TG_SESSION=prod-session
```
And save the file

## Start
```bash
uv run start.py
```

## Project
Minimum project structure
```
GRYT/
├── .gitignore
├── .env.example
├── pyproject.toml
├── cookies/
│   ├── yt_cookies.txt
│   └── etc...
├── start.py
├── src/
│   ├── bot.py
│   ├── database.py
│   ├── logger.py
│   ├── translations.py
│   └── 
```
