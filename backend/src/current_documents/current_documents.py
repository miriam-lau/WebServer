from typing import Dict


# TODO: Consider splitting this file up into the current one and a current_documents_database.py file.
class CurrentDocuments:
    def __init__(self, database):
        self._database = database

    def get_current_documents(self, username) -> Dict:
        current_documents = self._database.execute_query(
            "SELECT * from current_documents where username = %s", (username,))

        ret = {}
        for current_document in current_documents:
            ret[current_document["id"]] = current_document
        return ret

    def delete_document(self, document_id) -> Dict:
        deleted_id = self._database.execute_commit_with_return(
            "DELETE from current_documents where id = %s RETURNING id", (document_id,))[0]
        return {"id": deleted_id}

    def edit_document(self, document_id, document) -> Dict:
        document_values = self._database.execute_commit_with_return(
            "UPDATE current_documents SET title = %s, url = %s, priority = %s, category = %s, notes = %s " +
            "where id = %s RETURNING *",
            (document["title"], document["url"], document["priority"], document["category"], document["notes"],
             document_id))
        ret = CurrentDocuments._tuple_to_document(document_values)
        return {"document": ret}

    @staticmethod
    def _tuple_to_document(values):
        ret = dict()
        ret["id"] = values[0]
        ret["username"] = values[1]
        ret["title"] = values[2]
        ret["priority"] = values[3]
        ret["category"] = values[4]
        ret["url"] = values[5]
        ret["notes"] = values[6]
        return ret

    def add_document(self, document) -> Dict:
        document_id = self._database.execute_commit_with_return(
            "INSERT INTO current_documents(title, username, url, priority, category, notes) " +
            "VALUES(%s, %s, %s, %s, %s, %s) RETURNING id",
            (document["title"], document["username"], document["url"], document["priority"], document["category"],
             document["notes"]))[0]
        return {"id": document_id}
