from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS


# Must correspond to what is used in Vue.
USERNAME_REQUEST_NAME = "username"
ID_REQUEST_NAME = "id"
DOCUMENT_REQUEST_NAME = "document"


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
conn = None


# TODO: This is totally insecure.
@app.route("/get_current_documents", methods=["POST"])
def get_current_documents():
    username = request.json[USERNAME_REQUEST_NAME]
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * from current_documents where username = %s", (username,))
    ret = {}

    for current_document in cur.fetchall():
        ret[current_document["id"]] = current_document
    return jsonify(ret)


@app.route("/delete_document", methods=["POST"])
def delete_document():
    id = request.json[ID_REQUEST_NAME]
    cur = conn.cursor()
    cur.execute("DELETE from current_documents where id = %s", (id,))
    conn.commit()
    cur.close()
    return jsonify({"id": str(id)})


@app.route("/edit_document", methods=["POST"])
def edit_document():
    id = request.json[ID_REQUEST_NAME]
    document = request.json[DOCUMENT_REQUEST_NAME]
    cur = conn.cursor()
    cur.execute(
        "UPDATE current_documents SET title = %s, url = %s, priority = %s, category = %s, notes = %s " +
        "where id = %s RETURNING *",
        (document['title'], document['url'], document['priority'], document['category'], document['notes'], id))
    document_values = cur.fetchone()
    conn.commit()
    cur.close()
    ret = {}
    ret['id'] = document_values[0]
    ret['username'] = document_values[1]
    ret['title'] = document_values[2]
    ret['priority'] = document_values[3]
    ret['category'] = document_values[4]
    ret['url'] = document_values[5]
    ret['notes'] = document_values[6]
    return jsonify({"document": ret})


@app.route("/add_document", methods=["POST"])
def add_document():
    document = request.json[DOCUMENT_REQUEST_NAME]
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO current_documents(title, username, url, priority, category, notes) " +
        "VALUES(%s, %s, %s, %s, %s, %s) RETURNING id",
        (document['title'], document['username'], document['url'], document['priority'], document['category'],
         document['notes']))
    id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return jsonify({"id": str(id)})


def initialize_app():
    global conn
    conn = psycopg2.connect(host="localhost", database="james", user="james", password="password")


initialize_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
