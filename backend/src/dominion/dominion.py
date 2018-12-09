import yaml
import random
import pprint

class Dominion:
    def __init__(self):
        # Cards includes all cards to select the randomized kingdom from. It includes events and
        # landmarks and does not include cards dependent on others like potion.
        self._cards = []
        self._boons = []
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
        self.generate_random_kingdom()

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
    def generate_random_kingdom(self):
        normal_cards = []
        sideways_cards = []
        bane = None

        boons = random.sample(self._boons, len(self._boons))[:3]

        shuffled_kingdom_cards = random.sample( self._cards, len(self._cards))
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
        ret["should_include_platinum_and_colony"] = Dominion.should_add_platinum_and_colony(normal_cards)
        ret["should_include_shelters"] = Dominion.should_add_shelters(normal_cards)
        if not Dominion.should_include_boons(normal_cards):
            boons = []
        ret["boons"] = boons
        return ret

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
        if cards[0]["set"] == "Prosperity":
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
