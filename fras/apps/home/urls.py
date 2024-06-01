from django.urls import path
from apps.home import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
app_name = 'user'

urlpatterns = [

    # The home page
    path('', views.index, name='user_home'),
    path('user_register/', views.user_register, name='user_register'),
    path('create_one/', views.create_one, name='create_one'),
    path('user_register_attendance/<int:id>/', views.user_register_attendance, name='user_register_attendance'),
    path('camera_feed/',views.camera_feed, name='camera_feed'),
    path('get_id/',views.get_id, name='get_id'),
    path('train_data/',views.train_data, name='train_data'),
    path('In_cam/',views.In_cam, name='In_cam'),
    path('Out_cam/',views.Out_cam, name='Out_cam'),
    path('report/',views.report, name='report'),
    path('User_report/<int:id>/',views.User_report, name='User_report'),
    path('calender/', views.calender, name='calender'),
    path('IN_Temp/',views.IN_Temp, name='IN_Temp'),
    path('Out_Temp/',views.Out_Temp, name='Out_Temp'),
    path('attendance_report/',views.attendance_report, name='attendance_report'),
    path('get_attendance_events/', views.get_attendance_events, name='get_attendance_events'),
    path('api/employees', views.fetch_employees, name='fetch_employees'),
    path('api/attendance/', views.attendance_view, name='attendance_view'),
    path('api/employee-details', views.check_employee_presence, name='employee_details'),
    path('api/eventdata', views.calender_event_data, name='eventdata'),
    path('unknow_view',views.unknown_view, name='unknow_view'),
    path('daily_attendance_page/',views.daily_attendance_page, name='daily_attendance_page'),
    path('api/check_daily_employee_presence', views.check_daily_employee_presence, name='check_daily_employee_presence'),
    path('accept_unknown/<int:id>/', views.accept_unknown, name='accept_unknown'),
    path('reject_unknown/<int:id>/', views.reject_unknown, name='reject_unknown'),
    path('api/fetch_daily_employees', views.fetch_daily_employees, name='fetch_daily_employees'),
    path('api/daily_employee_attendance/', views.daily_employee_attendance, name='daily_employee_attendance'),
    path('show_rejected', views.show_rejected, name='show_rejected'),
    path('delete_rejected/<int:id>/', views.delete_rejected, name='delete_rejected'),
    path('delete_selected_unknowns/', views.delete_selected_unknowns, name='delete_selected_unknowns'),
    path('delete_selected_rejects/', views.delete_selected_rejects, name='delete_selected_rejects'),
    path('generate_report/',views.generate_report, name='generate_report'),
    # path('chart/attendance/', views.daily_attendance_view, name='attendance_view'),
    
 ]

urlpatterns += staticfiles_urlpatterns()

    