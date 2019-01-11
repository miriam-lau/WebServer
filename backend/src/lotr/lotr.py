import yaml
import random
import pprint
from src.lotr.lotr_database import LotrDatabase
from typing import List, Optional, Dict
import psycopg2
import os
import xml.etree.ElementTree as ET
from src.common.xml import Xml
import yaml

class Lotr:
  def __init__(self, database):
    self._image_name_to_url = {}
    # A map of card id to card objects.
    #   key: The card id.
    #   value: An object with the following data:
    #       key: One of the following strings: "Text", "Card Number", "Quantity", "Encounter Set", "Keywords", "Type",
    #           "Victory Points", "Attack", "Defense", "Health", "Shadow", "Traits", "Threat", "Quest Points",
    #           "Engagement Cost", "Cost", "Sphere", "Willpower", "Unique", "Setup", "SetId", "SetName", "Id", "Name",
    #           "Size"
    #       value: A string representing the corresponding value for the key.
    self._card_data = {}
    # A map of scenario name to scenario objects.
    #   key: The scenario property name.
    #   value: An object with the following data:
    #       key: One of the following strings: Setup, Second Special, Special, Staging Setup, Second Quest Deck, Quest,
    #            Encounter, Active Setup.
    #       value: An array of card objects in the deck.
    self._scenario_data = {}
    self._populate_image_name_to_url("static/lotr/image-name-to-url.yaml")
    self._load_card_data("static/lotr/Sets/")
    self._load_scenario_data("static/lotr/Decks/")
    self._lotr_database = LotrDatabase(database)

  def _populate_image_name_to_url(self, filename):
    with open(filename, 'r') as stream:
      try:
        root = yaml.load(stream)
        for name in root:
          self._image_name_to_url[name] = root[name]
      except yaml.YAMLError as exc:
        print(exc)

  # Populates the _scenario_data map with the following data using files in the given directory. See _scenario_data for
  # mroe info.
  def _load_scenario_data(self, directory):
    scenario_folders = list(filter(lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)))
    for scenario_folder in scenario_folders:
      for scenario_name in os.listdir(directory + "/" + scenario_folder):
        scenario = {}
        tree = ET.parse(directory + "/" + scenario_folder + "/" + scenario_name)
        card_deck_xml = tree.getroot()
        Xml.verify_tag(card_deck_xml, ["deck"])
        all_cards_in_scenario_exist = True
        for section_xml in list(card_deck_xml):
          scenario_property_name = None
          if section_xml.tag == "notes":
            continue
          Xml.verify_tag(section_xml, ["section"])
          section_name = section_xml.get("name")
          cards_xml = list(section_xml)
          if len(cards_xml) == 0:
            continue
          if section_name in ["Hero", "Attachment", "Setup"]:
            scenario_property_name = "Setup"
          elif section_name in [
              "Second Special", "Special", "Staging Setup", "Second Quest Deck", "Quest", "Encounter", "Active Setup"]:
            scenario_property_name = section_name
          else:
            raise Exception("Unexpected section name.")

          if scenario_property_name is None:
            continue
          if scenario_property_name not in scenario:
            scenario[scenario_property_name] = []

          success = self._add_cards_to_array(scenario[scenario_property_name], cards_xml)
          if not success:
            all_cards_in_scenario_exist = False
            break
        if all_cards_in_scenario_exist:
          self._scenario_data[scenario_name] = scenario

  # Populates the _card_data map with the following data using files in the given directory. See _card_data for more
  # info.
  # TODO: 21573ac7-f7f6-49e5-a26f-5070573374f1 is special - markers. Not processed fully.
  # TODO: Maybe handle processing of markers.
  def _load_card_data(self, directory):
    for subdirectory in os.listdir(directory):
      tree = ET.parse("static/lotr/Sets/" + subdirectory + "/set.xml")
      card_set_xml = tree.getroot()
      Xml.verify_tag(card_set_xml, ["set"])
      set_name = card_set_xml.get("name")
      set_id = card_set_xml.get("id")
      for cards_xml in list(card_set_xml):
        if cards_xml.tag != "cards":
          continue
        for card_xml in list(cards_xml):
          card = {}
          Xml.verify_tag(card_xml, ["card"])
          card["SetId"] = set_id
          card["SetName"] = set_name
          card["Id"] = card_xml.get("id")
          # TODO: Figure out which cards are missing images and populate them. For now we just remove
          # cards that don't have images.
          if card["Id"] not in self._image_name_to_url:
            continue
          card["image"] = self._image_name_to_url[card["Id"]]
          card["Name"] = card_xml.get("name")
          card["Size"] = card_xml.get("size")
          for property_or_alternate_xml in list(card_xml):
            Xml.verify_tag(property_or_alternate_xml, ["property", "alternate"])
            if property_or_alternate_xml.tag == "property":
              name = property_or_alternate_xml.get("name")
              value = property_or_alternate_xml.get("value")
              card[name] = value
            elif property_or_alternate_xml.tag == "alternate":
              card["Alternate"] = {}
              for property_xml in list(property_or_alternate_xml):
                name = property_xml.get("name")
                value = property_xml.get("value")
                card["Alternate"][name] = value
              card["flippedImage"] = self._image_name_to_url[card["Id"] + ".B"]
              card["flipped"] = False
          card["attachments"] = []
          card["resources"] = 0
          card["damage"] = 0
          card["progress"] = 0
          self._card_data[card["Id"]] = card

  # Read {@code cards_xml}, an array of Xml card objects, and append them to {@code arr}.
  # Returns success if all cards could be added.
  def _add_cards_to_array(self, arr, cards_xml):
    for card_xml in list(cards_xml):
      qty = int(card_xml.get("qty"))
      card_id = card_xml.get("id")
      if card_id not in self._card_data:
        return False
      for i in range(qty):
        card = self._card_data[card_id]
        arr.append(card)
    return True

  # Draws an initial Lotr hand from the deck.
  @staticmethod
  def _draw_hand(deck, hand):
    for i in range(6):
      hand.append(deck.pop())

  # Creates a JS player object.
  def _parse_player_xml(self, player_name, deck_xml_string):
    deck_xml = ET.fromstring(deck_xml_string)
    hero_cards = []
    deck = []
    hand = []
    for section_xml in list(deck_xml):
      if section_xml.tag == "notes":
        continue
      Xml.verify_tag(section_xml, ["section"])
      section_name = section_xml.get("name")
      cards_xml = list(section_xml)
      if section_name in ["Quest", "Encounter", "Special", "Setup"] and len(cards_xml) > 0:
        raise Exception("Unexpected cards.")
      if section_name == "Hero":
        self._add_cards_to_array(hero_cards, cards_xml)
        continue
      if section_name not in ["Hero", "Attachment", "Event", "Side Quest"]:
        continue

      self._add_cards_to_array(deck, cards_xml)

    random.shuffle(deck)
    Lotr._draw_hand(deck, hand)

    threat = 0
    for card in hero_cards:
      threat += int(card["Cost"])

    return {
      "name": player_name,
      "characters": hero_cards,
      "deck": deck,
      "hand": hand,
      "discard": [],
      "engagedEnemies": [],
      "secondaryDeck": [],
      "secondaryDiscard": [],
      "secondaryReveal": [],
      "threat": threat
    }

  def create_game(self, scenario_name, player1_name, player2_name, player1_deck_xml, player2_deck_xml) -> int:
    if not player1_deck_xml:
      player1_deck_xml = self.get_latest_deck(player1_name)
    if not player2_deck_xml:
      player2_deck_xml = self.get_latest_deck(player2_name)
    if not player1_deck_xml or not player2_deck_xml:
      raise Exception("No deck available.")
    player1 = self._parse_player_xml(player1_name, player1_deck_xml)
    player2 = self._parse_player_xml(player2_name, player2_deck_xml)
    scenario = self._scenario_data[scenario_name].copy()

    data = {
      "trash": [],
      "playedCards": [],
      "stagingArea": [],
      "activeLocation": [],
      "questReveal": [],
      "questDeck": [],
      "questDiscard": [],
      "revealArea": [],
      "secondQuestDeck": [],
      "secondQuestDiscard": [],
      "secondQuestReveal": [],
      "encounterDeck": [],
      "encounterDiscard": [],
      "victory": [],
      "specialDeck": [],
      "specialDiscard": [],
      "specialReveal": [],
      "secondSpecialDeck": [],
      "secondSpecialDiscard": [],
      "secondSpecialReveal": [],
      "setupArea": []
    }
    if "Staging Setup" in scenario:
      data["stagingArea"] = scenario.pop("Staging Setup")
    if "Setup" in scenario:
      data["setupArea"] = scenario.pop("Setup")
      data["hasSetup"] = True
    if "Special" in scenario:
      data["hasSpecial"] = True
      data["specialDeck"] = list(reversed(scenario.pop("Special")))
      random.shuffle(data["specialDeck"])
    if "Second Special" in scenario:
      data["hasSecondSpecial"] = True
      data["secondSpecialDeck"] = list(reversed(scenario.pop("Second Special")))
      random.shuffle(data["secondSpecialDeck"])
    if "Quest" in scenario:
      data["questDeck"] = list(reversed(scenario.pop("Quest")))
      data["questReveal"].append(data["questDeck"].pop())
    if "Second Quest" in scenario:
      data["hasSecondQuest"] = True
      data["secondQuestDeck"] = list(reversed(scenario.pop("Second Quest")))
    if "Encounter" in scenario:
      data["encounterDeck"] = scenario.pop("Encounter")
      random.shuffle(data["encounterDeck"])
    if "Active Setup" in scenario:
      locations = scenario.pop("Active Setup")
      if len(locations) != 1:
        raise Exception("Expected only one location.")
      data["activeLocation"] = locations

    if len(scenario) > 0:
      raise Exception("Unexpected keys left in scenario.")

    data["players"] = [player1, player2]

    cur = self._lotr_database.get_cursor()

    try:
      game_id = LotrDatabase.add_game(cur, player1_name, player2_name, {}, player1_deck_xml, player2_deck_xml)
      data["gameId"] = game_id
      LotrDatabase.update_game(cur, game_id, data)

      self._lotr_database.commit()
      cur.close()
    except psycopg2.Error:
      self._lotr_database.rollback()
      cur.close()
      raise

    return data

  # Returns the latest player deck represented as xml.
  def get_latest_deck(self, player):
    cur = self._lotr_database.get_cursor()

    try:
      deck = LotrDatabase.get_latest_deck(cur, player)
      cur.close()
      if deck is None:
        return None
    except psycopg2.Error:
      self._lotr_database.rollback()
      cur.close()
      raise

    return deck

  # Returns the game as a dict.
  def get_latest_game(self, player) -> Optional[Dict]:
    cur = self._lotr_database.get_cursor()

    try:
      game = LotrDatabase.get_latest_game(cur, player)
      cur.close()
      if game is None:
        return None
    except psycopg2.Error:
      self._lotr_database.rollback()
      cur.close()
      raise

    return game

  def get_scenario_names(self) -> Optional[Dict]:
    scenario_names = list(self._scenario_data.keys()).copy()
    scenario_names.sort()
    return scenario_names

  def update_game(self, game_id, data) -> int:
    cur = self._lotr_database.get_cursor()

    try:
      LotrDatabase.update_game(cur, game_id, data)

      self._lotr_database.commit()
      cur.close()
    except psycopg2.Error:
      self._lotr_database.rollback()
      cur.close()
      raise
