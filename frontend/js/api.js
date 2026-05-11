const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
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
    }
};