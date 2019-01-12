import yaml
import random
import pprint
from src.dominion.dominion_database import DominionDatabase
from typing import List, Optional, Dict
import psycopg2
import re

# Static files taken from DominionRandomizer/DominionWiki.


class Dominion:
  NON_SUPPLY_CARDS = "non_supply_cards"
  KINGDOM_CARDS = "kingdom_cards"
  VP_CARDS = "vp_cards"
  TREASURE_CARDS = "treasure_cards"
  NORMAL_CARDS = "normal_cards"
  SIDEWAYS_CARDS = "sideways_cards"
  TRASH = "trash"
  PLAYER_1_DECK = "player_1_deck"
  PLAYER_2_DECK = "player_2_deck"
  PLAYER_1_HAND = "player_1_hand"
  PLAYER_2_HAND = "player_2_hand"
  BOONS = "boons"
  BANE = "bane"
  HEXES = "hexes"

  def __init__(self, database):
    # All the cards initialized below will have data specified in their corresponding yaml field as well as
    # the set it comes from,
    # Cards includes all cards to select the randomized kingdom from.
    #     It includes events and landmarks and does not include cards dependent on others like potion.
    self._image_name_to_url = {}
    self._cards = []
    self._boons = []
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
    self._populate_image_name_to_url(
      "static/dominion/image-name-to-url.yaml")
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
    self._dominion_database = DominionDatabase(database)

  def _populate_image_name_to_url(self, filename):
    with open(filename, 'r') as stream:
      try:
        root = yaml.load(stream)
        for name in root:
          self._image_name_to_url[name] = root[name]
      except yaml.YAMLError as exc:
        print(exc)

  # Adds the fields "type", and "iamge" to {@code card}.
  # card: Object
  # type: string
  # return: The modified card object.
  def _add_additional_card_info(self, card, type):
    card["type"] = type
    self._add_image_to_card(card)
    return card

  # Adds the field "image" to {@code card}.
  # card: Object
  # return: The modified card object.
  def _add_image_to_card(self, card):
    card["image"] = self._get_image_for_card(card)
    return card

  # Adds the field "image" to {@code cards}.
  # card: Array<Object>
  # return: The modified card object.
  def _add_images_to_cards(self, cards):
    for card in cards:
      self._add_image_to_card(card)
    return cards

  # Returns a string with a link to the image for the given {@code card}
  def _get_image_for_card(self, card):
    image_name = card["name"]
    image_name = re.sub(" / ", "", image_name)
    image_name = re.sub("[ ]", "_", image_name)
    return self._image_name_to_url[image_name]

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

  def remove_banned_cards_from_kingdom(self):
    self._cards = [
        card for card in self._cards if card["name"] != "Black Market"]
    self._cards = [
        card for card in self._cards if card["name"] != "Possession"]

  # Generates a random dominion kingdom. It has the following keys:
  # normal_cards: The normal set of 10 kingdom cards.
  # sideways_cards: The landmarks, events, and projects.
  # bane: If young witch is present, a bane card is added to the kingdom.
  # should_include_potion: Whether or not the kingdom requires a potion.
  # should_include_platinum_and_colony: Whether or not to include platinum and colony.
  # should_include_shelters: Whether or not to use shelters instead of estates.
  # boons: If Druid is in the game, these are the boons to use for it.
  # supplementary_cards: Redundant with the should_include_* lines. Contains the cards to include
  #     if those are selected.
  # TODO: Skips Stash, Pearl Diver, and Secret Passage because they're unimplemented in the front end.
  def generate_random_kingdom(self):
    normal_cards = []
    sideways_cards = []
    bane = None

    boons = random.sample(self._boons, len(self._boons))[:3]

    shuffled_kingdom_cards = random.sample(self._cards, len(self._cards))
    for card in shuffled_kingdom_cards:
      if card["name"] in ["Stash", "Secret Passage", "Pearl Diver"]:
        continue
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
    ret["should_include_platinum_and_colony"] = Dominion.should_add_platinum_and_colony(
        normal_cards)
    ret["should_include_shelters"] = Dominion.should_add_shelters(
        normal_cards)
    if not Dominion.should_include_boons(normal_cards):
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

  def generate_random_kingdom_for_online_game(self):
    random_cards = self.generate_random_kingdom()
    normal_cards = random_cards["normal_cards"].copy()
    normal_cards.sort(key=lambda card: card["cost"]["treasure"])

    sideways_cards = random_cards["sideways_cards"].copy()
    sideways_cards.sort(key=lambda card: card["cost"]["treasure"])
    all_cards = normal_cards.copy()
    bane = None
    if random_cards["bane"]:
      all_cards += [random_cards["bane"]]
      bane = random_cards["bane"]

    ret = {}
    ret[Dominion.KINGDOM_CARDS] = []  # A nested array
    ret[Dominion.NON_SUPPLY_CARDS] = []  # A nested array
    ret[Dominion.SIDEWAYS_CARDS] = sideways_cards
    ret[Dominion.BANE] = []
    ret[Dominion.TRASH] = []
    ret[Dominion.BOONS] = []
    ret[Dominion.HEXES] = []
    ret[Dominion.VP_CARDS] = []
    ret[Dominion.TREASURE_CARDS] = []
    ret[Dominion.PLAYER_1_DECK] = []
    ret[Dominion.PLAYER_2_DECK] = []
    non_supply_cards_index = 0

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

    for card in all_cards:
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

    if has_page_line:
      self.add_page_line(ret)

    if has_peasant_line:
      self.add_peasant_line(ret)

    if has_madman:
      self.add_madman(ret)

    if has_prizes:
      self.add_prizes(ret)

    if has_mercenary:
      self.add_mercenary(ret)

    if has_bat:
      self.add_bat(ret)

    if has_zombies:
      self.add_zombies(ret)

    if has_boons:
      self.add_boons(ret)

    if has_hexes:
      self.add_hexes(ret)

    if has_spoils:
      self.add_spoils(ret)

    if has_curses:
      self.add_curses(ret)

    if has_imp:
      self.add_imp(ret)

    if has_will_o_wisp:
      self.add_will_o_wisp(ret)

    if has_ghost:
      self.add_ghost(ret)

    if has_wishes:
      self.add_wishes(ret)

    if has_ruins:
      self.add_ruins(ret)

    if has_potion:
      self.add_potion(ret)

    self.add_vp_cards(ret, has_platinum_and_colony)
    self.add_treasure_cards(ret, has_platinum_and_colony)
    self.generate_player_cards(
        ret[Dominion.PLAYER_1_DECK], has_magic_lamp, has_haunted_mirror, has_goat,
        has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)
    self.generate_player_cards(
        ret[Dominion.PLAYER_2_DECK], has_magic_lamp, has_haunted_mirror, has_goat,
        has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)
    ret[Dominion.PLAYER_1_HAND] = []
    ret[Dominion.PLAYER_2_HAND] = []
    for i in range(5):
      ret[Dominion.PLAYER_1_HAND].append(
          ret[Dominion.PLAYER_1_DECK].pop())
      ret[Dominion.PLAYER_2_HAND].append(
          ret[Dominion.PLAYER_2_DECK].pop())

    for card in normal_cards:
      ret[Dominion.KINGDOM_CARDS].append(self.generate_pile(card))

    if bane:
      ret[Dominion.BANE] = self.generate_pile(bane)

    Dominion.annotate_card_piles(ret)
    return ret

  @staticmethod
  def get_copper_pile_index(card_map):
    for (pile_index, card_array) in enumerate(card_map[Dominion.TREASURE_CARDS]):
      if card_array[0]["name"] == "Copper":
        return pile_index

  @staticmethod
  def get_estate_pile_index(card_map):
    for (pile_index, card_array) in enumerate(card_map[Dominion.VP_CARDS]):
      if card_array[0]["name"] == "Estate":
        return pile_index

  @staticmethod
  def annotate_card_piles(card_map):
    copper_pile_index = Dominion.get_copper_pile_index(card_map)
    estate_pile_index = Dominion.get_estate_pile_index(card_map)
    for pile_type in [Dominion.TREASURE_CARDS, Dominion.VP_CARDS, Dominion.KINGDOM_CARDS, Dominion.NON_SUPPLY_CARDS]:
      for (pile_index, card_array) in enumerate(card_map[pile_type]):
        for card in card_array:
          card["pile_type"] = pile_type
          card["pile_index"] = pile_index
    for pile_type in [Dominion.PLAYER_1_DECK, Dominion.PLAYER_2_DECK, Dominion.PLAYER_1_HAND, Dominion.PLAYER_2_HAND]:
      for card in card_map[pile_type]:
        if card["name"] == "Copper":
          card["pile_type"] = Dominion.TREASURE_CARDS
          card["pile_index"] = copper_pile_index
        elif card["name"] == "Estate":
          card["pile_type"] = Dominion.VP_CARDS
          card["pile_index"] = estate_pile_index

  def add_treasure_cards(self, card_map, has_platinum_and_colony):
    if has_platinum_and_colony:
      card_map[Dominion.TREASURE_CARDS].append(
        Dominion.create_n_copies(self._platinum, 12))
    card_map[Dominion.TREASURE_CARDS].append(
      Dominion.create_n_copies(self._gold, 30))
    card_map[Dominion.TREASURE_CARDS].append(
      Dominion.create_n_copies(self._silver, 40))
    card_map[Dominion.TREASURE_CARDS].append(
      Dominion.create_n_copies(self._copper, 46))

  def add_vp_cards(self, card_map, has_platinum_and_colony):
    if has_platinum_and_colony:
      card_map[Dominion.VP_CARDS].append(
        Dominion.create_n_copies(self._colony, 8))
    card_map[Dominion.VP_CARDS].append(
      Dominion.create_n_copies(self._province, 8))
    card_map[Dominion.VP_CARDS].append(
      Dominion.create_n_copies(self._duchy, 8))
    card_map[Dominion.VP_CARDS].append(
      Dominion.create_n_copies(self._estate, 8))

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
      ret = self._knights.copy()
      random.shuffle(ret)
      return ret
    if card_name == "Castles":
      ret = self._castles.copy()
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

  def add_page_line(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._treasure_hunter, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._warrior, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._hero, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._champion, 5))

  def add_peasant_line(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._soldier, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._fugitive, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._disciple, 5))
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._teacher, 5))

  def add_madman(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._madman, 10))

  def add_prizes(self, card_map):
    for prize in self._prizes:
      card_map[Dominion.NON_SUPPLY_CARDS].append(
        Dominion.create_n_copies(prize, 1))

  def add_mercenary(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._mercenary, 10))

  def add_potion(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._potion, 16))

  def add_bat(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._bat, 10))

  def add_zombies(self, card_map):
    for zombie in self._zombies:
      card_map[Dominion.TRASH].append(zombie)

  def add_boons(self, card_map):
    card_map[Dominion.BOONS] = random.sample(self._boons, len(self._boons))

  def add_hexes(self, card_map):
    card_map[Dominion.HEXES] = random.sample(self._hexes, len(self._hexes))

  def add_spoils(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._spoils, 15))

  def add_curses(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._curse, 10))

  def add_imp(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._imp, 13))

  def add_will_o_wisp(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._will_o_wisp, 12))

  def add_ghost(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._ghost, 6))

  def add_wishes(self, card_map):
    card_map[Dominion.NON_SUPPLY_CARDS].append(
      Dominion.create_n_copies(self._wish, 12))

  def generate_player_cards(self, player_deck, has_magic_lamp, has_haunted_mirror, has_goat,
                            has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters):
    if has_magic_lamp:
      player_deck.append(self._magic_lamp)
    else:
      player_deck.append(self._copper)

    if has_haunted_mirror:
      player_deck.append(self._haunted_mirror)
    else:
      player_deck.append(self._copper)

    if has_goat:
      player_deck.append(self._goat)
    else:
      player_deck.append(self._copper)

    if has_pasture:
      player_deck.append(self._pasture)
    else:
      player_deck.append(self._copper)

    if has_pouch:
      player_deck.append(self._pouch)
    else:
      player_deck.append(self._copper)

    if has_cursed_gold:
      player_deck.append(self._cursed_gold)
    else:
      player_deck.append(self._copper)

    if has_lucky_coin:
      player_deck.append(self._lucky_coin)
    else:
      player_deck.append(self._copper)

    if has_shelters:
      player_deck += self._shelters
    else:
      player_deck.append(self._estate)
      player_deck.append(self._estate)
      player_deck.append(self._estate)
    random.shuffle(player_deck)

  def add_ruins(self, card_map):
    ruins = []
    for i in range(10):
      ruins += self._ruins
    card_map[Dominion.NON_SUPPLY_CARDS].append(random.sample(ruins, 10))

  @staticmethod
  def create_n_copies(obj, num):
    return [obj for i in range(num)]

  @staticmethod
  def should_add_bane(cards):
    for card in cards:
      if card["name"] == "Young Witch":
        return True
    return False

  @staticmethod
  def should_add_potion(cards):
    for card in cards:
      if card["cost"]["potion"] > 0:
        return True
    return False

  @staticmethod
  def should_add_platinum_and_colony(cards):
    return random.random() < 0.2

  @staticmethod
  def should_add_shelters(cards):
    return random.random() < 0.1

  @staticmethod
  def should_include_boons(cards):
    for card in cards:
      if card["name"] == "Druid":
        return True
    return False

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
        "deck": game_data["player_1_deck"],
        "hand": game_data["player_1_hand"],
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
        "deck": game_data["player_2_deck"],
        "hand": game_data["player_2_hand"],
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
    data["nonSupplyCards"] = game_data["non_supply_cards"]
    data["kingdomCards"] = game_data["kingdom_cards"]
    data["vpCards"] = game_data["vp_cards"]
    data["treasureCards"] = game_data["treasure_cards"]
    data["trash"] = game_data["trash"]
    data["bane"] = game_data["bane"]
    data["hexesDeck"] = game_data["hexes"]
    data["boonsDeck"] = game_data["boons"]
    data["sidewaysCards"] = game_data["sideways_cards"]
    data["hasBane"] = len(game_data["bane"]) > 0
    data["hasBoons"] = len(game_data["boons"]) > 0
    data["hasHexes"] = len(game_data["hexes"]) > 0

    cur = self._dominion_database.get_cursor()

    try:
      game_id = DominionDatabase.add_game(cur, player1, player2, {})
      data["gameId"] = game_id
      DominionDatabase.update_game(cur, game_id, data)

      self._dominion_database.commit()
      cur.close()
    except psycopg2.Error:
      self._dominion_database.rollback()
      cur.close()
      raise

    return data

  # Returns the game as a dict.
  def get_latest_game(self, player) -> Optional[Dict]:
    cur = self._dominion_database.get_cursor()

    try:
      game = DominionDatabase.get_latest_game(cur, player)
      cur.close()
      if game is None:
        return None
    except psycopg2.Error:
      self._dominion_database.rollback()
      cur.close()
      raise

    return game

  def update_game(self, game_id, data) -> int:
    cur = self._dominion_database.get_cursor()

    try:
      DominionDatabase.update_game(cur, game_id, data)

      self._dominion_database.commit()
      cur.close()
    except psycopg2.Error:
      self._dominion_database.rollback()
      cur.close()
      raise
