from django import forms

# iterable
strategy_choices =(
    ("1", "MACD + RENKO"),
    ("2", "Harami and Engulfing Reversal")
)

# creating a form
class TradingForm(forms.Form):
    trading_field = forms.ChoiceField(choices = strategy_choices)
    trading_amount = forms.DecimalField(label = 'Trading Amount' , widget = forms.TextInput(attrs={
                "placeholder" : "0.00",
                "class" : "form-control"
        }))

class StockForm(forms.Form):
        nse_code = forms.CharField(label ='NSE Code', widget = forms.TextInput(attrs={
                "placeholder" : "SYMBOL",
                "class" : "form-control"
        }))
        quantity = forms.DecimalField(label = 'Quantity', widget = forms.TextInput(attrs={
                "placeholder" : "0",
                "class" : "form-control"
        }))
        limit_price = forms.DecimalField(label = 'Limit Price', initial=0.00, widget = forms.TextInput(attrs={
                "placeholder" : "0.00",
                "class" : "form-control"
        }))

class DummyForm(forms.Form):
        val = forms.CharField(widget = forms.HiddenInput(), required = False)