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
from src.card_games.card_games import CardGames
import copy

# Backend for the Lotr game.
class Lotr:
  LOTR_TABLE_NAME = "lotr_games"
  LOTR_DATA_TABLE_NAME = "lotr_game_data"

  def __init__(self, database):
    self._lotr_database = LotrDatabase(database)
    self._card_games = CardGames(database, Lotr.LOTR_TABLE_NAME, Lotr.LOTR_DATA_TABLE_NAME)
    # {map<string, string>} a map from local image filename to the url for rendering it.
    self._image_name_to_url = self._get_image_name_to_url("static/lotr/image-name-to-url.yaml")
    # {map<string, string>} a map from scenario name to the manual url.
    self._scenario_name_to_manual = self._get_scenario_name_to_manual("static/lotr/scenario-name-to-manual.yaml")
    # {map<string, Card}. A map of card id to card objects. The card id is a unique identifier
    #     for each card determined by the input files.
    #
    # Card represents a card in the game. It contains many keys which can be found in the .xml files.
    # Some but not all keys include: "Text", "Card Number", "Quantity", "Encounter Set", "Keywords", "Type",
    #     "Victory Points", "Attack", "Defense", "Health", "Shadow", "Traits", "Threat", "Quest Points",
    #     "Engagement Cost", "Cost", "Sphere", "Willpower", "Unique", "Setup", "SetId", "SetName", "Id", "Name",
    #     "Size"
    # The relevant keys to us are the following:
    # image {string} the url to render the card. Populated from the .xml files.
    # flippedImage {string} the url to render the card when it is flipped. Populated from the .xml files.
    # flipped {boolean?} whether the card is flipped or not. Usually only set if the card is flipped.
    # gameCardId {number} a unique identifier for each specific card (e.g. even cards with the same name will have
    #     its own unique id). Each card will be populated with this just before sending it to the client
    #     when a game is created.
    self._card_data = self._load_card_data("static/lotr/Sets/")
    # {map<string, Scenario>} A map of scenario name to scenario objects. Scenario objects will have many
    #     keys populated from the .xml files such as:
    #         Setup, Second Special, Special, Staging Setup, Second Quest Deck, Quest, Encounter, Active Setup.
    self._scenario_data = self._load_scenario_data("static/lotr/Decks/")

  # Returns a map of local image name to url for rendering.
  # filename{string} the filename to read the image name to url data from.
  # return {map<string, string>} local image name to url for rendering.
  def _get_image_name_to_url(self, filename):
    ret = {}
    with open(filename, 'r') as stream:
      try:
        root = yaml.load(stream)
        for name in root:
          ret[name] = root[name]
      except yaml.YAMLError as exc:
        print(exc)
    return ret

  # Returns a map of scenario name to a url for rendering the manual.
  # filename{string} the filename to read the scenario name to manual info from.
  # return {map<string, string>} scenario name to manual url.
  def _get_scenario_name_to_manual(self, filename):
    ret = {}
    with open(filename, 'r') as stream:
      try:
        root = yaml.load(stream)
        for name in root:
          ret[name] = root[name]
      except yaml.YAMLError as exc:
        print(exc)
    return ret

  # Populates the _scenario_data map with the following data using files in the given directory. See _scenario_data for
  # more info.
  # Returns a map of scenario id to scenario data.
  # directory {string} the directory of scenario files to read in.
  # returns {map<string, Scenario>} of scenario id to Scenario object.
  def _load_scenario_data(self, directory):
    ret = {}
    scenario_folders = list(filter(lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)))
    for scenario_folder in scenario_folders:
      for scenario_name in os.listdir(directory + "/" + scenario_folder):
        scenario = {}
        if scenario_name in self._scenario_name_to_manual:
          scenario['manual'] = self._scenario_name_to_manual[scenario_name]
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
          ret[scenario_name] = scenario
    return ret

  # Returns a map of card id to card data.
  # directory {string} the directory of card files to read in.
  # returns {map<string, Card>} of card id to Card object.
  # info.
  # TODO: 21573ac7-f7f6-49e5-a26f-5070573374f1 is special - markers. Not processed fully.
  # TODO: Maybe handle processing of markers.
  def _load_card_data(self, directory):
    ret = {}
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
          card["exhausted"] = False
          card["resources"] = 0
          card["damage"] = 0
          card["progress"] = 0
          ret[card["Id"]] = card
    return ret

  # Creates a JS player object representing a player for return to the frontend.
  # player_name {string} the name of the player to return.
  # deck_xml_string {string} a string representing an Octagn XML representation of a player deck.
  # return {Object} an object representing a player. It has the following keys:
  #     name {string} the name of the player
  #     characters {array<Card>} an array of the hero cards the player controls.
  #     deck {array<Card>} the deck of cards of the player.
  #     hand {array<Card>} the hand of cards of the player.
  #     discard {array<Card>} the discard pile of cards of the player.
  #     engagedEnemies {array<Card>} the array of engaged enemy cards of the player.
  #     secondaryDeck {array<Card>} the secondary deck of the player.
  #     secondaryDiscard {array<Card>} the secondary discard pile of the player.
  #     secondaryReveal {array<Card>} the secondary reveal pile of the player.
  #     threat {number} the total threat points of the player.
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
      if section_name not in ["Hero", "Attachment", "Event", "Side Quest", "Ally"]:
        continue

      self._add_cards_to_array(deck, cards_xml)

    random.shuffle(deck)
    Lotr._draw_hand(deck, hand)

    threat = 0
    for card in hero_cards:
      card['resources'] = 1
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
      "selectedAttachment": [],
      "threat": threat
    }

  # Read {@code cards_xml}, an array of Xml card objects, and append the referenced cards to
  # {@code arr}. Creates a copy of the card so they can be modified without affecting the
  # original map of cards.
  # arr {array<Card>} an array of cards to add to. (This will be modified.)
  # cards_xml {ElementTree} the XML element to add card data from.
  # Returns success if all cards could be added.
  def _add_cards_to_array(self, arr, cards_xml):
    for card_xml in list(cards_xml):
      qty = int(card_xml.get("qty"))
      card_id = card_xml.get("id")
      if card_id not in self._card_data:
        return False
      for i in range(qty):
        card = copy.deepcopy(self._card_data[card_id])
        arr.append(card)
    return True

  # Draws an initial Lotr hand from the deck.
  # deck {array<Card>} the array of cards in the deck to draw from. (Will be modified)
  # hand {array<Card>} the hand of cards in the deck to draw into. (Will be modified)
  @staticmethod
  def _draw_hand(deck, hand):
    for i in range(6):
      hand.append(deck.pop())

  # Creates a game
  # scenario_name {string} the name of the scenario to load the data of.
  # player1_name {string} the name of the first player in the game.
  # player2_name {string} the name of the second player in the game.
  # player1_deck_xml {string} the Octagn representation of the first player's deck. If empty, the
  #     most recently used deck by the player is used to generate the player's deck.
  # player2_deck_xml {string} the Octagn representation of the second player's deck. If empty, the
  #     most recently used deck by the player is used to generate the player's deck.
  # return {Object} an object representing a new game. It contains the keys:
  #     trash {array<Card>} the trash pile.
  #     stagingArea {array<Card>} the staging area.
  #     activeLocation {array<Card>} the active location. It is an array for convenience even though there can
  #         only be one.
  #     questDeck {array<Card>} the quest deck.
  #     questDiscard {array<Card>} the discard pile of the quest deck.
  #     revealArea {array<Card>} the revealed cards area.
  #     secondQuestDeck {array<Card>} the second quest deck if one exists.
  #     secondQuestDiscard {array<Card>} the second quest deck's discard area if one exists.
  #     secondQuestReveal {array<Card>} the second quest deck's reveal area if one exists.
  #     encounterDeck {array<Card>} the encounter deck.
  #     encounterDiscard {array<Card>} the discard pile of the encounter deck.
  #     victory {array<Card>} the victory pile of the game.
  #     specialDeck {array<Card>} the special deck in the game if one exists.
  #     specialDiscard {array<Card>} the special discard in the game if one exists.
  #     specialReveal {array<Card>} the reveal area of the special deck if one exists.
  #     secondSpecialDeck {array<Card>} the second special deck in the game if one exists.
  #     secondSpecialDiscard {array<Card>} the second special discard in the game if one exists.
  #     secondSpecialReveal {array<Card>} the reveal area of the second special deck if one exists.
  #     setupArea {array<Card>} the setup area if one exists.
  #     hasSecondQuest {boolean?} whether there's a second quest deck in the game.
  #     hasSpecial {boolean?} whether there is a special deck in the game.
  #     hasSecondSpecial {boolean?} whether there's a second special deck in the game.
  #     hasSetup {boolean?} whether there is a setup area in the game.
  #     players {array<Player>} an array of player objects as generated from the player xml.
  #     gameId {number} the id of the game. (Added automatically by the CardGames class.)

  def create_game(self, scenario_name, player1_name, player2_name, player1_deck_xml, player2_deck_xml) -> int:
    if not player1_deck_xml:
      player1_deck_xml = self.get_latest_deck(player1_name)
    if not player2_deck_xml:
      player2_deck_xml = self.get_latest_deck(player2_name)
    if not player1_deck_xml or not player2_deck_xml:
      raise Exception("No deck available.")
    player1 = self._parse_player_xml(player1_name, player1_deck_xml)
    player2 = self._parse_player_xml(player2_name, player2_deck_xml)
    scenario = copy.deepcopy(self._scenario_data[scenario_name])

    data = {
      "trash": [],
      "stagingArea": [],
      "activeLocation": [],
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
      "setupArea": [],
    }
    if "manual" in scenario:
      data["manual"] = scenario.pop("manual")
    if "Staging Setup" in scenario:
      data["stagingArea"] += scenario.pop("Staging Setup")
    if "Setup" in scenario:
      data["setupArea"] += scenario.pop("Setup")
      data["hasSetup"] = True
    if "Special" in scenario:
      data["hasSpecial"] = True
      data["specialDeck"] += list(reversed(scenario.pop("Special")))
      random.shuffle(data["specialDeck"])
    if "Second Special" in scenario:
      data["hasSecondSpecial"] = True
      data["secondSpecialDeck"] += list(reversed(scenario.pop("Second Special")))
      random.shuffle(data["secondSpecialDeck"])
    if "Quest" in scenario:
      reversedQuestDeck = list(reversed(scenario.pop("Quest")))
      while len(reversedQuestDeck) > 0 and reversedQuestDeck[len(reversedQuestDeck) - 1]["Type"] == "Campaign":
        data["setupArea"].append(reversedQuestDeck.pop())
      data["questDeck"] += reversedQuestDeck
    if "Second Quest" in scenario:
      data["hasSecondQuest"] = True
      data["secondQuestDeck"] += list(reversed(scenario.pop("Second Quest")))
    if "Encounter" in scenario:
      data["encounterDeck"] += scenario.pop("Encounter")
      random.shuffle(data["encounterDeck"])
    if "Active Setup" in scenario:
      locations = scenario.pop("Active Setup")
      if len(locations) != 1:
        raise Exception("Expected only one location.")
      data["activeLocation"] += locations

    if len(scenario) > 0:
      raise Exception("Unexpected keys left in scenario.")

    data["players"] = [player1, player2]

    Lotr.annotate_card_piles(data)

    self._card_games.create_game(player1_name, player2_name, data)

    return data

  # Only used by create_game. This will annotate the map it generates just before returning
  # with additional information such as gameCardId - a unique identifier for each card.
  # card_map {Object} the object which is (almost) generated by create_game. See the
  #     comment for that function for the parameters expected in card_map. This parameter will be modified by this
  #     function.
  @staticmethod
  def annotate_card_piles(card_map):
    game_card_id = 0

    for pile_type in card_map:
      if pile_type in [
        "trash",
        "stagingArea",
        "activeLocation",
        "questDeck",
        "questDiscard",
        "revealArea",
        "secondQuestDeck",
        "secondQuestDiscard",
        "secondQuestReveal",
        "encounterDeck",
        "encounterDiscard",
        "victory",
        "specialDeck",
        "specialDiscard",
        "specialReveal",
        "secondSpecialDeck",
        "secondSpecialDiscard",
        "secondSpecialReveal",
        "setupArea"]:
        for card in card_map[pile_type]:
          card["gameCardId"] = game_card_id
          game_card_id += 1
    for pile_type in card_map["players"][0]:
      if pile_type in [
        "characters",
        "deck",
        "hand",
        "discard",
        "engagedEnemies",
        "secondaryDeck",
        "secondaryDiscard",
        "secondaryReveal"]:
        for card in card_map["players"][0][pile_type]:
          card["owner"] = "player1"
          card["gameCardId"] = game_card_id
          game_card_id += 1
    for pile_type in card_map["players"][1]:
      if pile_type in [
        "characters",
        "deck",
        "hand",
        "discard",
        "engagedEnemies",
        "secondaryDeck",
        "secondaryDiscard",
        "secondaryReveal"]:
        for card in card_map["players"][1][pile_type]:
          card["owner"] = "player2"
          card["gameCardId"] = game_card_id
          game_card_id += 1

  # Returns the most recently used deck of the player as an xml string.
  # player {string} the name of the player to get the most recently used deck of.
  # return {string} an xml representation of the most recent deck used by the player.
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

  # Gets the names of all the scenarios currently available for playing.
  # return {array<string>} the names of the scenarios to load.
  def get_scenario_names(self) -> Optional[Dict]:
    scenario_names = list(self._scenario_data.keys()).copy()
    scenario_names.sort()
    return scenario_names

  # Get the latest game for the given player.
  # player {string} the name of the player to fetch the latest game of.
  def get_latest_game(self, player) -> Optional[Dict]:
    return self._card_games.get_latest_game(player)

  # See comment in card_games.py.
  def mutate_game(self, game_id, mutations):
    return self._card_games.mutate_game(game_id, mutations)

# See comment in card_games.py.
  def undo_and_fetch_latest(self, game_id):
    return self._card_games.undo_and_fetch_latest(game_id)