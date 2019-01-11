<template>
  <div class="lotr-game">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="card-games-new-game">
      <span class="card-games-text-on-background">Invite:</span> <input v-model="playerToInvite" class="card-games-player-to-invite"/>
      <span class="card-games-text-on-background">Scenario:</span> <select v-model="scenarioName">
                  <option v-for="scenario in scenarioList" :key="scenario">
                    {{ scenario }}
                  </option>
                </select>
      <span class="card-games-text-on-background">Your Deck:</span> <textarea v-model="player1DeckXml"/>
      <span class="card-games-text-on-background">Partner's Deck:</span> <textarea v-model="player2DeckXml"/>
      <button v-on:click="newGame">New Game</button>
    </div>
    <div v-if="isInGame">
      <button @click="shownPage = 'main'">Main</button>
      <button @click="shownPage = 'quest'">Quest</button>
      <button v-if="game['hasSetup']" @click="shownPage = 'setup'">Setup</button>
      <button v-if="game['revealArea'].length > 0" @click="shownPage = 'revealArea'"><u>R</u>evealed</button>
      <button v-if="game['hasSecondQuest']" @click="shownPage = 'secondQuest'">Second Quest</button>
      <button @click="shownPage = 'encounterDiscard'">Encounter Discard</button>
      <button @click="shownPage = 'victory'">Victory</button>
      <button @click="shownPage = 'secondDeck'">Second Deck</button>
      <button v-if="game['hasSpecial']" @click="shownPage = 'special'">Special</button>
      <button v-if="game['hasSecondSpecial']" @click="shownPage = 'secondSpecial'">Second Special</button>
      <button @click="shownPage = 'discard'">Your <u>D</u>iscard</button>
      <button @click="shownPage = 'trash'"><u>T</u>rash</button>
      <button @click="shownPage = 'notes'">Notes</button>
      <button @click="shownPage = 'shortcuts'">Shortcuts</button>
      <img
          v-if="games_currentCardSelection['exists']"
          :class="getPreviewClassName()"
          :src="getImageForCurrentCardLotr()"/>
      <div class="lotr-cards-area-above-hand">
        <div v-if="shownPage === 'main'">
          <div class="lotr-staging-area">
            <span class="card-games-text-on-background">Staging Area</span>
            <div class="lotr-single-cards-row">
              <LotrCardList
                  :cardArray="game['stagingArea']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-active-location">
            <span class="card-games-text-on-background">Location</span>
            <div class="lotr-single-cards-row">
              <LotrCardList
                  :cardArray="game['activeLocation']"
                  :defaultMoveArray="game['encounterDiscard']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-quest">
            <span class="card-games-text-on-background">Quest</span>
            <div class="lotr-single-cards-row">
              <LotrCardList
                :cardArray="game['questReveal']"
                :defaultMoveArray="game['questDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="sidewaysCardWidth"
                :cardMargin="cardMargin"
                :getImageForCard="getImageForCard" />
              </div>
          </div>
          <div class="lotr-encounter">
            <span class="card-games-text-on-background">Encounter</span>
            <div class="lotr-single-cards-row">
              <CardStack
                :cardArray="game['encounterDeck']"
                :defaultMoveArray="game['stagingArea']"
                :reshuffleArray="game['encounterDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="cardWidth"
                :cardMargin="cardMargin"
                :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="clearfix"/>
          <div class="lotr-player-play-area">
            <div>
              <span class="card-games-text-on-background">Your Engaged Enemies</span>
              <div class="lotr-engaged-enemies">
                <LotrCardList
                    :cardArray="player['engagedEnemies']"
                    :defaultMoveArray="game['encounterDiscard']"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
            <div>
              <span class="card-games-text-on-background">Your Characters</span>
              <div class="lotr-characters">
                <LotrCardList
                    :cardArray="player['characters']"
                    :defaultMoveArray="player['discard']"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
          </div>
          <div class="lotr-played">
            <span class="card-games-text-on-background">Played Cards</span>
            <div class="lotr-played-cards-area">
              <LotrCardList
                  :cardArray="game['playedCards']"
                  :defaultMoveArray="player['discard']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-player-play-area">
            <div>
              <span class="card-games-text-on-background">{{partner['name']}}'s Engaged Enemies</span>
              <div class="lotr-engaged-enemies">
                <LotrCardList
                    :cardArray="partner['engagedEnemies']"
                    :defaultMoveArray="game['encounterDiscard']"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
            <div>
              <span class="card-games-text-on-background">{{partner['name']}}'s Characters</span>
              <div class="lotr-characters">
                <LotrCardList
                    :cardArray="partner['characters']"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="shownPage === 'quest'">
          <div class="lotr-quest-deck-and-discard">
            <CardStack
              :cardArray="game['questDeck']"
              :defaultMoveArray="game['questReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <CardStack
              :cardArray="game['questDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <CardList
              :cardArray="game['questReveal']"
              :defaultMoveArray="game['questDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondQuest'">
          <div class="lotr-quest-deck-and-discard">
            <CardStack
              :cardArray="game['secondQuestDeck']"
              :defaultMoveArray="game['secondQuestReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <CardStack
              :cardArray="game['secondQuestDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <CardList
              :cardArray="game['secondQuestReveal']"
              :defaultMoveArray="game['secondQuestDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondDeck'">
          <div class="lotr-deck-and-discard">
            <CardStack
              :cardArray="game['secondDeck']"
              :defaultMoveArray="game['secondReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <CardStack
              :cardArray="game['secondDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <CardList
              :cardArray="game['secondReveal']"
              :defaultMoveArray="game['secondDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <CardList
            v-else-if="shownPage === 'setup'"
            :cardArray="game['setupArea']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'revealArea'"
            :cardArray="game['revealArea']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'encounterDiscard'"
            :cardArray="game['encounterDiscard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'victory'"
            :cardArray="game['victory']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <div v-else-if="shownPage === 'special'">
          <div class="lotr-deck-and-discard">
            <CardStack
              :cardArray="game['specialDeck']"
              :defaultMoveArray="game['specialReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <CardStack
              :cardArray="game['specialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <CardList
              :cardArray="game['specialReveal']"
              :defaultMoveArray="game['specialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondSpecial'">
          <div class="lotr-deck-and-discard">
            <CardStack
              :cardArray="game['secondSpecialDeck']"
              :defaultMoveArray="game['secondSpecialReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <CardStack
              :cardArray="game['secondSpecialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <CardList
              :cardArray="game['secondSpecialReveal']"
              :defaultMoveArray="game['secondSpecialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <CardList
            v-else-if="shownPage === 'trash'"
            :cardArray="game['trash']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'discard'"
            :cardArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <textarea v-else-if="shownPage === 'notes'" class="lotr-note" v-model="notes"></textarea>
        <div v-else-if="shownPage === 'shortcuts'" class="card-games-text-on-background">
          a (A) - Increment num actions (Decrement num actions)<br/>
          b (B) - Increment num buys (Decrement num buys)<br/>
          c (C) - Increment num coins (Decrement num coins)<br/>
          d - Discard the card.<br/>
          D - Discard all cards in your hand and play area and end the turn.<br/>
          e - End the turn.
          h - Draw the card into your hand.<br/>
          H - Draw 5 new cards into your hand.<br/>
          k - Topdeck the card onto your deck.<br/>
          m - Move the card to your mat.<br/>
          o - Move the card to your opponent's hand.<br/>
          P - Play all cards in your hand.<br/>
          p - Play the card to your play area.<br/>
          r - Return the card to its original pile.<br/>
          s - Shuffle your deck.<br/><br/>
          t - Trash the card.<br/>
          w - Draw a single card from deck into your hand.<br/>
          v - Reveal the card in the revealed area.<br/>
        </div>
      </div>
      <div class="clearfix"/>
      <div class="lotr-player-area">
        <div class="card-games-stats-line">
          <span class="card-games-stat-item card-games-text-on-background">Threat Points: <button @click="decrementThreat">-</button><input class="card-games-counter" v-model="player['threat']"/><button @click="incrementThreat">+</button></span>
          <span class="card-games-stat-item card-games-text-on-background">Partner Threat Points: {{partner['threat']}}</span>
        </div>
        <div class="lotr-deck-and-hand">
          <div class="lotr-single-pile">
            <span class="card-games-text-on-background">Dec<u>k</u></span>
            <div class="lotr-single-pile-cards">
              <CardStack
                  :cardArray="player['deck']"
                  :defaultMoveArray="player['hand']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="lotr-single-pile">
            <span class="card-games-text-on-background"><u>D</u>iscard</span>
            <div class="lotr-single-pile-cards">
              <CardStack
                  :cardArray="player['discard']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="lotr-hand-area">
            <span class="card-games-text-on-background">Your <u>H</u>and</span>
            <div class="lotr-hand-cards-area">
              <LotrCardList
                  :cardArray="player['hand']"
                  :defaultMoveArray="game['playedCards']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="clearfix"/>
  </div>
