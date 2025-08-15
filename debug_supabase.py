# test_completo.py - Verificar RLS y crear datos de prueba
import requests
import json
import uuid
from datetime import datetime, date
from config import SUPABASE_URL, SUPABASE_KEY

def test_completo():
    """Test completo: RLS, permisos y datos de prueba"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    print("🔍 TEST COMPLETO - RLS Y DATOS DE PRUEBA")
    print("="*60)
    
    # 1. Verificar información de la tabla
    print("1️⃣ Verificando información de la tabla...")
    try:
        # Intentar obtener metadata de la tabla
        url = f"{SUPABASE_URL}/rest/v1/sanciones"
        params = {'select': 'count'}
        response = requests.head(url, headers=headers)
        print(f"   Status HEAD: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error verificando metadata: {e}")
    
    # 2. Intentar insertar una sanción de prueba
    print("\n2️⃣ Intentando insertar sanción de prueba...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sanciones"
        
        # Datos de prueba
        sancion_prueba = {
            "supervisor_id": "00000000-0000-0000-0000-000000000000",  # UUID dummy
            "empleado_cod": 12345,
            "empleado_nombre": "EMPLEADO PRUEBA",
            "puesto": "VIGILANTE",
            "agente": "AGENTE PRUEBA",
            "fecha": date.today().isoformat(),
            "hora": "08:00:00",
            "tipo_sancion": "ATRASO",
            "observaciones": "Sanción de prueba para testing",
            "status": "aprobado",
            "comentarios_rrhh": None  # NULL para que aparezca en el query
        }
        
        response = requests.post(url, headers=headers, json=sancion_prueba)
        print(f"   Status INSERT: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Sanción de prueba insertada exitosamente")
            inserted_data = response.json()
            if isinstance(inserted_data, list) and len(inserted_data) > 0:
                sancion_id = inserted_data[0].get('id')
                print(f"   📋 ID sanción creada: {sancion_id}")
            else:
                print(f"   📋 Respuesta: {inserted_data}")
        else:
            print(f"   ❌ Error insertando: {response.text}")
            
            # Si falla, puede ser por RLS o foreign keys
            print(f"   🔍 Verificando si es problema de RLS o FK...")
            
    except Exception as e:
        print(f"   ❌ Error en INSERT: {e}")
    
    # 3. Intentar con datos mínimos (por si hay problema con FK)
    print("\n3️⃣ Intentando inserción mínima...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sanciones"
        
        # Datos mínimos de prueba (sin FKs)
        sancion_minima = {
            "empleado_cod": 99999,
            "empleado_nombre": "PRUEBA SISTEMA",
            "puesto": "TEST",
            "agente": "SYSTEM",
            "fecha": date.today().isoformat(),
            "hora": "12:00:00",
            "tipo_sancion": "FALTA",
            "status": "aprobado"
            # No incluimos supervisor_id para ver si eso causa el problema
        }
        
        response = requests.post(url, headers=headers, json=sancion_minima)
        print(f"   Status INSERT mínimo: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        
    except Exception as e:
        print(f"   ❌ Error en INSERT mínimo: {e}")
    
    # 4. Verificar si ahora hay datos
    print("\n4️⃣ Verificando datos después de inserción...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sanciones"
        params = {'select': '*'}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            sanciones = response.json()
            print(f"   ✅ Sanciones encontradas: {len(sanciones)}")
            
            if len(sanciones) > 0:
                print("\n   📋 DATOS ENCONTRADOS:")
                for i, sancion in enumerate(sanciones):
                    print(f"   {i+1}. ID: {sancion.get('id', 'N/A')}")
                    print(f"      Empleado: {sancion.get('empleado_cod')} - {sancion.get('empleado_nombre')}")
                    print(f"      Status: {sancion.get('status')}")
                    print(f"      Comentarios RRHH: {sancion.get('comentarios_rrhh')}")
                    print(f"      Tipo: {sancion.get('tipo_sancion')}")
                    print()
        else:
            print(f"   ❌ Error obteniendo datos: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error verificando datos: {e}")
    
    # 5. Probar query específico del sistema
    print("\n5️⃣ Probando query específico del sistema...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sanciones"
        params = {
            'select': '*',
            'status': 'eq.aprobado',
            'comentarios_rrhh': 'is.null',
            'order': 'fecha.desc'
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            sanciones = response.json()
            print(f"   ✅ Sanciones que cumplen criterios: {len(sanciones)}")
            
            if len(sanciones) > 0:
                print("   🎯 ¡ESTAS SON LAS QUE DEBERÍA PROCESAR EL SISTEMA!")
                for sancion in sanciones:
                    print(f"   - {sancion.get('empleado_nombre')} ({sancion.get('tipo_sancion')})")
            else:
                print("   ⚠️ No hay sanciones aprobadas sin comentario RRHH")
        else:
            print(f"   ❌ Error en query: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en query específico: {e}")
    
    # 6. Verificar problemas de autenticación/RLS
    print("\n6️⃣ Verificando autenticación y RLS...")
    try:
        # Probar diferentes endpoints
        endpoints_test = [
            "/rest/v1/",
            "/rest/v1/sanciones?select=count",
            "/rest/v1/sanciones?limit=0"
        ]
        
        for endpoint in endpoints_test:
            url = f"{SUPABASE_URL}{endpoint}"
            response = requests.get(url, headers=headers)
            print(f"   {endpoint}: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error probando endpoints: {e}")
    
    print("\n" + "="*60)
    print("🏁 TEST COMPLETO FINALIZADO")
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Si no se pudieron insertar datos, revisar RLS en Supabase")
    print("2. Si se insertaron pero no aparecen en query, revisar permisos")
    print("3. Si todo funciona, el sistema debería funcionar correctamente")

if __name__ == "__main__":
    test_completo()
