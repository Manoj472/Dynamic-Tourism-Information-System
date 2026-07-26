from django.contrib import admin
from .models import (
    Accommodation,
    Activity,
    AttractionImage,
    City,
    ContactInfo,
    ContactMessage,
    Country,
    Culture,
    LocalFood,
    State,
    TouristAttraction,
    Transportation,
    WeatherCache,
)


admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(TouristAttraction)
admin.site.register(AttractionImage)
admin.site.register(Activity)
admin.site.register(Accommodation)
admin.site.register(LocalFood)
admin.site.register(Culture)
admin.site.register(Transportation)
admin.site.register(WeatherCache)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "email", "phone")
    fieldsets = (
        (None, {
            "fields": ("title", "description", "email", "phone", "address")
        }),
        ("Social Links", {
            "fields": (
                "linkedin_url",
                "github_url",
                "discord_url",
                "twitter_url",
                "instagram_url",
                "facebook_url",
            )
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "newsletter", "created_at")
    list_filter = ("newsletter", "created_at")
    search_fields = ("full_name", "email", "subject", "message")
    readonly_fields = ("created_at",)
