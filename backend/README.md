Frontend: `bun run dev`
Backend: `uv run flask run`
Celery Worker: `uv run celery -A tasks.celery worker --beat --loglevel=info`
Redis: `redis-server`


# Enter your backend directory
uv run python -c "from tasks import generate_monthly_report; generate_monthly_report.delay()"