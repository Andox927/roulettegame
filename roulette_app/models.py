from django.db import models


class RouletteConfig(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Prize(models.Model):
    config = models.ForeignKey(RouletteConfig, related_name='prizes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    probability = models.FloatField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"{self.name} ({self.probability})"


class DrawHistory(models.Model):
    config = models.ForeignKey(RouletteConfig, related_name='draws', on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)
    prize_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.nickname} - {self.prize_name}"
