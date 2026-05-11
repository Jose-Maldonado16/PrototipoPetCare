# PetCare - Módulo Gestión de Usuarios

Sistema completo de gestión de usuarios para la plataforma PetCare con autenticación, CRUD de usuarios, búsqueda en tiempo real y estadísticas.

## Tecnologías Utilizadas

- **Backend**: Python 3 + Flask
- **Base de Datos**: SQLite 3
- **Frontend**: JavaScript Vanilla + HTML5 + CSS3

## Requisitos Previos

- Python 3.7 o superior instalado
- Pip (gestor de paquetes de Python)
- Navegador web moderno

## Instalación y Ejecución

### 1. Configuración del Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor Flask
python app.py