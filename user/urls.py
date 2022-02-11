
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('', views.dashboard, name="Dashboard"),
    path('profile', views.profile, name="Profile"),
    path('profile/change-password', views.change_password, name="ChangePassword"),
    path('profile/edit-profile', views.edit_profile, name="EditProfile"),
    path('contact', views.contact, name="Contact"),
    path('files', views.files, name="Files"),
    path('files/upload', views.upload, name="Upload"),
    path('files/enc_upload', views.enc_upload, name="EncUpload"),
    path('files/download', views.download, name="Download"),
    path('files/delete', views.delete, name="Delete"),
    path('files/dec_download', views.dec_download, name="DecDownload"),
    path('plan', views.plan, name="Plan"),
    path('plan/checkout/<str:plan>', views.checkout, name="Checkout"),
    path('callback/<str:plan>', views.callback, name="Callback"),
    path('files/forget-key/<str:filename>', views.forget_key, name="ForgetKey"),
]