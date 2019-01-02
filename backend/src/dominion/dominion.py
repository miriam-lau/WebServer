import yaml
import random
import pprint
from src.dominion.dominion_database import DominionDatabase
from typing import List, Optional, Dict
import psycopg2

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
    BOONS = "boons"
    BANE = "bane"
    HEXES = "hexes"

    def __init__(self, database):
        # Cards includes all cards to select the randomized kingdom from. It includes events and
        # landmarks and does not include cards dependent on others like potion.
        self._cards = []
        self._boons = []
        self._hexes = []
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
        self._add_cards_from_file("static/dominion/sets/seaside.yaml")
        self.remove_banned_cards_from_kingdom()
        self._dominion_database = DominionDatabase(database)

    def _add_cards_from_file(self, filename):
        with open(filename, 'r') as stream:
            try:
                set = yaml.load(stream)
                if "cards" in set:
                    for card in set["cards"]:
                        card["set"] = set["name"]
                        card["type"] = "card"
                        self._cards.append(card)
                if "events" in set:
                    for card in set["events"]:
                        card["set"] = set["name"]
                        card["type"] = "event"
                        self._cards.append(card)
                if "landmarks" in set:
                    for card in set["landmarks"]:
                        card["set"] = set["name"]
                        card["type"] = "landmark"
                        self._cards.append(card)
                if "projects" in set:
                    for card in set["projects"]:
                        card["set"] = set["name"]
                        card["type"] = "project"
                        self._cards.append(card)
                if "boons" in set:
                    for card in set["boons"]:
                        card["set"] = set["name"]
                        card["type"] = "boon"
                        self._boons.append(card)
                if "hexes" in set:
                    for card in set["hexes"]:
                        card["set"] = set["name"]
                        card["type"] = "hexes"
                        self._hexes.append(card)
            except yaml.YAMLError as exc:
                print(exc)

    def remove_banned_cards_from_kingdom(self):
        self._cards = [card for card in self._cards if card["name"] != "Black Market"]
        self._cards = [card for card in self._cards if card["name"] != "Possession"]

    # Generates a random dominion kingdom. It has the following keys:
    # normal_cards: The normal set of 10 kingdom cards.
    # sideways_cards: The landmarks, events, and projects.
    # bane: If young witch is present, a bane card is added to the kingdom.
    # should_include_potion: Whether or not the kingdom requires a potion.
    # should_include_platinum_and_colony: Whether or not to include platinum and colony.
    # should_include_shelters: Whether or not to use shelters instead of estates.
    # boons: If Druid is in the game, these are the boons to use for it.
    # TODO: Skips Stash, Pearl Diver, and Secret Passage because they're unimplemented in the front end.
    def generate_random_kingdom(self):
        normal_cards = []
        sideways_cards = []
        bane = None

        boons = random.sample(self._boons, len(self._boons))[:3]

        shuffled_kingdom_cards = random.sample( self._cards, len(self._cards))
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
        ret["should_include_platinum_and_colony"] = Dominion.should_add_platinum_and_colony(normal_cards)
        ret["should_include_shelters"] = Dominion.should_add_shelters(normal_cards)
        if not Dominion.should_include_boons(normal_cards):
            boons = []
        ret["boons"] = boons
        return ret

    def generate_random_kingdom_for_online_game(self):
        random_cards = self.generate_random_kingdom()
        normal_cards = random_cards["normal_cards"].copy()
        normal_cards.sort(key=lambda card: card["cost"]["treasure"])
        if len(normal_cards) != 10:
            raise Exception("Expected 10 normal cards per kingdom")

        sideways_cards = random_cards["sideways_cards"].copy()
        sideways_cards.sort(key=lambda card: card["cost"]["treasure"])
        all_cards = normal_cards.copy()
        bane = None
        if random_cards["bane"]:
            all_cards += [random_cards["bane"]]
            bane = random_cards["bane"]

        ret = {}
        ret[Dominion.KINGDOM_CARDS] = [] # A nested array
        ret[Dominion.NON_SUPPLY_CARDS] = [] # A nested array
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
            if card_name == "Cemetary":
                has_ghost = True
            if card_name in ["Secret Cave", "Leprechaun"]:
                has_wishes = True
            if card_name == "Secret Cave":
                has_magic_lamp = True
            if card_name == "Cemetary":
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

        if has_boons:
            has_will_o_wisp = True

        if has_page_line:
            Dominion.add_page_line(ret)

        if has_peasant_line:
            Dominion.add_peasant_line(ret)

        if has_madman:
            Dominion.add_madman(ret)

        if has_prizes:
            Dominion.add_prizes(ret)

        if has_mercenary:
            Dominion.add_mercenary(ret)

        if has_bat:
            Dominion.add_bat(ret)

        if has_zombies:
            Dominion.add_zombies(ret)

        if has_boons:
            self.add_boons(ret)

        if has_hexes:
            self.add_hexes(ret)

        if has_spoils:
            Dominion.add_spoils(ret)

        if has_curses:
            Dominion.add_curses(ret)

        if has_imp:
            Dominion.add_imp(ret)

        if has_will_o_wisp:
            Dominion.add_will_o_wisp(ret)

        if has_ghost:
            Dominion.add_ghost(ret)

        if has_wishes:
            Dominion.add_wishes(ret)

        if has_ruins:
            Dominion.add_ruins(ret)

        if has_potion:
            Dominion.add_potion(ret)

        Dominion.add_vp_cards(ret, has_platinum_and_colony)
        Dominion.add_treasure_cards(ret, has_platinum_and_colony)
        Dominion.generate_player_cards(
            ret[Dominion.PLAYER_1_DECK], has_magic_lamp, has_haunted_mirror, has_goat,
            has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)
        Dominion.generate_player_cards(
            ret[Dominion.PLAYER_2_DECK], has_magic_lamp, has_haunted_mirror, has_goat,
            has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters)

        for card in normal_cards:
            ret[Dominion.KINGDOM_CARDS].append(Dominion.generate_pile(card))

        if bane:
            ret[Dominion.BANE] = Dominion.generate_pile(bane)

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
        for pile_type in [Dominion.PLAYER_1_DECK, Dominion.PLAYER_2_DECK]:
            for card in card_map[pile_type]:
                if card["name"] == "Copper":
                    card["pile_type"] = Dominion.TREASURE_CARDS
                    card["pile_index"] = copper_pile_index
                elif card["name"] == "Estate":
                    card["pile_type"] = Dominion.VP_CARDS
                    card["pile_index"] = estate_pile_index

    @staticmethod
    def add_treasure_cards(card_map, has_platinum_and_colony):
        if has_platinum_and_colony:
            card_map[Dominion.TREASURE_CARDS].append(Dominion.create_n_copies({
                "name": "Platinum",
                "cost": { "treasure": 9 },
                "set": "Prosperity",
                "type": "card"
            }, 12))
        card_map[Dominion.TREASURE_CARDS].append(Dominion.create_n_copies({
            "name": "Gold",
            "cost": { "treasure": 6 },
            "set": "Common",
            "type": "card"
        }, 30))
        card_map[Dominion.TREASURE_CARDS].append(Dominion.create_n_copies({
            "name": "Silver",
            "cost": { "treasure": 3 },
            "set": "Common",
            "type": "card"
        }, 40))
        card_map[Dominion.TREASURE_CARDS].append(Dominion.create_n_copies({
            "name": "Copper",
            "cost": { "treasure": 0 },
            "set": "Common",
            "type": "card"
        }, 46))

    @staticmethod
    def add_vp_cards(card_map, has_platinum_and_colony):
        if has_platinum_and_colony:
            card_map[Dominion.VP_CARDS].append(Dominion.create_n_copies({
                "name": "Colony",
                "cost": { "treasure": 11 },
                "set": "Prosperity",
                "type": "card"
            }, 8))
        card_map[Dominion.VP_CARDS].append(Dominion.create_n_copies({
            "name": "Province",
            "cost": { "treasure": 8 },
            "set": "Common",
            "type": "card"
        }, 8))
        card_map[Dominion.VP_CARDS].append(Dominion.create_n_copies({
            "name": "Duchy",
            "cost": { "treasure": 5 },
            "set": "Common",
            "type": "card"
        }, 8))
        card_map[Dominion.VP_CARDS].append(Dominion.create_n_copies({
            "name": "Estate",
            "cost": { "treasure": 2 },
            "set": "Common",
            "type": "card"
        }, 8))

    @staticmethod
    def generate_pile(card):
        card_name = card["name"]

        ret = []
        if card_name == "Encampment / Plunder":
            ret += Dominion.create_n_copies({
                "name": "Plunder",
                "cost": { "treasure": 5 },
                "set": "Empires",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Encampment",
                "cost": { "treasure": 2 },
                "set": "Empires",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Patrician / Emporium":
            ret += Dominion.create_n_copies({
                "name": "Emporium",
                "cost": { "treasure": 5 },
                "set": "Empires",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Patrician",
                "cost": { "treasure": 2 },
                "set": "Empires",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Settlers / Bustling Village":
            ret += Dominion.create_n_copies({
                "name": "Bustling Village",
                "cost": { "treasure": 5 },
                "set": "Empires",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Settlers",
                "cost": { "treasure": 2 },
                "set": "Empires",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Catapult / Rocks":
            ret += Dominion.create_n_copies({
                "name": "Rocks",
                "cost": { "treasure": 4 },
                "set": "Empires",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Catapult",
                "cost": { "treasure": 3 },
                "set": "Empires",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Gladiator / Fortune":
            ret += Dominion.create_n_copies({
                "name": "Fortune",
                "cost": { "treasure": 8 },
                "set": "Empires",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Gladiator",
                "cost": { "treasure": 3 },
                "set": "Empires",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Sauna / Avanto":
            ret += Dominion.create_n_copies({
                "name": "Avanto",
                "cost": { "treasure": 5 },
                "set": "Promos",
                "type": "card"
            }, 5)
            ret += Dominion.create_n_copies({
                "name": "Sauna",
                "cost": { "treasure": 4 },
                "set": "Promos",
                "type": "card"
            }, 5)
            return ret
        if card_name == "Knights":
            ret.append({
                "name": "Dame Anna",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Dame Josephine",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Dame Molly",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Dame Natalie",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Dame Sylvia",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Sir Bailey",
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Sir Destry",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Sir Martin",
                "cost": { "treasure": 4 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Sir Michael",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            ret.append({
                "name": "Sir Vander",
                "cost": { "treasure": 5 },
                "set": "Dark Ages",
                "type": "card"
            })
            random.shuffle(ret)
            return ret
        if card_name == "Castles":
            ret.append({
                "name": "King's Castle",
                "cost": { "treasure": 10 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Grand Castle",
                "cost": { "treasure": 9 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Sprawling Castle",
                "cost": { "treasure": 8 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Opulent Castle",
                "cost": { "treasure": 7 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Haunted Castle",
                "cost": { "treasure": 6 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Small Castle",
                "cost": { "treasure": 5 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Crumbling Castle",
                "cost": { "treasure": 4 },
                "set": "Empires",
                "type": "card"
            })
            ret.append({
                "name": "Humble Castle",
                "cost": { "treasure": 3 },
                "set": "Empires",
                "type": "card"
            })
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

    @staticmethod
    def add_page_line(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Treasure Hunter",
            "cost": { "treasure": 3 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Warrior",
            "cost": { "treasure": 4 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Hero",
            "cost": { "treasure": 5 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Champion",
            "cost": { "treasure": 6 },
            "set": "Adventures",
            "type": "card"
        }, 5))

    @staticmethod
    def add_peasant_line(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Soldier",
            "cost": { "treasure": 3 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Fugitive",
            "cost": { "treasure": 4 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Disciple",
            "cost": { "treasure": 5 },
            "set": "Adventures",
            "type": "card"
        }, 5))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Teacher",
            "cost": { "treasure": 6 },
            "set": "Adventures",
            "type": "card"
        }, 5))

    @staticmethod
    def add_madman(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Madman",
            "cost": { "treasure": 0 },
            "set": "Adventures",
            "type": "card"
        }, 10))

    @staticmethod
    def add_prizes(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Trusty Steed",
            "cost": { "treasure": 0 },
            "set": "Cornucopia",
            "type": "card"
        }, 1))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Followers",
            "cost": { "treasure": 0 },
            "set": "Cornucopia",
            "type": "card"
        }, 1))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Diadem",
            "cost": { "treasure": 0 },
            "set": "Cornucopia",
            "type": "card"
        }, 1))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Princess",
            "cost": { "treasure": 0 },
            "set": "Cornucopia",
            "type": "card"
        }, 1))
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Bag of Gold",
            "cost": { "treasure": 0 },
            "set": "Cornucopia",
            "type": "card"
        }, 1))

    @staticmethod
    def add_mercenary(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Mercenary",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10))

    @staticmethod
    def add_potion(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Potion",
            "cost": { "treasure": 4 },
            "set": "Alchemy",
            "type": "card"
        }, 16))

    @staticmethod
    def add_bat(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Bat",
            "cost": { "treasure": 2 },
            "set": "Nocturne",
            "type": "card"
        }, 10))

    @staticmethod
    def add_zombies(card_map):
        card_map[Dominion.TRASH].append({
            "name": "Zombie Apprentice",
            "cost": { "treasure": 3 },
            "set": "Nocturne",
            "type": "card"
        })
        card_map[Dominion.TRASH].append({
            "name": "Zombie Spy",
            "cost": { "treasure": 3 },
            "set": "Nocturne",
            "type": "card"
        })
        card_map[Dominion.TRASH].append({
            "name": "Zombie Mason",
            "cost": { "treasure": 3 },
            "set": "Nocturne",
            "type": "card"
        })

    def add_boons(self, card_map):
        card_map[Dominion.BOONS] = random.sample( self._boons, len(self._boons))

    def add_hexes(self, card_map):
        card_map[Dominion.HEXES] = random.sample( self._hexes, len(self._hexes))

    @staticmethod
    def add_spoils(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Spoils",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 15))

    @staticmethod
    def add_curses(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Curse",
            "cost": { "treasure": 0 },
            "set": "Common",
            "type": "card"
        }, 10))

    @staticmethod
    def add_imp(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Imp",
            "cost": { "treasure": 2 },
            "set": "Nocturne",
            "type": "card"
        }, 13))

    @staticmethod
    def add_will_o_wisp(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Will-o'-Wisp",
            "cost": { "treasure": 0 },
            "set": "Nocturne",
            "type": "card"
        }, 12))

    @staticmethod
    def add_ghost(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Ghost",
            "cost": { "treasure": 4 },
            "set": "Nocturne",
            "type": "card"
        }, 6))

    @staticmethod
    def add_wishes(card_map):
        card_map[Dominion.NON_SUPPLY_CARDS].append(Dominion.create_n_copies({
            "name": "Wish",
            "cost": { "treasure": 0 },
            "set": "Nocturne",
            "type": "card"
        }, 12))

    @staticmethod
    def generate_player_cards(player_deck, has_magic_lamp, has_haunted_mirror, has_goat,
            has_pasture, has_pouch, has_cursed_gold, has_lucky_coin, has_shelters):
        copper = {
            "name": "Copper",
            "cost": { "treasure": 0 },
            "set": "Common",
            "type": "card"
        }
        if has_magic_lamp:
            player_deck.append({
                "name": "Magic Lamp",
                "cost": { "treasure": 0 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_haunted_mirror:
            player_deck.append({
                "name": "Haunted Mirror",
                "cost": { "treasure": 0 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_goat:
            player_deck.append({
                "name": "Goat",
                "cost": { "treasure": 2 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_pasture:
            player_deck.append({
                "name": "Pasture",
                "cost": { "treasure": 2 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_pouch:
            player_deck.append({
                "name": "Pouch",
                "cost": { "treasure": 2 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_cursed_gold:
            player_deck.append({
                "name": "Cursed Gold",
                "cost": { "treasure": 4 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_lucky_coin:
            player_deck.append({
                "name": "Lucky Coin",
                "cost": { "treasure": 4 },
                "set": "Nocturne",
                "type": "card"
            })
        else:
            player_deck.append(copper)

        if has_shelters:
            player_deck.append({
                "name": "Necropolis",
                "cost": { "treasure": 1 },
                "set": "Dark Ages",
                "type": "card"
            })
            player_deck.append({
                "name": "Overgrown Estate",
                "cost": { "treasure": 1 },
                "set": "Dark Ages",
                "type": "card"
            })
            player_deck.append({
                "name": "Hovel",
                "cost": { "treasure": 1 },
                "set": "Dark Ages",
                "type": "card"
            })
        else:
            estate = {
                "name": "Estate",
                "cost": { "treasure": 2 },
                "set": "Common",
                "type": "card"
            }
            player_deck.append(estate)
            player_deck.append(estate)
            player_deck.append(estate)
        random.shuffle(player_deck)

    @staticmethod
    def add_ruins(card_map):
        ruins = []
        ruins += Dominion.create_n_copies({
            "name": "Abandoned Mine",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10)
        ruins += Dominion.create_n_copies({
            "name": "Ruined Library",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10)
        ruins += Dominion.create_n_copies({
            "name": "Ruined Market",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10)
        ruins += Dominion.create_n_copies({
            "name": "Ruined Village",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10)
        ruins += Dominion.create_n_copies({
            "name": "Survivors",
            "cost": { "treasure": 0 },
            "set": "Dark Ages",
            "type": "card"
        }, 10)
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
        first_set = cards[0]["set"]
        if first_set == "Prosperity" or first_set == "Empires" or first_set == "Cornucopia":
            return True
        return False

    @staticmethod
    def should_add_shelters(cards):
        if cards[1]["set"] == "Dark Ages":
            return True
        return False

    @staticmethod
    def should_include_boons(cards):
        for card in cards:
            if card["name"] == "Druid":
                return True
        return False

    # Returns both players in the game as a list with the order: [player1, player2].
    def get_players_in_game(self, game_id) -> List[str]:
        cur = self._dominion_database.get_cursor()

        try:
            game = DominionDatabase.get_game(cur, game_id)
            cur.close()
        except psycopg2.Error:
            self._dominion_database.rollback()
            cur.close()
            raise

        if game is None:
            return None
        return [game[DominionDatabase.DOMINION_GAMES_PLAYER1], game[DominionDatabase.DOMINION_GAMES_PLAYER2]]

    def create_game(self, player1, player2) -> int:
        game_data = self.generate_random_kingdom_for_online_game()

        data = {}
        data["playerOrder"] = [player1, player2]
        data["currentPlayerTurn"] = 0
        data["revealArea"] = []
        data["isInGame"] = True
        data["players"] = [{
            "name": player1,
            "notes": '',
            "playArea": [],
            "deck": game_data["player_1_deck"],
            "hand": [],
            "mats": [],
            "discard": [],
            "numActions": 1,
            "numBuys": 1,
            "numCoins": 0,
            "numVP": 0,
            "numCoffers": 0,
            "numVillagers": 0,
            "numDebt": 0,
            "shownPage": 'kingdom'
        }, {
            "name": player2,
            "notes": '',
            "playArea": [],
            "deck": game_data["player_2_deck"],
            "hand": [],
            "mats": [],
            "discard": [],
            "numActions": 1,
            "numBuys": 1,
            "numCoins": 0,
            "numVP": 0,
            "numCoffers": 0,
            "numVillagers": 0,
            "numDebt": 0,
            "shownPage": 'kingdom'
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
