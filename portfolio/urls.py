from django.urls import path
from django.views.generic import TemplateView

from .views import BlogDetailView, BlogListView, HomeView, PasswordGeneratorView, robots_txt, sitemap_xml

app_name = "portfolio"

urlpatterns = [
    path("it-support-falkirk/", TemplateView.as_view(template_name="portfolio/it_support_falkirk.html"), name="it_support_falkirk"),
    path("", HomeView.as_view(), name="home"),
    path("blog/", BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
    path("password-generator/", PasswordGeneratorView.as_view(), name="password_generator"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
]
