from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns("",
    url(r"^$", "mud.views.home", name="home"),
    url(r"^player_login$", "mud.views.player_login", name="player_login"),
    url(r"^game/submit_command$", "mud.views.submit_command", name="ajax_submit_command"),
    url(r"^game/get_messages", "mud.views.get_messages", name="ajax_get_messages"),
    url(r"^game/(\d{1,10})$", "mud.views.game", name="game"),

    url(r"^admin/", include(admin.site.urls)),
    url(r"^accounts/login/$", "django.contrib.auth.views.login", {"template_name": "mud/login.html"})
)
