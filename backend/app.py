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
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Tabla usuarios (Sprint 1)
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
        
        # Tabla productos_servicios (Sprint 2 - NUEVA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos_servicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                categoria TEXT NOT NULL CHECK(categoria IN ('paseo', 'guarderia', 'alojamiento')),
                ofertante_id INTEGER NOT NULL,
                estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'aprobado', 'rechazado')),
                motivo_rechazo TEXT,
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (ofertante_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Crear índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON usuarios(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_ofertante ON productos_servicios(ofertante_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_estado ON productos_servicios(estado)')
        
        # Usuario administrador por defecto
        admin_email = "admin@petcare.com"
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        if not cursor.fetchone():
            admin_pass = hash_password("admin123")
            cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, activo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Administrador", "Sistema", admin_email, admin_pass, "123456789", "administrador", 1, datetime.now().isoformat()))
        
        # Usuario cuidador de ejemplo (ofertante)
        cuidador_email = "cuidador@petcare.com"
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (cuidador_email,))
        if not cursor.fetchone():
            cuidador_pass = hash_password("cuidador123")
            cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, activo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Carlos", "Cuidador", cuidador_email, cuidador_pass, "77777777", "cuidador", 1, datetime.now().isoformat()))
        
        db.commit()
        print("✓ Base de datos inicializada con tablas de usuarios y productos/servicios")

# ==================== ENDPOINTS USUARIOS (Sprint 1) ====================

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        db = get_db()
        cursor = db.cursor()
        hashed_pass = hash_password(password)
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios WHERE email = ? AND password = ?
        ''', (email, hashed_pass))
        
        user = cursor.fetchone()
        if user:
            if user['activo'] != 1:
                return jsonify({'error': 'Usuario inactivo'}), 401
            return jsonify(dict(user)), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios', methods=['GET', 'OPTIONS'])
def get_usuarios():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios ORDER BY id DESC
        ''')
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['GET', 'OPTIONS'])
def get_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios WHERE id = ?
        ''', (id,))
        user = cursor.fetchone()
        if user:
            return jsonify(dict(user)), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios', methods=['POST', 'OPTIONS'])
def create_usuario():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        required = ['nombre', 'apellido', 'email', 'password', 'rol']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'La contraseña debe tener mínimo 6 caracteres'}), 400
        
        if data['rol'] not in ['dueño', 'cuidador', 'administrador']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        hashed_pass = hash_password(data['password'])
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, password, telefono, rol, foto_url, activo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['nombre'], data['apellido'], data['email'], hashed_pass, 
              data.get('telefono', ''), data['rol'], data.get('foto_url', ''), 
              data.get('activo', 1), created_at))
        
        db.commit()
        user_id = cursor.lastrowid
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios WHERE id = ?
        ''', (user_id,))
        new_user = cursor.fetchone()
        
        return jsonify(dict(new_user)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'OPTIONS'])
