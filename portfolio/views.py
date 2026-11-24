import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from functools import lru_cache
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from .models import BlogPost

YOUTUBE_CHANNEL_ID = "UCxVnLNkd4kKK_A-ky4kt_6A"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0 Safari/537.36"
)


def _thumbnail_from_id(video_id: str) -> str:
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


DEFAULT_FEATURED_VIDEOS = [
    {
        "title": "3 Easy Ways to Free Up Space on C Drive Using OneDrive or Synced SharePoint",
        "url": "https://www.youtube.com/watch?v=DeW1gAfdGOA",
        "thumbnail": _thumbnail_from_id("DeW1gAfdGOA"),
    },
    {
        "title": "How to build a Terminal Server 2022 for home lab",
        "url": "https://www.youtube.com/watch?v=kZmeQgz3G_o",
        "thumbnail": _thumbnail_from_id("kZmeQgz3G_o"),
    },
    {
        "title": "How to build Domain Controller server 2019 for home lab",
        "url": "https://www.youtube.com/watch?v=MrkkHZqCpJE",
        "thumbnail": _thumbnail_from_id("MrkkHZqCpJE"),
    },
]


def _fetch(url: str, timeout: int = 6, headers=None) -> bytes:
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


@lru_cache(maxsize=1)
def fetch_latest_videos(limit: int = 3):
    try:
        feed = _fetch(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
        )
    except Exception:
        return [dict(item) for item in DEFAULT_FEATURED_VIDEOS[:limit]]

    try:
        root = ET.fromstring(feed)
    except ET.ParseError:
        return [dict(item) for item in DEFAULT_FEATURED_VIDEOS[:limit]]

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }

    entries = []
    for entry in root.findall("atom:entry", ns):
        video_id = entry.findtext("yt:videoId", default="", namespaces=ns)
        title = entry.findtext("atom:title", default="", namespaces=ns)
        published = entry.findtext("atom:published", default="", namespaces=ns)
        if not video_id or not title:
            continue
        entries.append((published, video_id, title))

    entries.sort(reverse=True)

    primary, backup = [], []
    for published, video_id, title in entries[:10]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            raw_html = _fetch(video_url, timeout=6)
        except Exception:
            continue

        match = re.search(
            r"ytInitialPlayerResponse\s*=\s*(\{.*?\})\s*;",
            raw_html.decode("utf-8", "ignore"),
            flags=re.DOTALL,
        )
        if not match:
            continue

        try:
            details = json.loads(match.group(1)).get("videoDetails", {})
        except json.JSONDecodeError:
            continue

        if details.get("isLiveContent"):
            continue

        length = int(details.get("lengthSeconds", "0") or 0)
        is_shorts = bool(
            details.get("isShortsEligible") or details.get("isShortsVideo")
        )

        if is_shorts:
            continue

        thumbnails = details.get("thumbnail", {}).get("thumbnails", [])
        thumb_url = thumbnails[-1].get("url") if thumbnails else _thumbnail_from_id(video_id)

        record = {
            "title": title,
            "url": video_url,
            "thumbnail": thumb_url,
            "published": published,
        }

        if length >= 120:
            primary.append(record)
        elif length >= 60:
            backup.append(record)

        if len(primary) >= limit:
            break

    videos = primary
    if len(videos) < limit:
        for item in backup:
            if item not in videos:
                videos.append(item)
            if len(videos) >= limit:
                break

    if not videos:
        return [dict(item) for item in DEFAULT_FEATURED_VIDEOS[:limit]]

    videos.sort(key=lambda item: item.get("published", ""), reverse=True)
    for item in videos:
        item.pop("published", None)
    return videos[:limit]


GITHUB_USERNAME = "Dprimc"
GITHUB_PROJECT_CACHE_KEY = "portfolio.github_projects"
GITHUB_CACHE_TIMEOUT = getattr(settings, "PORTFOLIO_GITHUB_CACHE_TIMEOUT", 60 * 60 * 24)


