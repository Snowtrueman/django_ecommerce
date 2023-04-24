from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Settings
import re


class RegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=50, label="Имя",
                           widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Андрей"}))
    surname = forms.CharField(max_length=50, label="Фамилия",
                              widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Афанасьев"}))
    email = forms.EmailField(label="E-mail",
                             widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "andrey@yandex.ru"}))
    phone = forms.CharField(max_length=15, label="Телефон",
                            widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "+7999999999"}))
    city = forms.CharField(max_length=50, label="Город",
                           widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Москва"}))

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "name", "surname", "email", "phone", "city"]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-input"
        self.fields["username"].widget.attrs["placeholder"] = "andrey2023"
        self.fields["username"].label = "Логин"
        self.fields["password1"].widget.attrs["class"] = "form-input"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].widget.attrs["class"] = "form-input"
        self.fields["password2"].label = "Подтверждение пароля"

    @staticmethod
    def is_alpha_or_error(string):
        if not all(char.isalpha() or char in [" ", "-"] for char in string):
            raise forms.ValidationError("Допустимы только буквы, симовол пробела и тире.")
        return string

    def clean_name(self):
        return self.is_alpha_or_error(self.cleaned_data.get("name").strip())

    def clean_surname(self):
        return self.is_alpha_or_error(self.cleaned_data.get("surname").strip())

    def clean_city(self):
        return self.is_alpha_or_error(self.cleaned_data.get("city").strip())

    def clean_phone(self):
        pattern = re.compile(r"^(?:\+7)?9(?:\d{9})$")
        phone_with_code = self.cleaned_data.get("phone").strip()
        if pattern.match(phone_with_code) and len(phone_with_code[2:]) == 10:
            return phone_with_code[2:]
        else:
            raise forms.ValidationError("Введите телефон в формате +7хххххххххх.")


class UpdateProfileForm(forms.Form):
    avatar = forms.ImageField(required=False, label="Аватар")
    full_name = forms.CharField(max_length=50, label="Имя")
    phone = forms.CharField(max_length=12, label="Телефон")
    email = forms.EmailField(label="E-mail")
    password1 = forms.CharField(required=False, label="Пароль")
    password2 = forms.CharField(required=False, label="Подтверждение пароля")

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name").strip()
        if not all(char.isalpha() or char.isspace() for char in full_name):
            raise forms.ValidationError("Допустимы только буквы и симовол пробела.")
        try:
            first_name, second_name = full_name.split(" ")
        except ValueError:
            raise forms.ValidationError("Имя и фамилия должны быть разделены одним символом пробела.")
        return full_name

    def clean_phone(self):
        pattern = re.compile(r"^(?:\+7)?9(?:\d{9})$")
        phone_with_code = self.cleaned_data.get("phone").strip()
        if pattern.match(phone_with_code) and len(phone_with_code[2:]) == 10:
            return phone_with_code[2:]
        else:
            raise forms.ValidationError("Введите телефон в формате +7хххххххххх.")


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ["general_phone", "general_email", "general_address", "facebook_url", "twitter_url",
                  "linkedin_url", "pinterest_url", "product_cache_time", "ordinary_delivery_price",
                  "express_delivery_price", "delivery_sum_to_free"]

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields["general_phone"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.general_phone }}"}
        self.fields["general_phone"].label = "Общий телефон"
        self.fields["general_email"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.general_email }}"}
        self.fields["general_email"].label = "Общий адрес электронной почты"
        self.fields["general_address"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.general_address }}", "rows": "5", "resize": "none"}
        self.fields["general_address"].label = "Общий адрес местонахождения"
        self.fields["facebook_url"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.facebook_url }}"}
        self.fields["facebook_url"].label = "Страница в Facebook"
        self.fields["twitter_url"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.twitter_url }}"}
        self.fields["twitter_url"].label = "Страница в Twitter"
        self.fields["linkedin_url"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.linkedin_url }}"}
        self.fields["linkedin_url"].label = "Страница в LinkedIn"
        self.fields["pinterest_url"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.pinterest_url }}"}
        self.fields["pinterest_url"].label = "Страница в Pinterest"
        self.fields["product_cache_time"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.product_cache_time }}"}
        self.fields["product_cache_time"].label = "Время кеширования карточки товара (с)"
        self.fields["ordinary_delivery_price"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.ordinary_delivery_price }}"}
        self.fields["ordinary_delivery_price"].label = "Стоимость обычной доставки"
        self.fields["express_delivery_price"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.express_delivery_price }}"}
        self.fields["express_delivery_price"].label = "Стоимость экспресс-доставки"
        self.fields["delivery_sum_to_free"].widget.attrs = \
            {"class": "form-input", "value": "{{ form.delivery_sum_to_free }}"}
        self.fields["delivery_sum_to_free"].label = "Порог бесплатной доставки"
