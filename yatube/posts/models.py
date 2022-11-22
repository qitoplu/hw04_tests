from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата'
                                    'публикации')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = ('Посты')
        verbose_name_plural = ('Посты')
        ordering = ['pub_date']


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=200)
    slug = models.SlugField(verbose_name='Слаг', unique=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = ('Группы')
        verbose_name_plural = ('Группы')

    def __str__(self):
        return self.title
