# Website Django Project

This repository contains a Dockerized Django starter project. It exposes the development server on port 8000 and stores project dependencies in `requirements.txt`.

## Prerequisites

- Docker Engine
- Docker Compose (v1.29+ or the `docker compose` plugin)

## Getting started

```bash
sudo docker-compose up --build
```

The development server will be available at `http://localhost:8000` (or `http://192.168.2.210:8000` from your Windows machine).

To stop the stack:

```bash
sudo docker-compose down
```

## Environment variables

Environment variables can be customised in `docker-compose.yml`:

- `DJANGO_SECRET_KEY`: Secret used by Django.
- `DJANGO_DEBUG`: Set to `0` for production-like behaviour.
- `DJANGO_ALLOWED_HOSTS`: Comma-separated hosts allowed to connect (defaults to `localhost,127.0.0.1,0.0.0.0`).

## Next steps

- Add Django apps and templates to build your site.
- Replace SQLite with PostgreSQL by extending `docker-compose.yml`.
- Configure static and media files for production deployment.
