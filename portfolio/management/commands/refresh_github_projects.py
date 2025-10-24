from django.core.management.base import BaseCommand

from portfolio.views import fetch_github_projects


class Command(BaseCommand):
    help = "Refresh and warm the cached GitHub project list."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=6,
            help="Number of public repositories to cache (defaults to 6).",
        )

    def handle(self, *args, **options):
        limit = max(options.get("limit", 6), 0)
        if limit == 0:
            self.stdout.write(self.style.WARNING("Limit is 0; nothing to refresh."))
            return

        projects = fetch_github_projects(limit=limit, force_refresh=True)
        if projects:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cached {len(projects)} GitHub project{'s' if len(projects) != 1 else ''}."
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                "No GitHub projects were cached. Verify API availability and repository visibility."
            )
        )
