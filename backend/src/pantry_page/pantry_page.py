from typing import Dict, List
import psycopg2
import re


class PantryPage:
  IGNORED_WORDS = [
      "",
      "t", "tsp",
      "tbl", "tbs", "tbsp",
      "fl", "oz", "floz",
      "cup", "cups",
      "c",
      "p", "pt", "flpt",
      "q", "qt", "flqt",
      "g", "gal",
      "milliliter", "milliliters", "millilitre", "millilitres", "cc", "ml",
      "liter", "liters", "litre", "litres", "l",
      "deciliter", "deciliters", "decilitre", "decilitres", "dl",
      "pound", "pounds", "lb", "lbs"
      "ounce", "ounces", "oz",
      "milligram", "milligrams", "milligramme", "milligrammes", "mg",
      "g", "gram", "grams", "gramme", "grammes",
      "kg", "kilogram", "kilograms", "kilogramme", "kilogrammes",
      "pint", "pints",
      "stick", "small", "medium", "large"]

  def __init__(self, database):
    self._database = database

  # Returns an object containing the data for the pantry page. Consists of the keys:
  #   grocery_lists: An array of grocery list objects.
  #   pantry: An array of pantry items.
  def get_pantry_page_data(self) -> Dict:
    cur = self._database.get_cursor()

    try:
      cur.execute("SELECT * from grocery_lists order by date desc")
      grocery_lists = cur.fetchall()
      cur.execute("SELECT * from pantry order by item")
      pantry_items = cur.fetchall()
      cur.execute(
          "SELECT * from grocery_known_words order by should_save desc, word")
      known_words = cur.fetchall()
      cur.execute(
          "SELECT * from grocery_store_categories order by store, category")
      store_categories = cur.fetchall()

      known_words_map = {}
      for known_word in known_words:
        known_words_map[known_word["word"]] = known_word["category"]

      for grocery_list in grocery_lists:
        list_text = []
        for grocery_list_line in (grocery_list["list"].split("\n")):
          list_text.append(grocery_list_line)
        list_text.sort()
        grocery_list["list"] = "\n".join(list_text)

      cur.close()
      return {
          "grocery_lists": grocery_lists,
          "pantry": pantry_items,
          "store_categories": store_categories,
          "known_words": known_words
      }
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def delete_grocery_list(self, grocery_list_id):
    cur = self._database.get_cursor()

    try:
      cur.execute(
          "DELETE from grocery_lists where id = %s RETURNING *", (grocery_list_id,))
      ret = cur.fetchone()
      self._database.commit()
      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def edit_grocery_list_metadata(self, grocery_list_id, grocery_list_store, grocery_list_date):
    cur = self._database.get_cursor()

    try:
      cur.execute("UPDATE grocery_lists SET store = %s, date = %s where id = %s RETURNING *",
                  (grocery_list_store, grocery_list_date, grocery_list_id))
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

  def add_grocery_list(self, store, date):
    cur = self._database.get_cursor()

    try:
      cur.execute("INSERT INTO grocery_lists(store, date, list, imported) VALUES(%s, %s, %s, false) RETURNING *",
                  (store, date, ""))
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
      cur.execute("DELETE from pantry where item = %s RETURNING *",
                  (pantry_item,))
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
      raise Exception("pantry_item must not be empty.")

    cur = self._database.get_cursor()

    try:
      cur.execute(
          "SELECT * from grocery_known_words where word = %s and should_save = True", (pantry_item,))
      word = cur.fetchone()
      if word is None:
        raise Exception(
            "Word not in known words that can be added to the pantry.")

      cur.execute(
          "INSERT INTO pantry(item) VALUES(%s) RETURNING *", (pantry_item,))
      ret = cur.fetchone()
      self._database.commit()
      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def delete_store_category(self, store, category):
    cur = self._database.get_cursor()

    try:
      cur.execute(
          "DELETE from grocery_store_categories where store = %s and category = %s RETURNING *", (store, category))
      ret = cur.fetchone()
      self._database.commit()
      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def add_store_category(self, store, category, label):
    if not category or not store or not label:
      raise Exception("store, category, and label must all not be empty.")

    cur = self._database.get_cursor()

    try:
      cur.execute(
          "INSERT INTO grocery_store_categories(store, category, label) VALUES(%s, %s, %s) RETURNING *",
          (store, category, label))
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
      cur.execute(
          "DELETE from grocery_known_words where word = %s RETURNING *", (known_word,))
      ret = cur.fetchone()
      self._database.commit()
      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def add_known_word(self, known_word, category, should_save):
    if not known_word:
      raise Exception("pantry_item must not be empty.")

    cur = self._database.get_cursor()

    try:
      cur.execute(
          "INSERT INTO grocery_known_words(word, category, should_save) VALUES(%s, %s, %s) RETURNING *",
          (known_word, category, should_save))
      ret = cur.fetchone()
      self._database.commit()
      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def add_known_words(self, known_words):
    if not known_words:
      raise Exception("known word must not be empty.")

    cur = self._database.get_cursor()
    ret = []

    try:
      for known_word in known_words:
        cur.execute(
            "INSERT INTO grocery_known_words(word, category, should_save) VALUES(%s, %s, %s) RETURNING *",
            (known_word['name'], known_word['category'], known_word['should_save']))
        ret.append(cur.fetchone())
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
        pantry_words.append(pantry_item["item"])

      cur.execute("SELECT * from grocery_known_words")
      known_words = cur.fetchall()
      known_words_map = {}
      for known_word in known_words:
        known_words_map[known_word["word"]] = known_word["should_save"]

      ret = {
          "add": [],
          "ignore": [],
          "unrecognized": [],
          "already_in_pantry": []
      }

      for grocery_list_line in (grocery_list["list"].split("\n")):
        grocery_list_line = grocery_list_line.strip()
        if len(grocery_list_line) > 0 and grocery_list_line[0] == '?':
          ret["ignore"].append(grocery_list_line)
          continue
        if grocery_list_line == '':
          continue
        grocery_list_word = PantryPage._get_grocery_word_from_line(
            grocery_list_line)
        if grocery_list_word in known_words_map:
          known_word = known_words_map[grocery_list_word]
          if known_word:
            if grocery_list_word in pantry_words:
              ret["already_in_pantry"].append(grocery_list_word)
            else:
              ret["add"].append(grocery_list_word)
          else:
            ret["ignore"].append(grocery_list_word)
        else:
          ret["unrecognized"].append(grocery_list_word)

      if not commit:
        cur.close()
        return ret

      if len(ret["unrecognized"]) != 0:
        raise Exception("Must not have unrecognized words.")

      for word in ret["add"]:
        cur.execute("INSERT INTO pantry(item) VALUES(%s)", (word,))

      cur.execute("UPDATE grocery_lists SET imported = True where id = %s RETURNING *",
                  (grocery_list_id,))

      cur.close()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  def get_export_text(self, grocery_list_id):
    cur = self._database.get_cursor()

    try:
      cur.execute(
          "SELECT * from grocery_lists where id = %s", (grocery_list_id,))
      grocery_list = cur.fetchone()
      if grocery_list is None:
        raise Exception("Grocery list could not be found.")

      cur.execute("SELECT * from grocery_known_words")
      known_words = cur.fetchall()
      known_words_map = {}
      for known_word in known_words:
        known_words_map[known_word["word"]] = known_word["category"]

      cur.execute("SELECT * from grocery_store_categories where store  = %s",
                  (grocery_list["store"],))
      grocery_store_categories = cur.fetchall()
      category_labels = {}
      for grocery_store_category in grocery_store_categories:
        category_labels[grocery_store_category["category"]
                        ] = grocery_store_category["label"]

      ret = []

      for grocery_list_line in (grocery_list["list"].split("\n")):
        grocery_list_line = grocery_list_line.strip()
        if grocery_list_line == '':
          continue
        grocery_list_word = PantryPage._get_grocery_word_from_line(
            grocery_list_line)
        line_to_add = ''
        if grocery_list_word in known_words_map and known_words_map[grocery_list_word]:
          category = known_words_map[grocery_list_word]
          if category in category_labels and category_labels[category]:
            label = category_labels[category]
            line_to_add += label + " - "
          line_to_add += category + ": "
        line_to_add += grocery_list_line
        ret.append(line_to_add)

      cur.close()
      ret.sort()
      return ret
    except psycopg2.Error:
      self._database.rollback()
      cur.close()
      raise

  @staticmethod
  def _strip_parentheses(input):
    # From stackoverflow.
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in input:
      if i == '[':
        skip1c += 1
      elif i == '(':
        skip2c += 1
      elif i == ']' and skip1c > 0:
        skip1c -= 1
      elif i == ')'and skip2c > 0:
        skip2c -= 1
      elif skip1c == 0 and skip2c == 0:
        ret += i
    return ret

  @staticmethod
  def _get_grocery_word_from_line(grocery_list_line):
    grocery_list_line = grocery_list_line.lower()
    grocery_list_line = grocery_list_line.replace("\xa0", " ")
    split_on_dash = grocery_list_line.split("-", 1)
    if len(split_on_dash) > 0:
      grocery_list_line = split_on_dash[0]
    grocery_list_line = PantryPage._strip_parentheses(grocery_list_line)
    remove_words = str.maketrans('', '', '.-,0123456789')
    grocery_list_line = grocery_list_line.translate(remove_words)
    line_array = grocery_list_line.split(" ")
    line_array = [
        word for word in line_array if word not in PantryPage.IGNORED_WORDS]
    return " ".join(line_array)
