from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns("",
    url(r"^$", "mud.views.home", name="home"),
    url(r"^game$", "mud.views.game", name="game"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^accounts/login/$", "django.contrib.auth.views.login", {"template_name": "mud/login.html"})
)
