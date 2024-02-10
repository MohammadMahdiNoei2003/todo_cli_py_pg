import psycopg2
from typing import List
import datetime
from model import Todo

conn = psycopg2.connect(database="todo", user="postgres", password="Mdb82n", host="localhost")
c  = conn.cursor()

def create_table():
    c.execute("""CREATE TABLE IF NOT EXISTS todos(
              task TEXT,
              category TEXT,
              date_added TEXT,
              date_completed TEXT,
              status INTEGER,
              position INTEGER
    )""")
    conn.commit()

create_table()

def insert_todo(todo: Todo):
    c.execute('select count(*) FROM todos')
    count = c.fetchone()[0]
    todo.position = count if count else 0
    with conn:
        c.execute("INSERT INTO todos (task, category, date_added, date_completed, status, position) VALUES (%s, %s, %s, %s, %s, %s)", 
          (todo.task, todo.category, todo.date_added, todo.date_completed, todo.status, todo.position))

def get_all_todos() -> List[Todo]:
    c.execute('select * from todos')
    results = c.fetchall()
    todos = []
    for result in results:
        todos.append(Todo(*result))
    return todos

def delete_todo(position):
    c.execute('select count(*) from todos')
    count = c.fetchone()[0]

    with conn:
        c.execute("DELETE from todos WHERE position = %s", (position,))
        for pos in range(position+1, count):
            change_position(pos, pos-1, False)

def change_position(old_position: int, new_position: int, commit=True):
    c.execute("UPDATE todos SET position = %s WHERE position = %s", (new_position, old_position))
    if (commit):
        conn.commit()

def update_todo(position: int, task: str, category:str):
    with conn:
        if task is not None and category is not None:
            c.execute("UPDATE todos SET task = %s, category = %s WHERE position = :position", (task, category, position))
        elif task is not None:
            c.execute("UPDATE todos SET task = %s WHERE position = %s", (task, position))
        elif category is not None:
            c.execute("UPDATE todos SET category = %s WHERE position = %s", (category, position))

def complete_todo(position: int):
    with conn:
        c.execute("UPDATE todos SET status = 2, date_completed = %s WHERE position = %s", (datetime.datetime.now().isoformat(), position))