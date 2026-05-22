"""
Script para migrar datos de SQLite a Supabase
Ejecutar: python migrar_supabase.py
"""

import os
import sqlite3
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def migrar_usuarios(supabase: Client, cursor):
    print("📤 Migrando usuarios...")
    cursor.execute("SELECT id, nombre, apellido, email, password, telefono, rol, foto_url, activo, created_at FROM usuarios")
    usuarios = cursor.fetchall()
    
    for user in usuarios:
        data = {
            'id': user[0],
            'nombre': user[1],
            'apellido': user[2],
            'email': user[3],
            'password': user[4],
            'telefono': user[5],
            'rol': user[6],
            'foto_url': user[7],
            'activo': user[8],
            'created_at': user[9]
        }
        try:
            supabase.table('usuarios').upsert(data).execute()
            print(f"  ✅ Usuario {user[3]} migrado")
        except Exception as e:
            print(f"  ❌ Error con {user[3]}: {e}")

def migrar_productos(supabase: Client, cursor):
    print("\n📤 Migrando productos/servicios...")
    cursor.execute("SELECT * FROM productos_servicios")
    productos = cursor.fetchall()
    
    for prod in productos:
        data = {
            'id': prod[0],
            'titulo': prod[1],
            'descripcion': prod[2],
            'precio': prod[3],
            'categoria': prod[4],
            'ofertante_id': prod[5],
            'estado': prod[6],
            'motivo_rechazo': prod[7],
            'fecha_creacion': prod[8],
            'fecha_actualizacion': prod[9],
            'activo': prod[10]
        }
        try:
            supabase.table('productos_servicios').upsert(data).execute()
            print(f"  ✅ Producto {prod[1]} migrado")
        except Exception as e:
            print(f"  ❌ Error con {prod[1]}: {e}")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Configura SUPABASE_URL y SUPABASE_KEY en el archivo .env")
        return
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Conectar a SQLite local
    conn = sqlite3.connect('petcare.db')
    cursor = conn.cursor()
    
    print("="*50)
    print("🚀 Migración PetCare Connect a Supabase")
    print("="*50)
    
    migrar_usuarios(supabase, cursor)
    migrar_productos(supabase, cursor)
    
    conn.close()
    print("\n✅ Migración completada!")

if __name__ == '__main__':
    main()