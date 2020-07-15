from django import forms


class NewTermForm(forms.Form):
    label = forms.CharField(label='Label', max_length=100, widget=forms.TextInput(
        attrs={'class': 'uk-input field field__text-field'}))
    description = forms.CharField(label='Description', max_length=500,
                                  widget=forms.Textarea(attrs={'class': 'uk-textarea field field__text-area'}))
    cross_refs = forms.CharField(label='Cross References', max_length=200,
                                 widget=forms.Textarea(attrs={'class': 'uk-textarea field field__text-area'}))
