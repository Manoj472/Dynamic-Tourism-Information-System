"""URL configuration for trailsite project."""

from django.contrib import admin
from django.urls import path
from newapp import views

urlpatterns = [
    path("admin/",               admin.site.urls),

    # Pages
    path("",                     views.home,               name="home"),
    path("beaches/",             views.beaches,            name="beaches"),
    path("parks/",               views.parks,              name="parks"),
    path("beaches/rk-beach/",    views.rkbeach,            name="rkbeach"),
    path("parks/vuda-park/",     views.vudapark,           name="vudapark"),
    path("activity/<slug:slug>/",views.activity_detail,    name="activity_detail"),

    # Location detection — JS calls this first
    path("detect-location/",     views.detect_location,    name="detect_location"),

    # AJAX data endpoints (DB-first → Geoapify fallback)
    path("api/attractions/",     views.api_attractions,    name="api_attractions"),
    path("api/accommodations/",  views.api_accommodations, name="api_accommodations"),
    path("api/activities/",      views.api_activities,     name="api_activities"),
    path("api/city-description/",views.api_city_description,  name="api_city_description"),
]
