from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Calificacion

class CalificacionModelTest(TestCase):
    """Tests para el modelo Calificacion"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.calificacion = Calificacion.objects.create(
            nombre_estudiante="Juan Pérez",
            identificacion="123456789",
            asignatura="Matemáticas",
            nota1=Decimal('85.50'),
            nota2=Decimal('90.00'),
            nota3=Decimal('88.25')
        )
    
    def test_calcular_promedio_automatico(self):
        """Test: El promedio se calcula automáticamente al guardar"""
        esperado = Decimal('87.92')
        self.assertEqual(self.calificacion.promedio, esperado)
    
    def test_recalculo_promedio_al_editar(self):
        """Test: El promedio se recalcula al editar notas"""
        self.calificacion.nota1 = Decimal('100.00')
        self.calificacion.nota2 = Decimal('100.00')
        self.calificacion.nota3 = Decimal('100.00')
        self.calificacion.save()
        self.assertEqual(self.calificacion.promedio, Decimal('100.00'))
    
    def test_promedio_con_decimales(self):
        """Test: El promedio maneja correctamente decimales"""
        cal = Calificacion.objects.create(
            nombre_estudiante="María López",
            identificacion="987654321",
            asignatura="Física",
            nota1=Decimal('33.33'),
            nota2=Decimal('33.33'),
            nota3=Decimal('33.34')
        )
        self.assertEqual(cal.promedio, Decimal('33.33'))
    
    def test_promedio_cero(self):
        """Test: El promedio puede ser 0.00"""
        cal = Calificacion.objects.create(
            nombre_estudiante="Pedro Gómez",
            identificacion="111222333",
            asignatura="Química",
            nota1=Decimal('0.00'),
            nota2=Decimal('0.00'),
            nota3=Decimal('0.00')
        )
        self.assertEqual(cal.promedio, Decimal('0.00'))


class PromedioGeneralTest(TestCase):
    """Tests para el cálculo del promedio general"""
    
    def setUp(self):
        """Crear usuario y calificaciones de prueba"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        Calificacion.objects.create(
            nombre_estudiante="Estudiante 1",
            identificacion="001",
            asignatura="Materia A",
            nota1=Decimal('80.00'),
            nota2=Decimal('85.00'),
            nota3=Decimal('90.00')
        )
        Calificacion.objects.create(
            nombre_estudiante="Estudiante 2",
            identificacion="002",
            asignatura="Materia B",
            nota1=Decimal('70.00'),
            nota2=Decimal('75.00'),
            nota3=Decimal('80.00')
        )
    
    def test_promedio_general_calculado(self):
        """Test: El promedio general se calcula correctamente"""
        from django.db.models import Avg
        promedio = Calificacion.objects.all().aggregate(Avg('promedio'))['promedio__avg']
        self.assertIsNotNone(promedio)
        # Promedio de 85.00 y 75.00 = 80.00
        self.assertAlmostEqual(float(promedio), 80.00, places=2)
    
    def test_promedio_general_vista(self):
        """Test: La vista de promedio general funciona"""
        response = self.client.get(reverse('promedio_general'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('promedio_general', response.context)
        self.assertIsNotNone(response.context['promedio_general'])
    
    def test_promedio_general_con_cero(self):
        """Test: El promedio general muestra 0.00 correctamente"""
        Calificacion.objects.all().delete()
        Calificacion.objects.create(
            nombre_estudiante="Estudiante Cero",
            identificacion="000",
            asignatura="Materia C",
            nota1=Decimal('0.00'),
            nota2=Decimal('0.00'),
            nota3=Decimal('0.00')
        )
        response = self.client.get(reverse('listar_calificaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['promedio_general'], Decimal('0.00'))


class CRUDTest(TestCase):
    """Tests para las operaciones CRUD"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_crear_calificacion(self):
        """Test: Crear una nueva calificación"""
        data = {
            'nombre_estudiante': 'Ana García',
            'identificacion': '444555666',
            'asignatura': 'Historia',
            'nota1': '88.50',
            'nota2': '92.00',
            'nota3': '85.75'
        }
        response = self.client.post(reverse('crear_calificacion'), data)
        self.assertEqual(Calificacion.objects.count(), 1)
        cal = Calificacion.objects.first()
        self.assertEqual(cal.nombre_estudiante, 'Ana García')
        self.assertIsNotNone(cal.promedio)
    
    def test_listar_calificaciones(self):
        """Test: Listar calificaciones"""
        Calificacion.objects.create(
            nombre_estudiante="Test Student",
            identificacion="999",
            asignatura="Test Subject",
            nota1=Decimal('50.00'),
            nota2=Decimal('60.00'),
            nota3=Decimal('70.00')
        )
        response = self.client.get(reverse('listar_calificaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['calificaciones']), 1)
    
    def test_editar_calificacion(self):
        """Test: Editar una calificación existente"""
        cal = Calificacion.objects.create(
            nombre_estudiante="Original Name",
            identificacion="777",
            asignatura="Original Subject",
            nota1=Decimal('50.00'),
            nota2=Decimal('50.00'),
            nota3=Decimal('50.00')
        )
        data = {
            'nombre_estudiante': 'Updated Name',
            'identificacion': '777',
            'asignatura': 'Updated Subject',
            'nota1': '80.00',
            'nota2': '85.00',
            'nota3': '90.00'
        }
        response = self.client.post(reverse('editar_calificacion', args=[cal.pk]), data)
        cal.refresh_from_db()
        self.assertEqual(cal.nombre_estudiante, 'Updated Name')
        self.assertEqual(cal.promedio, Decimal('85.00'))
    
    def test_eliminar_calificacion(self):
        """Test: Eliminar una calificación"""
        cal = Calificacion.objects.create(
            nombre_estudiante="To Delete",
            identificacion="888",
            asignatura="Delete Subject",
            nota1=Decimal('60.00'),
            nota2=Decimal('60.00'),
            nota3=Decimal('60.00')
        )
        response = self.client.post(reverse('eliminar_calificacion', args=[cal.pk]))
        self.assertEqual(Calificacion.objects.count(), 0)


class LoginProtectionTest(TestCase):
    """Tests para protección de login"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
    
    def test_listar_requiere_login(self):
        """Test: Listar calificaciones requiere login"""
        response = self.client.get(reverse('listar_calificaciones'))
        self.assertEqual(response.status_code, 302)  # Redirect
        # Verifica que redirige a login (puede ser / o /login dependiendo de settings)
        self.assertTrue(response.url.startswith('/') or 'login' in response.url)
    
    def test_crear_requiere_login(self):
        """Test: Crear calificación requiere login"""
        response = self.client.get(reverse('crear_calificacion'))
        self.assertEqual(response.status_code, 302)
    
    def test_promedio_general_requiere_login(self):
        """Test: Ver promedio general requiere login"""
        response = self.client.get(reverse('promedio_general'))
        self.assertEqual(response.status_code, 302)
    
    def test_acceso_con_login(self):
        """Test: Con login se puede acceder"""
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('listar_calificaciones'))
        self.assertEqual(response.status_code, 200)


class FormValidationTest(TestCase):
    """Tests para validaciones del formulario"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_nota_fuera_de_rango_superior(self):
        """Test: Nota mayor a 100 es rechazada"""
        data = {
            'nombre_estudiante': 'Test Student',
            'identificacion': '123',
            'asignatura': 'Test',
            'nota1': '150.00',
            'nota2': '80.00',
            'nota3': '90.00'
        }
        response = self.client.post(reverse('crear_calificacion'), data)
        self.assertEqual(Calificacion.objects.count(), 0)
    
    def test_nota_fuera_de_rango_inferior(self):
        """Test: Nota menor a 0 es rechazada"""
        data = {
            'nombre_estudiante': 'Test Student',
            'identificacion': '123',
            'asignatura': 'Test',
            'nota1': '-10.00',
            'nota2': '80.00',
            'nota3': '90.00'
        }
        response = self.client.post(reverse('crear_calificacion'), data)
        self.assertEqual(Calificacion.objects.count(), 0)
    
    def test_nombre_muy_corto(self):
        """Test: Nombre muy corto es rechazado"""
        data = {
            'nombre_estudiante': 'AB',
            'identificacion': '123',
            'asignatura': 'Test',
            'nota1': '80.00',
            'nota2': '80.00',
            'nota3': '80.00'
        }
        response = self.client.post(reverse('crear_calificacion'), data)
        self.assertEqual(Calificacion.objects.count(), 0)
