from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from taskList import views
from django.conf.urls import *



urlpatterns = [
    url(r'^$', views.home, name ='home'),
    url(r'^add-task$', views.add_task, name='add'),
    # Parses number from URL and uses it as the item_id argument to the action
    #url(r'^follow/(?P<user>\w+)$', views.follow, name='follow'),
    #url(r'^add-follow/(?P<user>\w+)$', views.add_follow, name='add_follow'),
    #url(r'^un-follow/(?P<user>\w+)$', views.un_follow, name='un_follow'),

    # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name':'taskList/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name ='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^user/(?P<user>\d+)/$', views.user, name='user'),
    url(r'^user/(?P<user>\d+)/(?P<page>\d+)/$', views.user, name='user_pages'),

    url(r'^task/(?P<task>\d+)/$', views.task, name='task'),
    url(r'^edit_user/(?P<user>\w+)/$', views.edit_user, name='edit_user'),
    url(r'^edit_tasks/(?P<task>\w+)/$', views.edit_tasks, name='edit_tasks'),
    url(r'^task_cat/(?P<task_cat>\w+)/$', views.task_cat, name='task_cat'),
    url(r'^task_cat/(?P<task_cat>\w+)/(?P<page>\d+)/$', views.task_cat, name='task_cat_page'),

    #url(r'^photo/(?P<user>\w+)/$', views.photo, name='photo'),
    #url(r'^edit/(?P<user>\w+)/images/(?P<photo>\w+)', views.photo),
    #url(r'^add-comment/(?P<itemid>\w+)$', views.add_comment, name='comment'),
    #url(r'^get-list-json$', views.get_list_json),



    #not exist user 
    #not to type in some info 
    #check if some info is right


]

