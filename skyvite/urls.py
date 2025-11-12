from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    # Auth
    path('only-admin-can-create-account/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.signout_view, name='signout'),
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # School Management
    path('welcome-onboard/', views.add_school_view, name='add_school'),
    # path('add-school/', views.add_school_view, name='add_school'),
    path('school/delete/<int:school_id>/', views.delete_school_view, name='delete_school'),
    path('school-detail/', views.school_detail_view, name='school_detail'),
    path('school/update/', views.update_school_ajax, name='update_school_ajax'),
    # Session / Class / Section
    path("student-master/", views.class_section_view, name="class_section"),
    path("delete-session/<int:session_id>/", views.delete_session, name="delete_session"),
    path("delete-class/<int:class_id>/", views.delete_class, name="delete_class"),
    path("delete-section/<int:section_id>/", views.delete_section, name="delete_section"),
    path("ajax/add-session/", views.ajax_add_session, name="ajax_add_session"),
    path("ajax/add-class/", views.ajax_add_class, name="ajax_add_class"),
    path("ajax/add-section/", views.ajax_add_section, name="ajax_add_section"),
    path("ajax/delete-item/", views.ajax_delete_item, name="ajax_delete_item"),
    # Student Management
    path('add-student/', views.add_student_view, name='add_student'),
    path('students/', views.student_list_view, name='student_list'),
    path('view/students/<int:student_id>/', views.view_student_view, name='view_student'),
    path('edit-students/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('students/print/', views.student_list_print, name='student_list_print'),
    path('api/gender-data/', views.gender_data, name='gender_data'),
    # AJAX
    path('get-classes/<int:session_id>/', views.get_classes, name='get_classes'),
    path('get-sections/<int:class_id>/', views.get_sections, name='get_sections'),
    #Certificate
    path('certificate-panel/', views.certificate_panel, name='certificate_panel'),
    path('print-certificate/<int:student_id>/<str:cert_type>/', views.print_certificate, name='print_certificate'),
    #Circulars
    path('manage-circular/', views.manage_circulars, name='manage-circular'),
    # Circulars API
    path("api/circulars/<int:user_id>/", views.circular_list_api, name="circular_list_api"),
    path('admission-form/', views.admission_form_view, name='admission_form'),
    # 🧾 Student Registration (public)
    path("student-registration/", views.enter_school_code, name="enter_school_code"),
    path("student-registration/<str:school_code>/", views.public_student_registration, name="public_student_registration"),

    # Fee Payment Testing
    path('payment/', views.payment_form, name='payment_form'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),


    #Notice
    path("manage-notice/", views.manage_notice, name="manage-notice"),
    

    #Fees
    path("fee-account-master/", views.fee_account_master_list, name="fee_account_master_list"),
    path("fee-account-master/save/", views.fee_account_master_save_ajax, name="add_fee_account"),
    path("fee-account-master/delete/<int:pk>/", views.fee_account_master_delete_ajax, name="delete_fee_account"),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
