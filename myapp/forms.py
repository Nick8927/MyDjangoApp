from django import forms
from .models import Review, Order


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
    """форма заказа"""

    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'address', 'delivery_time', 'comments']
        widgets = {
            'delivery_time': forms.TextInput(attrs={'placeholder': 'Например, с 10:00 до 12:00'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
