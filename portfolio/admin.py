from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "published_at", "updated_at")
    list_filter = ("status", "category", "published_at")
    search_fields = ("title", "summary", "body", "category")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body")}),
        ("Publishing", {"fields": ("category", "status", "published_at")}),
    )
