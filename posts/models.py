from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, unique=True,
                             verbose_name='Название группы')
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, verbose_name='Создатель группы', on_delete=models.SET_NULL, blank=True,
                              null=True)
    
    class Meta:
        ordering = ('title',)

    def get_url(self):
        return reverse('group_posts', args=[self.slug])

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=50, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите свой пост здесь')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу (не обязательно)')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, blank=False, null=False,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост с комментариями')
    author = models.ForeignKey(User, blank=False, null=False,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата публикации')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Тот, на кого подписаны')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Подписчик')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True,
                           verbose_name='Описание профиля')
    image = models.ImageField(upload_to='users/', blank=True,
                              null=True, verbose_name='Аватар')


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_likes')
    post = models.ForeignKey(Post, blank=False, null=False,
                             on_delete=models.CASCADE,
                             related_name='likes')
 
