"""
Script para crear tablas y migrar datos iniciales a Supabase
Ejecutar: python migrar_supabase.py
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def ejecutar_sql(supabase: Client, sql: str):
    """Ejecutar SQL en Supabase"""
    try:
        # Nota: Supabase no tiene ejecución directa de SQL desde Python
        # Debes ejecutar el SQL manualmente en el SQL Editor
        print("   ⚠️ Ejecuta el SQL manualmente en Supabase SQL Editor")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def crear_tablas_directamente(supabase: Client):
    """Crear tablas usando la API de Supabase"""
    print("\n📦 Creando tablas en Supabase...")
    
    # Verificar si la tabla usuarios existe
    try:
        supabase.table('usuarios').select('count', count='exact').limit(1).execute()
        print("   ✅ Tabla 'usuarios' ya existe")
    except:
        print("   ❌ Tabla 'usuarios' no existe. Debes crearla manualmente en SQL Editor")
        return False
    
    # Verificar si la tabla productos_servicios existe
    try:
        supabase.table('productos_servicios').select('count', count='exact').limit(1).execute()
        print("   ✅ Tabla 'productos_servicios' ya existe")
    except:
        print("   ❌ Tabla 'productos_servicios' no existe")
        return False
    
    return True

def insertar_datos_iniciales(supabase: Client):
    """Insertar datos de ejemplo"""
    print("\n📝 Insertando datos iniciales...")
    
    # Verificar admin
    admin = supabase.table('usuarios').select('id').eq('email', 'admin@petcare.com').execute()
    if not admin.data:
        supabase.table('usuarios').insert({
            'nombre': 'Administrador',
            'apellido': 'Sistema',
            'email': 'admin@petcare.com',
            'password': hash_password('admin123'),
            'telefono': '123456789',
            'rol': 'administrador',
            'activo': 1
        }).execute()
        print("   ✅ Admin creado")
    else:
        print("   ✅ Admin ya existe")
    
    # Verificar cuidador
    cuidador = supabase.table('usuarios').select('id').eq('email', 'cuidador@petcare.com').execute()
    if not cuidador.data:
        supabase.table('usuarios').insert({
            'nombre': 'Carlos',
            'apellido': 'Cuidador',
            'email': 'cuidador@petcare.com',
            'password': hash_password('cuidador123'),
            'telefono': '77777777',
            'rol': 'cuidador',
            'activo': 1
        }).execute()
        print("   ✅ Cuidador creado")
        cuidador_id = supabase.table('usuarios').select('id').eq('email', 'cuidador@petcare.com').execute().data[0]['id']
    else:
        print("   ✅ Cuidador ya existe")
        cuidador_id = cuidador.data[0]['id']
    
    # Verificar dueño
    dueno = supabase.table('usuarios').select('id').eq('email', 'dueno@petcare.com').execute()
    if not dueno.data:
        supabase.table('usuarios').insert({
            'nombre': 'María',
            'apellido': 'Dueña',
            'email': 'dueno@petcare.com',
            'password': hash_password('dueno123'),
            'telefono': '55555555',
            'rol': 'dueño',
            'activo': 1
        }).execute()
        print("   ✅ Dueño creado")
    
    # Productos de ejemplo
    productos = supabase.table('productos_servicios').select('id').eq('titulo', 'Paseo de mascotas').execute()
    if not productos.data and cuidador_id:
        supabase.table('productos_servicios').insert({
            'titulo': 'Paseo de mascotas',
            'descripcion': 'Paseo de 30 minutos por el parque',
            'precio': 50.00,
            'categoria': 'paseo',
            'ofertante_id': cuidador_id,
            'estado': 'pendiente',
            'activo': 1,
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat()
        }).execute()
        print("   ✅ Producto pendiente creado")
    
    productos2 = supabase.table('productos_servicios').select('id').eq('titulo', 'Guardería canina').execute()
    if not productos2.data and cuidador_id:
        supabase.table('productos_servicios').insert({
            'titulo': 'Guardería canina',
            'descripcion': 'Cuidado todo el día con áreas de juego',
            'precio': 150.00,
            'categoria': 'guarderia',
            'ofertante_id': cuidador_id,
            'estado': 'aprobado',
            'activo': 1,
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat()
        }).execute()
        print("   ✅ Producto aprobado creado")
    
    print("✅ Datos iniciales insertados")

def main():
    print("="*60)
    print("   🚀 PETCARE CONNECT - SETUP SUPABASE")
    print("="*60)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n❌ Error: Configura SUPABASE_URL y SUPABASE_KEY en el archivo .env")
        print("\nCrea un archivo .env en la carpeta backend con:")
        print("SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("SUPABASE_KEY=tu-anon-key-aqui")
        return
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"\n✅ Conectado a Supabase: {SUPABASE_URL}")
    
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES IMPORTANTES")
    print("="*60)
    print("""
Antes de continuar, debes crear las tablas en Supabase:

1. Ve a https://app.supabase.com
2. Selecciona tu proyecto
3. Ve a "SQL Editor"
4. Crea una nueva query
5. Ejecuta el siguiente SQL:

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    telefono TEXT,
    rol TEXT CHECK (rol IN ('dueño', 'cuidador', 'administrador')) DEFAULT 'dueño',
    foto_url TEXT,
    activo INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla productos_servicios
CREATE TABLE IF NOT EXISTS productos_servicios (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria TEXT NOT NULL CHECK (categoria IN ('paseo', 'guarderia', 'alojamiento')),
    ofertante_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aprobado', 'rechazado')),
    motivo_rechazo TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activo INTEGER DEFAULT 1
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_productos_ofertante ON productos_servicios(ofertante_id);
CREATE INDEX IF NOT EXISTS idx_productos_estado ON productos_servicios(estado);

6. Ejecuta el script
7. Luego ejecuta este script nuevamente para insertar los datos
""")
    
    input("\n⚠️ ¿Ya creaste las tablas en Supabase? Presiona Enter para continuar...")
    
    if crear_tablas_directamente(supabase):
        insertar_datos_iniciales(supabase)
        
        print("\n" + "="*60)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print("="*60)
        print("\n📊 CREDENCIALES DE ACCESO:")
        print("   Admin: admin@petcare.com / admin123")
        print("   Cuidador: cuidador@petcare.com / cuidador123")
        print("   Dueño: dueno@petcare.com / dueno123")
        print("\n🚀 Ahora puedes ejecutar: python app.py")
        print("="*60)
    else:
        print("\n❌ Configuración incompleta. Crea las tablas manualmente en Supabase.")

if __name__ == '__main__':
    main()