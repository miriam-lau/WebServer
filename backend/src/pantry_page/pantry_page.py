from typing import Dict, List
import psycopg2


class PantryPage:
    IGNORED_WORDS = [
        't', 'tsp',
        'tbl', 'tbs', 'tbsp',
        'fl', 'oz', 'floz',
        'cup', 'cups',
        'c',
        'p', 'pt', 'flpt',
        'q', 'qt', 'flqt',
        'g', 'gal',
        'milliliter', 'milliliters', 'millilitre', 'millilitres', 'cc', 'ml',
        'liter', 'liters', 'litre', 'litres', 'l',
        'deciliter', 'deciliters', 'decilitre', 'decilitres', 'dl',
        'pound', 'pounds', 'lb', 'lbs'
        'ounce', 'ounces', 'oz',
        'milligram', 'milligrams', 'milligramme', 'milligrammes', 'mg',
        'g', 'gram', 'grams', 'gramme', 'grammes',
        'kg', 'kilogram', 'kilograms', 'kilogramme', 'kilogrammes',
        'pint', 'pints']

    def __init__(self, database):
        self._database = database

    # Returns an object containing the data for the pantry page. Consists of the keys:
    #   grocery_lists: An array of grocery list objects.
    #   pantry: An array of pantry items.
    def get_pantry_page_data(self) -> Dict:
        cur = self._database.get_cursor()

        try:
            cur.execute("SELECT * from grocery_lists order by id")
            grocery_lists = cur.fetchall()
            cur.execute("SELECT * from pantry")
            pantry_items = cur.fetchall()
            cur.execute("SELECT * from grocery_known_words order by should_save desc, word")
            known_words = cur.fetchall()
            cur.close()
            return {
                'grocery_lists': grocery_lists,
                'pantry': pantry_items,
                'known_words': known_words
            }
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_grocery_list(self, grocery_list_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from grocery_lists where id = %s RETURNING *", (grocery_list_id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_grocery_list_metadata(self, grocery_list_id, grocery_list_title):
        if not grocery_list_title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE grocery_lists SET title = %s where id = %s RETURNING *",
                        (grocery_list_title, grocery_list_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_grocery_list(self, grocery_list_id, grocery_list):
        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE grocery_lists SET list = %s where id = %s RETURNING *",
                        (grocery_list, grocery_list_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_grocery_list(self, title):
        if not title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO grocery_lists(title, list, imported) VALUES(%s, '', false) RETURNING *", (title,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_pantry_item(self, pantry_item):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from pantry where item = %s RETURNING *", (pantry_item,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_pantry_item(self, pantry_item):
        if not pantry_item:
            raise Exception('pantry_item must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute(
                "SELECT * from grocery_known_words where word = %s and should_save = True", (pantry_item,))
            word = cur.fetchone()
            if word is None:
                raise Exception('Word not in known words that can be added to the pantry.')

            cur.execute("INSERT INTO pantry(item) VALUES(%s) RETURNING *", (pantry_item,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_known_word(self, known_word):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from grocery_known_words where word = %s RETURNING *", (known_word,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_known_word(self, known_word, should_save):
        if not known_word:
            raise Exception('pantry_item must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO grocery_known_words(word, should_save) VALUES(%s, %s) RETURNING *",
                (known_word, should_save))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_to_pantry(self, grocery_list_id, commit):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "SELECT * from grocery_lists where id = %s", (grocery_list_id,))
            grocery_list = cur.fetchone()
            if grocery_list is None:
                raise Exception("Grocery list could not be found.")

            cur.execute("SELECT * from pantry")
            pantry = cur.fetchall()
            pantry_words = []
            for pantry_item in pantry:
                pantry_words.append(pantry_item['item'])

            cur.execute("SELECT * from grocery_known_words")
            known_words = cur.fetchall()

            known_words_map = {}
            for known_word in known_words:
                known_words_map[known_word['word']] = known_word['should_save']

            ret = {
                'add': [],
                'ignore': [],
                'unrecognized': [],
                'already_in_pantry': []
            }

            for grocery_list_line in (
                grocery_list['list'].replace('.', '').replace(',', '').lower().split("\n")):
                line_array = grocery_list_line.split(' ')
                line_array = [word for word in line_array if not any(c.isdigit() for c in word)]
                line_array = [word for word in line_array if word not in PantryPage.IGNORED_WORDS]
                grocery_list_word = ' '.join(line_array)
                if not grocery_list_word:
                    continue
                if grocery_list_word in known_words_map:
                    known_word = known_words_map[grocery_list_word]
                    if known_word:
                        if grocery_list_word in pantry_words:
                            ret['already_in_pantry'].append(grocery_list_word)
                        else:
                            ret['add'].append(grocery_list_word)
                    else:
                        ret['ignore'].append(grocery_list_word)
                else:
                    ret['unrecognized'].append(grocery_list_word)

            if not commit:
                cur.close()
                return ret

            if len(ret['unrecognized']) != 0:
                raise Exception('Must not have unrecognized words.')

            for word in ret['add']:
                cur.execute("INSERT INTO pantry(item) VALUES(%s)", (word,))

            cur.execute("UPDATE grocery_lists SET imported = True where id = %s RETURNING *",
                        (grocery_list_id,))

            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
