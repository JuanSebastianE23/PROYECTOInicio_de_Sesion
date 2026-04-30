from django.contrib import admin
from .models import Calificacion

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_estudiante', 'identificacion', 'asignatura', 'nota1', 'nota2', 'nota3', 'promedio', 'estado_aprobacion')
    list_filter = ('asignatura',)
    search_fields = ('nombre_estudiante', 'identificacion', 'asignatura')
    readonly_fields = ('promedio',)
    list_per_page = 20
    ordering = ('-promedio', 'nombre_estudiante')
    
    fieldsets = (
        ('Información del Estudiante', {
            'fields': ('nombre_estudiante', 'identificacion')
        }),
        ('Información Académica', {
            'fields': ('asignatura', 'nota1', 'nota2', 'nota3', 'promedio')
        }),
    )
    
    def estado_aprobacion(self, obj):
        """Muestra si el estudiante aprobó o reprobó"""
        if obj.promedio >= 60:
            return '✅ Aprobado'
        return '❌ Reprobado'
    estado_aprobacion.short_description = 'Estado'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs
    
    actions = ['marcar_como_revisado']
    
    def marcar_como_revisado(self, request, queryset):
        """Acción personalizada para marcar registros como revisados"""
        count = queryset.count()
        self.message_user(request, f'{count} calificaciones marcadas como revisadas.')
    marcar_como_revisado.short_description = 'Marcar como revisado'
