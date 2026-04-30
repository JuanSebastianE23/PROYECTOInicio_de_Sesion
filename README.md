# Sistema de Calificaciones - Django

Proyecto de gestión de calificaciones de estudiantes con Django.

## 🚀 Despliegue en Railway

### Variables de entorno necesarias:

```env
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=.railway.app
DATABASE_URL=postgresql://... (Railway lo provee automáticamente)
```

### Pasos para desplegar:

1. **Conectar repositorio a Railway**
   - Ve a [railway.app](https://railway.app)
   - Crea nuevo proyecto
   - Conecta este repositorio de GitHub

2. **Agregar PostgreSQL**
   - En Railway, agrega un servicio PostgreSQL
   - Railway configurará DATABASE_URL automáticamente

3. **Configurar variables de entorno**
   - Agrega SECRET_KEY (genera una nueva)
   - Agrega DEBUG=False
   - Agrega ALLOWED_HOSTS=.railway.app

4. **Crear superusuario** (después del primer deploy)
   ```bash
   railway run python manage.py createsuperuser
   ```

## 💻 Desarrollo local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## 📝 Credenciales por defecto

- Usuario: `admin`
- Contraseña: `admin123`

## ✨ Funcionalidades

- ✅ CRUD de calificaciones
- ✅ Cálculo automático de promedio
- ✅ Dashboard con estadísticas
- ✅ Exportar/Importar CSV
- ✅ Búsqueda y filtros
- ✅ Sistema de autenticación
- ✅ Panel de administración
