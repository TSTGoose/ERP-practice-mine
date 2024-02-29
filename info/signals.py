from registration.signals import user_registered, user_activated
from info.models import School
from info.forms import CustomUserCreationForm
from django.contrib import auth

def user_created(sender, user, request, **kwargs):
    form = CustomUserCreationForm(request.POST)
    print(form.is_valid())
    profile = School(
        user=user, 
        user_pass=(form.data['password1']),
        last_name = (form.data['last_name']), 
        first_name = (form.data['first_name']), 
        second_name = (form.data['second_name']),
        date_of_birth = (form.data['date_of_birth']),
        phone_number = (form.data['phone_number']),
        town = (form.data['town']),
        vk_link = (form.data['vk_link']),
        fio_parent = (form.data['fio_parent']),
        phone_number_parent = (form.data['phone_number_parent']),
        school = (form.data['school']),
        class_number = (form.data['class_number']),
        format = (form.data['format']),
        
    )
    profile.save()
    
    #print(*form.cleaned_data.get("subject"))
    profile.subject.add(*form.cleaned_data.get("subject"))
    profile.subject_dop.add(*form.cleaned_data.get("subject_dop"))
    profile.save()


def login_on_activation(sender, user, request, **kwargs):
    user.backend='django.contrib.auth.backends.ModelBackend'
    auth.login(request,user)


user_activated.connect(login_on_activation)
user_registered.connect(user_created)