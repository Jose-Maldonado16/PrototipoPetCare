import os
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

print("="*50)
print("PRUEBA DE CONEXIÓN A SUPABASE")
print("="*50)

if not URL:
    print("❌ SUPABASE_URL no encontrada en .env")
    exit(1)

if not KEY:
    print("❌ SUPABASE_KEY no encontrada en .env")
    exit(1)

print(f"✅ URL encontrada: {URL}")
print(f"✅ KEY encontrada: {KEY[:30]}...")

try:
    supabase = create_client(URL, KEY)
    print("✅ Cliente creado correctamente")
    
    # Probar conexión a tabla usuarios
    response = supabase.table('usuarios').select('*').limit(10).execute()
    print(f"✅ Conexión exitosa! Usuarios encontrados: {len(response.data)}")
    
    for user in response.data:
        print(f"   - {user['email']} ({user['rol']})")
        
except Exception as e:
    print(f"❌ Error: {e}")