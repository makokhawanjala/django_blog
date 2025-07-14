from .models import Comment
from django.conf import settings
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