def _load_github_projects(limit: int) -> list[dict]:
    page_size = max(limit * 2, limit)
    try:
        payload = _fetch(
            (
                "https://api.github.com/users/"
                f"{GITHUB_USERNAME}/repos?sort=updated&per_page={page_size}"
            ),
            timeout=6,
            headers={"Accept": "application/vnd.github+json"},
        )
    except Exception:
        return []

    try:
        decoded = payload.decode("utf-8")
    except UnicodeDecodeError:
        return []

    try:
        repos = json.loads(decoded)
    except json.JSONDecodeError:
        return []

    if isinstance(repos, dict):
        return []

    projects = []
    for repo in repos:
        if repo.get("private") or repo.get("fork") or repo.get("archived"):
            continue
        project = {
            "name": repo.get("name") or "",
            "description": repo.get("description") or "No description provided yet.",
            "url": repo.get("html_url") or "",
            "language": repo.get("language") or "",
            "stars": int(repo.get("stargazers_count") or 0),
            "topics": repo.get("topics") or [],
            "updated": repo.get("pushed_at") or repo.get("updated_at") or "",
        }
        if not project["name"] or not project["url"]:
            continue
        projects.append(project)
        if len(projects) >= limit:
            break
    return projects


def fetch_github_projects(limit: int = 6, *, force_refresh: bool = False):
    if limit <= 0:
        return []

    cache_key = f"{GITHUB_PROJECT_CACHE_KEY}:{limit}"
    cached_projects = cache.get(cache_key)
    if cached_projects is not None and not force_refresh:
        return cached_projects

    projects = _load_github_projects(limit)
    if projects:
        cache.set(cache_key, projects, timeout=GITHUB_CACHE_TIMEOUT)
        return projects

    if cached_projects is not None:
        return cached_projects

    cache.delete(cache_key)
    return []


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "hero": {
                    "name": "Denis Primc",
                    "title": "Denis Primc · Practical IT Help",
                    "summary": (
                        "Practical IT help for home users and small businesses — from Microsoft 365 "
                        "and Windows to networks, servers, cloud and homelab solutions."
                    ),
                    "focus_title": "What This Site Is",
                    "focus_sections": [
                        {
                            "title": "1. Homelab and Business Solutions",
                            "body": "Testing practical IT solutions safely in a homelab before adapting them for small and medium-sized business use.",
                        },
                        {
                            "title": "2. Infrastructure and Cloud",
                            "body": "Windows Server, Linux, Hyper-V, Docker, Azure, Microsoft 365, secure access, maintenance, and recovery testing.",
                        },
                        {
                            "title": "3. Business Automation and AI",
                            "body": "PowerShell automation, monitoring, reporting, AI-assisted troubleshooting, and tools designed to save time.",
                        },
                    ],
                    "cta_links": [
                        {"label": "Contact Me", "url": "#contact"},
                        {"label": "View Projects", "url": "#projects"},
                    ],
                },
                "services": [
                    {
                        "title": "Homelab and Business Solutions",
                        "items": [
                            "Testing business IT solutions safely before deployment",
                            "Monitoring dashboards and service status pages",
                            "Backup, recovery, and update testing",
                            "Secure remote access and internal business tools",
                        ],
                    },
                    {
                        "title": "Infrastructure and Cloud",
                        "items": [
                            "Windows Server, Linux, Hyper-V, and Docker",
                            "Microsoft Azure and Microsoft 365 testing",
                            "Business networks, DNS, HTTPS, VPNs, and secure access",
                            "Server patching, firmware upgrades, backups, and maintenance",
                            "High availability and disaster-recovery testing",
                        ],
                    },
                    {
                        "title": "Business Automation and AI",
                        "items": [
                            "PowerShell automation for repetitive IT tasks",
                            "Automated monitoring, reporting, and maintenance",
                            "AI-assisted troubleshooting and documentation",
                            "Practical tools designed to save businesses time",
                        ],
                    },
                ],
                "problems": [
                    "Personal homelab systems and self-hosted tools",
                    "Firmware upgrades for routers, switches, access points, and server hardware",
                    "System, package, Docker, and service upgrades I do during maintenance",
                    "Automation scripts for maintenance and local workflows",
                    "AI-assisted troubleshooting and practical improvements",
                    "Dashboards, status pages, forms, and workflow tools",
                    "Domains, reverse proxies, Docker containers, tunnels, and services",
                    "Simple, reliable tools for infrastructure and maintenance",
                ],
                "about": {
                    "title": "About Denis Primc",
                    "body": (
                        "IT learning and hands-on practice: homelab systems, self-hosted services, technical videos, "
                        "Microsoft certificates, automation experiments, maintenance work, upgrades, and troubleshooting. "
                        "The focus is practical work with Linux servers, Docker containers, reverse proxies, dashboards, firmware upgrades, regular updates, and small tools."
                    ),
                },
                "microsoft_credentials": {
                    "profile_url": "https://learn.microsoft.com/en-us/users/denisprimc/credentials/certifications?tab=credentials-tab",
                    "summary": "A few Microsoft certificates and legacy credentials, linked to Microsoft Learn where available.",
                    "highlights": [
                        {
                            "type": "Certification",
                            "title": "Microsoft Certified: Azure Fundamentals",
                            "completed": "Verified on Microsoft Learn",
                            "note": "Foundational Microsoft Azure certification covering cloud concepts, Azure services, Azure workloads, security, privacy, pricing, and support.",
                            "url": "https://learn.microsoft.com/en-us/users/denisprimc/credentials/certification/azure-fundamentals?tab=credentials-tab",
                            "icon_url": "https://learn.microsoft.com/en-us/media/learn/certification/badges/microsoft-certified-fundamentals-badge.svg",
                        },
                        {
                            "type": "Certification",
                            "title": "MCSA: Windows Server 2016",
                            "completed": "Verified on Microsoft Learn",
                            "note": "Microsoft Certified Solutions Associate certification for Windows Server 2016 administration and infrastructure skills.",
                            "url": "https://learn.microsoft.com/en-us/users/denisprimc/credentials/certification-o-/mcsa-windows-server-2016-certification?tab=credentials-tab",
                            "icon_url": "https://learn.microsoft.com/en-us/media/learn/certification/badges/microsoft-certified-associate-badge.svg",
                        },
                        {
                            "type": "Certification",
                            "title": "Microsoft Legacy Certification",
                            "completed": "Verified on Microsoft Learn",
                            "note": "Legacy Microsoft certification credential published on the Microsoft Learn profile.",
                            "url": "https://learn.microsoft.com/en-us/users/denisprimc/credentials/certification-o-/nouid.1519?tab=credentials-tab",
                            "icon_url": "https://learn.microsoft.com/en-us/media/learn/certification/badges/microsoft-certified-general-badge.svg",
                        },
                    ],
                },
                "featured_videos": fetch_latest_videos(limit=3),
                "latest_blog_posts": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED, published_at__lte=timezone.now())[:3],
                "github_projects": fetch_github_projects(limit=6),
                "contact": {
                    "email": "info@denisprimc.com",
                    "coffee_url": "https://buymeacoffee.com/denisprimc",
                    "cta": "Have an IT question or problem? Send me a message — I’m happy to offer some initial advice for free. If you find my help useful, you can optionally buy me a coffee afterwards.",
                    "social_links": [
                        {"label": "YouTube", "url": "https://www.youtube.com/@denisprimc"},
                        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/denis-primc"},
                        {"label": "GitHub", "url": "https://github.com/Dprimc"},
                        {"label": "Buy Me a Coffee", "url": "https://buymeacoffee.com/denisprimc"},
                    ],
                },
            }
        )
        return context


