from flask import Flask, render_template, request, Response, redirect, url_for
import sqlalchemy

from werkzeug.exceptions import abort

from . import sql

db = None

app = Flask(__name__)

@app.before_first_request
def create_tables():
    global db
    db = db or sql.init_connection_engine()
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS rates "
            "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "candname VARCHAR(100) NOT NULL, skill1 VARCHAR(100) NOT NULL, feedbacks1 INT NOT NULL, skill2 VARCHAR(100) NOT NULL, "
            "feedbacks2 INT NOT NULL, skill3 VARCHAR(100), feedbacks3 INT, skill4 VARCHAR(100), feedbacks4 INT );"
        )

@app.route('/')
def index():
    with db.connect() as conn:
        rates = conn.execute(
            'SELECT id, created, candname'
            ' FROM rates p'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('rates.html', rates=rates)

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        candname = request.form['candname']
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        skill3 = request.form['skill3']
        skill4 = request.form['skill4']
        error = None

        if not candname:
            error = 'Name is required.'
        
        if error is not None:
            abort(404)
        else:
            stmt = sqlalchemy.text(
                "INSERT INTO rates (candname, skill1, skill2, skill3, skill4, feedbacks1, feedbacks2, feedbacks3, feedbacks4) "
                "VALUES (:q, :a1, :a2, :a3, :a4, 0, 0, 0, 0)"
            )
            with db.connect() as conn:
                conn.execute(
                    stmt,
                    q=candname,
                    a1=skill1,
                    a2=skill2,
                    a3=skill3,
                    a4=skill4
                )
        return redirect(url_for('index'))

    else:    
        return render_template('rate_create.html')

def get_rate(id):
    with db.connect() as conn:
        stmt = sqlalchemy.text(
            "SELECT * FROM rates p WHERE p.id = :id"
        )
        rate = conn.execute(
            stmt,
            id=id
        ).fetchone()

    if rate is None:
        abort(404, f"Candidate id {id} doesn't exist.")

    return rate

@app.route('/rate/<int:index>', methods=['GET','POST'])
def rate_view(index):
    if request.method == 'POST':
        rate = get_rate(index)
        feedback_name = request.form["feedback"]
        
        stmt = sqlalchemy.text(
            "UPDATE rates SET " + str(feedback_name) + " = " + str(feedback_name) + " + 1 WHERE id = :id"
        )
        with db.connect() as conn:
            conn.execute(
                stmt,
                id=index
            )

        return redirect(url_for('rate_view', index=index))

    else:
        rate = get_rate(index)
    
        return render_template('rate_view.html', rate=rate)

@app.route('/rate-delete/<int:index>')
def rate_delete(index):
    stmt = sqlalchemy.text(
        "DELETE FROM rates WHERE id = :id"
    )
    with db.connect() as conn:
        conn.execute(
            stmt,
            id=str(index)
        )
    return redirect(url_for('index'))
