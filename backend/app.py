import sqlite3
import hashlib
import re
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATABASE = 'petcare.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def hash_password(password):
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Valida formato de email con regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def init_db():
    """Inicializa la base de datos con tablas y datos por defecto"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
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
        
        # Crear índices para mejor rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON usuarios(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rol ON usuarios(rol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activo ON usuarios(activo)')
        
        # Verificar si ya existe el usuario administrador
        admin_email = "admin@petcare.com"
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        
        if not cursor.fetchone():
            # Crear usuario administrador por defecto
            admin_pass = hash_password("admin123")
            cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, activo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Administrador", "Sistema", admin_email, admin_pass, "123456789", "administrador", 1, datetime.now().isoformat()))
            
            # Crear usuarios de ejemplo
            usuarios_ejemplo = [
                ("María", "García", "maria@petcare.com", hash_password("maria123"), "555-0101", "dueño", 1),
                ("Carlos", "López", "carlos@petcare.com", hash_password("carlos123"), "555-0102", "cuidador", 1),
                ("Ana", "Martínez", "ana@petcare.com", hash_password("ana123"), "555-0103", "dueño", 1),
                ("Pedro", "Sánchez", "pedro@petcare.com", hash_password("pedro123"), "555-0104", "cuidador", 1),
                ("Laura", "Rodríguez", "laura@petcare.com", hash_password("laura123"), "555-0105", "dueño", 0),
                ("Javier", "Fernández", "javier@petcare.com", hash_password("javier123"), "555-0106", "administrador", 1),
                ("Sofia", "Gómez", "sofia@petcare.com", hash_password("sofia123"), "555-0107", "cuidador", 1),
                ("Diego", "Ruiz", "diego@petcare.com", hash_password("diego123"), "555-0108", "dueño", 1)
            ]
            
            for user in usuarios_ejemplo:
                try:
                    cursor.execute('''
                        INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, activo, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', user + (datetime.now().isoformat(),))
                except sqlite3.IntegrityError:
                    pass  # Si el email ya existe, lo omitimos
            
            db.commit()
            print("✓ Base de datos inicializada con usuarios de ejemplo")
        
        db.commit()

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Inicio de sesión de usuario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Validaciones
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        db = get_db()
        cursor = db.cursor()
        hashed_pass = hash_password(password)
        
        # Buscar usuario por email y contraseña
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            WHERE email = ? AND password = ?
        ''', (email, hashed_pass))
        
        user = cursor.fetchone()
        
        if user:
            # Verificar si el usuario está activo
            if user['activo'] != 1:
                return jsonify({'error': 'Usuario inactivo. Contacte al administrador'}), 401
            
            # Convertir a diccionario y eliminar campos sensibles
            user_dict = dict(user)
            return jsonify(user_dict), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

# ==================== ENDPOINTS DE USUARIOS ====================

@app.route('/api/usuarios', methods=['GET', 'OPTIONS'])
def get_usuarios():
    """Obtener lista de todos los usuarios"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Obtener todos los usuarios ordenados por ID descendente
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            ORDER BY id DESC
        ''')
        
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users]), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuarios: {str(e)}'}), 500

@app.route('/api/usuarios/<int:id>', methods=['GET', 'OPTIONS'])
def get_usuario(id):
    """Obtener un usuario específico por ID"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            WHERE id = ?
        ''', (id,))
        
        user = cursor.fetchone()
        
        if user:
            return jsonify(dict(user)), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuario: {str(e)}'}), 500

