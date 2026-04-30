from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
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

    def clean_nota1(self):
        nota = self.cleaned_data.get('nota1')
        if nota is not None and (nota < 0 or nota > 100):
            raise forms.ValidationError('La nota debe estar entre 0 y 100')
        return nota

    def clean_nota2(self):
        nota = self.cleaned_data.get('nota2')
        if nota is not None and (nota < 0 or nota > 100):
            raise forms.ValidationError('La nota debe estar entre 0 y 100')
        return nota

    def clean_nota3(self):
        nota = self.cleaned_data.get('nota3')
        if nota is not None and (nota < 0 or nota > 100):
            raise forms.ValidationError('La nota debe estar entre 0 y 100')
        return nota

    def clean_nombre_estudiante(self):
        nombre = self.cleaned_data.get('nombre_estudiante')
        if nombre and len(nombre.strip()) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        return nombre.strip()

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion and len(identificacion.strip()) < 3:
            raise forms.ValidationError('La identificación debe tener al menos 3 caracteres')
        return identificacion.strip()

    def clean_asignatura(self):
        asignatura = self.cleaned_data.get('asignatura')
        if asignatura and len(asignatura.strip()) < 3:
            raise forms.ValidationError('La asignatura debe tener al menos 3 caracteres')
        return asignatura.strip()
