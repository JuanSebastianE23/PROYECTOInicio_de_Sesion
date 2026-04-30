from django import forms
from .models import Calificacion

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nombre_estudiante', 'identificacion', 'asignatura', 'nota1', 'nota2', 'nota3']
        widgets = {
            'nombre_estudiante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del estudiante'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de identificación'}),
            'asignatura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la asignatura'}),
            'nota1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nota 1', 'step': '0.01', 'min': '0', 'max': '100'}),
            'nota2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nota 2', 'step': '0.01', 'min': '0', 'max': '100'}),
            'nota3': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nota 3', 'step': '0.01', 'min': '0', 'max': '100'}),
        }
        labels = {
            'nombre_estudiante': 'Nombre del Estudiante',
            'identificacion': 'Identificación',
            'asignatura': 'Asignatura',
            'nota1': 'Primera Nota',
            'nota2': 'Segunda Nota',
            'nota3': 'Tercera Nota',
        }
