# Website Django Project

A Dockerised Django application powering the denisprimc.com / primc.co.uk personal site. It ships with a portfolio homepage that highlights experience as an IT engineer and YouTube content creator.

## Prerequisites

- Docker Engine
- Docker Compose (v1.29+ or the `docker compose` plugin)

## Quick start

```bash
sudo docker-compose up --build
```

The development server listens on `http://localhost:8000` (from Windows, `http://192.168.2.210:8000`). Code changes hot-reload automatically.

To stop the stack:

```bash
sudo docker-compose down
```

## Project structure

- `portfolio/` – Django app with the homepage view and context data
- `templates/` – Jinja-style HTML templates (extends `base.html`)
- `static/css/styles.css` – Tailored styling for the personal brand
- `docker-compose.yml` / `Dockerfile` – Containerised runtime

## Customising content

The homepage content lives in `portfolio/views.py`. Update the context dictionaries for:

- `hero`: headline, summary, and call-to-action buttons
- `skills`, `experience`, `projects`: lists rendered on the page
- `featured_videos`: pulled automatically from the linked YouTube channel (falls back to a default list if the feed is unavailable)
- `contact`: email address and social links

Static styling can be tuned in `static/css/styles.css`. Add additional templates or sections by extending `templates/portfolio/home.html`.

## Environment variables

Set these in `docker-compose.yml` or your host shell before `docker-compose up`:

- `DJANGO_SECRET_KEY`: Django secret (defaults to a dev value)
- `DJANGO_DEBUG`: `1` for debug (default), `0` for production mode
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of domains (e.g. `denisprimc.com,primc.co.uk`)
- `PORTFOLIO_GITHUB_CACHE_TIMEOUT`: Cache duration (seconds) for public GitHub projects shown on the homepage (default `86400`, i.e. 24 hours)

## Keeping GitHub projects fresh

The GitHub section is cached to avoid rate limits. Update it manually or via cron with:

```bash
python manage.py refresh_github_projects --limit 6
```

With Docker Compose, wrap the command:

```bash
sudo docker compose run --rm web python manage.py refresh_github_projects --limit 6
```

Schedule the management command daily or weekly (for example via `cron`) to keep the cache current without restarting the app.

## Next steps

- Add HTTPS reverse proxy (nginx/Caddy) in front of the container for production.
- Swap SQLite for PostgreSQL and configure persistent storage.
- Automate deployments with GitHub Actions or another CI/CD tool.
