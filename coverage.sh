#!/bin/sh
python venv/bin/coverage run --source="zipfelchappe" --omit="*tests*"  ./manage.py test zipfelchappe
coverage html --omit="*tests*"
