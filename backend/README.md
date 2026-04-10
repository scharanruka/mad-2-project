Frontend: `bun run dev`

Backend: `uv run flask run`
Celery Worker: `uv run celery -A tasks.celery worker --beat --loglevel=info`
Redis: `redis-server`