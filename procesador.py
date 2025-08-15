# procesador_completo.py - Lógica de Procesamiento RRHH COMPLETA
import sqlite3
import requests
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from config import *

class ProcesadorRRHH:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        self.init_db_local()
    
    def init_db_local(self):
        """Inicializar base de datos local SQLite"""
        try:
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                
                # Tabla para sanciones procesadas
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS procesadas (
                        id TEXT PRIMARY KEY,
                        fecha_proceso DATE DEFAULT CURRENT_TIMESTAMP,
                        usuario TEXT,
                        empleado_cod INTEGER,
                        empleado_nombre TEXT,
                        tipo_sancion TEXT
                    )
                ''')
                
                # Tabla para usuarios
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        usuario TEXT PRIMARY KEY,
                        password TEXT,
                        activo INTEGER DEFAULT 1
                    )
                ''')
                
                # Insertar usuarios por defecto si no existen
                for user, pwd in USUARIOS_DEFAULT.items():
                    cursor.execute('''
                        INSERT OR IGNORE INTO usuarios (usuario, password) 
                        VALUES (?, ?)
                    ''', (user, pwd))
                
                conn.commit()
                print("✅ Base de datos local inicializada")
                
        except Exception as e:
            print(f"❌ Error inicializando DB local: {e}")
            raise
    
    def validar_usuario(self, usuario: str, password: str) -> bool:
        """Validar credenciales de usuario"""
        try:
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM usuarios 
                    WHERE usuario = ? AND password = ? AND activo = 1
                ''', (usuario, password))
                
                return cursor.fetchone()[0] > 0
                
        except Exception as e:
            print(f"❌ Error validando usuario: {e}")
            return False
    
    def test_conexion_supabase(self) -> bool:
        """Probar conexión con Supabase"""
        try:
            url = f"{SUPABASE_URL}/rest/v1/sanciones"
            params = {'select': 'count', 'limit': 1}
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error conexión Supabase: {e}")
            return False
    
    def obtener_sanciones_pendientes(self) -> List[Dict]:
        """Obtener sanciones aprobadas sin comentario RRHH"""
        try:
            # Obtener IDs ya procesadas
            procesadas_ids = self.obtener_procesadas_ids()
            
            print("🔍 Consultando sanciones en Supabase...")
            
            # Query a Supabase
            url = f"{SUPABASE_URL}/rest/v1/sanciones"
            params = {
                'select': '*',
                'status': 'eq.aprobado',
                'comentarios_rrhh': 'is.null',
                'order': 'fecha.desc'
            }
            
            print(f"🔗 URL: {url}")
            print(f"📋 Parámetros: {params}")
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            
            print(f"📡 Status respuesta: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error API Supabase: {response.status_code}")
                print(f"❌ Respuesta: {response.text}")
                return []
            
            sanciones = response.json()
            print(f"📊 Sanciones obtenidas de Supabase: {len(sanciones)}")
            
            if len(sanciones) == 0:
                print("⚠️ No hay sanciones aprobadas sin comentario RRHH en Supabase")
                print("💡 Esto puede significar:")
                print("   - No hay sanciones con status='aprobado'")
                print("   - Todas las sanciones aprobadas ya tienen comentarios_rrhh")
                print("   - Row Level Security (RLS) está bloqueando el acceso")
                print("   - La tabla está vacía")
            
            # Filtrar las ya procesadas localmente
            sanciones_filtradas = [
                s for s in sanciones 
                if s['id'] not in procesadas_ids
            ]
            
            if len(sanciones) > 0 and len(sanciones_filtradas) < len(sanciones):
                print(f"🔄 Filtradas {len(sanciones) - len(sanciones_filtradas)} ya procesadas localmente")
            
            print(f"📋 Sanciones pendientes finales: {len(sanciones_filtradas)}")
            return sanciones_filtradas
            
        except Exception as e:
            print(f"❌ Error obteniendo sanciones: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def obtener_procesadas_ids(self) -> set:
        """Obtener IDs de sanciones ya procesadas"""
        try:
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM procesadas')
                return {row[0] for row in cursor.fetchall()}
                
        except Exception as e:
            print(f"❌ Error obteniendo procesadas: {e}")
            return set()
    
    def categorizar_sanciones(self, sanciones: List[Dict]) -> Dict[str, List[Dict]]:
        """Organizar sanciones por categorías"""
        categorizadas = {categoria: [] for categoria in CATEGORIAS.keys()}
        
        for sancion in sanciones:
            tipo = sancion.get('tipo_sancion', '').upper()
            categorizada = False
            
            for categoria, tipos in CATEGORIAS.items():
                if tipo in tipos:
                    categorizadas[categoria].append(sancion)
                    categorizada = True
                    break
            
            # Si no encaja en ninguna categoría, va a "Resto"
            if not categorizada:
                categorizadas["Resto"].append(sancion)
        
        return categorizadas
    
    def procesar_sancion(self, sancion: Dict, usuario: str) -> bool:
        """Procesar una sanción individual"""
        try:
            sancion_id = sancion['id']
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            comentario = f"{MSG_PROCESADO} - {fecha_actual} - {usuario}"
            
            print(f"🔄 Procesando sanción {sancion_id[:8]}...")
            
            # 1. Actualizar en Supabase
            url = f"{SUPABASE_URL}/rest/v1/sanciones"
            params = {'id': f'eq.{sancion_id}'}
            data = {'comentarios_rrhh': comentario}
            
            response = requests.patch(
                url, 
                headers=self.supabase_headers, 
                params=params, 
                json=data
            )
            
            if response.status_code not in [200, 204]:
                print(f"❌ Error actualizando Supabase: {response.status_code}")
                print(f"❌ Respuesta: {response.text}")
                return False
            
            # 2. Guardar en base local
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO procesadas (
                        id, usuario, empleado_cod, empleado_nombre, tipo_sancion
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    sancion_id,
                    usuario,
                    sancion.get('empleado_cod'),
                    sancion.get('empleado_nombre'),
                    sancion.get('tipo_sancion')
                ))
                conn.commit()
            
            print(f"✅ Procesada sanción {sancion_id[:8]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error procesando sanción {sancion.get('id', 'N/A')[:8]}...: {e}")
            return False
    
    def procesar_multiples_sanciones(self, sanciones: List[Dict], usuario: str) -> tuple:
        """Procesar múltiples sanciones"""
        exitosas = 0
        fallidas = 0
        
        print(f"🚀 Iniciando procesamiento de {len(sanciones)} sanciones...")
        
        for i, sancion in enumerate(sanciones):
            print(f"📋 Procesando {i+1}/{len(sanciones)}: {sancion.get('empleado_nombre', 'N/A')}")
            
            if self.procesar_sancion(sancion, usuario):
                exitosas += 1
            else:
                fallidas += 1
        
        print(f"✅ Procesamiento completado: {exitosas} exitosas, {fallidas} fallidas")
        return exitosas, fallidas
    
    def crear_sancion_prueba(self) -> bool:
        """Crear una sanción de prueba para testing"""
        try:
            print("🧪 Creando sanción de prueba...")
            
            url = f"{SUPABASE_URL}/rest/v1/sanciones"
            
            # Datos de prueba
            sancion_prueba = {
                "empleado_cod": 99999,
                "empleado_nombre": "EMPLEADO PRUEBA SISTEMA",
                "puesto": "VIGILANTE DE PRUEBA",
                "agente": "SISTEMA AUTOMATICO",
                "fecha": date.today().isoformat(),
                "hora": "08:00:00",
                "tipo_sancion": "ATRASO",
                "observaciones": "Sanción creada automáticamente para prueba del sistema RRHH",
                "status": "aprobado",
                "comentarios_rrhh": None,
                "supervisor_id": "00000000-0000-0000-0000-000000000000"  # UUID dummy
            }
            
            headers = self.supabase_headers.copy()
            headers['Prefer'] = 'return=representation'
            
            response = requests.post(url, headers=headers, json=sancion_prueba)
            
            if response.status_code in [200, 201]:
                print("✅ Sanción de prueba creada exitosamente")
                return True
            else:
                print(f"❌ Error creando sanción de prueba: {response.status_code}")
                print(f"❌ Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creando sanción de prueba: {e}")
            return False
    
    def obtener_procesadas_completas(self) -> List[Dict]:
        """Obtener todas las sanciones procesadas con detalles completos"""
        try:
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, usuario, empleado_cod, empleado_nombre, 
                           tipo_sancion, fecha_proceso 
                    FROM procesadas 
                    ORDER BY fecha_proceso DESC
                ''')
                
                procesadas_locales = cursor.fetchall()
                
                if not procesadas_locales:
                    return []
                
                # Obtener detalles completos de Supabase
                ids_procesadas = [row[0] for row in procesadas_locales]
                
                # Consultar Supabase para obtener detalles completos
                url = f"{SUPABASE_URL}/rest/v1/sanciones"
                params = {
                    'select': '*',
                    'id': f'in.({",".join(ids_procesadas)})'
                }
                
                response = requests.get(url, headers=self.supabase_headers, params=params)
                
                if response.status_code == 200:
                    sanciones_supabase = response.json()
                    
                    # Combinar datos locales con datos de Supabase
                    sanciones_completas = []
                    for local_row in procesadas_locales:
                        id_local, usuario, emp_cod, emp_nombre, tipo, fecha_proc = local_row
                        
                        # Buscar datos completos en Supabase
                        sancion_supabase = next(
                            (s for s in sanciones_supabase if s['id'] == id_local), 
                            None
                        )
                        
                        if sancion_supabase:
                            # Agregar datos de procesamiento local
                            sancion_supabase['procesado_por'] = usuario
                            sancion_supabase['fecha_procesamiento'] = fecha_proc
                            sanciones_completas.append(sancion_supabase)
                    
                    return sanciones_completas
                else:
                    print(f"❌ Error obteniendo detalles de Supabase: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error obteniendo procesadas completas: {e}")
            return []
    
    def categorizar_procesadas(self, sanciones: List[Dict]) -> Dict[str, List[Dict]]:
        """Organizar sanciones procesadas por categorías"""
        return self.categorizar_sanciones(sanciones)
    
    def exportar_a_excel(self, sanciones: List[Dict], nombre_archivo: str = None) -> str:
        """Exportar sanciones a Excel"""
        try:
            print("📥 Iniciando exportación a Excel...")
            
            # Verificar que openpyxl esté disponible
            try:
                import openpyxl
                from openpyxl.styles import Font, Alignment, PatternFill
                from openpyxl.utils import get_column_letter
            except ImportError:
                print("❌ openpyxl no está instalado. Instalando automáticamente...")
                import subprocess
                import sys
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
                    print("✅ openpyxl instalado exitosamente")
                    import openpyxl
                    from openpyxl.styles import Font, Alignment, PatternFill
                    from openpyxl.utils import get_column_letter
                except Exception as install_error:
                    print(f"❌ Error instalando openpyxl: {install_error}")
                    return None
        
            # Nombre del archivo
            if not nombre_archivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"Sanciones_Procesadas_{timestamp}.xlsx"
            
            print(f"📄 Creando archivo: {nombre_archivo}")
            
            # Crear workbook
            wb = openpyxl.Workbook()
            
            # Organizar por categorías
            categorizadas = self.categorizar_sanciones(sanciones)
            
            # Eliminar hoja por defecto
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Crear hoja para cada categoría
            hojas_creadas = 0
            for categoria, sanciones_categoria in categorizadas.items():
                if not sanciones_categoria:
                    continue
                    
                print(f"📝 Creando hoja: {categoria} ({len(sanciones_categoria)} registros)")
                
                # Crear hoja
                nombre_hoja = categoria.replace('/', '-')[:30]  # Evitar caracteres inválidos
                ws = wb.create_sheet(title=nombre_hoja)
                
                # Estilo del header
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
                header_alignment = Alignment(horizontal="center", vertical="center")
                
                # Headers
                headers = [
                    'ID', 'Empleado Cod', 'Empleado Nombre', 'Puesto', 
                    'Agente', 'Fecha', 'Hora', 'Tipo Sanción', 
                    'Observaciones', 'Status', 'Comentarios Gerencia',
                    'Comentarios RRHH', 'Procesado Por', 'Fecha Procesamiento'
                ]
                
                # Escribir headers
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col, value=header)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                
                # Escribir datos
                for row, sancion in enumerate(sanciones_categoria, 2):
                    data_row = [
                        str(sancion.get('id', ''))[:12] + '...' if len(str(sancion.get('id', ''))) > 12 else str(sancion.get('id', '')),
                        sancion.get('empleado_cod', ''),
                        sancion.get('empleado_nombre', ''),
                        sancion.get('puesto', ''),
                        sancion.get('agente', ''),
                        sancion.get('fecha', ''),
                        sancion.get('hora', ''),
                        sancion.get('tipo_sancion', ''),
                        sancion.get('observaciones', ''),
                        sancion.get('status', ''),
                        sancion.get('comentarios_gerencia', ''),
                        sancion.get('comentarios_rrhh', ''),
                        sancion.get('procesado_por', ''),
                        sancion.get('fecha_procesamiento', '')
                    ]
                    
                    for col, value in enumerate(data_row, 1):
                        ws.cell(row=row, column=col, value=value)
                
                # Ajustar ancho de columnas
                for col in range(1, len(headers) + 1):
                    column_letter = get_column_letter(col)
                    ws.column_dimensions[column_letter].width = 15
                
                # Ajustar ancho específico para ciertas columnas
                ws.column_dimensions['C'].width = 25  # Nombre empleado
                ws.column_dimensions['I'].width = 30  # Observaciones
                ws.column_dimensions['L'].width = 30  # Comentarios RRHH
                
                hojas_creadas += 1
            
            # Si no se crearon hojas, crear una vacía
            if hojas_creadas == 0:
                ws = wb.create_sheet(title="Sin Datos")
                ws['A1'] = "No hay datos para exportar"
                ws['A1'].font = Font(bold=True)
            
            # Crear hoja resumen
            ws_resumen = wb.create_sheet(title="Resumen", index=0)
            
            # Escribir resumen
            ws_resumen['A1'] = "RESUMEN DE SANCIONES PROCESADAS"
            ws_resumen['A1'].font = Font(size=16, bold=True)
            
            ws_resumen['A3'] = f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ws_resumen['A4'] = f"Total de sanciones: {len(sanciones)}"
            
            row = 6
            for categoria, sanciones_cat in categorizadas.items():
                ws_resumen[f'A{row}'] = f"{categoria}: {len(sanciones_cat)} sanciones"
                row += 1
            
            # Guardar archivo
            print(f"💾 Guardando archivo: {nombre_archivo}")
            wb.save(nombre_archivo)
            print(f"✅ Excel exportado exitosamente: {nombre_archivo}")
            
            return nombre_archivo
            
        except Exception as e:
            print(f"❌ Error exportando a Excel: {e}")
            import traceback
            traceback.print_exc()
            return None

    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            with sqlite3.connect(DB_LOCAL) as conn:
                cursor = conn.cursor()
                
                # Total procesadas
                cursor.execute('SELECT COUNT(*) FROM procesadas')
                total_procesadas = cursor.fetchone()[0]
                
                # Por usuario
                cursor.execute('''
                    SELECT usuario, COUNT(*) 
                    FROM procesadas 
                    GROUP BY usuario
                ''')
                por_usuario = dict(cursor.fetchall())
                
                # Por tipo
                cursor.execute('''
                    SELECT tipo_sancion, COUNT(*) 
                    FROM procesadas 
                    GROUP BY tipo_sancion
                ''')
                por_tipo = dict(cursor.fetchall())
                
                # Hoy
                cursor.execute('''
                    SELECT COUNT(*) FROM procesadas 
                    WHERE DATE(fecha_proceso) = DATE('now')
                ''')
                hoy = cursor.fetchone()[0]
                
                return {
                    'total_procesadas': total_procesadas,
                    'por_usuario': por_usuario,
                    'por_tipo': por_tipo,
                    'procesadas_hoy': hoy
                }
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}

# Instancia global
procesador = ProcesadorRRHH()
