# config.py - Configuración del Sistema RRHH OPTIMIZADA
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
# ⚡ CONFIGURACIÓN DE RENDIMIENTO
# ===============================================
# Tamaño de lotes para procesamiento
BATCH_SIZE = 50
# Timeout para requests (segundos)
REQUEST_TIMEOUT = 10
# Máximo de reintentos
MAX_REINTENTOS = 3
# Threads para procesamiento paralelo
MAX_THREADS = 5

# ===============================================
# 🔒 CONFIGURACIÓN DE CONCURRENCIA
# ===============================================
# Tiempo de bloqueo para evitar procesamiento duplicado (minutos)
TIEMPO_BLOQUEO = 5
# Intervalo de verificación de estado (segundos)
INTERVALO_VERIFICACION = 30
# Campos que indican procesamiento
CAMPO_PROCESADO = 'comentarios_rrhh'
VALOR_PENDIENTE = None  # NULL indica pendiente

# ===============================================
# 🎨 CONFIGURACIÓN UI
# ===============================================
TITULO_APP = "Sistema RRHH - Procesador de Sanciones"
VERSION = "v2.0 - Optimizado"
EMPRESA = "INSEVIG"

# Colores
COLOR_PRINCIPAL = "#2E86AB"
COLOR_SECUNDARIO = "#A23B72" 
COLOR_EXITO = "#F18F01"
COLOR_ERROR = "#C73E1D"
COLOR_PROCESANDO = "#17a2b8"
COLOR_BLOQUEADO = "#ffc107"

# ===============================================
# 📝 MENSAJES DEL SISTEMA
# ===============================================
MSG_PROCESADO = "Procesado para nómina"
MSG_LOGIN_ERROR = "Usuario o contraseña incorrectos"
MSG_CONEXION_ERROR = "Error de conexión con Supabase"
MSG_DB_ERROR = "Error con base de datos local"
MSG_CONCURRENCIA = "Sanción siendo procesada por otro usuario"
MSG_PROCESAMIENTO = "Procesando sanciones en lote..."
MSG_VALIDANDO = "Validando disponibilidad..."

# ===============================================
# 🔍 QUERIES OPTIMIZADAS
# ===============================================
# Query para sanciones pendientes (solo Supabase)
QUERY_PENDIENTES = {
    'select': '*',
    'status': 'eq.aprobado',
    'comentarios_rrhh': 'is.null',
    'order': 'fecha.desc'
}

# Query para verificar concurrencia
QUERY_VERIFICAR_IDS = {
    'select': 'id,comentarios_rrhh,updated_at'
}

# ===============================================
# 📊 CONFIGURACIÓN DE LOGGING
# ===============================================
LOG_LEVEL = "INFO"
LOG_FILE = "rrhh_sistema.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

print(f"✅ Configuración cargada - {TITULO_APP} {VERSION}")
print(f"🔗 URL Supabase: {SUPABASE_URL[:30]}...")
print(f"💾 Base local: {DB_LOCAL}")
print(f"⚡ Optimizaciones: Batch({BATCH_SIZE}), Threads({MAX_THREADS}), Timeout({REQUEST_TIMEOUT}s)")
