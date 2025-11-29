import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

# ==============================================================================
# 1. Configuración y Cliente de Supabase
# ==============================================================================
# En Vercel, estas variables se cargarán automáticamente desde el entorno.
# Asegúrate de definirlas en la configuración de Vercel.
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "https://xxfummgzkjxpvrzfutby.supabase.co") 
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4ZnVtbWd6a2p4cHZyemZ1dGJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNzUxMTcsImV4cCI6MjA3Nzg1MTExN30.expLJm8IhweMGmXtkCdqX5Ix0hotEgdzdBHrzTgisew")
ADMIN_TOKEN: str = os.environ.get("ADMIN_TOKEN", "xrellmzGachidaxmll_contrasenia&&1234gamalele") 
SECRET_PASSWORD: str = os.environ.get("SECRET_PASSWORD", "mangas123") # Contraseña de login para demo

# Inicialización del cliente Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Conexión con Supabase establecida.")
except Exception as e:
    print(f"Error al conectar a Supabase: {e}")

# ==============================================================================
# 2. Configuración de Flask
# ==============================================================================
# La estructura de Vercel requiere que el archivo de la función sea 'api/index.py' 
# o similar, y que el manejador principal apunte a la aplicación Flask.
app = Flask(__name__)
CORS(app) 

# Función de utilidad para validar el token de administrador
def admin_required():
    """Verifica si el encabezado 'Authorization' contiene el token secreto."""
    token = request.headers.get('Authorization')
    # Nota: Usamos el token configurado en las variables de entorno de Vercel
    if token == f'Bearer {ADMIN_TOKEN}':
        return None  # Autorización exitosa
    return jsonify({"error": "No autorizado", "message": "Se requiere token de administrador."}, 401)

# ==============================================================================
# 3. Endpoints de la API
# ==============================================================================

# Endpoint de Prueba
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "API de Manga en funcionamiento",
        "service": "Flask & Supabase en Vercel",
        "docs": "Revisa los endpoints en /api/mangas"
    })

# Endpoint para el Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    secret_key = data.get('secret_key')
    
    if secret_key == SECRET_PASSWORD: 
        # Retorna el token de la variable de entorno
        return jsonify({
            "success": True, 
            "message": "Autenticación exitosa.",
            "token": ADMIN_TOKEN 
        })
    else:
        return jsonify({"success": False, "message": "Clave secreta incorrecta."}, 401)

# Endpoint para listar todos los mangas (Acceso Público)
@app.route('/api/mangas', methods=['GET'])
def get_mangas():
    try:
        response = supabase.table('mangas').select('id, titulo, autor, descripcion').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}, 500)

# Endpoint para crear un nuevo manga (REQUIERE AUTORIZACIÓN DE ADMIN)
@app.route('/api/mangas', methods=['POST'])
def create_manga():
    auth_error = admin_required()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    if not data or 'titulo' not in data:
        return jsonify({"error": "Faltan datos requeridos (ej. 'titulo')."}, 400)

    try:
        response = supabase.table('mangas').insert(data).execute()
        return jsonify(response.data[0], 201)
    except Exception as e:
        return jsonify({"error": str(e)}, 500)

# Endpoint para eliminar un manga (REQUIERE AUTORIZACIÓN DE ADMIN)
@app.route('/api/mangas/<int:manga_id>', methods=['DELETE'])
def delete_manga(manga_id):
    auth_error = admin_required()
    if auth_error:
        return auth_error
        
    try:
        response = supabase.table('mangas').delete().eq('id', manga_id).execute()
        
        if not response.data:
             return jsonify({"message": f"Manga con ID {manga_id} no encontrado."}, 404)
        
        return jsonify({"message": f"Manga con ID {manga_id} eliminado exitosamente."})
    except Exception as e:
        return jsonify({"error": str(e)}, 500)

# =VCEL_SERVERLESS_COMPATIBILITY
# Solo para desarrollo local, no es necesario para Vercel
if __name__ == '__main__':
    app.run(debug=True)
