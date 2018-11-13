class CurrentDocuments:
    def __init__(self, database):
        self._database = database

    def get_current_documents(self, username):
        current_documents = self._database.execute_query(
            "SELECT * from current_documents where username = %s", (username,))

        ret = {}
        for current_document in current_documents:
            ret[current_document["id"]] = current_document
        return ret

    def delete_document(self, document_id):
        deleted_id = self._database.execute_commit_with_return(
            "DELETE from current_documents where id = %s RETURNING id", (document_id,))[0]
        return {"id": deleted_id}

    def edit_document(self, document_id, document):
        document_values = self._database.execute_commit_with_return(
            "UPDATE current_documents SET title = %s, url = %s, priority = %s, category = %s, notes = %s " +
            "where id = %s RETURNING *",
            (document["title"], document["url"], document["priority"], document["category"], document["notes"],
             document_id))
        ret = dict()
        ret["id"] = document_values[0]
        ret["username"] = document_values[1]
        ret["title"] = document_values[2]
        ret["priority"] = document_values[3]
        ret["category"] = document_values[4]
        ret["url"] = document_values[5]
        ret["notes"] = document_values[6]
        return {"document": ret}

    def add_document(self, document):
        document_id = self._database.execute_commit_with_return(
            "INSERT INTO current_documents(title, username, url, priority, category, notes) " +
            "VALUES(%s, %s, %s, %s, %s, %s) RETURNING id",
            (document["title"], document["username"], document["url"], document["priority"], document["category"],
             document["notes"]))[0]
        return {"id": document_id}
