import { api } from './api.js';

let currentUser = null;
let usuarios = [];
let currentView = 'dashboard';

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
        usuarios = await api.getUsuarios();
        return usuarios;
    } catch (error) {
        console.error('Error loading usuarios:', error);
        return [];
    }
}

function renderNavBar() {
    if (!currentUser) return '';
    
    let navLinks = '';
    
    if (currentUser.rol === 'cuidador') {
        navLinks = `
            <button class="nav-btn" data-view="mis-productos">📦 Mis Productos</button>
            <button class="nav-btn" data-view="solicitudes-recibidas">📬 Solicitudes</button>
            <button class="nav-btn" data-view="dashboard">📊 Dashboard</button>
            <button class="nav-btn notif-btn" data-view="notificaciones">🔔 <span id="notifCount" class="notif-count">0</span></button>
        `;
    } else if (currentUser.rol === 'administrador') {
        navLinks = `
            <button class="nav-btn" data-view="validar-productos">✅ Validar Productos</button>
            <button class="nav-btn" data-view="todos-productos">📋 Todos los Productos</button>
            <button class="nav-btn" data-view="dashboard">📊 Dashboard</button>
            <button class="nav-btn" data-view="usuarios">👥 Usuarios</button>
            <button class="nav-btn notif-btn" data-view="notificaciones">🔔 <span id="notifCount" class="notif-count">0</span></button>
        `;
    } else {
        navLinks = `
            <button class="nav-btn" data-view="buscar-productos">🔍 Buscar Servicios</button>
            <button class="nav-btn" data-view="mis-solicitudes">📋 Mis Solicitudes</button>
            <button class="nav-btn" data-view="dashboard">📊 Dashboard</button>
            <button class="nav-btn notif-btn" data-view="notificaciones">🔔 <span id="notifCount" class="notif-count">0</span></button>
        `;
    }
    
    return `
        <div class="nav-bar">
            <div class="nav-brand">🐾 PetCare Connect</div>
            <div class="nav-links">
                ${navLinks}
                <button class="nav-btn btn-logout" id="logoutBtn">🚪 Salir</button>
            </div>
        </div>
    `;
}

function renderLogin() {
    app.innerHTML = `
        <div class="container">
            <div class="auth-container">
                <div class="auth-card">
                    <div class="logo">
                        <h1>🐾 PetCare Connect</h1>
                        <p>Conectando dueños con cuidadores confiables</p>
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
        
        try {
            const user = await api.login(email, password);
            saveSession(user);
            showMessage(`¡Bienvenido ${user.nombre}!`, 'success');
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
                        <h1>🐾 PetCare Connect</h1>
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
                                <option value="dueño">Dueño (busco servicios)</option>
                                <option value="cuidador">Cuidador (ofrezco servicios)</option>
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
    
    app.innerHTML = `
        ${renderNavBar()}
        <div class="dashboard">
            <div class="header">
                <div class="user-info">
                    <h1>🐾 PetCare Connect</h1>
                    <p>Bienvenido, ${currentUser.nombre} ${currentUser.apellido} 
                    <span class="role-badge role-${currentUser.rol}">${currentUser.rol}</span></p>
                </div>
            </div>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>📊 Total Usuarios</h3>
                    <p class="stat-number">${usuarios.length}</p>
                </div>
                <div class="stat-card">
                    <h3>🐕 Dueños</h3>
                    <p class="stat-number">${usuarios.filter(u => u.rol === 'dueño').length}</p>
                </div>
                <div class="stat-card">
                    <h3>🐈 Cuidadores</h3>
                    <p class="stat-number">${usuarios.filter(u => u.rol === 'cuidador').length}</p>
                </div>
                <div class="stat-card">
                    <h3>⭐ Administradores</h3>
                    <p class="stat-number">${usuarios.filter(u => u.rol === 'administrador').length}</p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 50px; background: white; border-radius: 15px;">
                <h2>🎉 Bienvenido al Sprint 3</h2>
                <p>Se ha implementado la Gestión de Solicitudes y Búsqueda de Servicios</p>
                <br>
                <div class="info-box">
                    <strong>📌 Novedades:</strong>
                    <ul style="text-align: left; margin-top: 15px;">
                        <li>✅ Dueños pueden buscar servicios con filtros (recientes, populares, mejor calificados)</li>
                        <li>✅ Dueños pueden solicitar servicios</li>
                        <li>✅ Cuidadores reciben solicitudes y pueden aceptar/rechazar</li>
                        <li>✅ Notificaciones en tiempo real</li>
                        <li>✅ Calificación de servicios (1-5 estrellas)</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    attachNavEvents();
    cargarNotificacionesNoLeidas();
}

// ==================== SOLICITUDES Y BÚSQUEDA (SPRINT 3) ====================

