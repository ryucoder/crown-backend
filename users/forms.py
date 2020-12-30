from django import forms

from users.models import EmailUser


class EmailUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=255)
    last_name = forms.CharField(required=True, max_length=255)

    class Meta:
        model = EmailUser
        fields = "__all__"
