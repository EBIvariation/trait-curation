from django import forms


class NewTermForm(forms.Form):
    label = forms.CharField(label='Label', max_length=100, widget=forms.TextInput(
        attrs={'class': 'uk-input field field__text-field field__text-field--large'}))
    description = forms.CharField(label='Description', max_length=500,
                                  widget=forms.Textarea(attrs={'class': 'uk-textarea field field__text-area'}))
    cross_refs = forms.CharField(label='Cross References', max_length=200,
                                 widget=forms.Textarea(attrs={'class': 'uk-textarea field field__text-area'}))


class GitHubSubmissionForm(forms.Form):
    repo = forms.CharField(label="GitHub Repository", initial="joj0s/django-notes-app",
                           widget=forms.TextInput(attrs={'class': 'uk-input field field__text-field'}))
    title = forms.CharField(label="Issue Title", widget=forms.TextInput(
        attrs={'class': 'uk-input field field__text-field field__text-field--large'}))
    body = forms.CharField(label="Issue Body", widget=forms.Textarea(
        attrs={'class': 'uk-textarea field field__text-area'}))
