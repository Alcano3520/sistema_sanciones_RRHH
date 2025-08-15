# config.py - Configuración del Sistema RRHH
import os

# ===============================================
# 🔗 CONFIGURACIÓN SUPABASE (SANCIONES)
# ===============================================
SUPABASE_URL = "https://syxzopyevfuwymmltbwn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5eHpvcHlldmZ1d3ltbWx0YnduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzNjkwMzYsImV4cCI6MjA2Nzk0NTAzNn0.fnxkNI4Hm4GgTAR8p1gsyeI8XPbmtDl0dF9PqxiMxsM"

# ===============================================
# 💾 BASE DE DATOS LOCAL
# ===============================================
DB_LOCAL = r"\\SERVER\Respaldo 2017\Base\procesadas.db"

# Si no existe el directorio, usar ruta local
if not os.path.exists(r"\\SERVER\Respaldo 2017\Base"):
    DB_LOCAL = "procesadas.db"

# ===============================================
# 📂 CATEGORÍAS DE SANCIONES
# ===============================================
CATEGORIAS = {
    "Faltas y Permisos": ['FALTA', 'PERMISO'],
    "Horas y Franco": ['HORAS EXTRAS', 'FRANCO TRABAJADO'],
    "Resto": [
        'ATRASO', 'DORMIDO', 'MALA URBANIDAD', 'FALTA DE RESPETO',
        'MAL UNIFORMADO', 'ABANDONO DE PUESTO', 'MAL SERVICIO DE GUARDIA',
        'INCUMPLIMIENTO DE POLITICAS', 'MAL USO DEL EQUIPO DE DOTACIÓN'
    ]
}

# ===============================================
# 👤 CONFIGURACIÓN DE USUARIOS
# ===============================================
USUARIOS_DEFAULT = {
    "admin": "123456",
    "rrhh": "rrhh2025",
    "supervisor": "super123"
}

# ===============================================
# 🎨 CONFIGURACIÓN UI
# ===============================================
TITULO_APP = "Sistema RRHH - Procesador de Sanciones"
VERSION = "v1.0"
EMPRESA = "INSEVIG"

# Colores
COLOR_PRINCIPAL = "#2E86AB"
COLOR_SECUNDARIO = "#A23B72" 
COLOR_EXITO = "#F18F01"
COLOR_ERROR = "#C73E1D"

# ===============================================
# 📝 MENSAJES DEL SISTEMA
# ===============================================
MSG_PROCESADO = "Procesado para nómina"
MSG_LOGIN_ERROR = "Usuario o contraseña incorrectos"
MSG_CONEXION_ERROR = "Error de conexión con Supabase"
MSG_DB_ERROR = "Error con base de datos local"

print(f"✅ Configuración cargada - {TITULO_APP} {VERSION}")
print(f"🔗 URL Supabase: {SUPABASE_URL[:30]}...")
print(f"💾 Base local: {DB_LOCAL}")
