from typing import Dict
from src.database.database import CommitStatement
import psycopg2


# TODO: Consider splitting this file up into the current one and a current_documents_database.py file.
class CurrentDocuments:
    def __init__(self, database):
        self._database = database

    # Returns a dictionary from document id to document.
    def get_current_documents(self, username) -> Dict:
        cur = self._database.get_cursor()
        current_documents = None

        try:
            cur.execute(
                "SELECT * from current_documents where username = %s ORDER BY sort_order", (username,))
            current_documents = cur.fetchall()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            raise

        for (index, current_document) in enumerate(current_documents):
            if current_document["sort_order"] != index:
                raise Exception("Current documents should be in sorted order starting with 0. %s" % current_documents)

        return current_documents

    def delete_document(self, document_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from current_documents where id = %s", (document_id,))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            raise

    def edit_document(self, document_id, document):
        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE current_documents SET title = %s, url = %s, notes = %s where id = %s",
                        (document["title"], document["url"], document["notes"], document_id))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            raise

    def add_document(self, document):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "SELECT * from current_documents where username = %s ORDER BY sort_order", (document["username"],))
            num_current_documents = len(cur.fetchall())
            cur.execute("INSERT INTO current_documents(title, username, url, sort_order, notes) " +
                        "VALUES(%s, %s, %s, %s, %s)",
                        (document["title"], document["username"], document["url"], num_current_documents,
                         document["notes"]))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            raise

    def reorder_documents(self, username, ordered_document_ids):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "SELECT * from current_documents where username = %s ORDER BY sort_order", (username,))
            num_current_documents = len(cur.fetchall())
            if num_current_documents != len(ordered_document_ids):
                raise Exception("Must pass all document ids for a user to reorder them.")
            for index, document_id in enumerate(ordered_document_ids):
                cur.execute("UPDATE current_documents SET sort_order = %s where id = %s", (index, document_id))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            raise
