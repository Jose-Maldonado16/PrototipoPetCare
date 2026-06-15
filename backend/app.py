"""
PETCARE CONNECT - API COMPLETA
Sprints 1, 2 y 3 - Usuarios, Productos, Solicitudes, Calificaciones
"""

import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

# ==================== SERVIR FRONTEND ====================
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('../frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('../frontend/js', filename)

# ==================== CONEXIÓN SUPABASE ====================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL y SUPABASE_KEY deben estar en .env")
    print("SUPABASE_URL:", SUPABASE_URL)
    print("SUPABASE_KEY:", SUPABASE_KEY)
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"✅ Conectado a Supabase: {SUPABASE_URL}")

# ==================== FUNCIONES DE AYUDA ====================

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ==================== ENDPOINTS USUARIOS (SPRINT 1) ====================

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
        
        response = supabase.table('usuarios').select('*').eq('email', email).eq('password', password).execute()
        
        if response.data:
            user = response.data[0]
            if user['activo'] != 1:
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
        response = supabase.table('usuarios').select('*').order('id', desc=True).execute()
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
        response = supabase.table('usuarios').select('*').eq('id', id).execute()
        if response.data:
            user = response.data[0]
            user.pop('password', None)
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
        
        existing = supabase.table('usuarios').select('id').eq('email', data['email']).execute()
        if existing.data:
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        new_user = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'password': data['password'],
            'telefono': data.get('telefono', ''),
            'rol': data['rol'],
            'foto_url': data.get('foto_url', ''),
            'activo': data.get('activo', 1)
        }
        
        response = supabase.table('usuarios').insert(new_user).execute()
        
        if response.data:
            created_user = response.data[0]
            created_user.pop('password', None)
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
        data = request.get_json()
        
        existing = supabase.table('usuarios').select('id').eq('id', id).execute()
        if not existing.data:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Email inválido'}), 400
            
            email_check = supabase.table('usuarios').select('id').eq('email', data['email']).neq('id', id).execute()
            if email_check.data:
                return jsonify({'error': 'El email ya está registrado'}), 409
        
        update_data = {}
        
        if 'nombre' in data:
            update_data['nombre'] = data['nombre']
        if 'apellido' in data:
            update_data['apellido'] = data['apellido']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'La contraseña debe tener mínimo 6 caracteres'}), 400
            update_data['password'] = data['password']
        if 'telefono' in data:
            update_data['telefono'] = data['telefono']
        if 'rol' in data:
            if data['rol'] not in ['dueño', 'cuidador', 'administrador']:
                return jsonify({'error': 'Rol inválido'}), 400
            update_data['rol'] = data['rol']
        if 'foto_url' in data:
            update_data['foto_url'] = data['foto_url']
        if 'activo' in data:
            update_data['activo'] = data['activo']
        
        if not update_data:
            return jsonify({'message': 'No se realizaron cambios'}), 200
        
        response = supabase.table('usuarios').update(update_data).eq('id', id).execute()
        
        if response.data:
            updated_user = response.data[0]
            updated_user.pop('password', None)
            return jsonify(updated_user), 200
        else:
            return jsonify({'error': 'No se pudo actualizar'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_usuario(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        user = supabase.table('usuarios').select('email').eq('id', id).execute()
        
        if not user.data:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user.data[0]['email'] == 'admin@petcare.com':
            return jsonify({'error': 'No se puede eliminar al administrador principal'}), 403
        
        supabase.table('usuarios').delete().eq('id', id).execute()
        
        return jsonify({'message': 'Usuario eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PRODUCTOS (SPRINT 2) ====================

@app.route('/api/productos', methods=['POST', 'OPTIONS'])
def create_producto():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        required = ['titulo', 'descripcion', 'precio', 'categoria', 'ofertante_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        if data['categoria'] not in ['paseo', 'guarderia', 'alojamiento']:
            return jsonify({'error': 'Categoría inválida'}), 400
        
        try:
            precio = float(data['precio'])
            if precio <= 0:
                return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
        except:
            return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        ofertante = supabase.table('usuarios').select('id, rol').eq('id', data['ofertante_id']).execute()
        
        if not ofertante.data:
            return jsonify({'error': 'Ofertante no encontrado'}), 404
        
        if ofertante.data[0]['rol'] not in ['cuidador', 'administrador']:
            return jsonify({'error': 'Solo los cuidadores pueden ofertar servicios'}), 403
        
        new_producto = {
            'titulo': data['titulo'],
            'descripcion': data['descripcion'],
            'precio': precio,
            'categoria': data['categoria'],
            'ofertante_id': data['ofertante_id'],
            'estado': 'pendiente',
            'activo': 1
        }
        
        response = supabase.table('productos_servicios').insert(new_producto).execute()
        
        if response.data:
            return jsonify(response.data[0]), 201
        else:
            return jsonify({'error': 'No se pudo crear el producto'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos', methods=['GET', 'OPTIONS'])
def get_productos():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        estado = request.args.get('estado')
        ofertante_id = request.args.get('ofertante_id')
        
        query = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido, telefono)').eq('activo', 1)
        
        if estado:
            query = query.eq('estado', estado)
        if ofertante_id:
            query = query.eq('ofertante_id', ofertante_id)
        
        response = query.order('fecha_creacion', desc=True).execute()
        
        productos = response.data
        for p in productos:
            if 'usuarios' in p and p['usuarios']:
                p['nombre'] = p['usuarios']['nombre']
                p['apellido'] = p['usuarios']['apellido']
                p['telefono'] = p['usuarios']['telefono']
            del p['usuarios']
        
        return jsonify(productos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET', 'OPTIONS'])
def get_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido, telefono, email)').eq('id', id).execute()
        
        if response.data:
            producto = response.data[0]
            if 'usuarios' in producto and producto['usuarios']:
                producto['nombre'] = producto['usuarios']['nombre']
                producto['apellido'] = producto['usuarios']['apellido']
                producto['telefono'] = producto['usuarios']['telefono']
                producto['email'] = producto['usuarios']['email']
            del producto['usuarios']
            return jsonify(producto), 200
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['PUT', 'OPTIONS'])
def update_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        original = supabase.table('productos_servicios').select('*').eq('id', id).execute()
        
        if not original.data:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        original_producto = original.data[0]
        
        campos_criticos = ['titulo', 'descripcion', 'precio', 'categoria']
        cambios_criticos = False
        
        update_data = {}
        
        if 'titulo' in data:
            update_data['titulo'] = data['titulo']
            if data['titulo'] != original_producto['titulo']:
                cambios_criticos = True
        
        if 'descripcion' in data:
            update_data['descripcion'] = data['descripcion']
            if data['descripcion'] != original_producto['descripcion']:
                cambios_criticos = True
        
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio <= 0:
                    return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
                update_data['precio'] = precio
                if precio != original_producto['precio']:
                    cambios_criticos = True
            except:
                return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        if 'categoria' in data:
            if data['categoria'] not in ['paseo', 'guarderia', 'alojamiento']:
                return jsonify({'error': 'Categoría inválida'}), 400
            update_data['categoria'] = data['categoria']
            if data['categoria'] != original_producto['categoria']:
                cambios_criticos = True
        
        update_data['fecha_actualizacion'] = datetime.now().isoformat()
        
        if cambios_criticos and original_producto['estado'] == 'aprobado':
            update_data['estado'] = 'pendiente'
            update_data['motivo_rechazo'] = None
        
        if not update_data:
            return jsonify({'message': 'No se realizaron cambios'}), 200
        
        response = supabase.table('productos_servicios').update(update_data).eq('id', id).execute()
        
        if response.data:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({'error': 'No se pudo actualizar'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        existing = supabase.table('productos_servicios').select('id').eq('id', id).execute()
        if not existing.data:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        supabase.table('productos_servicios').update({'activo': 0}).eq('id', id).execute()
        
        return jsonify({'message': 'Producto eliminado correctamente'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>/validar', methods=['PUT', 'OPTIONS'])
def validar_producto(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        estado = data.get('estado')
        motivo_rechazo = data.get('motivo_rechazo')
        
        if estado not in ['aprobado', 'rechazado']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        existing = supabase.table('productos_servicios').select('id').eq('id', id).execute()
        if not existing.data:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        if estado == 'rechazado' and not motivo_rechazo:
            return jsonify({'error': 'Debe proporcionar un motivo de rechazo'}), 400
        
        update_data = {
            'estado': estado,
            'fecha_actualizacion': datetime.now().isoformat()
        }
        
        if motivo_rechazo:
            update_data['motivo_rechazo'] = motivo_rechazo
        
        supabase.table('productos_servicios').update(update_data).eq('id', id).execute()
        
        return jsonify({'message': f'Producto {estado} correctamente'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/pendientes', methods=['GET', 'OPTIONS'])
def get_productos_pendientes():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido, email, telefono)').eq('estado', 'pendiente').eq('activo', 1).order('fecha_creacion').execute()
        
        productos = response.data
        for p in productos:
            if 'usuarios' in p and p['usuarios']:
                p['nombre'] = p['usuarios']['nombre']
                p['apellido'] = p['usuarios']['apellido']
                p['email'] = p['usuarios']['email']
                p['telefono'] = p['usuarios']['telefono']
            del p['usuarios']
        
        return jsonify(productos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mis-productos/<int:ofertante_id>', methods=['GET', 'OPTIONS'])
def get_mis_productos(ofertante_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido)').eq('ofertante_id', ofertante_id).eq('activo', 1).order('fecha_creacion', desc=True).execute()
        
        productos = response.data
        for p in productos:
            if 'usuarios' in p and p['usuarios']:
                p['nombre'] = p['usuarios']['nombre']
                p['apellido'] = p['usuarios']['apellido']
            del p['usuarios']
        
        return jsonify(productos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/aprobados', methods=['GET', 'OPTIONS'])
def get_productos_aprobados():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido, telefono)').eq('estado', 'aprobado').eq('activo', 1).order('fecha_creacion', desc=True).execute()
        
        productos = response.data
        for p in productos:
            if 'usuarios' in p and p['usuarios']:
                p['nombre'] = p['usuarios']['nombre']
                p['apellido'] = p['usuarios']['apellido']
                p['telefono'] = p['usuarios']['telefono']
            del p['usuarios']
        
        return jsonify(productos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SPRINT 3 - SOLICITUDES Y BÚSQUEDA ====================

@app.route('/api/productos/buscar', methods=['GET', 'OPTIONS'])
def buscar_productos():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        filtro = request.args.get('filtro', 'recientes')
        categoria = request.args.get('categoria')
        busqueda = request.args.get('busqueda')
        
        query = supabase.table('productos_servicios').select('*, usuarios(nombre, apellido, telefono, email)').eq('estado', 'aprobado').eq('activo', 1)
        
        if categoria and categoria != 'todos':
            query = query.eq('categoria', categoria)
        
        if busqueda:
            query = query.ilike('titulo', f'%{busqueda}%')
        
        if filtro == 'recientes':
            query = query.order('fecha_creacion', desc=True)
        elif filtro == 'populares':
            query = query.order('total_solicitudes', desc=True)
        elif filtro == 'mejor_calificados':
            query = query.order('promedio_calificacion', desc=True)
        
        response = query.execute()
        
        productos = response.data
        for p in productos:
            if 'usuarios' in p and p['usuarios']:
                p['nombre_cuidador'] = p['usuarios']['nombre']
                p['apellido_cuidador'] = p['usuarios']['apellido']
                p['telefono_cuidador'] = p['usuarios']['telefono']
                p['email_cuidador'] = p['usuarios']['email']
            del p['usuarios']
        
        return jsonify(productos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solicitudes', methods=['POST', 'OPTIONS'])
def crear_solicitud():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        required = ['producto_id', 'solicitante_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        producto = supabase.table('productos_servicios').select('*, usuarios(email, nombre, apellido)').eq('id', data['producto_id']).eq('estado', 'aprobado').execute()
        
        if not producto.data:
            return jsonify({'error': 'Producto no disponible'}), 404
        
        producto_data = producto.data[0]
        ofertante_id = producto_data['ofertante_id']
        
        solicitante = supabase.table('usuarios').select('rol').eq('id', data['solicitante_id']).execute()
        if not solicitante.data or solicitante.data[0]['rol'] != 'dueño':
            return jsonify({'error': 'Solo los dueños pueden solicitar servicios'}), 403
        
        existing = supabase.table('solicitudes').select('id').eq('producto_id', data['producto_id']).eq('solicitante_id', data['solicitante_id']).eq('estado', 'pendiente').execute()
        if existing.data:
            return jsonify({'error': 'Ya tienes una solicitud pendiente para este servicio'}), 409
        
        nueva_solicitud = {
            'producto_id': data['producto_id'],
            'solicitante_id': data['solicitante_id'],
            'mensaje': data.get('mensaje', ''),
            'estado': 'pendiente',
            'activo': 1
        }
        
        response = supabase.table('solicitudes').insert(nueva_solicitud).execute()
        
        if response.data:
            solicitud = response.data[0]
            
            supabase.table('notificaciones').insert({
                'usuario_id': ofertante_id,
                'tipo': 'solicitud_nueva',
                'titulo': 'Nueva solicitud de servicio',
                'mensaje': f'El dueño {solicitante.data[0]["nombre"]} ha solicitado tu servicio "{producto_data["titulo"]}"',
                'data_extra': {'solicitud_id': solicitud['id'], 'producto_id': data['producto_id']}
            }).execute()
            
            return jsonify(solicitud), 201
        else:
            return jsonify({'error': 'No se pudo crear la solicitud'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mis-solicitudes', methods=['GET', 'OPTIONS'])
def get_mis_solicitudes():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        solicitante_id = request.args.get('solicitante_id')
        if not solicitante_id:
            return jsonify({'error': 'solicitante_id es requerido'}), 400
        
        # ✅ CORREGIDO: usar 'usuarios' en lugar de 'usuarios_solicitante'
        response = supabase.table('solicitudes').select('*, productos_servicios(titulo, precio, categoria, usuarios(nombre, apellido, email))').eq('solicitante_id', solicitante_id).eq('activo', 1).order('fecha_solicitud', desc=True).execute()
        
        solicitudes = response.data
        for s in solicitudes:
            if 'productos_servicios' in s:
                s['producto_titulo'] = s['productos_servicios']['titulo']
                s['producto_precio'] = s['productos_servicios']['precio']
                s['producto_categoria'] = s['productos_servicios']['categoria']
                if 'usuarios' in s['productos_servicios']:
                    s['cuidador_nombre'] = s['productos_servicios']['usuarios']['nombre']
                    s['cuidador_apellido'] = s['productos_servicios']['usuarios']['apellido']
                    s['cuidador_email'] = s['productos_servicios']['usuarios']['email']
            del s['productos_servicios']
        
        return jsonify(solicitudes), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solicitudes-recibidas', methods=['GET', 'OPTIONS'])
def get_solicitudes_recibidas():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        cuidador_id = request.args.get('cuidador_id')
        if not cuidador_id:
            return jsonify({'error': 'cuidador_id es requerido'}), 400
        
        # Obtener productos del cuidador
        productos = supabase.table('productos_servicios').select('id').eq('ofertante_id', cuidador_id).execute()
        productos_ids = [p['id'] for p in productos.data] if productos.data else []
        
        if not productos_ids:
            return jsonify([]), 200
        
        # ✅ CORREGIDO: usar 'usuarios' en lugar de 'usuarios_solicitante'
        response = supabase.table('solicitudes').select('*, productos_servicios(titulo, precio, categoria), usuarios!solicitudes_solicitante_id_fkey(nombre, apellido, email, telefono)').in_('producto_id', productos_ids).eq('activo', 1).order('fecha_solicitud', desc=True).execute()
        
        solicitudes = response.data
        for s in solicitudes:
            if 'productos_servicios' in s:
                s['producto_titulo'] = s['productos_servicios']['titulo']
                s['producto_precio'] = s['productos_servicios']['precio']
                s['producto_categoria'] = s['productos_servicios']['categoria']
            del s['productos_servicios']
            
            # ✅ CORREGIDO: acceder a los datos del usuario
            if 'usuarios' in s:
                s['solicitante_nombre'] = s['usuarios']['nombre']
                s['solicitante_apellido'] = s['usuarios']['apellido']
                s['solicitante_email'] = s['usuarios']['email']
                s['solicitante_telefono'] = s['usuarios']['telefono']
            del s['usuarios']
        
        return jsonify(solicitudes), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solicitudes/<int:id>/responder', methods=['PUT', 'OPTIONS'])
def responder_solicitud(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        estado = data.get('estado')
        motivo_rechazo = data.get('motivo_rechazo')
        
        if estado not in ['aceptado', 'rechazado']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        if estado == 'rechazado' and not motivo_rechazo:
            return jsonify({'error': 'Debe proporcionar un motivo de rechazo'}), 400
        
        solicitud = supabase.table('solicitudes').select('*, productos_servicios(titulo, ofertante_id), solicitante_id').eq('id', id).execute()
        
        if not solicitud.data:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
        
        solicitud_data = solicitud.data[0]
        
        update_data = {
            'estado': estado,
            'fecha_respuesta': datetime.now().isoformat()
        }
        
        if motivo_rechazo:
            update_data['motivo_rechazo'] = motivo_rechazo
        
        response = supabase.table('solicitudes').update(update_data).eq('id', id).execute()
        
        if response.data:
            producto = solicitud_data.get('productos_servicios', {})
            titulo = 'Solicitud aceptada' if estado == 'aceptado' else 'Solicitud rechazada'
            mensaje = f'Tu solicitud para "{producto.get("titulo", "el servicio")}" ha sido {estado}'
            if estado == 'rechazado':
                mensaje += f'. Motivo: {motivo_rechazo}'
            
            supabase.table('notificaciones').insert({
                'usuario_id': solicitud_data['solicitante_id'],
                'tipo': 'solicitud_respondida',
                'titulo': titulo,
                'mensaje': mensaje,
                'data_extra': {'solicitud_id': id, 'estado': estado}
            }).execute()
            
            return jsonify(response.data[0]), 200
        else:
            return jsonify({'error': 'No se pudo actualizar'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones', methods=['GET', 'OPTIONS'])
def get_notificaciones():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        usuario_id = request.args.get('usuario_id')
        if not usuario_id:
            return jsonify({'error': 'usuario_id es requerido'}), 400
        
        response = supabase.table('notificaciones').select('*').eq('usuario_id', usuario_id).order('fecha', desc=True).execute()
        
        return jsonify(response.data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/<int:id>/leer', methods=['PUT', 'OPTIONS'])
def marcar_notificacion_leida(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('notificaciones').update({'leido': 1}).eq('id', id).execute()
        
        if response.data:
            return jsonify({'message': 'Notificación marcada como leída'}), 200
        else:
            return jsonify({'error': 'Notificación no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calificaciones', methods=['POST', 'OPTIONS'])
def crear_calificacion():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        required = ['solicitud_id', 'cuidador_id', 'solicitante_id', 'puntuacion']
        for field in required:
            if field not in data:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        if data['puntuacion'] < 1 or data['puntuacion'] > 5:
            return jsonify({'error': 'La puntuación debe ser entre 1 y 5'}), 400
        
        solicitud = supabase.table('solicitudes').select('estado').eq('id', data['solicitud_id']).execute()
        if not solicitud.data or solicitud.data[0]['estado'] != 'aceptado':
            return jsonify({'error': 'Solo se pueden calificar servicios aceptados'}), 400
        
        existing = supabase.table('calificaciones').select('id').eq('solicitud_id', data['solicitud_id']).execute()
        if existing.data:
            return jsonify({'error': 'Ya calificaste este servicio'}), 409
        
        nueva_calificacion = {
            'cuidador_id': data['cuidador_id'],
            'solicitante_id': data['solicitante_id'],
            'solicitud_id': data['solicitud_id'],
            'puntuacion': data['puntuacion'],
            'comentario': data.get('comentario', '')
        }
        
        response = supabase.table('calificaciones').insert(nueva_calificacion).execute()
        
        if response.data:
            supabase.table('solicitudes').update({
                'estado': 'completado',
                'fecha_completado': datetime.now().isoformat()
            }).eq('id', data['solicitud_id']).execute()
            
            return jsonify(response.data[0]), 201
        else:
            return jsonify({'error': 'No se pudo crear la calificación'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calificaciones/cuidador/<int:cuidador_id>', methods=['GET', 'OPTIONS'])
def get_calificaciones_cuidador(cuidador_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        response = supabase.table('calificaciones').select('*, usuarios_solicitante!calificaciones_solicitante_id_fkey(nombre, apellido)').eq('cuidador_id', cuidador_id).order('fecha', desc=True).execute()
        
        calificaciones = response.data
        for c in calificaciones:
            if 'usuarios_solicitante' in c:
                c['solicitante_nombre'] = c['usuarios_solicitante']['nombre']
                c['solicitante_apellido'] = c['usuarios_solicitante']['apellido']
            del c['usuarios_solicitante']
        
        if calificaciones:
            promedio = sum(c['puntuacion'] for c in calificaciones) / len(calificaciones)
        else:
            promedio = 0
        
        return jsonify({
            'calificaciones': calificaciones,
            'promedio': round(promedio, 2),
            'total': len(calificaciones)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/solicitudes/<int:id>', methods=['GET', 'OPTIONS'])
def get_solicitud(id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # ✅ CORREGIDO: usar 'usuarios' en lugar de 'usuarios_solicitante'
        response = supabase.table('solicitudes').select('*, productos_servicios(*), usuarios!solicitudes_solicitante_id_fkey(nombre, apellido, email, telefono)').eq('id', id).execute()
        
        if response.data:
            solicitud = response.data[0]
            if 'productos_servicios' in solicitud:
                solicitud['producto'] = solicitud['productos_servicios']
            del solicitud['productos_servicios']
            
            if 'usuarios' in solicitud:
                solicitud['solicitante'] = solicitud['usuarios']
            del solicitud['usuarios']
            
            return jsonify(solicitud), 200
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ==================== INICIO ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   🐾 PETCARE CONNECT - SPRINTS 1, 2 y 3")
    print("="*60)
    print(f"\n🔌 Conectado a Supabase: {SUPABASE_URL}")
    print("\n📊 CREDENCIALES DE ACCESO:")
    print("   Admin: admin@petcare.com / admin123")
    print("   Cuidador: cuidador@petcare.com / cuidador123")
    print("   Dueño: dueno@petcare.com / dueno123")
    print("="*60)
    
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Servidor iniciado en puerto: {port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

    #RESUMEN EN UNA FRASE
#Fetch es la forma en que JavaScript pide datos a un servidor y espera a que le respondan.
#El backend es un programa en Python que escucha peticiones, valida datos, habla con la base de datos y devuelve respuestas.
