import yaml
import random
import pprint
from src.card_games.card_games import CardGames
from typing import List, Optional, Dict
import psycopg2
import re
import copy

# Backend for the Dominion game.
# Static files taken from DominionRandomizer/DominionWiki.
class Dominion:
  DOMINION_TABLE_NAME = "dominion_games"
  DOMINION_DATA_TABLE_NAME = "dominion_game_data"
  NON_SUPPLY_CARDS = "nonSupplyCards"
  KINGDOM_CARDS = "kingdomCards"
  VP_CARDS = "vpCards"
  TREASURE_CARDS = "treasureCards"
  NORMAL_CARDS = "normalCards"
  SIDEWAYS_CARDS = "sidewaysCards"
  TRASH = "trash"
  PLAYER_1_DECK = "player1Deck"
  PLAYER_2_DECK = "player2Deck"
  PLAYER_1_HAND = "player1Hand"
  PLAYER_2_HAND = "player2Hand"
  BOONS = "boons"
  BANE = "bane"
  HEXES = "hexes"

  # database {Database} the database used to save games.
  def __init__(self, database):
    self._card_games = CardGames(database, Dominion.DOMINION_TABLE_NAME, Dominion.DOMINION_DATA_TABLE_NAME)
    # NOTE: After population of all member variables, they should never be mutated.

    # {map<string, string>} a map from local image filename to the url for rendering it.
    self._image_name_to_url = self._get_image_name_to_url(
      "static/dominion/image-name-to-url.yaml")
    # {array<Card>} an array of all kingdom cards in dominion. Does not include cards not in the supply.
    # It includes events and landmarks and does not include cards dependent on others like potion.
    # It is used to generate the iniital kingdom cards.
    #
    # Card represents a card in the game. It contains many keys which can be found in the .yaml files.
    # The relevant keys to us are the following:
    # name {string} the name of the card. Populated automatically from the .yaml files.
    # cost {
    #   potion {number} the number of potions needed to buy the card.
    #   treasure {number} the number of coins to buy this.
    # } the cost of the card. Populated automatically from the .yaml files.
    # image {string} the url to render the card. Added in the _add_additional_card_info function for
    #     kingdom cards and in supplemental.yaml for non kingdom cards.
    # type {string} the type of card it is (card, event, landmark, project, ...). Added in the
    #     _add_additional_card_info function for kingdom cards and in supplemental.yaml for non kingdom cards.
    # pileType {string} the type of pile the card belongs to. Not present in the self._cards array. This is
    #     only populated on each card just before sending the cards to the client when starting a new game.
    #     This is used by the client to determine which pile in the game the card can be returned to.
    # pileIndex {number} the index number of the pile the card originally belongs to. Not present in the self._cards array.
    #     Similar to pileType, this is only populated just before sending the cards to the client.
    # gameCardId {number} a unique identifier for each specific card (e.g. each copper card will have its own unique id).
    #     Not present in the self._cards array. Each card will be populated with this just before sending it to the client
    #     when a game is created.
    self._cards = []
    # {array<Card>} an array of all boons in dominion.
    self._boons = []
    # {array<Card>} an array of all hexes in dominion.
    self._hexes = []

    self._potion = {}
    self._shelters_card = {}
    self._colonies_platinums = {}
    self._platinum = {}
    self._gold = {}
    self._silver = {}
    self._copper = {}
    self._colony = {}
    self._province = {}
    self._duchy = {}
    self._estate = {}
    self._plunder = {}
    self._encampment = {}
    self._patrician = {}
    self._emporium = {}
    self._settlers = {}
    self._bustling_village = {}
    self._catapult = {}
    self._rocks = {}
    self._gladiator = {}
    self._fortune = {}
    self._sauna = {}
    self._avanto = {}
    self._knights = []
    self._castles = []
    self._treasure_hunter = {}
    self._warrior = {}
    self._hero = {}
    self._champion = {}
    self._soldier = {}
    self._fugitive = {}
    self._disciple = {}
    self._teacher = {}
    self._madman = {}
    self._mercenary = {}
    self._prizes = []
    self._bat = {}
    self._zombies = []
    self._spoils = {}
    self._curse = {}
    self._will_o_wisp = {}
    self._imp = {}
    self._ghost = {}
    self._wish = {}
    self._magic_lamp = {}
    self._haunted_mirror = {}
    self._goat = {}
    self._pasture = {}
    self._pouch = {}
    self._cursed_gold = {}
    self._lucky_coin = {}
    self._shelters = []
    self._ruins = []

    self._add_cards_from_file("static/dominion/sets/adventures.yaml")
    self._add_cards_from_file("static/dominion/sets/alchemy.yaml")
    self._add_cards_from_file("static/dominion/sets/base-set-2.yaml")
    self._add_cards_from_file("static/dominion/sets/cornucopia.yaml")
    self._add_cards_from_file("static/dominion/sets/dark-ages.yaml")
    self._add_cards_from_file("static/dominion/sets/empires.yaml")
    self._add_cards_from_file("static/dominion/sets/guilds.yaml")
    self._add_cards_from_file("static/dominion/sets/hinterlands.yaml")
    self._add_cards_from_file("static/dominion/sets/intrigue-2.yaml")
    self._add_cards_from_file("static/dominion/sets/nocturne.yaml")
    self._add_cards_from_file("static/dominion/sets/promos.yaml")
    self._add_cards_from_file("static/dominion/sets/prosperity.yaml")
    self._add_cards_from_file("static/dominion/sets/renaissance.yaml")
    self._process_supplementary_cards(
        "static/dominion/sets/supplementary.yaml")
    self.remove_banned_cards_from_kingdom()

  # Returns a map of local image name to url for rendering.
  # filename{string} the filename to read the image name to url data from.
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

  # Populates the _cards, _hexes, and _boones variables with information about each card from the given filename
  # filename {string} the name of the file to get card data from.
  def _add_cards_from_file(self, filename):
    with open(filename, 'r') as stream:
      try:
        set = yaml.load(stream)
        if "cards" in set:
          for card in set["cards"]:
            self._add_additional_card_info(card, "card")
            self._cards.append(card)
        if "events" in set:
          for card in set["events"]:
            self._add_additional_card_info(card, "event")
            self._cards.append(card)
        if "landmarks" in set:
          for card in set["landmarks"]:
            self._add_additional_card_info(card, "landmark")
            self._cards.append(card)
        if "projects" in set:
          for card in set["projects"]:
            self._add_additional_card_info(card, "project")
            self._cards.append(card)
        if "boons" in set:
          for card in set["boons"]:
            self._add_additional_card_info(card, "boon")
            self._boons.append(card)
        if "hexes" in set:
          for card in set["hexes"]:
            self._add_additional_card_info(card, "hexes")
            self._hexes.append(card)
      except yaml.YAMLError as exc:
        print(exc)

  # Adds the fields "type", and "image" to {@code card}.
  # card {Card} the card to modify.
  # type {string} the type of the card.
  # return: The modified card object.
  def _add_additional_card_info(self, card, type):
    card["type"] = type
    self._add_image_to_card(card)
    return card

  # Adds the field "image" to {@code card}.
  # card {Card} the card to modify.
  # return: The modified card object.
  def _add_image_to_card(self, card):
    card["image"] = self._get_image_for_card(card)
    return card

  # Adds the field "image" to {@code cards}.
  # cards {Array<Card>} the cards to modify.
  # return: The modified card object.
  def _add_images_to_cards(self, cards):
    for card in cards:
      self._add_image_to_card(card)
    return cards

  # Returns a string with a link to the image for the given {@code card}
  # card {Card} the card to get the image url for.
  # return {string} the image url to render for the card.
  def _get_image_for_card(self, card):
    image_name = card["name"]
    image_name = re.sub(" / ", "", image_name)
    image_name = re.sub("[ ]", "_", image_name)
    return self._image_name_to_url[image_name]

  # Populates the special cards in the game based on the data in filename.
  # filename {string} the name of the file to read this special card data from.
  def _process_supplementary_cards(self, filename):
    with open(filename, 'r') as stream:
      try:
        cards = yaml.load(stream)
        self._potion = self._add_image_to_card(cards["potion"][0])
        self._shelters_card = self._add_image_to_card(
          cards["shelters_card"][0])
        self._colonies_platinums = self._add_image_to_card(
          cards["colonies_platinums"][0])
        self._platinum = self._add_image_to_card(cards["platinum"][0])
        self._gold = self._add_image_to_card(cards["gold"][0])
        self._silver = self._add_image_to_card(cards["silver"][0])
        self._copper = self._add_image_to_card(cards["copper"][0])
        self._colony = self._add_image_to_card(cards["colony"][0])
        self._province = self._add_image_to_card(cards["province"][0])
        self._duchy = self._add_image_to_card(cards["duchy"][0])
        self._estate = self._add_image_to_card(cards["estate"][0])
        self._plunder = self._add_image_to_card(cards["plunder"][0])
        self._encampment = self._add_image_to_card(cards["encampment"][0])
        self._patrician = self._add_image_to_card(cards["patrician"][0])
        self._emporium = self._add_image_to_card(cards["emporium"][0])
        self._settlers = self._add_image_to_card(cards["settlers"][0])
        self._bustling_village = self._add_image_to_card(
          cards["bustling_village"][0])
        self._catapult = self._add_image_to_card(cards["catapult"][0])
        self._rocks = self._add_image_to_card(cards["rocks"][0])
        self._gladiator = self._add_image_to_card(cards["gladiator"][0])
        self._fortune = self._add_image_to_card(cards["fortune"][0])
        self._sauna = self._add_image_to_card(cards["sauna"][0])
        self._avanto = self._add_image_to_card(cards["avanto"][0])
        self._treasure_hunter = self._add_image_to_card(
          cards["treasure_hunter"][0])
        self._warrior = self._add_image_to_card(cards["warrior"][0])
        self._hero = self._add_image_to_card(cards["hero"][0])
        self._champion = self._add_image_to_card(cards["champion"][0])
        self._soldier = self._add_image_to_card(cards["soldier"][0])
        self._fugitive = self._add_image_to_card(cards["fugitive"][0])
        self._disciple = self._add_image_to_card(cards["disciple"][0])
        self._teacher = self._add_image_to_card(cards["teacher"][0])
        self._madman = self._add_image_to_card(cards["madman"][0])
        self._mercenary = self._add_image_to_card(cards["mercenary"][0])
        self._bat = self._add_image_to_card(cards["bat"][0])
        self._spoils = self._add_image_to_card(cards["spoils"][0])
        self._curse = self._add_image_to_card(cards["curse"][0])
        self._will_o_wisp = self._add_image_to_card(cards["will_o_wisp"][0])
        self._imp = self._add_image_to_card(cards["imp"][0])
        self._ghost = self._add_image_to_card(cards["ghost"][0])
        self._wish = self._add_image_to_card(cards["wish"][0])
        self._magic_lamp = self._add_image_to_card(cards["magic_lamp"][0])
        self._haunted_mirror = self._add_image_to_card(
          cards["haunted_mirror"][0])
        self._goat = self._add_image_to_card(cards["goat"][0])
        self._pasture = self._add_image_to_card(cards["pasture"][0])
        self._pouch = self._add_image_to_card(cards["pouch"][0])
        self._cursed_gold = self._add_image_to_card(cards["cursed_gold"][0])
        self._lucky_coin = self._add_image_to_card(cards["lucky_coin"][0])
        self._knights = self._add_images_to_cards(cards["knights"])
        self._castles = self._add_images_to_cards(cards["castles"])
        self._prizes = self._add_images_to_cards(cards["prizes"])
        self._zombies = self._add_images_to_cards(cards["zombies"])
        self._shelters = self._add_images_to_cards(cards["shelters"])
        self._ruins = self._add_images_to_cards(cards["ruins"])
      except yaml.YAMLError as exc:
        print(exc)

  # Removes banned cards from the kingdom. These cards are typically banned due to the client not supporting
  # them yet.
  def remove_banned_cards_from_kingdom(self):
    self._cards = [
        card for card in self._cards if card["name"] not in ["Black Market", "Possession", "Stash", "Secret Passage", "Pearl Diver"]]

  # Generates a random dominion kingdom. It has the following keys:
  # normal_cards array{Card} The normal set of 10 kingdom cards.
  # sideways_cards array{Card} The landmarks, events, and projects.
  # bane {Card?} If young witch is present, a bane card is added to the kingdom.
  # should_include_potion {boolean} Whether or not the kingdom requires a potion.
  # should_include_platinum_and_colony {boolean} Whether or not to include platinum and colony.
  # should_include_shelters {boolean} Whether or not to use shelters instead of estates.
  # boons array{Card} If Druid is in the game, these are the boons to use for it.
  # supplementary_cards array{Card} Redundant with the should_include_* lines. Contains the cards to include
  #     if those are selected. Included for convenience when rendering the kingdom generated for an in-person game.
  #
  # Note, none of the objects directly references any member variables.
  def generate_random_kingdom(self):
    normal_cards = []
    sideways_cards = []
    bane = None

    boons = copy.deepcopy(random.sample(self._boons, len(self._boons))[:3])

    shuffled_kingdom_cards = copy.deepcopy(random.sample(self._cards, len(self._cards)))
    for card in shuffled_kingdom_cards:
      if bane is None:
        if card["type"] == "card":
          bane = card
        continue
      if card["type"] == "card":
        normal_cards.append(card)
      else:
        sideways_cards.append(card)
      if len(normal_cards) == 10:
        break

    sideways_cards = sideways_cards[:2]

    normal_cards.sort(key=lambda card: card['name'])
    sideways_cards.sort(key=lambda card: card['name'])
    boons.sort(key=lambda card: card['name'])

    ret = {}
    ret["normal_cards"] = normal_cards
    ret["sideways_cards"] = sideways_cards
    if not Dominion.should_add_bane(normal_cards):
      bane = None
    ret["bane"] = bane
    ret["should_include_potion"] = Dominion.should_add_potion(normal_cards)
    ret["should_include_platinum_and_colony"] = Dominion.should_add_platinum_and_colony()
    ret["should_include_shelters"] = Dominion.should_add_shelters()
    if not Dominion.should_include_druid_boons(normal_cards):
      boons = []
    ret["boons"] = boons
    ret["supplementary_cards"] = []
    if ret["should_include_potion"]:
      ret["supplementary_cards"].append(self._potion)
    if ret["should_include_platinum_and_colony"]:
      ret["supplementary_cards"].append(self._colonies_platinums)
    if ret["should_include_shelters"]:
      ret["supplementary_cards"].append(self._shelters_card)
    return ret

  # Given a list of cards, determines whether any of them causes a bane to be added to the kingdom.
  # cards {array<Card>} the cards.
  # return {boolean}
  @staticmethod
  def should_add_bane(cards):
    for card in cards:
      if card["name"] == "Young Witch":
        return True
    return False

  # Given a list of cards, determines whether any of them causes a potion to be added to the kingdom.
  # cards {array<Card>} the cards.
  # return {boolean}
  @staticmethod
  def should_add_potion(cards):
    for card in cards:
      if card["cost"]["potion"] > 0:
        return True
    return False

  # Determines whether platina and colonies should be added to the kingdom.
  # return {boolean}
  @staticmethod
  def should_add_platinum_and_colony():
    return random.random() < 0.2

  # Determines whether shelters should be added to the kingdom.
  # return {boolean}
  @staticmethod
  def should_add_shelters():
    return random.random() < 0.1

  # Determines whether 3 boons should be added to the kingdom face up.
  # return {boolean}
  @staticmethod
  def should_include_druid_boons(cards):
    for card in cards:
      if card["name"] == "Druid":
        return True
    return False

  # Generates the data used to render an online game. It contains the following keys:
  # Dominion.KINGDOM_CARDS {array<array<Card>>} a nested array of Cards representing the cards in the kingdom.
  # Dominion.NON_SUPPLY_CARDS {array<array<Card>>} a nested array of Cards not in the supply.
  # Dominion.SIDEWAYS_CARDS {array<Card>} an array of sideways Cards in the game.
  # Dominion.BANE {Card?} the bane card in the game if any.
  # Dominion.TRASH {array<Card>} an array of trashed Cards in the game.
  # Dominion.BOONS {array<Card>?} an array of boons Cards in the game.
  # Dominion.HEXES {array<Card>?} an array of hex Cards in the game.
  # Dominion.VP_CARDS {array<Card>} an array of the victory point Cards in the game.
  # Dominion.TREASURE_CARDS {array<Card>} an array of the treasure Cards in the game.
  # Dominion.PLAYER_1_DECK {array<Card>} an array of player 1's Cards in the game.
  # Dominion.PLAYER_2_DECK {array<Card>} an array of player 2's Cards in the game.
  # Dominion.PLAYER_1_HAND {array<Card>} an array of player 1's Cards in their hand.
  # Dominion.PLAYER_2_HAND {array<Card>} an array of player 2's Cards in their hand.
  def generate_random_kingdom_for_online_game(self):
    random_cards = copy.deepcopy(self.generate_random_kingdom())
    normal_cards = random_cards["normal_cards"]
    normal_cards.sort(key=lambda card: card["cost"]["treasure"])

    sideways_cards = random_cards["sideways_cards"]
    sideways_cards.sort(key=lambda card: card["cost"]["treasure"])
    all_non_sideways_cards = copy.deepcopy(normal_cards)
    bane = None
    if random_cards["bane"]:
      all_non_sideways_cards += [random_cards["bane"]]
      bane = random_cards["bane"]

    ret = {}
    ret[Dominion.SIDEWAYS_CARDS] = copy.deepcopy(sideways_cards)
    ret[Dominion.TRASH] = []

    has_potion = random_cards["should_include_potion"]
    has_platinum_and_colony = random_cards["should_include_platinum_and_colony"]
    has_shelters = random_cards["should_include_shelters"]
    has_page_line = False
    has_peasant_line = False
    has_madman = False
    has_prizes = False
    has_mercenary = False
    has_bat = False
    has_zombies = False
    has_hexes = False
    has_boons = False
    has_spoils = False
    has_curses = False
    has_ruins = False
    has_will_o_wisp = False
    has_imp = False
    has_ghost = False
    has_wishes = False
    has_magic_lamp = False
    has_haunted_mirror = False
    has_goat = False
    has_pasture = False
    has_pouch = False
    has_cursed_gold = False
    has_lucky_coin = False

    for card in all_non_sideways_cards:
      card_name = card["name"]
      if card_name == "Page":
        has_page_line = True
      if card_name == "Peasant":
        has_peasant_line = True
      if card_name == "Hermit":
        has_madman = True
      if card_name == "Tournament":
        has_prizes = True
      if card_name == "Urchin":
        has_mercenary = True
      if card_name == "Vampire":
        has_bat = True
      if card_name == "Necromancer":
        has_zombies = True
      if "isDoom" in card and card["isDoom"]:
        has_hexes = True
      if "isFate" in card and card["isFate"]:
        has_boons = True
      if "isLooter" in card and card["isLooter"]:
        has_ruins = True
      if card_name in ["Bandit Camp", "Marauder", "Pillage"]:
        has_spoils = True
      if card_name in ["Witch", "Sea Hag", "Familiar", "Mountebank", "Young Witch",
                        "Ill-Gotten Gains", "Soothsayer", "Old Witch", "Swindler", "Replace",
                        "Torturer", "Ambassador", "Tournament", "Giant", "Swamg Hag", "Embargo",
                        "Hideout", "Leprechaun", "Skulk", "Cursed Village", "Tormentor", "Vampire",
                        "Werewolf", "Pooka"]:
        has_curses = True
      if card_name in ["Devil's Workshop", "Tormentor"]:
        has_imp = True
      if card_name == "Exorcist":
        has_will_o_wisp = True
        has_imp = True
        has_ghost = True
      if card_name == "Cemetery":
        has_ghost = True
      if card_name in ["Secret Cave", "Leprechaun"]:
        has_wishes = True
      if card_name == "Secret Cave":
        has_magic_lamp = True
      if card_name == "Cemetery":
        has_haunted_mirror = True
      if card_name == "Pixie":
        has_goat = True
      if card_name == "Shepherd":
        has_pasture = True
      if card_name == "Tracker":
        has_pouch = True
      if card_name == "Pooka":
        has_cursed_gold = True
      if card_name == "Fool":
        has_lucky_coin = True

    for card in sideways_cards:
      if card["name"] == "Ritual":
        has_curses = True
      if card["name"] == "Defiled Shrine":
        has_curses = True

    if has_boons:
      has_will_o_wisp = True

    ret[Dominion.NON_SUPPLY_CARDS] = []

    if has_page_line:
      ret[Dominion.NON_SUPPLY_CARDS] += self.generate_page_line()

    if has_peasant_line:
      ret[Dominion.NON_SUPPLY_CARDS] += self.generate_peasant_line()

    if has_prizes:
      ret[Dominion.NON_SUPPLY_CARDS] += self.generate_prizes()

    if has_zombies:
      ret[Dominion.TRASH] += self.generate_zombies()

    if has_madman:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_madman())

    if has_mercenary:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_mercenary())

    if has_bat:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_bat())

    if has_boons:
      ret[Dominion.BOONS] = self.generate_boons()

    if has_hexes:
      ret[Dominion.HEXES] = self.generate_hexes()

    if has_spoils:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_spoils())

    if has_curses:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_curses())

    if has_imp:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_imp())

    if has_will_o_wisp:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_will_o_wisp())

    if has_ghost:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_ghost())

    if has_wishes:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_wishes())

    if has_ruins:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_ruins())

    if has_potion:
      ret[Dominion.NON_SUPPLY_CARDS].append(self.generate_potion())

    ret[Dominion.VP_CARDS] = self.generate_vp_cards(has_platinum_and_colony)
    ret[Dominion.TREASURE_CARDS] = self.generate_treasure_cards(has_platinum_and_colony)
    ret[Dominion.PLAYER_1_DECK] = self.generate_player_cards(
        has_magic_lamp, has_haunted_mirror, has_goat,
        has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)
    ret[Dominion.PLAYER_2_DECK] = self.generate_player_cards(
        has_magic_lamp, has_haunted_mirror, has_goat,
        has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)
    ret[Dominion.PLAYER_1_HAND] = []
    ret[Dominion.PLAYER_2_HAND] = []
    for i in range(5):
      ret[Dominion.PLAYER_1_HAND].append(ret[Dominion.PLAYER_1_DECK].pop())
      ret[Dominion.PLAYER_2_HAND].append(ret[Dominion.PLAYER_2_DECK].pop())

    ret[Dominion.KINGDOM_CARDS] = []
    for card in normal_cards:
      ret[Dominion.KINGDOM_CARDS].append(self.generate_pile(card))

    if bane:
      ret[Dominion.BANE] = self.generate_pile(bane)

    Dominion.annotate_card_piles(ret)
    return ret

  # Generates the victory point cards for use in a Dominion game.
  # has_platinum_and_colony {boolean} whether there is a platinum and colony in the game.
  # return {array<array<Card>>} a nested array of Cards which are the victory point cards in the game.
  def generate_vp_cards(self, has_platinum_and_colony):
    ret = []
    if has_platinum_and_colony:
      ret.append(Dominion.create_n_copies(self._colony, 8))
    ret.append(Dominion.create_n_copies(self._province, 8))
    ret.append(Dominion.create_n_copies(self._duchy, 8))
    ret.append(Dominion.create_n_copies(self._estate, 8))
    return ret

  @staticmethod
  def create_n_copies(obj, num):
    return [copy.deepcopy(obj) for i in range(num)]

  # Generates the treasure cards for use in a Dominion game.
  # has_platinum_and_colony {boolean} whether there is a platinum and colony in the game.
  # return {array<array<Card>>} a nested array of Cards which are the treasure cards in the game.
  def generate_treasure_cards(self, has_platinum_and_colony):
    ret = []
    if has_platinum_and_colony:
      ret.append(Dominion.create_n_copies(self._platinum, 12))
    ret.append(Dominion.create_n_copies(self._gold, 30))
    ret.append(Dominion.create_n_copies(self._silver, 40))
    ret.append(Dominion.create_n_copies(self._copper, 46))
    return ret

  # Generates the initial cards for a player's deck.
  # has_* {boolean} whether the card is in the game.
  # return {array<Card>} the cards in the player's hand.
  def generate_player_cards(self, has_magic_lamp, has_haunted_mirror, has_goat,
                            has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters):
    ret = []
    if has_magic_lamp:
      ret.append(copy.deepcopy(self._magic_lamp))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_haunted_mirror:
      ret.append(copy.deepcopy(self._haunted_mirror))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_goat:
      ret.append(copy.deepcopy(self._goat))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_pasture:
      ret.append(copy.deepcopy(self._pasture))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_pouch:
      ret.append(copy.deepcopy(self._pouch))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_cursed_gold:
      ret.append(copy.deepcopy(self._cursed_gold))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_lucky_coin:
      ret.append(copy.deepcopy(self._lucky_coin))
    else:
      ret.append(copy.deepcopy(self._copper))

    if has_shelters:
      ret += copy.deepcopy(self._shelters)
    else:
      ret.append(copy.deepcopy(self._estate))
      ret.append(copy.deepcopy(self._estate))
      ret.append(copy.deepcopy(self._estate))
    random.shuffle(ret)
    return ret

  # Generates a pile of cards corresponding to the given card.
  # card {Card} the card to make a pile of.
  # return {<array[Card]>} the array of Cards representing the pile.
  def generate_pile(self, card):
    card_name = card["name"]

    ret = []
    if card_name == "Encampment / Plunder":
      ret += Dominion.create_n_copies(self._plunder, 5)
      ret += Dominion.create_n_copies(self._encampment, 5)
      return ret
    if card_name == "Patrician / Emporium":
      ret += Dominion.create_n_copies(self._emporium, 5)
      ret += Dominion.create_n_copies(self._patrician, 5)
      return ret
    if card_name == "Settlers / Bustling Village":
      ret += Dominion.create_n_copies(self._bustling_village, 5)
      ret += Dominion.create_n_copies(self._settlers, 5)
      return ret
    if card_name == "Catapult / Rocks":
      ret += Dominion.create_n_copies(self._rocks, 5)
      ret += Dominion.create_n_copies(self._catapult, 5)
      return ret
    if card_name == "Gladiator / Fortune":
      ret += Dominion.create_n_copies(self._fortune, 5)
      ret += Dominion.create_n_copies(self._gladiator, 5)
      return ret
    if card_name == "Sauna / Avanto":
      ret += Dominion.create_n_copies(self._avanto, 5)
      ret += Dominion.create_n_copies(self._sauna, 5)
      return ret
    if card_name == "Knights":
      ret = copy.deepcopy(self._knights)
      random.shuffle(ret)
      return ret
    if card_name == "Castles":
      ret = copy.deepcopy(self._castles)
      return ret

    num_cards = 10
    if "isVictory" in card and card["isVictory"]:
      num_cards = 8
    elif card_name == "Port":
      num_cards = 12
    elif card_name == "Rats":
      num_cards = 20
    ret += Dominion.create_n_copies(card, num_cards)
    return ret

  # Only used by generate_random_kingdom_for_online_game. This will annotate the map it generates just before returning
  # with additional information.
  # card_map {Object} the object which is (almost) generated by generate_random_kingdom_for_online_game. See the
  #     comment for that function for the parameters expected in card_map. This parameter will be modified by this
  #     function.
  @staticmethod
  def annotate_card_piles(card_map):
    copper_pile_index = Dominion.get_copper_pile_index(card_map[Dominion.TREASURE_CARDS])
    estate_pile_index = Dominion.get_estate_pile_index(card_map[Dominion.VP_CARDS])
    game_card_id = 0
    for pile_type in card_map:
      if pile_type in [Dominion.TREASURE_CARDS, Dominion.VP_CARDS, Dominion.KINGDOM_CARDS, Dominion.NON_SUPPLY_CARDS]:
        for (pile_index, card_array) in enumerate(card_map[pile_type]):
          for card in card_array:
            card["gameCardId"] = game_card_id
            game_card_id += 1
            card["pileType"] = pile_type
            card["pileIndex"] = pile_index
            if card["name"] == "Copper":
              copper_pile_index = pile_index
            if card["name"] == "Estate":
              estate_pile_index = pile_index
      elif pile_type in [Dominion.SIDEWAYS_CARDS, Dominion.BANE, Dominion.BOONS, Dominion.HEXES, Dominion.TRASH]:
        for card in card_map[pile_type]:
          card["gameCardId"] = game_card_id
          game_card_id += 1
          card["pileType"] = pile_type
      elif pile_type in [Dominion.PLAYER_1_DECK, Dominion.PLAYER_2_DECK, Dominion.PLAYER_1_HAND, Dominion.PLAYER_2_HAND]:
        for card in card_map[pile_type]:
          card["gameCardId"] = game_card_id
          game_card_id += 1
          if card["name"] == "Copper":
            card["pileType"] = Dominion.TREASURE_CARDS
            card["pileIndex"] = copper_pile_index
          elif card["name"] == "Estate":
            card["pileType"] = Dominion.VP_CARDS
            card["pileIndex"] = estate_pile_index
      else:
        raise Exception("Unexpected key.")

  # Gets the index of the copper pile in the given array of cards if any.
  @staticmethod
  def get_copper_pile_index(arr):
    for (pile_index, card_array) in enumerate(arr):
      if card_array[0]["name"] == "Copper":
        return pile_index

  # Gets the index of the estate pile in the given array of cards if any.
  @staticmethod
  def get_estate_pile_index(arr):
    for (pile_index, card_array) in enumerate(arr):
      if card_array[0]["name"] == "Estate":
        return pile_index

  # Returns an array containing the page related supply piles.
  # return {array<array<Card>>} an array of Card piles.
  def generate_page_line(self):
    ret = []
    ret.append(Dominion.create_n_copies(self._treasure_hunter, 5))
    ret.append(Dominion.create_n_copies(self._warrior, 5))
    ret.append(Dominion.create_n_copies(self._hero, 5))
    ret.append(Dominion.create_n_copies(self._champion, 5))
    return ret

  # Returns an array containing the peasant related supply piles.
  # return {array<array<Card>>} an array of Card piles.
  def generate_peasant_line(self):
    ret = []
    ret.append(Dominion.create_n_copies(self._soldier, 5))
    ret.append(Dominion.create_n_copies(self._fugitive, 5))
    ret.append(Dominion.create_n_copies(self._disciple, 5))
    ret.append(Dominion.create_n_copies(self._teacher, 5))
    return ret

  # Returns an array containing the prize supply piles.
  # return {array<array<Card>>} an array of Card piles.
  def generate_prizes(self):
    ret = []
    for prize in self._prizes:
      ret.append(Dominion.create_n_copies(prize, 1))
    return ret

  # Returns the zombie cards as an array.
  # return {array<Card>} an array of zombie cards.
  def generate_zombies(self):
    ret = []
    for zombie in self._zombies:
      ret.append(zombie)
    return ret

  # Returns the madman cards.
  # return {array<Card>} an array of madman cards.
  def generate_madman(self):
    return Dominion.create_n_copies(self._madman, 10)

  # Returns the mercenary cards.
  # return {array<Card>} an array of mercenary cards.
  def generate_mercenary(self):
    return Dominion.create_n_copies(self._mercenary, 10)

  # Returns the potion cards.
  # return {array<Card>} an array of potion cards.
  def generate_potion(self):
    return Dominion.create_n_copies(self._potion, 16)

  # Returns the bat cards.
  # return {array<Card>} an array of bat cards.
  def generate_bat(self):
    return Dominion.create_n_copies(self._bat, 10)

  # Returns the boons cards.
  # return {array<Card>} an array of boons cards.
  def generate_boons(self):
    return copy.deepcopy(random.sample(self._boons, len(self._boons)))

  # Returns the hex cards.
  # return {array<Card>} an array of hex cards.
  def generate_hexes(self):
    return copy.deepcopy(random.sample(self._hexes, len(self._hexes)))

  # Returns the spoils cards.
  # return {array<Card>} an array of spoils cards.
  def generate_spoils(self):
    return Dominion.create_n_copies(self._spoils, 15)

  # Returns the curse cards.
  # return {array<Card>} an array of curse cards.
  def generate_curses(self):
    return Dominion.create_n_copies(self._curse, 10)

  # Returns the imp cards.
  # return {array<Card>} an array of imp cards.
  def generate_imp(self):
    return Dominion.create_n_copies(self._imp, 13)

  # Returns the will o' wisp cards.
  # return {array<Card>} an array of will o' wisp cards.
  def generate_will_o_wisp(self):
    return Dominion.create_n_copies(self._will_o_wisp, 12)

  # Returns the ghost cards.
  # return {array<Card>} an array of ghost cards.
  def generate_ghost(self):
    return Dominion.create_n_copies(self._ghost, 6)

  # Returns the wish cards.
  # return {array<Card>} an array of wish cards.
  def generate_wishes(self):
    return Dominion.create_n_copies(self._wish, 12)

  # Returns the ruins cards.
  # return {array<Card>} an array of ruin cards.
  def generate_ruins(self):
    ruins = []
    for i in range(10):
      ruins += copy.deepcopy(self._ruins)
    return random.sample(ruins, 10)

  # Creates a new game with the given player names.
  # player1 {string} the name of the first player in the game.
  # player2 {string} the name of the second player in the game.
  def create_game(self, player1, player2) -> int:
    game_data = self.generate_random_kingdom_for_online_game()

    data = {}
    data["playerOrder"] = [player1, player2]
    data["currentPlayerTurn"] = 0
    data["revealArea"] = []
    data["gameLog"] = []
    data["players"] = [{
        "name": player1,
        "durationArea": [],
        "playArea": [],
        "deck": game_data[Dominion.PLAYER_1_DECK],
        "hand": game_data[Dominion.PLAYER_1_HAND],
        "mats": [],
        "discard": [],
        "numActions": 1,
        "numBuys": 1,
        "numCoins": 0,
        "numVP": 0,
        "numCoffers": 0,
        "numVillagers": 0,
        "numDebt": 0,
        "displayedPlayer": 0
    }, {
        "name": player2,
        "durationArea": [],
        "playArea": [],
        "deck": game_data[Dominion.PLAYER_2_DECK],
        "hand": game_data[Dominion.PLAYER_2_HAND],
        "mats": [],
        "discard": [],
        "numActions": 1,
        "numBuys": 1,
        "numCoins": 0,
        "numVP": 0,
        "numCoffers": 0,
        "numVillagers": 0,
        "numDebt": 0,
        "displayedPlayer": 0
    }]
    data["boonsDiscard"] = []
    data["hexesDiscard"] = []
    data["boonsDeck"] = []
    data["boonsReveal"] = []
    data["hexesDeck"] = []
    data["hexesReveal"] = []
    data["nonSupplyCards"] = game_data[Dominion.NON_SUPPLY_CARDS]
    data["kingdomCards"] = game_data[Dominion.KINGDOM_CARDS]
    data["vpCards"] = game_data[Dominion.VP_CARDS]
    data["treasureCards"] = game_data[Dominion.TREASURE_CARDS]
    data["trash"] = game_data[Dominion.TRASH]
    if Dominion.BANE in game_data:
      data["bane"] = game_data[Dominion.BANE]
    if Dominion.HEXES in game_data:
      data["hexesDeck"] = game_data[Dominion.HEXES]
    if Dominion.BOONS in game_data:
      data["boonsDeck"] = game_data[Dominion.BOONS]
    data["sidewaysCards"] = game_data[Dominion.SIDEWAYS_CARDS]
    data["hasBane"] = Dominion.BANE in game_data
    data["hasBoons"] = Dominion.BOONS in game_data
    data["hasHexes"] = Dominion.HEXES in game_data

    self._card_games.create_game(player1, player2, data)

    return data

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