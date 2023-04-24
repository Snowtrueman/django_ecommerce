from django import forms
from .models import Reviews


class ReviewForm(forms.ModelForm):
    email = forms.CharField(max_length=60)

    class Meta:
        model = Reviews
        fields = ["text", "email"]
