from django.forms import ModelForm

from .models import Comment, Post, Group, User, Profile


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'group', 'text', 'image')
        labels = {'group': 'Выберите группу', 'text': 'Текст поста',
                  'image': 'Загрузите изображение', 'title': 'Заголовок'}

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ('title','slug','description')
        labels = {'title': 'Название группы', 'slug': 'Адрес группы', 'description': 'Описание' }


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('image', 'bio')
        labels = {'image': 'Загрузите аватар', 'bio': 'Напишите о себе',}
