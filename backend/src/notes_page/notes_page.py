from typing import Dict, List
import psycopg2


class NotesPage:
    def __init__(self, database):
        self._database = database

    # Returns an array containing the data for the notes page.
    def get_notes_page_data(self) -> Dict:
        cur = self._database.get_cursor()

        try:
            cur.execute("SELECT * from notes order by id")
            notes = cur.fetchall()
            cur.close()
            return notes
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_note(self, note_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from notes where id = %s RETURNING *", (note_id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_note_metadata(self, note_id, note_title):
        if not note_title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE notes SET title = %s where id = %s RETURNING *",
                        (note_title, note_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_note(self, note_id, text):
        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE notes SET text = %s where id = %s RETURNING *",
                        (text, note_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_note(self, title):
        if not title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO notes(title, text) VALUES(%s, '') RETURNING *", (title,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