class BlogListView(ListView):
    model = BlogPost
    template_name = "portfolio/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED, published_at__lte=timezone.now())


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "portfolio/blog_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED, published_at__lte=timezone.now())


class PasswordGeneratorView(TemplateView):
    template_name = "portfolio/password_generator.html"


def robots_txt(request):
    content = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Sitemap: https://denisprimc.com/sitemap.xml",
        "",
    ])
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    urls = [
        {"loc": "https://denisprimc.com/it-support-falkirk/", "changefreq": "monthly", "priority": "0.9"},
        {
            "loc": "https://denisprimc.com/",
            "changefreq": "weekly",
            "priority": "1.0",
        },
        {
            "loc": "https://denisprimc.com/blog/",
            "changefreq": "weekly",
            "priority": "0.8",
        },
    ]
    for post in BlogPost.objects.filter(
        status=BlogPost.Status.PUBLISHED,
        published_at__lte=timezone.now(),
    ).only("slug", "updated_at"):
        urls.append(
            {
                "loc": f"https://denisprimc.com{post.get_absolute_url()}",
                "lastmod": post.updated_at.date().isoformat(),
                "changefreq": "monthly",
                "priority": "0.7",
            }
        )

    entries = []
    for url in urls:
        lines = ["  <url>", f"    <loc>{escape(url['loc'])}</loc>"]
        if url.get("lastmod"):
            lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        lines.extend(
            [
                f"    <changefreq>{url['changefreq']}</changefreq>",
                f"    <priority>{url['priority']}</priority>",
                "  </url>",
            ]
        )
        entries.append("\n".join(lines))

    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
""".format("\n".join(entries))
    return HttpResponse(content, content_type="application/xml")
