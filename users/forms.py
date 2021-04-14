from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=data).exists():
            raise ValidationError("Пользователь с таким именем уже"
                                  "существует. Пожалуйста, придумайте"
                                  "другой логин.")
        return data
