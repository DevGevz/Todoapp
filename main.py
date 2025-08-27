import sqlite3
import os

def get_connection(name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, name)
    return sqlite3.connect(db_path)

# -------------------- Users --------------------
def create_users_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """
    with conn:
        conn.execute(query)

def insert_user(conn, name: str, email: str, password: str, role: str):
    q = "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)"
    with conn:
        conn.execute(q, (name, email, password, role))

def cherche_tous(conn):
    q = "SELECT * FROM users"
    with conn:
        return conn.execute(q).fetchall()

def delete_user(conn, user_id: int):
    q = "DELETE FROM users WHERE id = ?"
    with conn:
        conn.execute(q, (user_id,))

def update_email(conn, user_id: int, new_email: str):
    q = "UPDATE users SET email=? WHERE id=?"
    with conn:
        conn.execute(q, (new_email, user_id))

def set_admin(conn, name: str):
    q = "UPDATE users SET role='admin' WHERE name=?"
    with conn:
        conn.execute(q, (name,))

# -------------------- Tasks --------------------
def create_tasks_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        text TEXT,
        image_path TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
    with conn:
        conn.execute(query)

def insert_task(conn, user_id: int, name: str, text: str, image_path: str):
    q = "INSERT INTO tasks (user_id, name, text, image_path) VALUES (?, ?, ?, ?)"
    with conn:
        cur = conn.execute(q, (user_id, name, text, image_path))
        return cur.lastrowid


def get_user_tasks(conn, user_id: int):
    q = "SELECT id, name, text, image_path FROM tasks WHERE user_id=?"
    with conn:
        rows = conn.execute(q, (user_id,)).fetchall()
    return [
        {"id": r[0], "name": r[1], "text": r[2], "image_path": r[3] if r[3] else ""}
        for r in rows
    ]

def delete_tasks_for_user(conn, user_id: int):
    q = "DELETE FROM tasks WHERE user_id=?"
    with conn:
        conn.execute(q, (user_id,))

def delete_task(conn, task_id: int):
    q = "DELETE FROM tasks WHERE id=?"
    with conn:
        conn.execute(q, (task_id,))



# -------------------- Main --------------------
def main():
    conn = get_connection("users.db")
    
    # Création des tables si elles n'existent pas
    create_users_table(conn)
    create_tasks_table(conn)
    
    print("Database ready !")

    try:
        while True:
            start = input(
                "\nEnter Option (AddUser, DeleteUser, UpdateEmail, SetAdmin, ViewUsers, "
                "AddTask, DeleteTask, ViewTasks, Quit): "
            ).lower()

            if start == 'adduser':
                name = input("Enter Name: ")
                email = input("Enter Email: ")
                password = input("Enter Password: ")
                insert_user(conn, name, email, password, "utilisateur")

            elif start == 'viewusers':
                print("All Users:")
                for user in cherche_tous(conn):
                    print(user)

            elif start == 'deleteuser':
                user_id = int(input("User ID to delete: "))
                delete_user(conn, user_id)

            elif start == 'updateemail':
                user_id = int(input("Enter user ID: "))
                new_email = input("New Email: ")
                update_email(conn, user_id, new_email)  # ← nom uniforme

            elif start == 'setadmin':
                name = input("Enter Username: ")
                set_admin(conn, name)  # ← nom uniforme

            elif start == 'addtask':
                user_id = int(input("Enter User ID: "))
                task_name = input("Task Name: ")
                task_text = input("Task Text: ")
                icon = input("Icon for Task (e.g., fa-graduation-cap): ")
                insert_task(conn, user_id, task_name, task_text, icon)

            elif start == 'viewtasks':
                user_id = int(input("Enter User ID to view tasks: "))
                tasks = get_user_tasks(conn, user_id)  # ← nom uniforme
                for task in tasks:
                    print(task)

            elif start == 'deletetask':
                user_id = int(input("Enter User ID: "))
                confirm = input(f"Delete ALL tasks for user {user_id}? (y/n): ").lower()
                if confirm == 'y':
                    delete_tasks_for_user(conn, user_id)  # à créer
                    print(f"All tasks for user {user_id} deleted.")

            elif start == 'quit':
                break

            else:
                print("Invalid option. Try again.")
    finally:
        conn.close()
        print("Connection closed.")



if __name__ == "__main__":
    main()
