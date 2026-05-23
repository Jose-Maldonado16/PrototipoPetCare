const API_BASE_URL = 'http://localhost:5000/api';

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
    
    // ==================== PRODUCTOS/SERVICIOS ====================
    
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
    }
};