from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from main import (
    get_connection, 
    insert_user, 
    cherche_tous, 
    insert_task, 
    get_user_tasks, 
    delete_task   # ⚡ supprime une tâche
)

import os

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------- Routes --------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    conn = get_connection("users.db")
    insert_user(conn, username, email, password, "utilisateur")
    conn.close()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    identifier = request.form["username"]
    password = request.form['password']

    conn = get_connection("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, role, name, email FROM users 
        WHERE (name = ? OR email = ?) AND password = ?
    """, (identifier, identifier, password))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, role, name, email = user
        session['user_id'] = user_id
        session['role'] = role
        session['name'] = name
        session['email'] = email

        conn = get_connection("users.db")
        if role == "admin":
            users = cherche_tous(conn)
            conn.close()
            return render_template("admin.html", users=users)
        else:
            tasks = get_user_tasks(conn, user_id)
            conn.close()
            return render_template("logged.html", tasks=tasks, name=name, email=email)
    else:
        return "Nom d'utilisateur ou mot de passe incorrect", 401

@app.route('/add_task', methods=['POST'])
def add_task_route():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    name = request.form['name']
    text = request.form['text']
    image_path = request.form.get('image_path')

    conn = get_connection("users.db")
    task_id = insert_task(conn, user_id, name, text, image_path)
    conn.close()

    return jsonify({"id": task_id}), 200

@app.route('/delete_task', methods=['POST'])
def delete_task_route():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    task_id = data.get("id")

    if not task_id:
        return jsonify({"error": "Missing task id"}), 400

    try:
        task_id = int(task_id)
        user_id = session['user_id']

        conn = get_connection("users.db")
        c = conn.cursor()
        c.execute("SELECT id FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        row = c.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Task not found or not yours"}), 404

        delete_task(conn, task_id)
        conn.close()
        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Gestion du compte --------------------
@app.route('/update_name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return redirect(url_for("index"))
    new_name = request.form.get("new_name")
    if not new_name:
        return redirect(url_for("index"))

    conn = get_connection("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET name=? WHERE id=?", (new_name, session['user_id']))
    conn.commit()
    conn.close()

    session['name'] = new_name  # mettre à jour la session
    return redirect(url_for("index"))

@app.route('/update_email', methods=['POST'])
def update_email():
    if 'user_id' not in session:
        return redirect(url_for("index"))
    new_email = request.form.get("new_email")
    if not new_email:
        return redirect(url_for("index"))

    conn = get_connection("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET email=? WHERE id=?", (new_email, session['user_id']))
    conn.commit()
    conn.close()

    session['email'] = new_email
    return redirect(url_for("index"))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for("index"))

    user_id = session['user_id']
    conn = get_connection("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    session.clear()  # vider la session après suppression
    return redirect(url_for("index"))

# -------------------- Run --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback 5000 si local
    app.run(host="0.0.0.0", port=port)

