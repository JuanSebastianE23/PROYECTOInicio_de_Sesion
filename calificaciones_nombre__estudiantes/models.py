from django.db import models
from decimal import Decimal

class Calificacion(models.Model):
    """
    Modelo para almacenar calificaciones de estudiantes.
    
    Campos:
        - nombre_estudiante: Nombre completo del estudiante (máx 150 caracteres)
        - identificacion: Número de identificación único (máx 15 caracteres)
        - asignatura: Nombre de la asignatura (máx 100 caracteres)
        - nota1, nota2, nota3: Notas individuales (Decimal 0-100)
        - promedio: Promedio calculado automáticamente (no editable)
    
    El promedio se calcula automáticamente al guardar usando Decimal
    para mayor precisión en operaciones matemáticas.
    """
    nombre_estudiante = models.CharField(max_length=150, verbose_name="Nombre del Estudiante")
    identificacion = models.CharField(max_length=15, verbose_name="Identificación")
    asignatura = models.CharField(max_length=100, verbose_name="Asignatura")
    nota1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota 1")
    nota2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota 2")
    nota3 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota 3")
    promedio = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name="Promedio")

    def calcular_promedio(self):
        """
        Calcula el promedio de las tres notas usando Decimal para precisión.
        
        Returns:
            Decimal: Promedio redondeado a 2 decimales
        
        Example:
            >>> cal = Calificacion(nota1=85.50, nota2=90.00, nota3=88.25)
            >>> cal.calcular_promedio()
            Decimal('87.92')
        """
        suma = self.nota1 + self.nota2 + self.nota3
        promedio = suma / Decimal('3')
        return promedio.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        """
        Recalcula el promedio automáticamente antes de guardar.
        
        Este método se ejecuta tanto al crear como al actualizar,
        garantizando que el promedio siempre esté sincronizado con las notas.
        """
        self.promedio = self.calcular_promedio()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_estudiante} - {self.asignatura}"

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
