from django import forms
from .models import Review, Order
import re
from django.utils import timezone


class ReviewForm(forms.ModelForm):
    """Форма отзыва с ограничением длины текста
    ограничение на уровне браузера и сервера (clean_text)
    """

    MAX_TEXT_LENGTH = 100

    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 100,
                'placeholder': 'Максимум 100 символов'
            }),
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5
            }),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if len(text) > self.MAX_TEXT_LENGTH:
            raise forms.ValidationError(
                f"Отзыв не должен превышать {self.MAX_TEXT_LENGTH} символов."
            )

        return text


class OrderForm(forms.ModelForm):
    """Форма заказа с серверной валидацией"""

    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'address', 'delivery_time', 'comments']
        widgets = {
            'delivery_time': forms.TextInput(
                attrs={'placeholder': 'Например, с 10:00 до 12:00'}
            ),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if len(name) < 2:
            raise forms.ValidationError(
                "Имя должно содержать минимум 2 символа."
            )

        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not re.match(r'^\+?\d{10,15}$', phone):
            raise forms.ValidationError(
                "Введите корректный номер телефона (10–15 цифр)."
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and "@" not in email:
            raise forms.ValidationError(
                "Введите корректный email."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()
        delivery_time = cleaned_data.get("delivery_time")

        if delivery_time:
            if len(delivery_time) < 5:
                raise forms.ValidationError(
                    "Укажите более точное время доставки."
                )

        return cleaned_data
