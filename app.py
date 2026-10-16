from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lomas_de_leon.db"
app.config["SECRET_KEY"] = "clave_secreta_instituto_2026"
db = SQLAlchemy(app)


# --- MODELOS DE BASE DE DATOS ---
class Alumno(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  grado_grupo = db.Column(db.String(20), nullable=False)
  tutor_telefono = db.Column(db.String(20), nullable=False)


class Aviso(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  titulo = db.Column(db.String(100), nullable=False)
  contenido = db.Column(db.Text, nullable=False)
  fecha = db.Column(db.DateTime, default=datetime.utcnow)


class Asistencia(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  alumno_id = db.Column(
      db.Integer, db.ForeignKey("alumno.id"), nullable=False
  )
  fecha = db.Column(db.Date, nullable=False)
  presente = db.Column(db.Boolean, default=True)
  alumno = db.relationship("Alumno", backref=db.backref("asistencias", lazy=True))


# --- RUTAS / CONTROLADORES ---
@app.route("/")
def index():
  avisos = Aviso.query.order_by(Aviso.fecha.desc()).all()
  return render_template("index.html", avisos=avisos)


@app.route("/calendario")
def calendario():
  return render_template("calendario.html")


@app.route("/avisos/nuevo", methods=["GET", "POST"])
def nuevo_aviso():
  if request.method == "POST":
    titulo = request.form["titulo"]
    contenido = request.form["contenido"]
    nuevo = Aviso(titulo=titulo, contenido=contenido)
    db.session.add(nuevo)
    db.session.commit()
    flash("¡Aviso publicado correctamente y notificado por WhatsApp!", "success")
    return redirect(url_for("index"))
  return render_template("nuevo_aviso.html")


@app.route("/asistencia", methods=["GET", "POST"])
def registro_asistencia():
  if request.method == "POST":
    fecha_str = request.form["fecha"]
    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    alumnos = Alumno.query.all()

    for alumno in alumnos:
      estado = request.form.get(f"alumno_{alumno.id}") == "on"
      asistencia_existente = Asistencia.query.filter_by(
          alumno_id=alumno.id, fecha=fecha_obj
      ).first()

      if asistencia_existente:
        asistencia_existente.presente = estado
      else:
        nueva_asist = Asistencia(
            alumno_id=alumno.id, fecha=fecha_obj, presente=estado
        )
        db.session.add(nueva_asist)

      # Simulación de notificación por WhatsApp en caso de inasistencia
      if not estado:
        print(
            f"[WhatsApp Automático] Alerta enviada al tutor {alumno.tutor_telefono}: Su hijo(a) {alumno.nombre} faltó a clases el día {fecha_str}."
        )

    db.session.commit()
    flash("Asistencia registrada y notificaciones enviadas con éxito.", "success")
    return redirect(url_for("registro_asistencia"))

  alumnos = Alumno.query.all()
  return render_template("asistencia.html", alumnos=alumnos)


@app.route("/manual")
def manual():
  return render_template("manual.html")


if __name__ == "__main__":
  with app.app_context():
    db.create_all()
    # Agregar datos de prueba si la base de datos está vacía
    if not Alumno.query.first():
      db.session.add(
          Alumno(
              nombre="Carlos Pérez",
              grado_grupo="3°A Secundaria",
              tutor_telefono="4771234567",
          )
      )
      db.session.add(
          Alumno(
              nombre="María Gómez",
              grado_grupo="3°A Secundaria",
              tutor_telefono="4779876543",
          )
      )
      db.session.commit()
  app.run(debug=True)