async function renderBuscarProductos() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando servicios...</div></div>`;
    attachNavEvents();
    
    try {
        let productos = await api.buscarProductos('recientes');
        let filtroActual = 'recientes';
        let categoriaActual = 'todos';
        let busquedaActual = '';
        
        await renderBusquedaUI(productos, filtroActual, categoriaActual, busquedaActual);
        
        async function renderBusquedaUI(productos, filtro, categoria, busqueda) {
            app.innerHTML = `
                ${renderNavBar()}
                <div class="container">
                    <div class="form-container" style="max-width: 1200px;">
                        <h2>🔍 Buscar Servicios</h2>
                        
                        <div class="filtros-busqueda">
                            <div class="filtro-grupo">
                                <label>Filtrar por:</label>
                                <select id="filtroSelect" class="filtro-select">
                                    <option value="recientes" ${filtro === 'recientes' ? 'selected' : ''}>📅 Más recientes</option>
                                    <option value="populares" ${filtro === 'populares' ? 'selected' : ''}>🔥 Más populares</option>
                                    <option value="mejor_calificados" ${filtro === 'mejor_calificados' ? 'selected' : ''}>⭐ Mejor calificados</option>
                                </select>
                            </div>
                            
                            <div class="filtro-grupo">
                                <label>Categoría:</label>
                                <select id="categoriaSelect" class="filtro-select">
                                    <option value="todos" ${categoria === 'todos' ? 'selected' : ''}>Todos</option>
                                    <option value="paseo" ${categoria === 'paseo' ? 'selected' : ''}>🐕 Paseo</option>
                                    <option value="guarderia" ${categoria === 'guarderia' ? 'selected' : ''}>🏠 Guardería</option>
                                    <option value="alojamiento" ${categoria === 'alojamiento' ? 'selected' : ''}>🛌 Alojamiento</option>
                                </select>
                            </div>
                            
                            <div class="filtro-grupo busqueda-grupo">
                                <label>Buscar:</label>
                                <input type="text" id="busquedaInput" class="search-input" placeholder="Buscar por título..." value="${busqueda}">
                            </div>
                        </div>
                        
                        <div class="productos-grid">
                            ${productos.length === 0 ? `
                                <div class="empty-state">
                                    <p>No hay servicios disponibles</p>
                                </div>
                            ` : productos.map(p => `
                                <div class="producto-card">
                                    <h3>${escapeHtml(p.titulo)}</h3>
                                    <span class="categoria-badge">${p.categoria}</span>
                                    <p class="precio">Bs. ${parseFloat(p.precio).toFixed(2)}</p>
                                    <p class="descripcion">${escapeHtml(p.descripcion.substring(0, 100))}...</p>
                                    <div class="ofertante">
                                        <small>👤 ${escapeHtml(p.nombre_cuidador || p.nombre)} ${escapeHtml(p.apellido_cuidador || p.apellido)}</small>
                                        <br>
                                        <small>⭐ ${p.promedio_calificacion || 0}/5 (${p.total_solicitudes || 0} solicitudes)</small>
                                    </div>
                                    <button class="btn btn-primary btn-sm solicitar-btn" data-id="${p.id}" data-titulo="${escapeHtml(p.titulo)}">📋 Solicitar</button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            attachNavEvents();
            cargarNotificacionesNoLeidas();
            
            document.getElementById('filtroSelect').addEventListener('change', async (e) => {
                filtroActual = e.target.value;
                productos = await api.buscarProductos(filtroActual, categoriaActual, busquedaActual);
                renderBusquedaUI(productos, filtroActual, categoriaActual, busquedaActual);
            });
            
            document.getElementById('categoriaSelect').addEventListener('change', async (e) => {
                categoriaActual = e.target.value;
                productos = await api.buscarProductos(filtroActual, categoriaActual, busquedaActual);
                renderBusquedaUI(productos, filtroActual, categoriaActual, busquedaActual);
            });
            
            document.getElementById('busquedaInput').addEventListener('input', async (e) => {
                busquedaActual = e.target.value;
                productos = await api.buscarProductos(filtroActual, categoriaActual, busquedaActual);
                renderBusquedaUI(productos, filtroActual, categoriaActual, busquedaActual);
            });
            
            document.querySelectorAll('.solicitar-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const productoId = parseInt(btn.dataset.id);
                    const productoTitulo = btn.dataset.titulo;
                    renderSolicitarModal(productoId, productoTitulo);
                });
            });
        }
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

function renderSolicitarModal(productoId, productoTitulo) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <h3>📋 Solicitar Servicio</h3>
            <p>Servicio: <strong>${escapeHtml(productoTitulo)}</strong></p>
            <form id="solicitarForm">
                <div class="form-group">
                    <label for="mensaje">Mensaje para el cuidador (opcional)</label>
                    <textarea id="mensaje" rows="3" placeholder="Escribe un mensaje para el cuidador..."></textarea>
                </div>
                <div class="modal-buttons">
                    <button type="submit" class="btn btn-primary">✅ Enviar Solicitud</button>
                    <button type="button" id="cancelSolicitarBtn" class="btn btn-secondary">❌ Cancelar</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('solicitarForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const mensaje = document.getElementById('mensaje').value;
        
        try {
            await api.crearSolicitud({
                producto_id: productoId,
                solicitante_id: currentUser.id,
                mensaje: mensaje
            });
            showMessage('✅ Solicitud enviada correctamente', 'success');
            modal.remove();
            renderBuscarProductos();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('cancelSolicitarBtn').addEventListener('click', () => {
        modal.remove();
    });
}

async function renderMisSolicitudes() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const solicitudes = await api.getMisSolicitudes(currentUser.id);
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 1200px;">
                    <h2>📋 Mis Solicitudes</h2>
                    ${solicitudes.length === 0 ? `
                        <div class="empty-state">
                            <p>No has realizado ninguna solicitud.</p>
                            <button class="btn btn-primary" id="buscarServiciosBtn">🔍 Buscar Servicios</button>
                        </div>
                    ` : `
                        <div class="table-container">
                            <table class="users-table">
                                <thead>
                                    <tr><th>Servicio</th><th>Cuidador</th><th>Precio</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr>
                                </thead>
                                <tbody>
                                    ${solicitudes.map(s => `
                                        <tr>
                                            <td><strong>${escapeHtml(s.producto_titulo)}</strong></td>
                                            <td>${escapeHtml(s.cuidador_nombre)} ${escapeHtml(s.cuidador_apellido)}</small></small></small></small></small></small></td>
                                            <td>Bs. ${parseFloat(s.producto_precio).toFixed(2)}</small></small></small></small></small></small></td>
                                            <td>${getEstadoSolicitudBadge(s.estado)}</small></small></small></small></small></small></td>
                                            <td><small>${new Date(s.fecha_solicitud).toLocaleDateString()}</small></small></small></small></small></td>
                                            <td class="actions">
                                                ${s.estado === 'aceptado' ? `<button class="btn-icon btn-calificar" data-id="${s.id}" data-cuidador="${s.cuidador_email}" title="Calificar">⭐ Calificar</button>` : ''}
                                                <button class="btn-icon btn-ver" data-id="${s.id}" title="Ver detalles">👁️</button>
                                            </small></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;
        
        attachNavEvents();
        
        document.getElementById('buscarServiciosBtn')?.addEventListener('click', () => renderBuscarProductos());
        
        document.querySelectorAll('.btn-calificar').forEach(btn => {
            btn.addEventListener('click', () => {
                const solicitudId = parseInt(btn.dataset.id);
                renderCalificarModal(solicitudId);
            });
        });
        
        document.querySelectorAll('.btn-ver').forEach(btn => {
            btn.addEventListener('click', async () => {
                const solicitudId = parseInt(btn.dataset.id);
                await renderDetalleSolicitud(solicitudId);
            });
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

async function renderSolicitudesRecibidas() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const solicitudes = await api.getSolicitudesRecibidas(currentUser.id);
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 1200px;">
                    <h2>📬 Solicitudes Recibidas</h2>
                    ${solicitudes.length === 0 ? `
                        <div class="empty-state">
                            <p>No tienes solicitudes pendientes.</p>
                        </div>
                    ` : `
                        <div class="table-container">
                            <table class="users-table">
                                <thead>
                                    <tr><th>Servicio</th><th>Solicitante</th><th>Mensaje</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr>
                                </thead>
                                <tbody>
                                    ${solicitudes.map(s => `
                                        <tr>
                                            <td><strong>${escapeHtml(s.producto_titulo)}</strong></small></small></small></small></small></small></td>
                                            <td>${escapeHtml(s.solicitante_nombre)} ${escapeHtml(s.solicitante_apellido)}<br><small>📞 ${s.solicitante_telefono || 'N/A'}</small></small></small></small></small></td>
                                            <td><small>${escapeHtml(s.mensaje || 'Sin mensaje')}</small></small></small></small></small></td>
                                            <td><small>${new Date(s.fecha_solicitud).toLocaleDateString()}</small></small></small></small></small></td>
                                            <td>${getEstadoSolicitudBadge(s.estado)}</small></small></small></small></small></small></td>
                                            <td class="actions">
                                                ${s.estado === 'pendiente' ? `
                                                    <button class="btn btn-success btn-sm aceptar-btn" data-id="${s.id}">✅ Aceptar</button>
                                                    <button class="btn btn-danger btn-sm rechazar-btn" data-id="${s.id}">❌ Rechazar</button>
                                                ` : ''}
                                                <button class="btn-icon btn-ver" data-id="${s.id}" title="Ver detalles">👁️</button>
                                            </small></small></small></small></small></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;
        
        attachNavEvents();
        
        document.querySelectorAll('.aceptar-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await responderSolicitud(id, 'aceptado');
            });
        });
        
        document.querySelectorAll('.rechazar-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                renderRechazarModal(id);
            });
        });
        
        document.querySelectorAll('.btn-ver').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await renderDetalleSolicitud(id);
            });
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

async function responderSolicitud(id, estado, motivo = null) {
    try {
        await api.responderSolicitud(id, estado, motivo);
        showMessage(`✅ Solicitud ${estado} correctamente`, 'success');
        renderSolicitudesRecibidas();
        cargarNotificacionesNoLeidas();
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

function renderRechazarModal(id) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <h3>❌ Rechazar Solicitud</h3>
            <p>Por favor, indica el motivo del rechazo:</p>
            <textarea id="motivoRechazo" rows="3" style="width: 100%; padding: 10px; margin: 10px 0;" placeholder="Ej: No estoy disponible en esa fecha..."></textarea>
            <div class="modal-buttons">
                <button id="confirmRechazarBtn" class="btn btn-danger">Confirmar Rechazo</button>
                <button id="cancelRechazarBtn" class="btn btn-secondary">Cancelar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('confirmRechazarBtn').addEventListener('click', async () => {
        const motivo = document.getElementById('motivoRechazo').value;
        if (!motivo) {
            showMessage('Debes proporcionar un motivo de rechazo', 'error');
            return;
        }
        await responderSolicitud(id, 'rechazado', motivo);
        modal.remove();
    });
    
    document.getElementById('cancelRechazarBtn').addEventListener('click', () => {
        modal.remove();
    });
}

function renderCalificarModal(solicitudId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <h3>⭐ Calificar Servicio</h3>
            <form id="calificarForm">
                <div class="form-group">
                    <label>Puntuación (1-5 estrellas)</label>
                    <div class="stars-container">
                        ${[1,2,3,4,5].map(i => `<span class="star" data-value="${i}">☆</span>`).join('')}
                    </div>
                    <input type="hidden" id="puntuacion" value="0">
                </div>
                <div class="form-group">
                    <label for="comentario">Comentario (opcional)</label>
                    <textarea id="comentario" rows="3" placeholder="Tu opinión sobre el servicio..."></textarea>
                </div>
                <div class="modal-buttons">
                    <button type="submit" class="btn btn-primary">Enviar Calificación</button>
                    <button type="button" id="cancelCalificarBtn" class="btn btn-secondary">Cancelar</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    let puntuacion = 0;
    const stars = modal.querySelectorAll('.star');
    stars.forEach(star => {
        star.addEventListener('click', () => {
            puntuacion = parseInt(star.dataset.value);
            document.getElementById('puntuacion').value = puntuacion;
            stars.forEach((s, i) => {
                s.textContent = i < puntuacion ? '★' : '☆';
            });
        });
    });
    
    document.getElementById('calificarForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (puntuacion === 0) {
            showMessage('Selecciona una puntuación', 'error');
            return;
        }
        
        try {
            await api.crearCalificacion({
                solicitud_id: solicitudId,
                cuidador_id: currentUser.id,
                solicitante_id: currentUser.id,
                puntuacion: puntuacion,
                comentario: document.getElementById('comentario').value
            });
            showMessage('✅ Calificación enviada, gracias por tu opinión', 'success');
            modal.remove();
            renderMisSolicitudes();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('cancelCalificarBtn').addEventListener('click', () => {
        modal.remove();
    });
}

async function renderDetalleSolicitud(id) {
    try {
        const solicitud = await api.getSolicitud(id);
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <h3>📋 Detalle de Solicitud</h3>
                <div class="info-box">
                    <p><strong>Servicio:</strong> ${escapeHtml(solicitud.producto?.titulo || 'N/A')}</p>
                    <p><strong>Solicitante:</strong> ${escapeHtml(solicitud.solicitante?.nombre || '')} ${escapeHtml(solicitud.solicitante?.apellido || '')}</p>
                    <p><strong>Email:</strong> ${escapeHtml(solicitud.solicitante?.email || '')}</p>
                    <p><strong>Teléfono:</strong> ${escapeHtml(solicitud.solicitante?.telefono || 'N/A')}</p>
                    <p><strong>Mensaje:</strong> ${escapeHtml(solicitud.mensaje || 'Sin mensaje')}</p>
                    <p><strong>Estado:</strong> ${getEstadoSolicitudBadge(solicitud.estado)}</p>
                    <p><strong>Fecha solicitud:</strong> ${new Date(solicitud.fecha_solicitud).toLocaleString()}</p>
                    ${solicitud.fecha_respuesta ? `<p><strong>Fecha respuesta:</strong> ${new Date(solicitud.fecha_respuesta).toLocaleString()}</p>` : ''}
                    ${solicitud.motivo_rechazo ? `<p><strong>Motivo rechazo:</strong> ${escapeHtml(solicitud.motivo_rechazo)}</p>` : ''}
                </div>
                <div class="modal-buttons">
                    <button id="closeModalBtn" class="btn btn-secondary">Cerrar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            modal.remove();
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function renderNotificaciones() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const notificaciones = await api.getNotificaciones(currentUser.id);
        const noLeidas = notificaciones.filter(n => n.leido === 0);
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 800px;">
                    <h2>🔔 Notificaciones ${noLeidas.length > 0 ? `<span class="notif-badge">${noLeidas.length} nuevas</span>` : ''}</h2>
                    ${notificaciones.length === 0 ? `
                        <div class="empty-state">
                            <p>No tienes notificaciones.</p>
                        </div>
                    ` : `
                        <div class="notificaciones-lista">
                            ${notificaciones.map(n => `
                                <div class="notificacion-item ${n.leido === 0 ? 'no-leida' : ''}" data-id="${n.id}">
                                    <div class="notif-titulo">${escapeHtml(n.titulo)}</div>
                                    <div class="notif-mensaje">${escapeHtml(n.mensaje)}</div>
                                    <div class="notif-fecha"><small>${new Date(n.fecha).toLocaleString()}</small></div>
                                </div>
                            `).join('')}
                        </div>
                        <button id="marcarTodasBtn" class="btn btn-secondary btn-sm" style="margin-top: 20px;">Marcar todas como leídas</button>
                    `}
                </div>
            </div>
        `;
        
        attachNavEvents();
        
        document.querySelectorAll('.notificacion-item').forEach(item => {
            item.addEventListener('click', async () => {
                const id = parseInt(item.dataset.id);
                if (item.classList.contains('no-leida')) {
                    await api.marcarNotificacionLeida(id);
                    item.classList.remove('no-leida');
                }
            });
        });
        
        document.getElementById('marcarTodasBtn')?.addEventListener('click', async () => {
            const noLeidasIds = notificaciones.filter(n => n.leido === 0).map(n => n.id);
            for (const id of noLeidasIds) {
                await api.marcarNotificacionLeida(id);
            }
            showMessage('Notificaciones marcadas como leídas', 'success');
            renderNotificaciones();
            cargarNotificacionesNoLeidas();
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

async function cargarNotificacionesNoLeidas() {
    if (!currentUser) return;
    try {
        const notificaciones = await api.getNotificaciones(currentUser.id);
        const noLeidas = notificaciones.filter(n => n.leido === 0).length;
        const notifSpan = document.querySelector('#notifCount');
        if (notifSpan) {
            notifSpan.textContent = noLeidas;
            notifSpan.style.display = noLeidas > 0 ? 'inline-block' : 'none';
        }
    } catch (error) {
        console.error('Error cargando notificaciones:', error);
    }
}

// ==================== PRODUCTOS (SPRINT 2) ====================

async function renderMisProductos() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const productos = await api.getMisProductos(currentUser.id);
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 1200px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>📦 Mis Productos/Servicios</h2>
                        <button class="btn btn-primary" id="crearProductoBtnHeader">➕ Nuevo Servicio</button>
                    </div>
                    
                    ${productos.length === 0 ? `
                        <div class="empty-state">
                            <p>No tienes productos registrados aún.</p>
                            <button class="btn btn-primary" id="crearPrimerProductoBtn">➕ Crear mi primer servicio</button>
                        </div>
                    ` : `
                        <div class="table-container">
                            <table class="users-table">
                                <thead>
                                    <tr><th>Título</th><th>Categoría</th><th>Precio (Bs.)</th><th>Estado</th><th>Motivo</th><th>Acciones</th></tr>
                                </thead>
                                <tbody>
                                    ${productos.map(p => `
                                        <tr>
                                            <td><strong>${escapeHtml(p.titulo)}</strong><br><small>${escapeHtml(p.descripcion.substring(0, 50))}...</small></td>
                                            <td><span class="role-badge">${p.categoria}</span></td>
                                            <td>Bs. ${parseFloat(p.precio).toFixed(2)}</small></small></small></small></small></small></td>
                                            <td>${getEstadoBadge(p.estado)}</small></small></small></small></small></small></td>
                                            <td>${p.motivo_rechazo ? `<small style="color: red;">${escapeHtml(p.motivo_rechazo)}</small>` : '-'}</td>
                                            <td class="actions">
                                                <button class="btn-icon btn-edit" data-id="${p.id}" title="Editar">✏️</button>
                                                <button class="btn-icon btn-delete" data-id="${p.id}" title="Eliminar">🗑️</button>
                                            </small></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;
        
        attachNavEvents();
        
        document.getElementById('crearProductoBtnHeader')?.addEventListener('click', () => renderCrearProducto());
        document.getElementById('crearPrimerProductoBtn')?.addEventListener('click', () => renderCrearProducto());
        
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', () => renderEditarProducto(parseInt(btn.dataset.id)));
        });
        
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', () => renderDeleteProductoModal(parseInt(btn.dataset.id)));
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

function renderCrearProducto() {
    app.innerHTML = `
        ${renderNavBar()}
        <div class="container">
            <div class="form-container">
                <h2>➕ Registrar Nuevo Servicio</h2>
                <form id="crearProductoForm">
                    <div class="form-group">
                        <label for="titulo">Título del servicio *</label>
                        <input type="text" id="titulo" name="titulo" required placeholder="Ej: Paseo de mascotas">
                    </div>
                    <div class="form-group">
                        <label for="descripcion">Descripción *</label>
                        <textarea id="descripcion" name="descripcion" rows="4" required placeholder="Describe tu servicio en detalle..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="precio">Precio/Tarifa (Bs.) *</label>
                        <input type="number" id="precio" name="precio" step="0.01" min="0.01" required placeholder="Ej: 50.00">
                    </div>
                    <div class="form-group">
                        <label for="categoria">Categoría *</label>
                        <select id="categoria" name="categoria" required>
                            <option value="paseo">🐕 Paseo</option>
                            <option value="guarderia">🏠 Guardería</option>
                            <option value="alojamiento">🛌 Alojamiento</option>
                        </select>
                    </div>
                    <div class="info-box" style="background: #FFF3E0; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                        <small>📌 Nota: Tu servicio quedará en estado <strong>PENDIENTE</strong> hasta que sea validado por un administrador.</small>
                    </div>
                    <div class="form-buttons">
                        <button type="submit" class="btn btn-primary">💾 Guardar Servicio</button>
                        <button type="button" id="cancelBtn" class="btn btn-secondary">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    attachNavEvents();
    
    document.getElementById('crearProductoForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const productoData = {
            titulo: document.getElementById('titulo').value,
            descripcion: document.getElementById('descripcion').value,
            precio: parseFloat(document.getElementById('precio').value),
            categoria: document.getElementById('categoria').value,
            ofertante_id: currentUser.id
        };
        
        try {
            await api.createProducto(productoData);
            showMessage('✅ Servicio registrado exitosamente', 'success');
            renderMisProductos();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('cancelBtn').addEventListener('click', () => renderMisProductos());
}

async function renderEditarProducto(id) {
    try {
        const producto = await api.getProducto(id);
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container">
                    <h2>✏️ Editar Servicio</h2>
                    <form id="editarProductoForm">
                        <div class="form-group">
                            <label for="titulo">Título del servicio *</label>
                            <input type="text" id="titulo" name="titulo" value="${escapeHtml(producto.titulo)}" required>
                        </div>
                        <div class="form-group">
                            <label for="descripcion">Descripción *</label>
                            <textarea id="descripcion" name="descripcion" rows="4" required>${escapeHtml(producto.descripcion)}</textarea>
                        </div>
                        <div class="form-group">
                            <label for="precio">Precio/Tarifa (Bs.) *</label>
                            <input type="number" id="precio" name="precio" step="0.01" min="0.01" value="${producto.precio}" required>
                        </div>
                        <div class="form-group">
                            <label for="categoria">Categoría *</label>
                            <select id="categoria" name="categoria" required>
                                <option value="paseo" ${producto.categoria === 'paseo' ? 'selected' : ''}>🐕 Paseo</option>
                                <option value="guarderia" ${producto.categoria === 'guarderia' ? 'selected' : ''}>🏠 Guardería</option>
                                <option value="alojamiento" ${producto.categoria === 'alojamiento' ? 'selected' : ''}>🛌 Alojamiento</option>
                            </select>
                        </div>
                        ${producto.estado === 'aprobado' ? `
                            <div class="info-box" style="background: #FFF3E0; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                                <small>⚠️ <strong>Advertencia:</strong> Si modificas algún campo, tu servicio volverá a estado <strong>PENDIENTE</strong>.</small>
                            </div>
                        ` : ''}
                        <div class="form-buttons">
                            <button type="submit" class="btn btn-primary">💾 Actualizar Servicio</button>
                            <button type="button" id="cancelBtn" class="btn btn-secondary">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        attachNavEvents();
        
        document.getElementById('editarProductoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const productoData = {
                titulo: document.getElementById('titulo').value,
                descripcion: document.getElementById('descripcion').value,
                precio: parseFloat(document.getElementById('precio').value),
                categoria: document.getElementById('categoria').value
            };
            
            try {
                await api.updateProducto(id, productoData);
                showMessage('✅ Servicio actualizado exitosamente', 'success');
                renderMisProductos();
            } catch (error) {
                showMessage(error.message, 'error');
            }
        });
        
        document.getElementById('cancelBtn').addEventListener('click', () => renderMisProductos());
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderMisProductos();
    }
}

function renderDeleteProductoModal(id) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Confirmar Eliminación</h3>
            <p>¿Estás seguro de que deseas eliminar este servicio?</p>
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
            await api.deleteProducto(id);
            showMessage('✅ Servicio eliminado exitosamente', 'success');
            renderMisProductos();
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

async function renderValidarProductos() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const productos = await api.getProductosPendientes();
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 1200px;">
                    <h2>✅ Validar Productos/Servicios</h2>
                    ${productos.length === 0 ? `
                        <div class="empty-state">
                            <p>No hay productos pendientes de validación.</p>
                        </div>
                    ` : `
                        <div class="table-container">
                            <table class="users-table">
                                <thead>
                                    <tr><th>Ofertante</th><th>Título</th><th>Categoría</th><th>Precio</th><th>Descripción</th><th>Acciones</th></tr>
                                </thead>
                                <tbody>
                                    ${productos.map(p => `
                                        <tr>
                                            <td><strong>${escapeHtml(p.nombre)} ${escapeHtml(p.apellido)}</strong><br><small>${escapeHtml(p.email)}</small></td>
                                            <td><strong>${escapeHtml(p.titulo)}</strong></td>
                                            <td><span class="role-badge">${p.categoria}</span></td>
                                            <td>Bs. ${parseFloat(p.precio).toFixed(2)}</small></small></small></small></small></small></td>
                                            <td><small>${escapeHtml(p.descripcion.substring(0, 80))}...</small></small></small></small></small></small></td>
                                            <td class="actions">
                                                <button class="btn btn-success btn-sm aprobar-btn" data-id="${p.id}">✅ Aprobar</button>
                                                <button class="btn btn-danger btn-sm rechazar-btn" data-id="${p.id}">❌ Rechazar</button>
                                            </small></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;
        attachNavEvents();
        
        document.querySelectorAll('.aprobar-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                try {
                    await api.validarProducto(id, 'aprobado');
                    showMessage('✅ Producto aprobado', 'success');
                    renderValidarProductos();
                } catch (error) {
                    showMessage(error.message, 'error');
                }
            });
        });
        
        document.querySelectorAll('.rechazar-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                renderRechazarProductoModal(id);
            });
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

function renderRechazarProductoModal(id) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <h3>❌ Rechazar Producto</h3>
            <p>Indica el motivo del rechazo:</p>
            <textarea id="motivoRechazo" rows="3" style="width: 100%; padding: 10px; margin: 10px 0;" placeholder="Ej: Precio no competitivo..."></textarea>
            <div class="modal-buttons">
                <button id="confirmRechazarBtn" class="btn btn-danger">Confirmar Rechazo</button>
                <button id="cancelRechazarBtn" class="btn btn-secondary">Cancelar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('confirmRechazarBtn').addEventListener('click', async () => {
        const motivo = document.getElementById('motivoRechazo').value;
        if (!motivo) {
            showMessage('Debes proporcionar un motivo', 'error');
            return;
        }
        try {
            await api.validarProducto(id, 'rechazado', motivo);
            showMessage('❌ Producto rechazado', 'success');
            renderValidarProductos();
            modal.remove();
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
    
    document.getElementById('cancelRechazarBtn').addEventListener('click', () => {
        modal.remove();
    });
}

async function renderTodosProductos() {
    app.innerHTML = `${renderNavBar()}<div class="container"><div class="loading">Cargando...</div></div>`;
    attachNavEvents();
    
    try {
        const productos = await api.getProductos();
        
        app.innerHTML = `
            ${renderNavBar()}
            <div class="container">
                <div class="form-container" style="max-width: 1200px;">
                    <h2>📋 Todos los Productos/Servicios</h2>
                    <div class="table-container">
                        <table class="users-table">
                            <thead>
                                <tr><th>ID</th><th>Ofertante</th><th>Título</th><th>Precio</th><th>Estado</th><th>Creado</th></tr>
                            </thead>
                            <tbody>
                                ${productos.map(p => `
                                    <tr>
                                        <td>${p.id}</small></small></small></small></small></small></td>
                                        <td>${escapeHtml(p.nombre)} ${escapeHtml(p.apellido)}</small></small></small></small></small></small></td>
                                        <td><strong>${escapeHtml(p.titulo)}</strong></small></small></small></small></small></small></td>
                                        <td>Bs. ${parseFloat(p.precio).toFixed(2)}</small></small></small></small></small></small></td>
                                        <td>${getEstadoBadge(p.estado)}</small></small></small></small></small></small></td>
                                        <td><small>${new Date(p.fecha_creacion).toLocaleDateString()}</small></small></small></small></small></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        attachNavEvents();
        
    } catch (error) {
        showMessage(error.message, 'error');
        renderDashboard();
    }
}

// ==================== USUARIOS (ADMIN) ====================

async function renderUsuarios() {
    app.innerHTML = `
        ${renderNavBar()}
        <div class="container">
            <div class="form-container" style="max-width: 1200px;">
                <h2>👥 Gestión de Usuarios</h2>
                <div class="table-container">
                    <table class="users-table">
                        <thead>
                            <tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
                        </thead>
                        <tbody>
                            ${usuarios.map(u => `
                                <tr>
                                    <td>${u.id}</small></small></small></small></small></small></td>
                                    <td>${escapeHtml(u.nombre)} ${escapeHtml(u.apellido)}</small></small></small></small></small></small></td>
                                    <td>${escapeHtml(u.email)}</small></small></small></small></small></small></td>
                                    <td><span class="role-badge role-${u.rol}">${u.rol}</span></small></small></small></small></small></small></td>
                                    <td><span class="status-badge status-${u.activo === 1 ? 'active' : 'inactive'}">${u.activo === 1 ? 'Activo' : 'Inactivo'}</span></small></small></small></small></small></small></td>
                                    <td class="actions">
                                        <select class="rol-select" data-id="${u.id}" data-rol="${u.rol}" ${u.email === 'admin@petcare.com' ? 'disabled' : ''}>
                                            <option value="dueño" ${u.rol === 'dueño' ? 'selected' : ''}>Dueño</option>
                                            <option value="cuidador" ${u.rol === 'cuidador' ? 'selected' : ''}>Cuidador</option>
                                            <option value="administrador" ${u.rol === 'administrador' ? 'selected' : ''}>Administrador</option>
                                        </select>
                                        <button class="btn-icon btn-edit-user" data-id="${u.id}" title="Editar" ${u.email === 'admin@petcare.com' ? 'disabled' : ''}>✏️</button>
                                        <button class="btn-icon btn-delete-user" data-id="${u.id}" title="Eliminar" ${u.email === 'admin@petcare.com' ? 'disabled' : ''}>🗑️</button>
                                    </small></small></small></small></small></small></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    attachNavEvents();
    
    document.querySelectorAll('.rol-select').forEach(select => {
        select.addEventListener('change', async (e) => {
            const userId = parseInt(select.dataset.id);
            const nuevoRol = select.value;
            try {
                await api.updateUsuario(userId, { rol: nuevoRol });
                showMessage(`Rol cambiado a ${nuevoRol}`, 'success');
                await loadUsuarios();
                renderUsuarios();
            } catch (error) {
                showMessage(error.message, 'error');
                renderUsuarios();
            }
        });
    });
    
    document.querySelectorAll('.btn-edit-user').forEach(btn => {
        btn.addEventListener('click', async () => {
            const userId = parseInt(btn.dataset.id);
            await renderEditarUsuarioModal(userId);
        });
    });
    
    document.querySelectorAll('.btn-delete-user').forEach(btn => {
        btn.addEventListener('click', () => {
            const userId = parseInt(btn.dataset.id);
            renderDeleteUserModal(userId);
        });
    });
}

async function renderEditarUsuarioModal(userId) {
    try {
        const user = await api.getUsuario(userId);
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <h3>✏️ Editar Usuario</h3>
                <form id="editarUsuarioForm">
                    <div class="form-group">
                        <label>Nombre</label>
                        <input type="text" id="edit_nombre" value="${escapeHtml(user.nombre)}" required>
                    </div>
                    <div class="form-group">
                        <label>Apellido</label>
                        <input type="text" id="edit_apellido" value="${escapeHtml(user.apellido)}" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="edit_email" value="${escapeHtml(user.email)}" required>
                    </div>
                    <div class="form-group">
                        <label>Teléfono</label>
                        <input type="text" id="edit_telefono" value="${user.telefono || ''}">
                    </div>
                    <div class="form-group">
                        <label>Nueva Contraseña (dejar vacío para no cambiar)</label>
                        <input type="password" id="edit_password" placeholder="Mínimo 6 caracteres">
                    </div>
                    <div class="form-buttons">
                        <button type="submit" class="btn btn-primary">💾 Guardar</button>
                        <button type="button" id="closeModalBtn" class="btn btn-secondary">Cancelar</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('editarUsuarioForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const updateData = {
                nombre: document.getElementById('edit_nombre').value,
                apellido: document.getElementById('edit_apellido').value,
                email: document.getElementById('edit_email').value,
                telefono: document.getElementById('edit_telefono').value
            };
            
            const newPassword = document.getElementById('edit_password').value;
            if (newPassword) {
                if (newPassword.length < 6) {
                    showMessage('La contraseña debe tener al menos 6 caracteres', 'error');
                    return;
                }
                updateData.password = newPassword;
            }
            
            try {
                await api.updateUsuario(userId, updateData);
                showMessage('✅ Usuario actualizado', 'success');
                await loadUsuarios();
                renderUsuarios();
                modal.remove();
            } catch (error) {
                showMessage(error.message, 'error');
            }
        });
        
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            modal.remove();
        });
        
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

function renderDeleteUserModal(userId) {
    const user = usuarios.find(u => u.id === userId);
    if (!user) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Confirmar Eliminación</h3>
            <p>¿Eliminar a <strong>${escapeHtml(user.nombre)} ${escapeHtml(user.apellido)}</strong>?</p>
            <p style="color: var(--danger-color); font-size: 12px;">Esta acción no se puede deshacer.</p>
            <div class="modal-buttons">
                <button id="confirmDeleteUserBtn" class="btn btn-danger">Eliminar</button>
                <button id="cancelDeleteUserBtn" class="btn btn-secondary">Cancelar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('confirmDeleteUserBtn').addEventListener('click', async () => {
        try {
            await api.deleteUsuario(userId);
            showMessage('✅ Usuario eliminado', 'success');
            await loadUsuarios();
            renderUsuarios();
            modal.remove();
        } catch (error) {
            showMessage(error.message, 'error');
            modal.remove();
        }
    });
    
    document.getElementById('cancelDeleteUserBtn').addEventListener('click', () => {
        modal.remove();
    });
}

// ==================== FUNCIONES DE APOYO ====================

function getEstadoBadge(estado) {
    const estados = {
        'pendiente': '<span class="status-badge" style="background: #FFF3E0; color: #F57C00;">⏳ Pendiente</span>',
        'aprobado': '<span class="status-badge status-active">✅ Aprobado</span>',
        'rechazado': '<span class="status-badge status-inactive">❌ Rechazado</span>'
    };
    return estados[estado] || estado;
}

function getEstadoSolicitudBadge(estado) {
    const estados = {
        'pendiente': '<span class="status-badge" style="background: #FFF3E0; color: #F57C00;">⏳ Pendiente</span>',
        'aceptado': '<span class="status-badge status-active">✅ Aceptado</span>',
        'rechazado': '<span class="status-badge status-inactive">❌ Rechazado</span>',
        'completado': '<span class="status-badge" style="background: #E8F5E9; color: #2E7D32;">⭐ Completado</span>'
    };
    return estados[estado] || estado;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function attachNavEvents() {
    const oldButtons = document.querySelectorAll('.nav-btn[data-view]');
    oldButtons.forEach(btn => {
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
    });
    
    document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const view = btn.dataset.view;
            switch(view) {
                case 'mis-productos': renderMisProductos(); break;
                case 'buscar-productos': renderBuscarProductos(); break;
                case 'mis-solicitudes': renderMisSolicitudes(); break;
                case 'solicitudes-recibidas': renderSolicitudesRecibidas(); break;
                case 'notificaciones': renderNotificaciones(); break;
                case 'validar-productos': renderValidarProductos(); break;
                case 'todos-productos': renderTodosProductos(); break;
                case 'usuarios': renderUsuarios(); break;
                case 'dashboard': renderDashboard(); break;
                default: renderDashboard();
            }
        });
    });
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        const newLogoutBtn = logoutBtn.cloneNode(true);
        logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);
        newLogoutBtn.addEventListener('click', () => {
            clearSession();
            showMessage('Sesión cerrada', 'success');
            renderLogin();
        });
    }
}

async function init() {
    await loadUsuarios();
    if (loadSession()) {
        renderDashboard();
    } else {
        renderLogin();
    }
}

setInterval(() => {
    if (currentUser) {
        cargarNotificacionesNoLeidas();
    }
}, 30000);

init();