</template>
<style>
  @import "../assets/style/card-games.css"
</style>
<style>
  @import "../assets/style/lotr-game.css"
</style>
<script>

import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import LotrCardList from './shared/games/LotrCardList'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { shuffle, getFullBackendUrlForPath, findPath, fetchFromPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'
import { moveCard, moveAllCards, moveCurrentCard, setCurrentCard,
  defaultPlayerToInvite, getImageForCard, getImageForCurrentCard,
  getCurrentCard, getImageForCardArray } from '../common/card_games'

const CREATE_LOTR_GAME_URL = getFullBackendUrlForPath('/create_lotr_game')
const LOTR_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/lotr_get_latest_game')
const LOTR_GET_SCENARIO_NAMES_URL = getFullBackendUrlForPath('/lotr_get_scenario_names')
const SAVE_LOTR_GAME_URL = getFullBackendUrlForPath('/save_lotr_game')

export default {
  name: 'LotrGame',
  components: { ButterBar, CardStack, CardList, LotrCardList },
  computed: { username () { return store.state.username } },
  watch: {
    username () { this.updateDisplayWithLatestGame() },
    game: {
      handler (val) {
        if (this.shouldSaveChanges) {
          this.saveGame()
        } else {
          this.shouldSaveChanges = true
        }
      },
      deep: true
    }
  },
  created () {
    var style = getComputedStyle(document.body)
    this.cardHeight = style.getPropertyValue('--lotr-card-height')
    this.cardWidth = style.getPropertyValue('--lotr-card-width')
    this.cardMargin = style.getPropertyValue('--card-margin')
    this.sidewaysCardWidth = style.getPropertyValue('--lotr-sideways-card-width')
    this.updateLotrScenarios()
    this.updateDisplayWithLatestGame()
    window.addEventListener('keyup', this.handleKeyPress)
    this.playerToInvite = defaultPlayerToInvite(this.username)
  },
  mounted () {
    socket.on('refresh_lotr', (data) => {
      if (!data['players'].includes(this.username) || data['player_triggering_update'] === this.username) {
        return
      }
      this.updateDisplayWithGameData(data['gameData'])
    })
  },
  data () {
    return {
      /**
       * Needed for butter bar.
       */
      butterBar_message: '',
      /**
       * Needed for butter bar.
       */
      butterBar_css: '',
      /**
       * Needed for card-games.js.
       */
      games_currentCardSelection: {'exists': false},
      /**
       * The name of the player to invite when creating a new game.
       */
      playerToInvite: '',
      /**
       * The deck the current player will use when creating a new game.
       */
      player1DeckXml: '',
      /**
       * The deck the partner player will use when creating a new game.
       */
      player2DeckXml: '',
      /**
       * The list of scenarios to choose from when creating a new game.
       */
      scenarioList: [],
      /**
       * The name of the scenario to create a new game with.
       */
      scenarioName: '',
      /**
       * Whether there is a game to display or not.
       */
      isInGame: false,
      /**
       * The height of a card in the game. Read from the css as a string.
       */
      cardHeight: '',
      /**
       * The width of a card in the game. Read from the css as a string.
       */
      cardWidth: '',
      /**
       * The margin of a card in the game. Read from the css as a string.
       */
      cardMargin: '',
      /**
       * The width of a sideways card in the game. Read from the css as a string.
       */
      sidewaysCardWidth: '',
      /**
       * Whether or not to save watched data changes to the database. Only false if we just received those changes from the server.
       */
      shouldSaveChanges: false,
      /**
       * In-game notes the player can type to themselves.
       */
      notes: '',
      /**
       * Represents the current game page to display.
       */
      shownPage: 'main',
      /**
       * For convenience, this points to the object representing the player within game['players'].
       */
      player: {},
      /**
       * For convenience, this points to the object representing the player's partner within game['players'].
       */
      partner: {},
      /**
       * The index of the player within game['players'].
       */
      playerIndex: 0,
      /**
       * The game object represents all the data needed to render a game. It contains the following nested data:
       * playedCards {array[Card]} the cards played by either player.
       * stagingArea {array[Card]} the staging area.
       * activeLocation {array[Card]} the active location.
       * questReveal {array[Card]} the currently revealed quest. Should only have one card at a time.
       * questDeck {array[Card]} the quest deck.
       * questDiscard {array[Card]} the quest discard pile.
       * revealArea {array[Card]} the cards revealed by either player. Used to store cards temporarily while the
       *     characters look at them and move to another pile.
       * secondQuestDeck {array[Card]} the second quest deck in the game if one is available.
       * secondQuestDiscard {array[Card]} the discard pile for the second quest deck.
       * secondQuestReveal {array[Card]} the reveal pile for the second quest deck.
       * encounterDeck {array[Card]} the encounter deck.
       * encounterDiscard {array[Card]} the discard pile for the encounter deck.
       * victory {array[Card]} the victory pile of cards earned by players.
       * specialDeck {array[Card]} the special deck in the game if one is available.
       * specialDiscard {array[Card]} the discard pile for the special deck.
       * specialReveal {array[Card]} the reveal pile for the special deck.
       * secondSpecialDeck {array[Card]} the second special deck in the game if one is available.
       * secondSpecialDiscard {array[Card]} the discard pile for the second special deck.
       * secondSpecialReveal {array[Card]} the reveal pile for the second special deck.
       * setupArea {array[Card]} the special setup area for the game if one exists.
       * trash {array[Card]} the cards which have been put into the trash for any reason.
       * hasSetup {boolean} whether the game has a setup area or not.
       * hasSecondQuest {boolean} whether the game has a second quest deck or not.
       * hasSpecial {boolean} whether the game has a special deck or not.
       * hasSecondSpecial {boolean} whether the game has a second special deck or not.
       * gameId {number} the database id of the created game.
       * players {array[Player]} the array of the two players in the game.
       *
       * The objects referenced in game are Players and Cards.
       *
       * Player represents a player in the game. It contains the following keys:
       * name {string} the name of the player
       * characters {array[Card]} the characters in the player's play area.
       * deck {array[Card]} the deck of cards of the player.
       * hand {array[Card]} the hand of cards of the player.
       * discard {array[Card]} the discard pile of cards of the player.
       * engagedEnemies {array[Card]} the enemies engaged with the player.
       * secondaryDeck {array[Card]}: the secondary deck of the player if they are using it.
       * secondaryDiscard {array[Card]}: the discard pile of the secondary deck if they are using one.
       * secondaryReveal {array[Card]}: the reveal pile of the secondary deck if they are using one.
       * threat {number}: the current threat of the player.
       *
       * Card represents a card in the game. It contains many keys which can be found in the lotr.py file but
       * the relevant ones are the following:
       * image {string} the url used to render the card.
       * flippedImage {string} the url used to render the flipped side of the card.
       * attachments {array[Card]} the list of cards attached to this card.
       * resources {number} the number of resource tokens on this card.
       * progress {number} the number of progress tokens on this card.
       * damage {number} the number of damage tokens on this card.
       * flipped {boolean} whether the card is flipped or not.
       */
      game: {}
    }
  },
  methods: {
    getImageForCard: getImageForCard,
    getImageForCurrentCardLotr () {
      return getImageForCurrentCard(
        this, {
          '/static/lotr/cards/card.jpg': [this.player['deck'], this.partner['deck']],
          '/static/lotr/cards/encounter.jpg': [this.game['encounterDeck']]
        })
    },
    getImageForCardArrayLotr (cardArray) {
      return getImageForCardArray(cardArray, {
        '/static/lotr/cards/card.jpg': [this.player['deck'], this.partner['deck']],
        '/static/lotr/cards/encounter.jpg': [this.game['encounterDeck']]
      })
    },
    /**
     * Calls the backend to generate a new game with the populated input fields. Updates the game display once it is created.
     */
    newGame () {
      callAxiosAndSetButterBar(
        this,
        CREATE_LOTR_GAME_URL,
        {
          scenario: this.scenarioName,
          player1: this.username,
          player2: this.playerToInvite,
          player1Deck: this.player1DeckXml,
          player2Deck: this.player2DeckXml,
          username: this.username
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        (response) => {
          let data = response.data
          this.updateDisplayWithGameData(data)
        })
    },
    getPreviewClassName () {
      if (!this.games_currentCardSelection['exists']) {
        return ''
      }
      let cardArray = this.games_currentCardSelection['array']
      return (
        cardArray === this.game['questDeck'] ||
        cardArray === this.game['questReveal'] ||
        cardArray === this.game['questDiscard'] ||
        cardArray === this.game['secondQuestDeck'] ||
        cardArray === this.game['secondQuestReveal'] ||
        cardArray === this.game['secondQuestDisard']) ? 'lotr-preview-sideways' : 'lotr-preview-normal'
    },
    saveGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_LOTR_GAME_URL,
        {
          gameId: this.game.gameId,
          gameData: this.game,
          username: this.username
        },
        null,
        'Failed to save lotr game.')
    },
    moveCard: moveCard,
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateDisplayWithLatestGame () {
      callAxiosAndSetButterBar(
        this,
        LOTR_GET_LATEST_GAME_URL,
        { username: this.username },
        null,
        'Failed to save lotr game.',
        (response) => {
          if (response.data === null) {
            this.isInGame = false
            return
          }
          this.updateDisplayWithGameData(response.data.data)
        })
    },
    updateLotrScenarios () {
      callAxiosAndSetButterBar(
        this,
        LOTR_GET_SCENARIO_NAMES_URL,
        {},
        null,
        'Failed to get scenarios.',
        (response) => {
          if (response.data === null) {
            return
          }
          this.scenarioList = response.data
          this.scenarioName = this.scenarioList[0]
        })
    },
    updateDisplayWithGameData (gameData) {
      let currentCardSelectionArrayPath
      if (this.games_currentCardSelection.exists) {
        currentCardSelectionArrayPath = findPath(this.games_currentCardSelection.array, this.game)
      }
      this.shouldSaveChanges = false
      this.isInGame = true
      this.game = gameData
      this.playerIndex = gameData.players[0].name === this.username ? 0 : 1
      this.player = this.game.players[this.playerIndex]
      this.partner = this.game.players[1 - this.playerIndex] // Only supports a 2 player game.

      if (currentCardSelectionArrayPath) {
        setCurrentCard(this, fetchFromPath(this.game, currentCardSelectionArrayPath), this.games_currentCardSelection.index)
      }
    },
    shuffleDeck () {
      shuffle(this.player.deck)
    },
    deckToDiscard () {
      moveAllCards(this.player.deck, this.player.discard)
    },
    singleCardFromDeckToHand () {
      moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
    },
    addResourcesToCurrentCard () {
      this.games_currentCardSelection.array[this.games_currentCardSelection.index]['resources']++
    },
    addProgressToCurrentCard () {
      this.games_currentCardSelection.array[this.games_currentCardSelection.index]['progress']++
    },
    addDamageToCurrentCard () {
      this.games_currentCardSelection.array[this.games_currentCardSelection.index]['damage']++
    },
    flipCurrentCard () {
      let card = getCurrentCard(this)
      if (!card) {
        return
      }
      if (!card.flippedImage) {
        return
      }
      card.flipped = !card.flipped
    },
    incrementThreat () { this.player.threat++ },
    decrementThreat () { this.player.threat-- },
    handleKeyPress (event) {
      if (!this.isInGame) {
        return
      }
      switch (event.key) {
        case 't': this.incrementThreat(); break
        case 'T': this.decrementThreat(); break
        case 'w': this.singleCardFromDeckToHand(); return
      }
      if (!this.games_currentCardSelection.exists) {
        return
      }
      let destinationArray = null
      let reshuffleArray = null
      switch (event.key) {
        case 'r': this.addResourcesToCurrentCard(); return
        case 'd': this.addDamageToCurrentCard(); return
        case 'f': this.flipCurrentCard(); return
        case 'p': this.addProgressToCurrentCard(); return
        case '1': destinationArray = this.player.characters[0]['attachments']; break
        case '2': destinationArray = this.player.characters[1]['attachments']; break
        case '3': destinationArray = this.player.characters[2]['attachments']; break
        case '4': destinationArray = this.player.characters[3]['attachments']; break
        case '5': destinationArray = this.player.characters[4]['attachments']; break
        case 'c': destinationArray = this.player.characters; break
        case 'e': destinationArray = this.player.engagedEnemies; break
        case 'l': destinationArray = this.game.activeLocation; break
        case 'o': destinationArray = this.partner.characters; break
        case 'i': destinationArray = this.player.discard; break
        case 'h': destinationArray = this.player.hand; break
        case 'k': destinationArray = this.player.deck; break
        case 's': this.shuffleDeck(); return
        case 't': destinationArray = this.game.trash; break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck) {
        reshuffleArray = this.player.discard
      }
      moveCurrentCard(this, destinationArray, reshuffleArray)
    }
  }
}
</script>
