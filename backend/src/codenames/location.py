# Each location in codenames has two possible types: one for player 1 and one for player 2.
class Location:
    # These constants correspond to the location type specified in the table codenames_games_to_locations.
    LOCATION_TYPE_AGENT = "agent"
    LOCATION_TYPE_ASSASSIN = "assassin"
    LOCATION_TYPE_BYSTANDER = "bystander"

    def __init__(self, player1_location_type: str, player2_location_type: str):
        self.player1_location_type = player1_location_type
        self.player2_location_type = player2_location_type

    def __str__(self):
        return "{%s, %s}" % (self.player1_location_type, self.player2_location_type)