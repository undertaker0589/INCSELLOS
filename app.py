from flask import Flask 
from flask import render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask import send_from_directory,jsonify, flash
from datetime import datetime
import os
import bcrypt


app = Flask(__name__)
app.secret_key = "incauca"

mysql= MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = "sellos"
mysql.init_app(app)



# home de la aplicacion web de sellos incauca
@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        role = session['role']
        return render_template('home.html', username=username, role=role)
    else:
        return redirect(url_for('index'))

# inicio de la aplicacion web de sellos incauca
@app.route('/')
def index():
    return render_template('index.html')

# script para ingresar al formulario de registro a un nuevo usuario en la aplicacion web de sellos incauca
@app.route('/registro')
def registro():
    return render_template('registro.html')

# script para cerrar sesion en la aplicacion web de sellos incauca
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# script para iniciar sesion en la aplicacion web de sellos incauca
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']                
        conexion= mysql.connection
        cursor= conexion.cursor()
        result= cursor.execute("SELECT * FROM usuarios WHERE username=%s",(username,))
        data= cursor.fetchone()
        conexion.commit()
        if result > 0:
            if bcrypt.checkpw(password.encode('utf-8'), data[2].encode('utf-8')):
                session['username'] = username
                session['role'] = data[3]
                return render_template('home.html')
            else:
                flash('Contraseña incorrecta', 'danger')
                return redirect(url_for('index'))
        else:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('index'))

# script para registrarse en la aplicacion web de sellos incauca
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())               
        conexion= mysql.connection
        cursor= conexion.cursor()
        cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)", (username,hashed_password, role))
        conexion.commit()
        return redirect(url_for('index'))
    

# script para AGREGAR un nuevo sello en la aplicacion web de sellos incauca
@app.route('/agregar_sello', methods=['POST'])
def agregar_sello():
    if request.method == 'POST':
        numero = request.form['numero']
        fecha = request.form['fecha']
        username = session['username']
        # Convertir la fecha a un objeto datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        # Verificar si la fecha es mayor a la fecha actual
        if fecha > fecha_actual or fecha < fecha_actual:
            flash('La fecha no puede ser MAYOR o MENOR a la fecha actual')
            return redirect(url_for('home'))
        else:
            # Verificar si el sello ya existe
            conexion= mysql.connection
            cursor= conexion.cursor()
            cursor.execute("SELECT * FROM incauca WHERE numero=%s", (numero,))
            result= cursor.fetchone()
            if result:
                flash(message='El sello ya existe')
                return redirect(url_for('home'))
            # Guardar el sello en la base de datos
            conexion= mysql.connection
            cursor= conexion.cursor()
            cursor.execute("INSERT INTO incauca (numero, fecha, supervisor) VALUES (%s, %s, %s)", (numero, fecha, username))
            conexion.commit()           
            return redirect(url_for('home',))
        
# script para AGREGAR un nuevo sello en la aplicacion web de sellos POLIPROPILENO
@app.route('/agregar_sello_pp', methods=['POST'])
def agregar_sello_pp():
    if request.method == 'POST':
        numero = request.form['numero']
        fecha = request.form['fecha']
        username = session['username']
        # Convertir la fecha a un objeto datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        # Verificar si la fecha es mayor a la fecha actual
        if fecha > fecha_actual or fecha < fecha_actual:
            flash('La fecha no puede ser MAYOR o MENOR a la fecha actual')
            return redirect(url_for('home'))
        else:
            # Verificar si el sello ya existe
            conexion= mysql.connection
            cursor= conexion.cursor()
            cursor.execute("SELECT * FROM polipropileno WHERE numero=%s", (numero,))
            result= cursor.fetchone()
            if result:
                flash(message='El sello ya existe')
                return redirect(url_for('home'))
            conexion.commit()
            # Guardar el sello en la base de datos
            conexion= mysql.connection
            cursor= conexion.cursor()
            cursor.execute("INSERT INTO polipropileno (numero, fecha, supervisor) VALUES (%s, %s, %s)", (numero, fecha, username))
            conexion.commit()           
            return redirect(url_for('home',))
        
# script para visualizar los sellos de incauca agregados 
@app.route('/view_sello')
def view_sello():
    if 'username' not in session:
        return redirect(url_for('index'))
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM incauca")
    sello= cursor.fetchall()      
    conexion.commit()
    return render_template('incauca.html', sellos=sello)

# script para visualizar los sellos de polipropileno agregados
@app.route('/view_sello_pp')
def view_sello_pp():
    if 'username' not in session:
        return redirect(url_for('index'))
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM polipropileno")
    dato= cursor.fetchall()      
    conexion.commit()
    return render_template('pp.html', datos=dato)

