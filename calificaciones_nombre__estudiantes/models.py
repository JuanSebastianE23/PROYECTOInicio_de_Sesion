from django.db import models
from decimal import Decimal

class Calificacion(models.Model):
    nombre_estudiante = models.CharField(max_length=150)
    identificacion = models.CharField(max_length=15)
    asignatura = models.CharField(max_length=100)
    nota1 = models.DecimalField(max_digits=5, decimal_places=2)
    nota2 = models.DecimalField(max_digits=5, decimal_places=2)
    nota3 = models.DecimalField(max_digits=5, decimal_places=2)
    promedio = models.DecimalField(max_digits=5, decimal_places=2, editable=False)

    def calcular_promedio(self):
        """Calcula el promedio de las tres notas usando Decimal para precisión"""
        suma = self.nota1 + self.nota2 + self.nota3
        promedio = suma / Decimal('3')
        return promedio.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        """Recalcula el promedio automáticamente antes de guardar"""
        self.promedio = self.calcular_promedio()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_estudiante} - {self.asignatura}"

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
