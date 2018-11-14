from typing import Dict


# TODO: Consider splitting this file up into the current one and a current_documents_database.py file.
class CurrentDocuments:
    def __init__(self, database):
        self._database = database

    # Returns a dictionary from document id to document.
    def get_current_documents(self, username) -> Dict:
        current_documents = self._database.query_multiple(
            "SELECT * from current_documents where username = %s", (username,))

        ret = {}
        for current_document in current_documents:
            ret[current_document["id"]] = current_document
        return ret

    # Returns a dictionary with key id corresponding to the id of the deleted document.
    def delete_document(self, document_id) -> Dict:
        deleted_id = self._database.commit_single_row_with_return(
            "DELETE from current_documents where id = %s RETURNING id", (document_id,))["id"]
        return {"id": deleted_id}

    # Returns a dictionary with key document corresponding to the edited document.
    def edit_document(self, document_id, document) -> Dict:
        document = self._database.commit_single_row_with_return(
            "UPDATE current_documents SET title = %s, url = %s, priority = %s, category = %s, notes = %s " +
            "where id = %s RETURNING *",
            (document["title"], document["url"], document["priority"], document["category"], document["notes"],
             document_id))
        return {"document": document}

    # Returns a dictionary with key id corresponding the key of the added document.
    def add_document(self, document) -> Dict:
        document_id = self._database.commit_single_row_with_return(
            "INSERT INTO current_documents(title, username, url, priority, category, notes) " +
            "VALUES(%s, %s, %s, %s, %s, %s) RETURNING id",
            (document["title"], document["username"], document["url"], document["priority"], document["category"],
             document["notes"]))["id"]
        return {"id": document_id}
