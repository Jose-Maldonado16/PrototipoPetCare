import sqlite3
import hashlib
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    # Conectar a la base de datos (la creará automáticamente)
    conn = sqlite3.connect('petcare.db')
    cursor = conn.cursor()
    
    # Crear tabla usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            telefono TEXT,
            rol TEXT CHECK(rol IN ('dueño', 'cuidador', 'administrador')) DEFAULT 'dueño',
            foto_url TEXT,
            activo INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')
    
    # Crear índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON usuarios(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rol ON usuarios(rol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activo ON usuarios(activo)')
    
    # Datos de ejemplo
    usuarios = [
        # Usuario administrador
        ("Administrador", "Sistema", "admin@petcare.com", hash_password("admin123"), "123456789", "administrador", None, 1),
        
        # Usuarios dueños
        ("María", "García", "maria@petcare.com", hash_password("maria123"), "555-0101", "dueño", None, 1),
        ("Carlos", "López", "carlos@petcare.com", hash_password("carlos123"), "555-0102", "dueño", None, 1),
        ("Laura", "Rodríguez", "laura@petcare.com", hash_password("laura123"), "555-0103", "dueño", None, 0),  # Inactivo
        
        # Usuarios cuidadores
        ("Ana", "Martínez", "ana@petcare.com", hash_password("ana123"), "555-0104", "cuidador", None, 1),
        ("Pedro", "Sánchez", "pedro@petcare.com", hash_password("pedro123"), "555-0105", "cuidador", None, 1),
        ("Sofia", "Gómez", "sofia@petcare.com", hash_password("sofia123"), "555-0106", "cuidador", None, 1),
        
        # Usuarios administradores adicionales
        ("Javier", "Fernández", "javier@petcare.com", hash_password("javier123"), "555-0107", "administrador", None, 1),
        ("Diego", "Ruiz", "diego@petcare.com", hash_password("diego123"), "555-0108", "dueño", None, 1)
    ]
    
    # Insertar usuarios
    for usuario in usuarios:
        try:
            cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, foto_url, activo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', usuario + (datetime.now().isoformat(),))
            print(f"✓ Usuario creado: {usuario[2]}")
        except sqlite3.IntegrityError:
            print(f"✗ Usuario ya existe: {usuario[2]}")
    
    # Confirmar cambios
    conn.commit()
    
    # Mostrar resumen
    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT rol, COUNT(*) as count FROM usuarios GROUP BY rol")
    roles = cursor.fetchall()
    
    print("\n" + "="*50)
    print("BASE DE DATOS CREADA EXITOSAMENTE")
    print("="*50)
    print(f"Total de usuarios: {total}")
    for rol, count in roles:
        print(f"  {rol}: {count}")
    print("="*50)
    print("\nCREDENCIALES DE ACCESO:")
    print("  Email: admin@petcare.com")
    print("  Contraseña: admin123")
    print("="*50)
    
    # Cerrar conexión
    conn.close()

if __name__ == '__main__':
    create_database()