@app.route('/api/usuarios', methods=['POST', 'OPTIONS'])
def create_usuario():
    """Crear un nuevo usuario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'email', 'password', 'rol']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar formato de email
        if not validate_email(data['email']):
            return jsonify({'error': 'El formato del email es inválido'}), 400
        
        # Validar longitud de contraseña
        if len(data['password']) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        # Validar rol
        if data['rol'] not in ['dueño', 'cuidador', 'administrador']:
            return jsonify({'error': 'Rol inválido. Debe ser: dueño, cuidador o administrador'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear el usuario
        hashed_password = hash_password(data['password'])
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, foto_url, activo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['nombre'],
            data['apellido'],
            data['email'],
            hashed_password,
            data.get('telefono', ''),
            data['rol'],
            data.get('foto_url', ''),
            data.get('activo', 1),
            created_at
        ))
        
        db.commit()
        user_id = cursor.lastrowid
        
        # Obtener el usuario creado
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            WHERE id = ?
        ''', (user_id,))
        
        new_user = cursor.fetchone()
        return jsonify(dict(new_user)), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'OPTIONS'])
def update_usuario(id):
    """Actualizar un usuario existente"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Construir consulta dinámica
        update_fields = []
        values = []
        
        # Actualizar campos proporcionados
        if 'nombre' in data:
            update_fields.append("nombre = ?")
            values.append(data['nombre'])
        
        if 'apellido' in data:
            update_fields.append("apellido = ?")
            values.append(data['apellido'])
        
        if 'email' in data:
            # Validar email
            if not validate_email(data['email']):
                return jsonify({'error': 'Formato de email inválido'}), 400
            
            # Verificar que el email no esté en uso por otro usuario
            cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (data['email'], id))
            if cursor.fetchone():
                return jsonify({'error': 'El email ya está registrado por otro usuario'}), 409
            
            update_fields.append("email = ?")
            values.append(data['email'])
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
            update_fields.append("password = ?")
            values.append(hash_password(data['password']))
        
        if 'telefono' in data:
            update_fields.append("telefono = ?")
            values.append(data['telefono'])
        
        if 'rol' in data:
            if data['rol'] not in ['dueño', 'cuidador', 'administrador']:
                return jsonify({'error': 'Rol inválido'}), 400
            update_fields.append("rol = ?")
            values.append(data['rol'])
        
        if 'foto_url' in data:
            update_fields.append("foto_url = ?")
            values.append(data['foto_url'])
        
        if 'activo' in data:
            update_fields.append("activo = ?")
            values.append(data['activo'])
        
        # Ejecutar actualización si hay campos para actualizar
        if update_fields:
            values.append(id)
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            db.commit()
        
        # Obtener usuario actualizado
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            WHERE id = ?
        ''', (id,))
        
        updated_user = cursor.fetchone()
        return jsonify(dict(updated_user)), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500

@app.route('/api/usuarios/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_usuario(id):
    """Eliminar un usuario"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT id, email FROM usuarios WHERE id = ?", (id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # No permitir eliminar al administrador principal
        if user['email'] == 'admin@petcare.com':
            return jsonify({'error': 'No se puede eliminar al administrador principal del sistema'}), 403
        
        # Eliminar usuario
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        db.commit()
        
        return jsonify({
            'message': 'Usuario eliminado correctamente',
            'id': id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al eliminar usuario: {str(e)}'}), 500

# ==================== ENDPOINTS ADICIONALES ====================

@app.route('/api/usuarios/rol/<string:rol>', methods=['GET', 'OPTIONS'])
def get_usuarios_by_rol(rol):
    """Obtener usuarios por rol"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if rol not in ['dueño', 'cuidador', 'administrador']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios 
            WHERE rol = ?
            ORDER BY nombre ASC
        ''', (rol,))
        
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users]), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuarios: {str(e)}'}), 500

@app.route('/api/usuarios/estadisticas', methods=['GET', 'OPTIONS'])
def get_estadisticas():
    """Obtener estadísticas de usuarios"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Contar usuarios por rol
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN rol = 'dueño' THEN 1 ELSE 0 END) as duenos,
                SUM(CASE WHEN rol = 'cuidador' THEN 1 ELSE 0 END) as cuidadores,
                SUM(CASE WHEN rol = 'administrador' THEN 1 ELSE 0 END) as administradores,
                SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as activos,
                SUM(CASE WHEN activo = 0 THEN 1 ELSE 0 END) as inactivos
            FROM usuarios
        ''')
        
        stats = cursor.fetchone()
        
        return jsonify(dict(stats)), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

# ==================== MANEJADOR DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== INICIO DE LA APLICACIÓN ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   PETCARE - SISTEMA DE GESTIÓN DE USUARIOS")
    print("="*50)
    
    # Inicializar base de datos
    init_db()
    
    print("\n✅ Base de datos inicializada correctamente")
    print("\n📊 CREDENCIALES DE ACCESO:")
    print("   Email: admin@petcare.com")
    print("   Contraseña: admin123")
    print("\n🔧 ENDPOINTS DISPONIBLES:")
    print("   POST   /api/auth/login")
    print("   GET    /api/usuarios")
    print("   GET    /api/usuarios/<id>")
    print("   POST   /api/usuarios")
    print("   PUT    /api/usuarios/<id>")
    print("   DELETE /api/usuarios/<id>")
    print("   GET    /api/usuarios/rol/<rol>")
    print("   GET    /api/usuarios/estadisticas")
    print("\n🚀 Servidor iniciado en: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='localhost', port=5000, threaded=True)