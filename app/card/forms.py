from django.forms import ModelForm

from card.models import Card


class AddCardForm(ModelForm):
    class Meta:
        model = Card
        fields = ["name", "text", "instruction"]