#script para filtrar los sellos de incauca
@app.route('/filtrar_sello', methods=['POST'])
def filtrar_sello():
    if request.method == 'POST':
        numero= request.form['numero']
        conexion= mysql.connection
        cursor= conexion.cursor()
        cursor.execute("SELECT * FROM incauca WHERE numero=%s", (numero,))
        sello= cursor.fetchall()      
        conexion.commit()
        if sello:
            return render_template('incauca.html', sellos=sello)
        else:
            flash(message='El sello no existe')
            return redirect(url_for('view_sello'))
        
#script para filtrar los sellos de polipropileno
@app.route('/filtrar_sello_pp', methods=['POST'])
def filtrar_sello_pp():
    if request.method == 'POST':
        numero = request.form['numero']
        conexion= mysql.connection
        cursor= conexion.cursor()
        cursor.execute("SELECT * FROM polipropileno WHERE numero=%s", (numero,))
        dato= cursor.fetchall()      
        conexion.commit()
        if dato:
            return render_template('pp.html', datos=dato)
        else:
            flash(message='El sello no existe')
            return redirect(url_for('view_sello_pp'))
        
#script para ver los graficos de los sellos de incauca
@app.route('/graficos')
def graficos():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('graficos.html')

# api para obtener los sellos de incauca
@app.route('/get_api_developer', methods=['GET'])
def get_api_developer():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT supervisor, COUNT(*) AS cantidad_registros FROM incauca GROUP BY supervisor")
    usuario= cursor.fetchall()
    conexion.commit()
    return jsonify({"datos":usuario})

# api para ver registros por mes de los sellos incauca 
@app.route("/get_api_month", methods=['GET'])
def get_api_month():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT MONTHNAME(fecha) AS mes, COUNT(*) AS cantidad_eventos FROM incauca GROUP BY MONTHNAME(fecha) DESC;;")
    usuario= cursor.fetchall()
    conexion.commit()
    return jsonify({"datos":usuario})

# api para ver registros sellos (graficos)
@app.route('/get_api_polipro', methods=['GET'])
def get_api_polipro():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT MONTHNAME(fecha) AS mes, COUNT(*) AS cantidad_eventos FROM polipropileno GROUP BY MONTHNAME(fecha) DESC;;")
    usuario= cursor.fetchall()
    conexion.commit()
    return jsonify({"datos":usuario})

#script para editar valores desde la app web sellos incauca
@app.route('/editar/<id>')
def editar(id):
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM incauca WHERE id=%s",[id])
    fruta= cursor.fetchall()
    conexion.commit()
    return render_template('editar_incauca.html', sello=fruta[0])

# script para actualizar los valores de los sellos incauca
@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        numero= request.form["numero"]
        conexion= mysql.connection
        cursor= conexion.cursor()
        cursor.execute("UPDATE incauca SET numero=%s WHERE id=%s",(numero,id))
        conexion.commit()
        return redirect(url_for('view_sello'))
    
# script para eliminar un registro de la base de datos de la app web
@app.route('/delete/<string:id>')
def delete(id):
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM incauca WHERE id=%s",[id])
    conexion.commit()
    return redirect(url_for('view_sello'))

# script para editar sellos de la app web 
@app.route('/editar_poli/<id>')
def editar_poli(id):
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM polipropileno WHERE id=%s",[id])
    ventana= cursor.fetchall()
    conexion.commit()
    return render_template('editar_pp.html', dato=ventana[0])

# script para actualizar los valores de los sellos polipropileno
@app.route('/update_poli/<id>',methods=['POST'])
def update_poli(id):
    if request.method == 'POST':
        numero= request.form["numero"]
        conexion= mysql.connection
        cursor= conexion.cursor()
        cursor.execute("UPDATE polipropileno SET numero=%s WHERE id=%s",(numero,id))
        conexion.commit()
        return redirect(url_for('view_sello_pp'))
    
# script para eliminar un registro de la base de datos de la app web
@app.route('/delete_pp/<string:id>')
def delete_pp(id):
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM polipropileno WHERE id=%s",[id])
    conexion.commit()
    return redirect(url_for('view_sello_pp'))

# api para contar los sellos de la app web incauca
@app.route('/get_api_total', methods=['GET'])
def get_api_count():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM incauca")
    total= cursor.fetchone()
    conexion.commit()
    return jsonify({"total": total[0]})

# api para contar los sellos de la app web polipropileno
@app.route('/get_api_total_pp', methods=['GET'])
def get_api_count_pp():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM polipropileno")
    totalp= cursor.fetchone()
    conexion.commit()
    return jsonify({"totalp": totalp[0]})

# script de la api calcular promedio del gasto de los sellos por mes 
@app.route('/promedio_incauca',methods=['GET'])
def promedio_incauca():
    conexion= mysql.connection
    cursor= conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM incauca UNION ALL SELECT COUNT(*) FROM polipropileno;")
    promedio_inc= cursor.fetchall()
    conexion.commit()
    return jsonify({"promedio":promedio_inc})




     
        

if __name__ == '__main__':app.run(debug=True)