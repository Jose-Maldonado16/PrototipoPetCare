const API_BASE_URL = '/api';

export const api = {
    // ==================== USUARIOS ====================
    async login(email, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error en el inicio de sesión');
        }
        return await response.json();
    },
    
    async getUsuarios() {
        const response = await fetch(`${API_BASE_URL}/usuarios`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener usuarios');
        }
        return await response.json();
    },
    
    async getUsuario(id) {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener usuario');
        }
        return await response.json();
    },
    
    async createUsuario(usuarioData) {
        const response = await fetch(`${API_BASE_URL}/usuarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(usuarioData)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear usuario');
        }
        return await response.json();
    },
    
    async updateUsuario(id, usuarioData) {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(usuarioData)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al actualizar usuario');
        }
        return await response.json();
    },
    
    async deleteUsuario(id) {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al eliminar usuario');
        }
        return await response.json();
    },
    
    // ==================== PRODUCTOS ====================
    async createProducto(data) {
        const response = await fetch(`${API_BASE_URL}/productos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear producto');
        }
        return await response.json();
    },
    
    async getProductos(estado = null, ofertanteId = null) {
        let url = `${API_BASE_URL}/productos?`;
        if (estado) url += `estado=${estado}&`;
        if (ofertanteId) url += `ofertante_id=${ofertanteId}&`;
        const response = await fetch(url);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener productos');
        }
        return await response.json();
    },
    
    async getProducto(id) {
        const response = await fetch(`${API_BASE_URL}/productos/${id}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener producto');
        }
        return await response.json();
    },
    
    async updateProducto(id, data) {
        const response = await fetch(`${API_BASE_URL}/productos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al actualizar producto');
        }
        return await response.json();
    },
    
    async deleteProducto(id) {
        const response = await fetch(`${API_BASE_URL}/productos/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al eliminar producto');
        }
        return await response.json();
    },
    
    async validarProducto(id, estado, motivoRechazo = null) {
        const response = await fetch(`${API_BASE_URL}/productos/${id}/validar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado, motivo_rechazo: motivoRechazo })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al validar producto');
        }
        return await response.json();
    },
    
    async getProductosPendientes() {
        const response = await fetch(`${API_BASE_URL}/productos/pendientes`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener productos pendientes');
        }
        return await response.json();
    },
    
    async getMisProductos(ofertanteId) {
        const response = await fetch(`${API_BASE_URL}/mis-productos/${ofertanteId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener mis productos');
        }
        return await response.json();
    },
    
    async getProductosAprobados() {
        const response = await fetch(`${API_BASE_URL}/productos/aprobados`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener productos aprobados');
        }
        return await response.json();
    },
    
    // ==================== SPRINT 3 - SOLICITUDES ====================
    async buscarProductos(filtro = 'recientes', categoria = null, busqueda = null) {
        let url = `${API_BASE_URL}/productos/buscar?filtro=${filtro}`;
        if (categoria && categoria !== 'todos') url += `&categoria=${categoria}`;
        if (busqueda) url += `&busqueda=${encodeURIComponent(busqueda)}`;
        const response = await fetch(url);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al buscar productos');
        }
        return await response.json();
    },
    
    async crearSolicitud(data) {
        const response = await fetch(`${API_BASE_URL}/solicitudes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear solicitud');
        }
        return await response.json();
    },
    
    async getMisSolicitudes(solicitanteId) {
        const response = await fetch(`${API_BASE_URL}/mis-solicitudes?solicitante_id=${solicitanteId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener solicitudes');
        }
        return await response.json();
    },
    
    async getSolicitudesRecibidas(cuidadorId) {
        const response = await fetch(`${API_BASE_URL}/solicitudes-recibidas?cuidador_id=${cuidadorId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener solicitudes recibidas');
        }
        return await response.json();
    },
    
    async responderSolicitud(id, estado, motivoRechazo = null) {
        const response = await fetch(`${API_BASE_URL}/solicitudes/${id}/responder`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado, motivo_rechazo: motivoRechazo })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al responder solicitud');
        }
        return await response.json();
    },
    
    async getNotificaciones(usuarioId) {
        const response = await fetch(`${API_BASE_URL}/notificaciones?usuario_id=${usuarioId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener notificaciones');
        }
        return await response.json();
    },
    
    async marcarNotificacionLeida(id) {
        const response = await fetch(`${API_BASE_URL}/notificaciones/${id}/leer`, {
            method: 'PUT'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al marcar notificación');
        }
        return await response.json();
    },
    
    async crearCalificacion(data) {
        const response = await fetch(`${API_BASE_URL}/calificaciones`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear calificación');
        }
        return await response.json();
    },
    
    async getCalificacionesCuidador(cuidadorId) {
        const response = await fetch(`${API_BASE_URL}/calificaciones/cuidador/${cuidadorId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener calificaciones');
        }
        return await response.json();
    },
    
    async getSolicitud(id) {
        const response = await fetch(`${API_BASE_URL}/solicitudes/${id}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al obtener solicitud');
        }
        return await response.json();
    }
};