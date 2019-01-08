import yaml
import random
import pprint
from src.lotr.lotr_database import LotrDatabase
from typing import List, Optional, Dict
import psycopg2
import os
import xml.etree.ElementTree as ET
from src.common.xml import Xml

class Lotr:
  def __init__(self, database):
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
    self._load_card_data("static/lotr/Sets/")
    self._load_scenario_data("static/lotr/Decks/")
    self._lotr_database = LotrDatabase(database)

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

          self._add_cards_to_array(scenario[scenario_property_name], cards_xml)
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
          self._card_data[card["Id"]] = card

  # Read {@code cards_xml}, an array of Xml card objects, and append them to {@code arr}.
  def _add_cards_to_array(self, arr, cards_xml):
    for card_xml in list(cards_xml):
      qty = int(card_xml.get("qty"))
      card_id = card_xml.get("id")
      if card_id not in self._card_data:
        raise Exception("Could not find card with id %s and name %s" % (card_id, card_xml.text))
      for i in range(qty):
        card = self._card_data[card_id]
        arr.append(card)

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
      "characters": [],
      "deck": deck,
      "hand": hand,
      "discard": [],
      "engagedEnemies": [],
      "secondaryDeck": [],
      "secondaryDeckDiscard": [],
      "threat": threat
    }

  def create_game(self, scenario_name, player1_name, player2_name, player1_deck_xml, player2_deck_xml) -> int:
    player1 = self._parse_player_xml(player1_name, player1_deck_xml)
    player2 = self._parse_player_xml(player2_name, player2_deck_xml)
    scenario = self._scenario_data[scenario_name]

    data = {
      "revealArea": [],
      "playedCards": [],
      "stagingArea": [],
      "activeLocation": [],
      "questDeck": [],
      "questDiscard": [],
      "secondQuestDeck": [],
      "secondQuestDiscard": [],
      "encounterDeck": [],
      "encounterDiscard": [],
      "victory": [],
      "specialDeck": [],
      "specialDiscard": [],
      "secondSpecialDeck": [],
      "secondSpecialDiscard": [],
      "setupArea": []
    }
    if "Staging Setup" in scenario:
      data["stagingArea"] = scenario.pop("Staging Setup")
    if "Setup" in scenario:
      data["setupArea"] = scenario.pop("Setup")
    if "Special" in scenario:
      data["specialDeck"] = scenario.pop("Special")
    if "Second Special" in scenario:
      data["secondSpecialDeck"] = scenario.pop("Second Special")
    if "Quest" in scenario:
      data["questDeck"] = scenario.pop("Quest")
    if "Second Quest" in scenario:
      data["secondQuestDeck"] = scenario.pop("Second Quest")
    if "Encounter" in scenario:
      data["encounterDeck"] = scenario.pop("Encounter")
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
      game_id = LotrDatabase.add_game(cur, player1_name, player2_name, {})
      data["gameId"] = game_id
      LotrDatabase.update_game(cur, game_id, data)

      self._lotr_database.commit()
      cur.close()
    except psycopg2.Error:
      self._lotr_database.rollback()
      cur.close()
      raise

    return data

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
