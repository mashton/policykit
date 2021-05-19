import urllib.parse

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path
from policyengine import views as policyviews

from policykit.settings import (DISCORD_CLIENT_ID, METAGOV_ENABLED,
                                REDDIT_CLIENT_ID, SERVER_URL, SLACK_CLIENT_ID)


urlpatterns = [
    path('login/', views.LoginView.as_view(
        template_name='policyadmin/login.html',
        extra_context={
            'server_url': urllib.parse.quote(SERVER_URL, safe=''),
            'slack_client_id': SLACK_CLIENT_ID,
            'reddit_client_id': REDDIT_CLIENT_ID,
            'discord_client_id': DISCORD_CLIENT_ID
        }
    )),
    path('logout/', policyviews.logout, name="logout"),
    path('main/', policyviews.v2),
    path('main/editor/', policyviews.editor),
    path('main/editor_upload/', policyviews.editor_upload),
    path('main/selectrole/', policyviews.selectrole),
    path('main/roleusers/', policyviews.roleusers),
    path('main/roleeditor/', policyviews.roleeditor),
    path('main/selectpolicy/', policyviews.selectpolicy),
    path('main/documenteditor/', policyviews.documenteditor),
    path('main/selectdocument/', policyviews.selectdocument),
    path('main/actions/', policyviews.actions),
    path('main/policyengine/', include('policyengine.urls')),
    path('main/settings/', policyviews.settings_page, name="settings"),
    path('main/logs/', include('django_db_logger.urls', namespace='django_db_logger')),
    path('admin/', admin.site.urls),
    path('slack/', include('integrations.slack.urls')),
    path('reddit/', include('integrations.reddit.urls')),
    path('discord/', include('integrations.discord.urls')),
    path('discourse/', include('integrations.discourse.urls')),
    url(r'^$', policyviews.homepage),
    url('^activity/', include('actstream.urls'))
]

if METAGOV_ENABLED:
    urlpatterns += [path('metagov/', include('integrations.metagov.urls'))]
