from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import re

app = Flask(__name__)

# Conexión a MongoDB
client = MongoClient("mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority")
db = client['<nombre_bd>']

# Colecciones
libros = db['libros']
usuarios = db['usuarios']
ventas = db['ventas']

# Función de validación de teléfono
def validar_telefono(numero):
    return re.match(r'^\d{10}$', numero)

# Rutas principales
@app.route('/')
def inicio():
    return render_template('base.html')

# ========== LIBROS ==========
@app.route('/libros', methods=['GET', 'POST'])
def gestion_libros():
    if request.method == 'POST':
        libro_data = {
            'titulo': request.form['titulo'],
            'autor': request.form['autor'],
            'isbn': request.form['isbn'],
            'editorial': request.form['editorial'],
            'anio': int(request.form['anio']),
            'cantidad': int(request.form['cantidad']),
            'precio': float(request.form['precio'])
        }
        libros.insert_one(libro_data)
        return redirect(url_for('gestion_libros'))
    
    todos_libros = list(libros.find())
    return render_template('libros.html', libros=todos_libros)

@app.route('/eliminar_libro/<id>')
def eliminar_libro(id):
    libros.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('gestion_libros'))

@app.route('/editar_libro/<id>', methods=['GET', 'POST'])
def editar_libro(id):
    libro = libros.find_one({'_id': ObjectId(id)})
    
    if request.method == 'POST':
        libros.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'titulo': request.form['titulo'],
                'autor': request.form['autor'],
                'isbn': request.form['isbn'],
                'editorial': request.form['editorial'],
                'anio': int(request.form['anio']),
                'cantidad': int(request.form['cantidad']),
                'precio': float(request.form['precio'])
            }}
        )
        return redirect(url_for('gestion_libros'))
    
    return render_template('editar_libro.html', libro=libro)

# ========== USUARIOS ==========
@app.route('/usuarios', methods=['GET', 'POST'])
def gestion_usuarios():
    if request.method == 'POST':
        if not validar_telefono(request.form['telefono']):
            return "Teléfono inválido, debe tener 10 dígitos", 400
            
        usuario_data = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'email': request.form['email'],
            'telefono': request.form['telefono']
        }
        usuarios.insert_one(usuario_data)
        return redirect(url_for('gestion_usuarios'))
    
    todos_usuarios = list(usuarios.find())
    return render_template('usuarios.html', usuarios=todos_usuarios)

@app.route('/eliminar_usuario/<id>')
def eliminar_usuario(id):
    usuarios.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('gestion_usuarios'))

@app.route('/editar_usuario/<id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = usuarios.find_one({'_id': ObjectId(id)})
    
    if request.method == 'POST':
        if not validar_telefono(request.form['telefono']):
            return "Teléfono inválido, debe tener 10 dígitos", 400
        
        usuarios.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'email': request.form['email'],
                'telefono': request.form['telefono']
            }}
        )
        return redirect(url_for('gestion_usuarios'))
    
    return render_template('editar_usuario.html', usuario=usuario)

# ========== VENTAS ==========



# En la ruta de ventas (/ventas)
@app.route('/ventas', methods=['GET', 'POST'])
def gestion_ventas():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            usuario_id = request.form['usuario']
            libros_ids = request.form.getlist('libro')
            cantidades = request.form.getlist('cantidad')
            monto_pagado = float(request.form['monto_pagado'])

            # Validaciones básicas
            if not libros_ids or not cantidades:
                return "Debe seleccionar al menos un libro", 400
                
            if len(libros_ids) != len(cantidades):
                return "Error en los datos enviados", 400

            total = 0
            libros_vendidos = []

            # Procesar cada libro
            for libro_id, cantidad in zip(libros_ids, cantidades):
                libro = libros.find_one({'_id': ObjectId(libro_id)})
                cantidad = int(cantidad)
                
                if not libro:
                    return f"Libro no encontrado: {libro_id}", 400
                
                if libro['cantidad'] < cantidad:
                    return f"Stock insuficiente para {libro['titulo']}", 400
                
                # Calcular subtotal
                subtotal = libro['precio'] * cantidad
                total += subtotal
                
                # Registrar libro vendido
                libros_vendidos.append({
                    'libro_id': ObjectId(libro_id),
                    'cantidad': cantidad,
                    'precio_unitario': libro['precio']
                })
                
                # Actualizar stock
                libros.update_one(
                    {'_id': ObjectId(libro_id)},
                    {'$inc': {'cantidad': -cantidad}}
                )

            # Calcular cambio
            cambio = monto_pagado - total
            if cambio < 0:
                return "El monto pagado es insuficiente", 400

            # Crear registro de venta
            venta_data = {
                'usuario_id': ObjectId(usuario_id),
                'libros': libros_vendidos,
                'fecha': datetime.now(),
                'total': total,
                'monto_pagado': monto_pagado,
                'cambio': cambio
            }
            
            # Insertar en la base de datos
            ventas.insert_one(venta_data)
            
            return redirect(url_for('gestion_ventas'))
            
        except Exception as e:
            return f"Error al procesar la venta: {str(e)}", 500

    # Obtener datos para el formulario (GET)
    todos_usuarios = list(usuarios.find())
    todos_libros = list(libros.find())
    
    # Obtener historial de ventas con lookups
    historial_ventas = list(ventas.aggregate([
        {
            '$lookup': {
                'from': 'usuarios',
                'localField': 'usuario_id',
                'foreignField': '_id',
                'as': 'usuario'
            }
        },
        {'$unwind': '$usuario'},
        {
            '$lookup': {
                'from': 'libros',
                'localField': 'libros.libro_id',
                'foreignField': '_id',
                'as': 'libros_info'
            }
        }
    ]))
    
    return render_template('ventas.html',
                         usuarios=todos_usuarios,
                         libros=todos_libros,
                         ventas=historial_ventas)

@app.route('/eliminar_venta/<id>')
def eliminar_venta(id):
    try:
        venta = ventas.find_one({'_id': ObjectId(id)})
        
        # Restaurar stock
        for libro in venta['libros']:
            libros.update_one(
                {'_id': libro['libro_id']},
                {'$inc': {'cantidad': libro['cantidad']}}
            )
        
        ventas.delete_one({'_id': ObjectId(id)})
        return redirect(url_for('gestion_ventas'))
    except Exception as e:
        return f"Error: {str(e)}", 400






if __name__ == '__main__':
    app.run(debug=True)