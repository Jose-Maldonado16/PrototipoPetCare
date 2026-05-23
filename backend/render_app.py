import os
import hashlib
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print(f"🔍 SUPABASE_URL: {'✅ CONFIGURADA' if SUPABASE_URL else '❌ NO CONFIGURADA'}")
print(f"🔍 SUPABASE_KEY: {'✅ CONFIGURADA' if SUPABASE_KEY else '❌ NO CONFIGURADA'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Faltan variables de entorno SUPABASE_URL y SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'supabase_configured': SUPABASE_URL is not None and SUPABASE_KEY is not None,
        'message': 'API funcionando correctamente'
    }), 200

# ==================== ENDPOINTS USUARIOS ====================

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        hashed_pass = hash_password(password)
        
        response = supabase.table('usuarios').select("*").eq('email', email).eq('password', hashed_pass).execute()
        
        if response.data:
            user = response.data[0]
            if user.get('activo', 1) != 1:
                return jsonify({'error': 'Usuario inactivo'}), 401
            del user['password']
            return jsonify(user), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios', methods=['GET', 'OPTIONS'])
def get_usuarios():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        response = supabase.table('usuarios').select("*").order('id', desc=True).execute()
        users = response.data
        for user in users:
            user.pop('password', None)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['GET', 'OPTIONS'])
def get_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        response = supabase.table('usuarios').select("*").eq('id', id).execute()
        if response.data:
            user = response.data[0]
            del user['password']
            return jsonify(user), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios', methods=['POST', 'OPTIONS'])
def create_usuario():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
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
        
        # Verificar si email ya existe
        existing = supabase.table('usuarios').select("id").eq('email', data['email']).execute()
        if existing.data:
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        hashed_pass = hash_password(data['password'])
        
        new_user = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'password': hashed_pass,
            'telefono': data.get('telefono', ''),
            'rol': data['rol'],
            'activo': data.get('activo', 1),
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('usuarios').insert(new_user).execute()
        
        if response.data:
            created_user = response.data[0]
            del created_user['password']
            return jsonify(created_user), 201
        else:
            return jsonify({'error': 'No se pudo crear el usuario'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'OPTIONS'])
def update_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        data = request.get_json()
        
        # Verificar si existe
        existing = supabase.table('usuarios').select("id").eq('id', id).execute()
        if not existing.data:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        update_data = {}
        
        if 'nombre' in data:
            update_data['nombre'] = data['nombre']
        if 'apellido' in data:
            update_data['apellido'] = data['apellido']
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Email inválido'}), 400
            update_data['email'] = data['email']
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'La contraseña debe tener mínimo 6 caracteres'}), 400
            update_data['password'] = hash_password(data['password'])
        if 'telefono' in data:
            update_data['telefono'] = data['telefono']
        if 'rol' in data:
            if data['rol'] not in ['dueño', 'cuidador', 'administrador']:
                return jsonify({'error': 'Rol inválido'}), 400
            update_data['rol'] = data['rol']
        if 'activo' in data:
            update_data['activo'] = data['activo']
        
        if update_data:
            response = supabase.table('usuarios').update(update_data).eq('id', id).execute()
        
        # Obtener usuario actualizado
        updated = supabase.table('usuarios').select("*").eq('id', id).execute()
        if updated.data:
            user = updated.data[0]
            del user['password']
            return jsonify(user), 200
        else:
            return jsonify({'error': 'Error al actualizar'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        # Verificar que no sea el admin principal
        admin_check = supabase.table('usuarios').select("email").eq('id', id).execute()
        if admin_check.data and admin_check.data[0]['email'] == 'admin@petcare.com':
            return jsonify({'error': 'No se puede eliminar al administrador principal'}), 403
        
        response = supabase.table('usuarios').delete().eq('id', id).execute()
        
        if response.data:
            return jsonify({'message': 'Usuario eliminado correctamente'}), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PRODUCTOS ====================

@app.route('/api/productos', methods=['POST', 'OPTIONS'])
def create_producto():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        data = request.get_json()
        
        required = ['titulo', 'descripcion', 'precio', 'categoria', 'ofertante_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        if data['categoria'] not in ['paseo', 'guarderia', 'alojamiento']:
            return jsonify({'error': 'Categoría inválida'}), 400
        
        try:
            precio = float(data['precio'])
            if precio <= 0:
                return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
        except:
            return jsonify({'error': 'Precio inválido'}), 400
        
        # Verificar ofertante
        ofertante = supabase.table('usuarios').select("rol").eq('id', data['ofertante_id']).execute()
        if not ofertante.data:
            return jsonify({'error': 'Ofertante no encontrado'}), 404
        
        new_producto = {
            'titulo': data['titulo'],
            'descripcion': data['descripcion'],
            'precio': precio,
            'categoria': data['categoria'],
            'ofertante_id': data['ofertante_id'],
            'estado': 'pendiente',
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat(),
            'activo': 1
        }
        
        response = supabase.table('productos_servicios').insert(new_producto).execute()
        
        if response.data:
            return jsonify(response.data[0]), 201
        else:
            return jsonify({'error': 'No se pudo crear el producto'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/aprobados', methods=['GET', 'OPTIONS'])
def get_productos_aprobados():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        response = supabase.table('productos_servicios').select("*").eq('estado', 'aprobado').eq('activo', 1).order('fecha_creacion', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/pendientes', methods=['GET', 'OPTIONS'])
def get_productos_pendientes():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        response = supabase.table('productos_servicios').select("*").eq('estado', 'pendiente').eq('activo', 1).order('fecha_creacion', asc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mis-productos/<int:ofertante_id>', methods=['GET', 'OPTIONS'])
def get_mis_productos(ofertante_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        response = supabase.table('productos_servicios').select("*").eq('ofertante_id', ofertante_id).eq('activo', 1).order('fecha_creacion', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>/validar', methods=['PUT', 'OPTIONS'])
def validar_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if not supabase:
            return jsonify({'error': 'Supabase no configurado'}), 500
            
        data = request.get_json()
        estado = data.get('estado')
        motivo_rechazo = data.get('motivo_rechazo')
        
        if estado not in ['aprobado', 'rechazado']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        update_data = {
            'estado': estado,
            'fecha_actualizacion': datetime.now().isoformat()
        }
        
        if estado == 'rechazado' and motivo_rechazo:
            update_data['motivo_rechazo'] = motivo_rechazo
        
        response = supabase.table('productos_servicios').update(update_data).eq('id', id).execute()
        
        if response.data:
            return jsonify({'message': f'Producto {estado} correctamente'}), 200
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== INICIO ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)