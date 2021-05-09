from django import forms

# iterable
strategy_choices =(
    ("1", "Strategy One"),
    ("2", "Strategy Two"),
    ("3", "Automatic")
)

# creating a form
class TradingForm(forms.Form):
    trading_field = forms.ChoiceField(choices = strategy_choices)