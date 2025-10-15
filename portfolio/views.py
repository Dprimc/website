from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "hero": {
                    "name": "Denis Primc",
                    "title": "Senior Support Analyst · MSP Specialist · Content Creator",
                    "summary": (
                        "For 15+ years I've supported users, infrastructure, and cloud services across MSPs. "
                        "I thrive on keeping customers productive, leading complex migrations, and sharing "
                        "what I learn with the wider community."
                    ),
                    "focus_title": "Where I Create Impact",
                    "focus_points": [
                        "Deliver 1st to 3rd line support with a relentless focus on service quality.",
                        "Plan and execute client onboarding, server migrations, and security rollouts.",
                        "Translate technical change into clear guidance for clients and teammates.",
                    ],
                    "cta_links": [
                        {"label": "View Experience", "url": "#experience"},
                        {
                            "label": "Watch YouTube Channel",
                            "url": "https://www.youtube.com/@denisprimc",
                        },
                    ],
                },
                "skills": [
                    {
                        "category": "MSP Platforms",
                        "items": [
                            "Datto RMM, Autotask, ITGlue",
                            "N-able N-central, Passportal, Secret Server",
                            "Addigy RMM for Apple fleets",
                            "Process documentation & runbooks",
                        ],
                    },
                    {
                        "category": "Backup & Security",
                        "items": [
                            "Cove & Datto Endpoint Backup",
                            "Cloud Ally & Rubrik backup platforms",
                            "Mimecast, AppRiver, SentinelOne, Heimdal",
                            "Fortinet FortiGate edge security & SD-WAN",
                            "CyberCNS vulnerability management",
                        ],
                    },
                    {
                        "category": "Platforms & Infrastructure",
                        "items": [
                            "Azure AD, Intune, SharePoint, Exchange Online",
                            "Windows Server 2016/2019/2022 & Hyper-V",
                            "VMware, VirtualBox, Synology NAS/CCTV",
                            "Networking with Meraki, Meraki Go, UniFi",
                        ],
                    },
                    {
                        "category": "Troubleshooting & Tools",
                        "items": [
                            "Advanced endpoint support across Windows, macOS, Linux",
                            "Domain management (MX, SPF, DKIM, TXT)",
                            "PowerShell & Bash scripting automation",
                            "Ivanti & remote workforce enablement playbooks",
                        ],
                    },
                ],
                "experience": {
                    "overview": [
                        (
                            "I’m a hands-on support analyst with more than fifteen years in IT and the last six immersed "
                            "in fast-paced MSP environments. From service desk triage to deep-dive root cause analysis, "
                            "I keep users productive while protecting uptime across mixed Windows, macOS, and Linux estates."
                        ),
                        (
                            "Day to day I own the full support lifecycle—onboarding new organisations, documenting their "
                            "infrastructure, deploying RMM tooling, and guiding them through migrations to modern platforms. "
                            "Server upgrades, Azure AD hardening, Intune rollout, and collaboration stack tuning are all part "
                            "of the toolkit."
                        ),
                        (
                            "Earlier in my career I led a datacentre relocation and domain migration for hundreds of users. "
                            "That experience cemented my focus on communication, change control, and making complex transitions "
                            "feel simple for the people relying on them."
                        ),
                    ],
                    "focus": [
                        "Delivering multi-tier support that blends speed with thorough root-cause resolutions.",
                        "Designing and executing migration runbooks for servers, email, and collaboration platforms.",
                        "Hardening tenant security with conditional access, backup policies, and endpoint protection.",
                        "Coaching junior technicians and translating technical change into plain-language updates.",
                    ],
                    "wins": [
                        "Standardised client onboarding to cut time-to-value for new MSP customers.",
                        "Migrated legacy VMware workloads into resilient Hyper-V clusters with minimal downtime.",
                        "Rolled out O365 security baselines, SharePoint rearchitecture, and SaaS backup coverage.",
                        "Maintained 3rd-line escalation ownership for complex networking, identity, and endpoint issues.",
                    ],
                },
                "projects": [
                    {
                        "name": "Client Onboarding Accelerator",
                        "summary": (
                            "Designed repeatable onboarding playbooks covering discovery, documentation, "
                            "and RMM deployment to bring new MSP clients online smoothly."
                        ),
                    },
                    {
                        "name": "Hybrid Infrastructure Migrations",
                        "summary": (
                            "Delivered VMware-to-Hyper-V transitions, Exchange 2016 to Microsoft 365 migrations, "
                            "and Azure AD security implementations with minimal downtime."
                        ),
                    },
                    {
                        "name": "Remote Workforce Enablement",
                        "summary": (
                            "Implemented remote desktop services, VPN access, and collaboration tooling "
                            "to keep hybrid teams productive and secure."
                        ),
                    },
                ],
                "skill_assessment_summary": "IKM TechChek score: 83 · 78th percentile overall.",
                "skill_assessment": [
                    {"name": "Devices & Printers", "score": 90, "level": "strong"},
                    {"name": "Office 365 Continuity & Availability", "score": 88, "level": "strong"},
                    {"name": "Windows 10 Security", "score": 86, "level": "strong"},
                    {"name": "Wireless Networking", "score": 84, "level": "strong"},
                    {"name": "File Systems & Management", "score": 82, "level": "strong"},
                    {"name": "Email Concepts & Client Support", "score": 80, "level": "strong"},
                ],
                "featured_videos": [
                    {
                        "title": "Azure AD Conditional Access Explained",
                        "url": "https://www.youtube.com/watch?v=wxXu5NXdUzw",
                    },
                    {
                        "title": "Datto RMM Tips for MSP Engineers",
                        "url": "https://www.youtube.com/watch?v=bURtVxifUUo",
                    },
                    {
                        "title": "Deploying Intune Endpoint Security Policies",
                        "url": "https://www.youtube.com/watch?v=urBEXzYkD7A",
                    },
                ],
                "contact": {
                    "email": "denis@denisprimc.com",
                    "cta": "Need help with MSP tooling, migrations, or endpoint strategy? Let’s talk.",
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
