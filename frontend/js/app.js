import { api } from './api.js';

let currentUser = null;
let usuarios = [];
let currentSearchTerm = '';
let currentFilterRol = 'todos';

const app = document.getElementById('app');

function showMessage(message, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.innerHTML = `<span>${type === 'success' ? '✅' : '❌'} ${message}</span>`;
    
    const existingMessage = document.querySelector('.message');
    if (existingMessage) existingMessage.remove();
    
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

function saveSession(user) {
    currentUser = user;
    localStorage.setItem('petcare_user', JSON.stringify(user));
}

function clearSession() {
    currentUser = null;
    localStorage.removeItem('petcare_user');
}

function loadSession() {
    const savedUser = localStorage.getItem('petcare_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        return true;
    }
    return false;
}

async function loadUsuarios() {
    try {
        const loadingDiv = document.querySelector('.loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'block';
        }
        
        usuarios = await api.getUsuarios();
        return usuarios;
    } catch (error) {
        showMessage(error.message, 'error');
        return [];
    } finally {
        const loadingDiv = document.querySelector('.loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
}

function getEstadisticas() {
    const total = usuarios.length;
    const duenos = usuarios.filter(u => u.rol === 'dueño').length;
    const cuidadores = usuarios.filter(u => u.rol === 'cuidador').length;
    const administradores = usuarios.filter(u => u.rol === 'administrador').length;
    const activos = usuarios.filter(u => u.activo === 1).length;
    const inactivos = usuarios.filter(u => u.activo === 0).length;
    
    return { total, duenos, cuidadores, administradores, activos, inactivos };
}

function getFilteredUsers() {
    let filtered = usuarios;
    
    // Filtrar por búsqueda
    if (currentSearchTerm) {
        filtered = filtered.filter(user => 
            user.nombre.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
            user.apellido.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
            user.email.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
            user.rol.toLowerCase().includes(currentSearchTerm.toLowerCase())
        );
    }
    
    // Filtrar por rol
    if (currentFilterRol !== 'todos') {
        filtered = filtered.filter(user => user.rol === currentFilterRol);
    }
    
    return filtered;
}

function renderLogin() {
    app.innerHTML = `
        <div class="container">
            <div class="auth-container">
                <div class="auth-card">
                    <div class="logo">
                        <h1>🐾 PetCare</h1>
                        <p>Gestión de Usuarios</p>
                    </div>
                    <h2>Iniciar Sesión</h2>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" placeholder="admin@petcare.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Contraseña</label>
                            <input type="password" id="password" name="password" placeholder="••••••" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Ingresar</button>
                    </form>
                    <p class="auth-link">¿No tienes cuenta? <a href="#" id="showRegisterLink">Regístrate aquí</a></p>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
            showMessage('Por favor complete todos los campos', 'error');
            return;
        }
        
        try {
            const user = await api.login(email, password);
            saveSession(user);
            showMessage(`¡Bienvenido ${user.nombre} ${user.apellido}!`, 'success');
            await loadUsuarios();
            renderDashboard();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('showRegisterLink').addEventListener('click', (e) => {
        e.preventDefault();
        renderRegister();
    });
}

function renderRegister() {
    app.innerHTML = `
        <div class="container">
            <div class="auth-container">
                <div class="auth-card">
                    <div class="logo">
                        <h1>🐾 PetCare</h1>
                        <p>Registro de Usuario</p>
                    </div>
                    <h2>Crear Cuenta</h2>
                    <form id="registerForm">
                        <div class="form-group">
                            <label for="nombre">Nombre *</label>
                            <input type="text" id="nombre" name="nombre" required>
                        </div>
                        <div class="form-group">
                            <label for="apellido">Apellido *</label>
                            <input type="text" id="apellido" name="apellido" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email *</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Contraseña * (mínimo 6 caracteres)</label>
                            <input type="password" id="password" name="password" required minlength="6">
                        </div>
                        <div class="form-group">
                            <label for="telefono">Teléfono</label>
                            <input type="tel" id="telefono" name="telefono">
                        </div>
                        <div class="form-group">
                            <label for="rol">Rol *</label>
                            <select id="rol" name="rol" required>
                                <option value="dueño">Dueño</option>
                                <option value="cuidador">Cuidador</option>
                                <option value="administrador">Administrador</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Registrarse</button>
                        <button type="button" id="backToLoginBtn" class="btn btn-secondary" style="margin-top: 10px;">Volver al Login</button>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        if (password.length < 6) {
            showMessage('La contraseña debe tener al menos 6 caracteres', 'error');
            return;
        }
        
        const usuarioData = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
            password: password,
            telefono: document.getElementById('telefono').value,
            rol: document.getElementById('rol').value,
            activo: 1
        };
        
        try {
            await api.createUsuario(usuarioData);
            showMessage('¡Registro exitoso! Ahora puedes iniciar sesión', 'success');
            renderLogin();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('backToLoginBtn').addEventListener('click', () => {
        renderLogin();
    });
}

function renderDashboard() {
    if (!currentUser) {
        renderLogin();
        return;
    }
    
    const stats = getEstadisticas();
    const filteredUsers = getFilteredUsers();
    
    app.innerHTML = `
        <div class="dashboard">
            <div class="header">
                <div class="user-info">
                    <h1>🐾 PetCare</h1>
                    <p>Bienvenido, ${currentUser.nombre} ${currentUser.apellido} <span class="role-badge role-${currentUser.rol}">${currentUser.rol}</span></p>
                </div>
                <button id="logoutBtn" class="btn btn-danger">🚪 Cerrar Sesión</button>
            </div>
            
            <div class="stats-container">
                <div class="stat-card" data-filter="todos">
                    <h3>📊 Total Usuarios</h3>
                    <p class="stat-number">${stats.total}</p>
                </div>
                <div class="stat-card" data-filter="dueño">
                    <h3>🐕 Dueños</h3>
                    <p class="stat-number">${stats.duenos}</p>
                </div>
                <div class="stat-card" data-filter="cuidador">
                    <h3>🐈 Cuidadores</h3>
                    <p class="stat-number">${stats.cuidadores}</p>
                </div>
                <div class="stat-card" data-filter="administrador">
                    <h3>⭐ Administradores</h3>
                    <p class="stat-number">${stats.administradores}</p>
                </div>
                <div class="stat-card" data-filter="activos">
                    <h3>✅ Activos</h3>
                    <p class="stat-number">${stats.activos}</p>
                </div>
            </div>
            
            <div class="dashboard-header">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Buscar por nombre, email o rol..." class="search-input">
                </div>
                <button id="createUserBtn" class="btn btn-primary">➕ Nuevo Usuario</button>
            </div>
            
            <div class="table-container">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre Completo</th>
                            <th>Email</th>
                            <th>Teléfono</th>
                            <th>Rol</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody id="usersTableBody">
                        ${filteredUsers.length === 0 ? `
                            <tr>
                                <td colspan="7" class="empty-state">
                                    <div class="empty-state-icon">📭</div>
                                    <h3>No hay usuarios</h3>
                                    <p>Haz clic en "Nuevo Usuario" para crear uno</p>
                                </td>
                            </tr>
                        ` : filteredUsers.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td><strong>${user.nombre} ${user.apellido}</strong></td>
                                <td>${user.email}</td>
                                <td>${user.telefono || '-'}</td>
                                <td><span class="role-badge role-${user.rol}">${user.rol}</span></td>
                                <td><span class="status-badge status-${user.activo === 1 ? 'active' : 'inactive'}">${user.activo === 1 ? 'Activo' : 'Inactivo'}</span></td>
                                <td class="actions">
                                    <button class="btn-icon btn-edit" data-id="${user.id}" title="Editar">✏️</button>
                                    <button class="btn-icon btn-delete" data-id="${user.id}" title="Eliminar">🗑️</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Event Listeners
    document.getElementById('logoutBtn').addEventListener('click', () => {
        clearSession();
        showMessage('Sesión cerrada exitosamente', 'success');
        renderLogin();
    });
    
    document.getElementById('createUserBtn').addEventListener('click', () => {
        renderCreateUser();
    });
    
    document.getElementById('searchInput').addEventListener('input', (e) => {
        currentSearchTerm = e.target.value;
        renderDashboard();
    });
    
    // Filtros por estadísticas
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('click', () => {
            const filter = card.dataset.filter;
            if (filter === 'activos') {
                filteredUsersManual();
            } else {
                currentFilterRol = filter;
                renderDashboard();
            }
        });
    });
    
    // Botones de editar y eliminar
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            await renderEditUser(id);
        });
    });
    
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            renderDeleteModal(id);
        });
    });
}

function filteredUsersManual() {
    const filtered = usuarios.filter(u => u.activo === 1);
    const stats = getEstadisticas();
    
    app.innerHTML = `
        <div class="dashboard">
            <div class="header">
                <div class="user-info">
                    <h1>🐾 PetCare</h1>
                    <p>Bienvenido, ${currentUser.nombre} ${currentUser.apellido}</p>
                </div>
                <button id="logoutBtn" class="btn btn-danger">Cerrar Sesión</button>
            </div>
            
            <div class="stats-container">
                <div class="stat-card" data-filter="todos">
                    <h3>Total Usuarios</h3>
                    <p class="stat-number">${stats.total}</p>
                </div>
                <div class="stat-card" data-filter="dueño">
                    <h3>Dueños</h3>
                    <p class="stat-number">${stats.duenos}</p>
                </div>
                <div class="stat-card" data-filter="cuidador">
                    <h3>Cuidadores</h3>
                    <p class="stat-number">${stats.cuidadores}</p>
                </div>
                <div class="stat-card" data-filter="administrador">
                    <h3>Administradores</h3>
                    <p class="stat-number">${stats.administradores}</p>
                </div>
                <div class="stat-card active" data-filter="activos">
                    <h3>Activos</h3>
                    <p class="stat-number">${stats.activos}</p>
                </div>
            </div>
            
            <div class="dashboard-header">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Buscar..." class="search-input">
                </div>
                <button id="createUserBtn" class="btn btn-primary">+ Nuevo Usuario</button>
                <button id="clearFilterBtn" class="btn btn-secondary">Mostrar Todos</button>
            </div>
            
            <div class="table-container">
                <table class="users-table">
                    <thead>
                        <tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
                    </thead>
                    <tbody>
                        ${filtered.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.nombre} ${user.apellido}</td>
                                <td>${user.email}</td>
                                <td><span class="role-badge role-${user.rol}">${user.rol}</span></td>
                                <td><span class="status-badge status-active">Activo</span></td>
                                <td class="actions">
                                    <button class="btn-icon btn-edit" data-id="${user.id}">✏️</button>
                                    <button class="btn-icon btn-delete" data-id="${user.id}">🗑️</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    document.getElementById('clearFilterBtn')?.addEventListener('click', () => {
        currentFilterRol = 'todos';
        renderDashboard();
    });
}

function renderCreateUser() {
    app.innerHTML = `
        <div class="container">
            <div class="form-container">
                <h2>➕ Crear Nuevo Usuario</h2>
                <form id="createUserForm">
                    <div class="form-group">
                        <label for="nombre">Nombre *</label>
                        <input type="text" id="nombre" name="nombre" required>
                    </div>
                    <div class="form-group">
                        <label for="apellido">Apellido *</label>
                        <input type="text" id="apellido" name="apellido" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email *</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Contraseña * (mínimo 6 caracteres)</label>
                        <input type="password" id="password" name="password" required minlength="6">
                    </div>
                    <div class="form-group">
                        <label for="telefono">Teléfono</label>
                        <input type="tel" id="telefono" name="telefono">
                    </div>
                    <div class="form-group">
                        <label for="rol">Rol *</label>
                        <select id="rol" name="rol" required>
                            <option value="dueño">Dueño</option>
                            <option value="cuidador">Cuidador</option>
                            <option value="administrador">Administrador</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="activo">Estado</label>
                        <select id="activo" name="activo">
                            <option value="1">Activo</option>
                            <option value="0">Inactivo</option>
                        </select>
                    </div>
                    <div class="form-buttons">
                        <button type="submit" class="btn btn-primary">💾 Crear Usuario</button>
                        <button type="button" id="cancelBtn" class="btn btn-secondary">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('createUserForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        if (password.length < 6) {
            showMessage('La contraseña debe tener al menos 6 caracteres', 'error');
            return;
        }
        
        const usuarioData = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
            password: password,
            telefono: document.getElementById('telefono').value,
            rol: document.getElementById('rol').value,
            activo: parseInt(document.getElementById('activo').value)
        };
        
        try {
            await api.createUsuario(usuarioData);
            showMessage('✅ Usuario creado exitosamente', 'success');
            await loadUsuarios();
            renderDashboard();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('cancelBtn').addEventListener('click', () => {
        renderDashboard();
    });
}

async function renderEditUser(id) {
    try {
        const user = await api.getUsuario(id);
        
        app.innerHTML = `
            <div class="container">
                <div class="form-container">
                    <h2>✏️ Editar Usuario</h2>
                    <form id="editUserForm">
                        <div class="form-group">
                            <label for="nombre">Nombre *</label>
                            <input type="text" id="nombre" name="nombre" value="${user.nombre}" required>
                        </div>
                        <div class="form-group">
                            <label for="apellido">Apellido *</label>
                            <input type="text" id="apellido" name="apellido" value="${user.apellido}" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email *</label>
                            <input type="email" id="email" name="email" value="${user.email}" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Nueva Contraseña (dejar vacío para no cambiar)</label>
                            <input type="password" id="password" name="password" placeholder="••••••" minlength="6">
                        </div>
                        <div class="form-group">
                            <label for="telefono">Teléfono</label>
                            <input type="tel" id="telefono" name="telefono" value="${user.telefono || ''}">
                        </div>
                        <div class="form-group">
                            <label for="rol">Rol *</label>
                            <select id="rol" name="rol" required>
                                <option value="dueño" ${user.rol === 'dueño' ? 'selected' : ''}>Dueño</option>
                                <option value="cuidador" ${user.rol === 'cuidador' ? 'selected' : ''}>Cuidador</option>
                                <option value="administrador" ${user.rol === 'administrador' ? 'selected' : ''}>Administrador</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="activo">Estado</label>
                            <select id="activo" name="activo">
                                <option value="1" ${user.activo === 1 ? 'selected' : ''}>Activo</option>
                                <option value="0" ${user.activo === 0 ? 'selected' : ''}>Inactivo</option>
                            </select>
                        </div>
                        <div class="form-buttons">
                            <button type="submit" class="btn btn-primary">💾 Actualizar Usuario</button>
                            <button type="button" id="cancelBtn" class="btn btn-secondary">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.getElementById('editUserForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const usuarioData = {
                nombre: document.getElementById('nombre').value,
                apellido: document.getElementById('apellido').value,
                email: document.getElementById('email').value,
                telefono: document.getElementById('telefono').value,
                rol: document.getElementById('rol').value,
                activo: parseInt(document.getElementById('activo').value)
            };
            
            const password = document.getElementById('password').value;
            if (password) {
                if (password.length < 6) {
                    showMessage('La contraseña debe tener al menos 6 caracteres', 'error');
                    return;
                }
                usuarioData.password = password;
            }
            
            try {
                await api.updateUsuario(id, usuarioData);
                showMessage('✅ Usuario actualizado exitosamente', 'success');
                await loadUsuarios();
                renderDashboard();
            } catch (error) {
                showMessage(error.message, 'error');
            }
        });
        
        document.getElementById('cancelBtn').addEventListener('click', () => {
            renderDashboard();
        });
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

function renderDeleteModal(id) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Confirmar Eliminación</h3>
            <p>¿Estás seguro de que deseas eliminar este usuario?</p>
            <p style="color: var(--danger-color); font-size: 12px;">Esta acción no se puede deshacer.</p>
            <div class="modal-buttons">
                <button id="confirmDeleteBtn" class="btn btn-danger">🗑️ Eliminar</button>
                <button id="cancelDeleteBtn" class="btn btn-secondary">❌ Cancelar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
        try {
            await api.deleteUsuario(id);
            showMessage('✅ Usuario eliminado exitosamente', 'success');
            await loadUsuarios();
            renderDashboard();
            modal.remove();
        } catch (error) {
            showMessage(error.message, 'error');
            modal.remove();
        }
    });
    
    document.getElementById('cancelDeleteBtn').addEventListener('click', () => {
        modal.remove();
    });
}

async function init() {
    await loadUsuarios();
    if (loadSession()) {
        renderDashboard();
    } else {
        renderLogin();
    }
}

init();