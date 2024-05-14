from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home'),
    path('index/', views.index, name='index'),
    path('error/', views.unauthorized_request, name='unauthorized_request'),
    path('post/process/', views.post_process, name='post_process'),
    path('post/process/app/', views.post_process_app, name='post_process_app'),
    
    path('delete_post_process/', views.delete_post_process, name='delete_post_process'),
    path('delete_post_process/app/', views.delete_post_process_app, name='delete_post_process_app'),
    
    path('post/', views.post, name='post'),
    path('post/<int:content_id>/', views.display_post, name='display_post'),
    path('signup/', views.signup, name='signup'),
    path('signup/process/', views.signup_process, name='signup_process'),
    path('login/', views.login_page, name='login_page'),

    path('login_process/', views.login_process, name='login_process'),
    path('login_process/app/', views.login_process_app, name='login_process_app'),
    
    path('logout_process/', views.logout_process, name='logout_process'),
    
    path('mypage/', views.my_page, name='my_page'),
    path('viewhistory/', views.view_history, name='view_history'),
    path('viewhistory/app/', views.get_view_history_app, name='view_history_app'),
    path('postedcontent/', views.posted_post, name='posted_content'),
    path('postedcontent/app/', views.get_my_post, name='get_my_post'),
    path('changepassword/', views.change_password, name='change_password'),
    path('changepassword/process/', views.change_password_process, name='change_password_process'),
    path('changepassword/success/', views.change_password_success, name='change_password_success'),
    path('search/', views.search, name='search'),
    path('user/<int:owner_user_id>/', views.user_page, name='user_page'),
    
    path('view_count_doubleplus/', views.view_count_doubleplus, name='view_count_doubleplus'),
    path('view_count_doubleplus/app/', views.view_count_doubleplus_app, name='view_count_doubleplus_app'),
    
    path('review_post/', views.review_post, name='review_post'),
    path('review_post/app/', views.review_post_app, name='review_post_app'),
    path('search_process_app/', views.search_process_app, name='search_process_app'),
    path('get_discussion_data/', views.get_discussion_data, name='get_discussion_data'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('add_comment/app/', views.add_comment_app, name='add_comment_app'),
    path('changeuserinfo/', views.change_user_info_page, name='change_user_info_page'),
    
    path('change_user_info_process/', views.change_user_info_process, name='change_user_info_process'),
    path('change_user_info_process/app/', views.change_user_info_process_app, name='change_user_info_process_app'),
    
    path('report/', views.report_page, name='report_page'),
    path('report_process/', views.report_process, name='report_process'),
    path('report_process/app/', views.report_process_app, name='report_process_app'),
    
    path('get_user_data_process/', views.get_user_data_process, name='get_user_data_process'),
    
    path('user_follow_process/', views.user_follow, name='user_follow'),
    path('user_follow_process/app/', views.user_follow_app, name='user_follow_app'),
    
    path('deleteaccount/', views.delete_account_page, name='delete_account_page'),
    path('deleteaccount/process/', views.delete_user_process, name='delete_user_process'),
    
    path('test/', views.test, name='test'),
    
]