def update_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Email inválido'}), 400
            cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (data['email'], id))
            if cursor.fetchone():
                return jsonify({'error': 'El email ya está registrado'}), 409
        
        update_fields = []
        values = []
        
        if 'nombre' in data:
            update_fields.append("nombre = ?")
            values.append(data['nombre'])
        if 'apellido' in data:
            update_fields.append("apellido = ?")
            values.append(data['apellido'])
        if 'email' in data:
            update_fields.append("email = ?")
            values.append(data['email'])
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'La contraseña debe tener mínimo 6 caracteres'}), 400
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
        
        if update_fields:
            values.append(id)
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            db.commit()
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol, foto_url, activo, created_at 
            FROM usuarios WHERE id = ?
        ''', (id,))
        updated_user = cursor.fetchone()
        
        return jsonify(dict(updated_user)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id, email FROM usuarios WHERE id = ?", (id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user['email'] == 'admin@petcare.com':
            return jsonify({'error': 'No se puede eliminar al administrador principal'}), 403
        
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        db.commit()
        
        return jsonify({'message': 'Usuario eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PRODUCTOS/SERVICIOS (Sprint 2 - NUEVOS) ====================

@app.route('/api/productos', methods=['POST', 'OPTIONS'])
def create_producto():
    """HU-01: Registrar producto/servicio (Ofertante) - Estado inicial: pendiente"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required = ['titulo', 'descripcion', 'precio', 'categoria', 'ofertante_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar categoría
        if data['categoria'] not in ['paseo', 'guarderia', 'alojamiento']:
            return jsonify({'error': 'Categoría inválida. Debe ser: paseo, guarderia o alojamiento'}), 400
        
        # Validar precio
        try:
            precio = float(data['precio'])
            if precio <= 0:
                return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
        except:
            return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verificar que el ofertante existe y es cuidador o administrador
        cursor.execute("SELECT id, rol FROM usuarios WHERE id = ?", (data['ofertante_id'],))
        ofertante = cursor.fetchone()
        if not ofertante:
            return jsonify({'error': 'Ofertante no encontrado'}), 404
        
        if ofertante['rol'] not in ['cuidador', 'administrador']:
            return jsonify({'error': 'Solo los cuidadores o administradores pueden ofertar servicios'}), 403
        
        # Crear producto con estado 'pendiente' (HU-01)
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO productos_servicios (titulo, descripcion, precio, categoria, ofertante_id, estado, fecha_creacion, fecha_actualizacion, activo)
            VALUES (?, ?, ?, ?, ?, 'pendiente', ?, ?, 1)
        ''', (data['titulo'], data['descripcion'], precio, data['categoria'], data['ofertante_id'], now, now))
        
        db.commit()
        producto_id = cursor.lastrowid
        
        # Obtener producto creado
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido 
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.id = ?
        ''', (producto_id,))
        
        producto = cursor.fetchone()
        return jsonify(dict(producto)), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos', methods=['GET', 'OPTIONS'])
def get_productos():
    """Listar productos con filtros opcionales"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        estado = request.args.get('estado')
        ofertante_id = request.args.get('ofertante_id')
        
        query = '''
            SELECT p.*, u.nombre, u.apellido, u.telefono
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.activo = 1
        '''
        params = []
        
        if estado:
            query += " AND p.estado = ?"
            params.append(estado)
        
        if ofertante_id:
            query += " AND p.ofertante_id = ?"
            params.append(ofertante_id)
        
        query += " ORDER BY p.fecha_creacion DESC"
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        
        return jsonify([dict(p) for p in productos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET', 'OPTIONS'])
def get_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido, u.telefono, u.email
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.id = ?
        ''', (id,))
        
        producto = cursor.fetchone()
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify(dict(producto)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['PUT', 'OPTIONS'])
def update_producto(id):
    """HU-02: Editar producto - Edición crítica cambia estado a pendiente"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        
        # Verificar que el producto existe
        cursor.execute("SELECT * FROM productos_servicios WHERE id = ?", (id,))
        producto_original = cursor.fetchone()
        if not producto_original:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Campos críticos (si cambian, el estado vuelve a pendiente)
        campos_criticos = ['titulo', 'descripcion', 'precio', 'categoria']
        cambios_criticos = False
        
        update_fields = []
        values = []
        
        for campo in campos_criticos:
            if campo in data and data[campo] != producto_original[campo]:
                cambios_criticos = True
                break
        
        # Construir UPDATE dinámico
        if 'titulo' in data:
            update_fields.append("titulo = ?")
            values.append(data['titulo'])
        
        if 'descripcion' in data:
            update_fields.append("descripcion = ?")
            values.append(data['descripcion'])
        
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio <= 0:
                    return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
                update_fields.append("precio = ?")
                values.append(precio)
            except:
                return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        if 'categoria' in data:
            if data['categoria'] not in ['paseo', 'guarderia', 'alojamiento']:
                return jsonify({'error': 'Categoría inválida'}), 400
            update_fields.append("categoria = ?")
            values.append(data['categoria'])
        
        # Siempre actualizar fecha
        update_fields.append("fecha_actualizacion = ?")
        values.append(datetime.now().isoformat())
        
        # Si hubo cambios críticos, cambiar estado a pendiente (HU-02)
        if cambios_criticos and producto_original['estado'] == 'aprobado':
            update_fields.append("estado = ?")
            values.append('pendiente')
            update_fields.append("motivo_rechazo = ?")
            values.append(None)
        
        if not update_fields:
            return jsonify({'message': 'No se realizaron cambios'}), 200
        
        values.append(id)
        query = f"UPDATE productos_servicios SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        db.commit()
        
        # Obtener producto actualizado
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido 
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.id = ?
        ''', (id,))
        
        producto = cursor.fetchone()
        return jsonify(dict(producto)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_producto(id):
    """HU-02: Eliminar producto (soft delete)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM productos_servicios WHERE id = ?", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Soft delete (activate en lugar de eliminar)
        cursor.execute("UPDATE productos_servicios SET activo = 0 WHERE id = ?", (id,))
        db.commit()
        
        return jsonify({'message': 'Producto eliminado correctamente'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>/validar', methods=['PUT', 'OPTIONS'])
def validar_producto(id):
    """HU-03: Administrador valida producto (aprobar/rechazar)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        estado = data.get('estado')
        motivo_rechazo = data.get('motivo_rechazo')
        
        if estado not in ['aprobado', 'rechazado']:
            return jsonify({'error': 'Estado inválido. Debe ser aprobado o rechazado'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM productos_servicios WHERE id = ?", (id,))
        producto = cursor.fetchone()
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Si es rechazado, requiere motivo
        if estado == 'rechazado' and not motivo_rechazo:
            return jsonify({'error': 'Debe proporcionar un motivo de rechazo'}), 400
        
        cursor.execute('''
            UPDATE productos_servicios 
            SET estado = ?, motivo_rechazo = ?, fecha_actualizacion = ?
            WHERE id = ?
        ''', (estado, motivo_rechazo, datetime.now().isoformat(), id))
        
        db.commit()
        
        return jsonify({
            'message': f'Producto {estado} correctamente',
            'estado': estado,
            'motivo_rechazo': motivo_rechazo
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/pendientes', methods=['GET', 'OPTIONS'])
def get_productos_pendientes():
    """HU-03: Obtener productos pendientes para validación"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido, u.email, u.telefono
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.estado = 'pendiente' AND p.activo = 1
            ORDER BY p.fecha_creacion ASC
        ''')
        
        productos = cursor.fetchall()
        return jsonify([dict(p) for p in productos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mis-productos/<int:ofertante_id>', methods=['GET', 'OPTIONS'])
def get_mis_productos(ofertante_id):
    """Obtener productos de un ofertante específico"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.ofertante_id = ? AND p.activo = 1
            ORDER BY p.fecha_creacion DESC
        ''', (ofertante_id,))
        
        productos = cursor.fetchall()
        return jsonify([dict(p) for p in productos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/aprobados', methods=['GET', 'OPTIONS'])
def get_productos_aprobados():
    """Productos aprobados (visibles para demandantes)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT p.*, u.nombre, u.apellido, u.telefono
            FROM productos_servicios p
            JOIN usuarios u ON p.ofertante_id = u.id
            WHERE p.estado = 'aprobado' AND p.activo = 1
            ORDER BY p.fecha_creacion DESC
        ''')
        
        productos = cursor.fetchall()
        return jsonify([dict(p) for p in productos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== INICIO ====================

if __name__ == '__main__':
    import os
    if os.path.exists(DATABASE):
        print("Base de datos existente encontrada. Actualizando...")
        # No eliminamos, solo agregamos la tabla nueva si no existe
    else:
        print("Creando nueva base de datos...")
    
    init_db()
    print("\n" + "="*50)
    print("   PETCARE CONNECT - SPRINT 2")
    print("="*50)
    print("\n✅ Base de datos inicializada")
    print("\n📊 CREDENCIALES DE ACCESO:")
    print("   Admin: admin@petcare.com / admin123")
    print("   Cuidador: cuidador@petcare.com / cuidador123")
    print("\n🔧 NUEVOS ENDPOINTS SPRINT 2:")
    print("   POST   /api/productos")
    print("   GET    /api/productos")
    print("   GET    /api/productos/<id>")
    print("   PUT    /api/productos/<id>")
    print("   DELETE /api/productos/<id>")
    print("   PUT    /api/productos/<id>/validar")
    print("   GET    /api/productos/pendientes")
    print("   GET    /api/mis-productos/<ofertante_id>")
    print("   GET    /api/productos/aprobados")
    print("\n🚀 Servidor iniciado en: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='localhost', port=5000, threaded=True)