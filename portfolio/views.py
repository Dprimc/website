import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.views.generic import TemplateView

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
        thumb_url = (
            thumbnails[-1].get("url")
            if thumbnails
            else _thumbnail_from_id(video_id)
        )

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
            "description": repo.get("description")
            or "No description provided yet.",
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
                    "title": "IT Foundations Specialist for Growing Businesses",
                    "summary": (
                        "I help startups and small businesses build a rock-solid IT foundation—fast, safe, and ready to scale. "
                        "From the first domain name to hybrid-cloud infrastructure, I turn ad‑hoc tech into a strategic asset."
                    ),
                    "focus_title": "How I Support New & Growing Teams",
                    "focus_points": [
                        "Assess current tools and design a future-proof IT blueprint aligned to business goals.",
                        "Deploy secure Microsoft 365, networking, and server platforms that scale without surprises.",
                        "Coach internal stakeholders so day-to-day operations and growth plans stay in sync."
                    ],
                    "cta_links": [
                        {"label": "Plan Your IT Foundations", "url": "#contact"},
                        {"label": "Explore Transformation Wins", "url": "#experience"},
                    ],
                },
                "skills": [
                    {
                        "category": "Cloud Workplace & Collaboration",
                        "items": [
                            "Microsoft 365 tenant build-outs with Azure AD & Intune",
                            "SharePoint, Teams, and OneDrive information architecture",
                            "Hybrid identity & conditional access policy design",
                            "Cross-Platform Systems Expertise (Microsoft, Apple & Linux)",
                        ],
                    },
                    {
                        "category": "Infrastructure & Continuity",
                        "items": [
                            "Windows Server 2016/2019/2022 & Hyper-V Clusters",
                            "Cluster-Aware Updating (CAU) & WSUS patch programs",
                            "Resilient network architecture and performance optimisation",
                            "Business continuity and disaster recovery planning with tested runbooks",
                        ],
                    },
                    {
                        "category": "Security & Operations",
                        "items": [
                            "Managed email security platforms with phishing defense & threat analytics",
                            "Edge security architectures with SD-WAN and zero-trust segmentation",
                            "Identity governance and privileged access controls",
                            "PowerShell and Bash automation supporting ITSM runbooks",
                        ],
                    },
                ],
                "experience": {
                    "overview": [
                        (
                            "I’ve spent over fifteen years guiding organisations through rapid change, and the last six inside "
                            "managed service providers where small-business growth lives or dies by its IT decisions."
                        ),
                        (
                            "My speciality is taking a patchwork of accounts, devices, and ad-hoc fixes and turning them into a "
                            "documented, secure, and scalable foundation. I partner with founders and operations leaders to map out "
                            "everything from identity to networking so expansion plans aren’t blocked by technology."
                        ),
                        (
                            "I bring the same rigour I used relocating datacentres and migrating hundreds of users to every new engagement—"
                            "clear communication, change control, and training so teams feel confident adopting new systems."
                        ),
                    ],
                    "focus": [
                        "Designing foundation blueprints covering connectivity, identity, collaboration, and security.",
                        "Executing phased migrations—from legacy servers to cloud-first platforms—without disrupting operations.",
                        "Embedding backup, monitoring, and patch routines that protect the business from the start.",
                        "Coaching internal teams so they can own day-to-day operations with confidence.",
                    ],
                    "wins": [
                        "Standardised MSP onboarding kits that took new businesses from chaos to full documentation in weeks.",
                        "Migrated ageing VMware footprints into Hyper-V clusters with CAU and WSUS-managed patching.",
                        "Rolled out Microsoft 365 security baselines, SharePoint intranets, and SaaS backup coverage for hybrid teams.",
                        "Built runbooks and training that empowered internal staff to support growth post-engagement.",
                    ],
                },
                "projects": [
                    {
                        "name": "IT Foundations Jumpstart",
                        "summary": (
                            "A four-week roadmap that audits your current stack, maps business goals, and delivers a phased build-out "
                            "plan for identity, devices, and collaboration."
                        ),
                    },
                    {
                        "name": "Modern Workplace Rollouts",
                        "summary": (
                            "End-to-end Microsoft 365, Intune, and SharePoint deployments with governance, security baselines, "
                            "and user enablement tailored for growing teams."
                        ),
                    },
                    {
                        "name": "Resilience & Continuity Programs",
                        "summary": (
                            "Hyper-V clustering, backup, and Fortinet-secured networking engineered to keep critical services online "
                            "and recoverable as your business scales."
                        ),
                    },
                ],
                "featured_videos": fetch_latest_videos(),
                "github_projects": fetch_github_projects(),
                "contact": {
                    "email": "denis@denisprimc.com",
                    "cta": (
                        "Ready to lay the right IT foundations for your business? "
                        "Reach out for a discovery call and I’ll map the next steps with you."
                    ),
                    "social_links": [
                        {
                            "label": "LinkedIn",
                            "url": "https://www.linkedin.com/in/denisprimc",
                        },
                        {
                            "label": "GitHub",
                            "url": "https://github.com/Dprimc",
                        },
                        {
                            "label": "YouTube",
                            "url": "https://www.youtube.com/@denisprimc",
                        },
                    ],
                },
            }
        )
        return context
