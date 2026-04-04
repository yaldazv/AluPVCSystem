from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Име")
    email = models.EmailField(verbose_name="Имейл")
    subject = models.CharField(max_length=150, verbose_name="Относно")
    message = models.TextField(verbose_name="Съобщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Изпратено на")
    is_read = models.BooleanField(default=False, verbose_name="Прочетено")

    def __str__(self):
        return f"{self.subject} от {self.name}"

    class Meta:
        verbose_name = "Съобщение"
        verbose_name_plural = "Съобщения (Контакти)"
        ordering = ['-created_at']
