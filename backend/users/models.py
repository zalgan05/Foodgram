from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):

    email = models.EmailField(
        unique=True,
    )
    is_subscribed = models.BooleanField(
        default=False,
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email


class Follow(models.Model):
    """Модель управления подписками на пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписки'
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('following')),
                name='check_myself',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
