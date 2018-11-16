from typing import Dict
from src.database.database import CommitStatement


# TODO: Consider splitting this file up into the current one and a current_documents_database.py file.
class CurrentDocuments:
    def __init__(self, database):
        self._database = database

    # Returns a dictionary from document id to document.
    def get_current_documents(self, username) -> Dict:
        current_documents = self._database.query_multiple(
            "SELECT * from current_documents where username = %s ORDER BY sort_order", (username,))

        ret = {}
        for current_document in current_documents:
            ret[current_document["id"]] = current_document
        return ret

    def delete_document(self, document_id):
        self._database.commit_single_row(
            "DELETE from current_documents where id = %s", (document_id,))

    # Returns a dictionary with key document corresponding to the edited document.
    def edit_document(self, document_id, document):
        self._database.commit_single_row(
            "UPDATE current_documents SET title = %s, url = %s, notes = %s where id = %s",
            (document["title"], document["url"], document["notes"], document_id))

    def add_document(self, document):
        num_current_documents = len(self.get_current_documents(document["username"]))
        self._database.commit_single_row(
            "INSERT INTO current_documents(title, username, url, sort_order, notes) " +
            "VALUES(%s, %s, %s, %s, %s)",
            (document["title"], document["username"], document["url"], num_current_documents, document["notes"]))

    def reorder_documents(self, username, ordered_document_ids):
        num_current_documents = len(self.get_current_documents(username))
        if num_current_documents != len(ordered_document_ids):
            raise Exception("Must pass all document ids for a user to reorder them.")
        commit_statements = []
        for index, document_id in enumerate(ordered_document_ids):
            commit_statements.append(
                CommitStatement("UPDATE current_documents SET sort_order = %s where id = %s", (index, document_id)))
        self._database.commit_multiple_rows(commit_statements)
