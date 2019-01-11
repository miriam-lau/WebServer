<template>
  <div class="dominion-game">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="card-games-new-game">
      Invite:
          <input v-model="playerToInvite" class="card-games-player-to-invite"/>
          <button v-on:click="newGame">New Game</button>
    </div>
    <div v-if="isInGame">
      <button @click="shownPage = 'kingdom'">Kingdom</button>
      <button v-if="game['nonSupplyCards'].length > 0" @click="shownPage = 'nonSupply'">Non Supply</button>
      <button v-if="game['hasBane']" @click="shownPage = 'bane'">Bane</button>
      <button v-if="game['hasBoons']" @click="shownPage = 'boons'">Boons</button>
      <button v-if="game['hasHexes']" @click="shownPage = 'hexes'">Hexes</button>
      <button v-if="player['mats'].length > 0" @click="shownPage = 'yourMats'">Your <u>M</u>ats</button>
      <button @click="shownPage = 'discard'">Your <u>D</u>iscard</button>
      <button v-if="opponent['mats'].length > 0" @click="shownPage = 'opponentMats'">Opponent Mats</button>
      <button v-if="game['revealArea'].length > 0" @click="shownPage = 'revealArea'"><u>R</u>evealed</button>
      <button @click="shownPage = 'trash'"><u>T</u>rash</button>
      <button @click="shownPage = 'notes'">Notes</button>
      <button @click="shownPage = 'allYourCards'">All your cards</button>
      <button @click="shownPage = 'shortcuts'">Shortcuts</button>
      <img
          v-if="games_currentCardSelection['exists']"
          :class="getPreviewClassName()"
          :src="getImageForCurrentCardDominion()"/>
      <div class="dominion-cards-area-above-play-area">
        <div v-if="shownPage === 'kingdom'">
          <div class="dominion-vp-treasure-area">
            <CardStack
              :key="'treasure' + index" v-for="(cardArray, index) in game['treasureCards']"
              :cardArray="cardArray"
              :defaultMoveArray="player['discard']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :callback="addGainToLog"
              :getImageForCardArray="getImageForCardArrayDominion" />
            <div class="clearfix"/>
            <CardStack
              :key="'vp' + index" v-for="(cardArray, index) in game['vpCards']"
              :cardArray="cardArray"
              :defaultMoveArray="player['discard']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :callback="addGainToLog"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <div class="dominion-kingdom-area">
            <CardStack
              :key="index" v-for="(cardArray, index) in game['kingdomCards']"
              :cardArray="cardArray"
              :defaultMoveArray="player['discard']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :callback="addGainToLog"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <div class="dominion-events-area">
            <CardList
                :cardArray="game['sidewaysCards']"
                :cardHeight="cardHeight"
                :cardWidth="sidewaysCardWidth"
                :cardMargin="cardMargin"
                :getImageForCard="getImageForCard" />
          </div>
        </div>
        <CardStack
            v-else-if="shownPage === 'nonSupply'"
            :key="index" v-for="(cardArray, index) in game['nonSupplyCards']"
            :cardArray="cardArray"
            :defaultMoveArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :callback="addGainToLog"
            :getImageForCardArray="getImageForCardArrayDominion" />
        <CardStack
            v-else-if="shownPage === 'bane'"
            :cardArray="game['bane']"
            :defaultMoveArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :callback="addGainToLog"
            :getImageForCardArray="getImageForCardArrayDominion" />
        <CardList
            v-else-if="shownPage === 'yourMats'"
            :cardArray="player['mats']"
            :defaultMoveArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'opponentMats'"
            :cardArray="opponent['mats']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'trash'"
            :cardArray="game['trash']"
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
            v-else-if="shownPage === 'discard'"
            :cardArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <CardList
            v-else-if="shownPage === 'allYourCards'"
            :cardArray="getAllPlayerCards()"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :shouldNotPopulateCurrentCard="true"
            :getImageForCard="getImageForCard" />
        <textarea v-else-if="shownPage === 'notes'" class="card-games-note" v-model="notes"></textarea>
        <div v-else-if="shownPage === 'shortcuts'" class="card-games-text">
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
        <div v-else-if="shownPage === 'boons'">
          <div class="dominion-boons-and-hexes-deck-and-discard">
            <CardStack
              :cardArray="game['boonsDeck']"
              :defaultMoveArray="game['boonsReveal']"
              :reshuffleArray="game['boonsDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
            <CardStack
              :cardArray="game['boonsDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <CardList
              :cardArray="game['boonsReveal']"
              :defaultMoveArray="game['boonsDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'hexes'">
          <div class="dominion-boons-and-hexes-deck-and-discard">
            <CardStack
              :cardArray="game['hexesDeck']"
              :defaultMoveArray="game['hexesReveal']"
              :reshuffleArray="game['hexesDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
            <CardStack
              :cardArray="game['hexesDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <CardList
              :cardArray="game['hexesReveal']"
              :defaultMoveArray="game['hexesDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
      </div>
      <div class="clearfix"/>
      <span v-if="isPlayerDisplayed()" class="card-games-text">Your display</span>
      <span v-else class="card-games-text">{{game['players'][player['displayedPlayer']]['name']}}'s display</span>
      <button @click="toggledisplayedPlayer">Toggle</button>
      <br/>
      <div class="dominion-game-log">
        <div>
          <div :key="index" v-for="(gameLogLine, index) in game['gameLog']" class="card-games-text">
            {{gameLogLine}}<br/>
          </div>
        </div>
      </div>
      <div class="dominion-player-area">
        <div class="dominion-play-area">
          <span class="card-games-text"><u>P</u>layed Cards</span>
          <div class="dominion-play-cards-area">
            <div v-if="isPlayerDisplayed()">
              <CardList
                  :cardArray="player['playArea']"
                  :defaultMoveArray="player.discard"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
            <div v-else>
              <CardList
                  :cardArray="opponent.playArea"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
        </div>
        <div class="dominion-duration-area">
          <span class="card-games-text">D<u>u</u>ration</span>
          <div class="dominion-duration-cards-area">
            <div v-if="isPlayerDisplayed()">
              <CardList
                  :cardArray="player['durationArea']"
                  :defaultMoveArray="player['discard']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
            <div v-else>
              <CardList
                  :cardArray="opponent['durationArea']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
        </div>
        <div class="clearfix"/>
        <div class="card-games-stats-line card-games-text">
          <div v-if="isPlayerDisplayed()">
            <span class="card-games-stat-item"><u>A</u>ctions: <button @click="decrementNumActions">-</button><input class="card-games-counter" v-model="player['numActions']"/><button @click="incrementNumActions">+</button></span>
            <span class="card-games-stat-item"><u>B</u>uys: <button @click="decrementNumBuys">-</button><input class="card-games-counter" v-model="player['numBuys']"/><button @click="incrementNumBuys">+</button></span>
            <span class="card-games-stat-item"><u>C</u>oins: <button @click="decrementNumCoins">-</button><input class="card-games-counter" v-model="player['numCoins']"/><button @click="incrementNumCoins">+</button></span>
            <span class="card-games-stat-item">VP: <button @click="decrementNumVP">-</button><input class="card-games-counter" v-model="player['numVP']"/><button @click="incrementNumVP">+</button></span>
            <span class="card-games-stat-item">Coffers: <button @click="decrementNumCoffers">-</button><input class="card-games-counter" v-model="player['numCoffers']"/><button @click="incrementNumCoffers">+</button></span>
            <span class="card-games-stat-item">Villagers: <button @click="decrementNumVillagers">-</button><input class="card-games-counter" v-model="player['numVillagers']"/><button @click="incrementNumVillagers">+</button></span>
            <span class="card-games-stat-item">Debt: <button @click="decrementNumDebt">-</button><input class="card-games-counter" v-model="player['numDebt']"/><button @click="incrementNumDebt">+</button></span>
            <span>Your turn</span>
          </div>
          <div v-else>
            <span class="card-games-stat-item">Actions: {{opponent['numActions']}}</span>
            <span class="card-games-stat-item">Buys: {{opponent['numBuys']}}</span>
            <span class="card-games-stat-item">Coins: {{opponent['numCoins']}}</span>
            <span class="card-games-stat-item">VP: {{opponent['numVP']}}</span>
            <span class="card-games-stat-item">Coffers: {{opponent['numCoffers']}}</span>
            <span class="card-games-stat-item">Villagers: {{opponent['numVillagers']}}</span>
            <span class="card-games-stat-item">Debt: {{opponent['numDebt']}}</span>
            <span>{{opponent['name']}}'s turn</span>
          </div>
        </div>
        <div class="dominion-deck-and-hand">
          <div class="dominion-single-pile">
            <span class="card-games-text">Dec<u>k</u><br/></span>
            <CardStack
              v-if="isPlayerDisplayed()"
              :reshuffleArray="player['discard']"
              :defaultMoveArray="player['hand']"
              :cardArray="player['deck']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
            <CardStack
              v-else
              :cardArray="opponent['deck']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <div class="dominion-single-pile">
            <span class="card-games-text"><u>D</u>iscard<br/></span>
            <CardStack
              v-if="isPlayerDisplayed()"
              :cardArray="player['discard']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
            <CardStack
              v-else
              :cardArray="opponent['discard']"
              :cardHeight="cardHeight"
              :cardWidth="cardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayDominion" />
          </div>
          <div class="dominion-hand-area">
            <span class="card-games-text">Your <u>H</u>and</span>
            <div class="dominion-hand-cards-area">
              <CardList
                  :defaultMoveArray="player['playArea']"
                  :cardArray="player['hand']"
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
  @import "../assets/style/dominion-game.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { shuffle, getFullBackendUrlForPath, findPath, fetchFromPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'
import { moveCard, moveAllCards, moveCurrentCard, setCurrentCard,
  clearCurrentCard, defaultPlayerToInvite, getImageForCard, getImageForCurrentCard,
  getCurrentCard, getImageForCardArray }
  from '../common/card_games'

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const SAVE_DOMINION_GAME_URL = getFullBackendUrlForPath('/save_dominion_game')

export default {
  name: 'DominionGame',
  components: { ButterBar, CardStack, CardList },
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
    this.cardHeight = style.getPropertyValue('--dominion-card-height')
    this.cardWidth = style.getPropertyValue('--dominion-card-width')
    this.cardMargin = style.getPropertyValue('--card-margin')
    this.sidewaysCardWidth = style.getPropertyValue('--dominion-sideways-card-width')
    this.updateDisplayWithLatestGame()
    window.addEventListener('keyup', this.handleKeyPress)
    this.playerToInvite = defaultPlayerToInvite(this.username)
  },
  mounted () {
    socket.on('refresh_dominion', (data) => {
      if (!data['players'].includes(this.username) || data['player_triggering_update'] === this.username) {
        return
      }
      this.updateDisplayWithReceivedGameData(data['gameData'])
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
      shownPage: 'kingdom',
      /**
       * For convenience, this points to the object representing the player within game['players'].
       */
      player: {},
      /**
       * For convenience, this points to the object representing the opponent within game['players'].
       */
      opponent: {},
      /**
       * The index of the player within game['players'].
       */
      playerIndex: 0,
      /**
       * The game object represents all the data needed to render a game. It contains the following nested data:
       * playerOrder {array[Player]} the players in the game in order.
       * currentPlayerTurn {number} the index of the player who has the current turn.
       * revealArea {array[Card]} the card which have been revealed by either player.
       * gameLog {array[String]} the game log.
       * boonsDiscard {array[Card]} if boons are in the game, the discard pile of boons.
       * hexesDiscard {array[Card]} if hexes are in the game, the discard pile of hexes.
       * boonsDeck {array[Card]} if boons are in the game, the deck of boons.
       * boonsReveal {array[Card]} if boons are in the game, the revealed boons.
       * hexesDeck {array[Card]} if hexes are in the game, the deck of hexes.
       * hexesReveal {array[Card]} if hexes are in the game, the revealed hexes.
       * nonSupplyCards {array[array[Card]]} the non supply cards in the game if any.
       * kingdomCards {array[array[Card]]} the kingdom cards in the game.
       * vpCards {array[array[Card]]} the victory point cards in the game.
       * treasureCards {array[array[Card]]} the treasure cards in the game.
       * trash {array[Card]} the trashed cards.
       * bane {Card} the bane card if Young Witch is in the game.
       * sidewaysCards {array[Card]} the sideways cards in the game (events, landmarks, or projects)
       * hasBane {boolean} whether or not a bane is present.
       * hasBoons {boolean} whether or not boons are in the game.
       * hasHexes {boolean} whether or not hexes are in the game.
       *
       * The objects referenced in game are Players and Cards.
       *
       * Player represents a player in the game. It contains the following keys:
       * name {string} the name of the player
       * durationArea {array[Card]} the duration cards played by the player.
       * playArea {array[Card]} the cards played by the player.
       * deck {array[Card]} the deck of the player.
       * hand {array[Card]} the hand of the player.
       * mats {array[Card]} the cards the player has put on any mat (not separated by mat).
       * discard {array[Card]} the discard pile of the player.
       * numActions {number} the number of actions the player has remaining in their turn.
       * numBuys {number} the number of buys the player has remaining in their turn.
       * numCoins {number} the number of coins the player has remaining in their turn.
       * numVP {number} the number of VP tokens the player has collected this game.
       * numCoffers {number} the number of coffers the player has.
       * numVillagers {number} the number of villagers the player has.
       * numDebt {number} the number of debt tokens the player has.
       * displayedPlayer {number} the index of the player who this player is viewing. (self or opponent)
       *
       * Card represents a card in the game. It contains many keys which can be found in the .yaml files
       * referenced by dominion.py. The relevant keys to us are the following:
       * cost {
       *   potion {number} the number of potions needed to buy the card.
       *   treasure {number} the number of coins to buy this.
       * }
       * image {string} the url to render the card.
       * name {string} the name of the card.
       * pile_type {string} the type of pile the card belongs to.
       * pile_index {number} the index number of the pile the card originally belongs to.
       *      (corresponding to pile_type)
       * type {string} the type of card it is (card, event, landmark, project, ...)
       */
      game: {}
    }
  },
  methods: {
    getImageForCard: getImageForCard,
    getImageForCurrentCardDominion () {
      return getImageForCurrentCard(
        this, {
          'https://www.dropbox.com/sh/b8erq310514f3pd/AACzjeN3dpgOoEha8_iOHEcPa/backside_blue.jpg?raw=1': [this.player['deck'], this.opponent['deck']],
          'https://www.dropbox.com/sh/b8erq310514f3pd/AABPc5Q1wzCaJ2LIoaYR3GhBa/Boon-back.jpg?raw=1': [this.game['boonsDeck']],
          'https://www.dropbox.com/sh/b8erq310514f3pd/AAA5FOdZEN8rfPrflQcrS6Mka/Hex-back.jpg?raw=1': [this.game['hexesDeck']]
        })
    },
    getImageForCardArrayDominion (cardArray) {
      return getImageForCardArray(cardArray, {
        'https://www.dropbox.com/sh/b8erq310514f3pd/AACzjeN3dpgOoEha8_iOHEcPa/backside_blue.jpg?raw=1': [this.player['deck'], this.opponent['deck']],
        'https://www.dropbox.com/sh/b8erq310514f3pd/AABPc5Q1wzCaJ2LIoaYR3GhBa/Boon-back.jpg?raw=1': [this.game['boonsDeck']],
        'https://www.dropbox.com/sh/b8erq310514f3pd/AAA5FOdZEN8rfPrflQcrS6Mka/Hex-back.jpg?raw=1': [this.game['hexesDeck']]
      })
    },
    /**
     * Calls the backend to generate a new game with the populated input fields. Updates the game display once it is created.
     */
    newGame () {
      var randomizedPlayers = [this.username, this.playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })

      callAxiosAndSetButterBar(
        this,
        CREATE_DOMINION_GAME_URL,
        {
          player1: randomizedPlayers[0],
          player2: randomizedPlayers[1],
          username: this.username
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        (response) => {
          let data = response.data
          this.updateDisplayWithReceivedGameData(data)
        })
    },
    /**
     * Gets the css class name to use for the preview card based on the currently selected card.
     */
    getPreviewClassName () {
      if (!this.games_currentCardSelection['exists']) {
        return ''
      }
      let currentCardSelectionArray = this.games_currentCardSelection['array']
      return (
        currentCardSelectionArray === this.game['sidewaysCards'] ||
        currentCardSelectionArray === this.game['boonsDeck'] ||
        currentCardSelectionArray === this.game['boonsDiscard'] ||
        currentCardSelectionArray === this.game['boonsReveal'] ||
        currentCardSelectionArray === this.game['hexesDeck'] ||
        currentCardSelectionArray === this.game['hexesDiscard'] ||
        currentCardSelectionArray === this.game['hexesReveal'])
        ? 'dominion-preview-sideways'
        : 'dominion-preview-normal'
    },
    /**
     * Returns an array containing all the cards in a player's deck. This array is just a view of all the arrays the
     * player owns. Cards do not 'belong' to this array in the same way they do to the arrays in the player object.
     * (Each card can only belong to one array at a time.)
     */
    getAllPlayerCards () {
      let allCards = [].concat(this.player['deck'], this.player['discard'], this.player['playArea'], this.player['hand'], this.player['mats'])
      allCards = allCards.sort(function (a, b) {
        if (a['isVictory'] && !b['isVictory']) {
          return -1
        } else if (b['isVictory'] && !a['isVictory']) {
          return 1
        } else if (a['isVictory'] && b['isVictory']) {
          return a['name'] < b['name'] ? -1 : 1
        }

        if (a['isAction'] && !b['isAction']) {
          return -1
        } else if (b['isAction'] && !a['isAction']) {
          return 1
        } else if (a['isAction'] && b['isAction']) {
          return a['name'] < b['name'] ? -1 : 1
        }

        if (a['isTreasure'] && !b['isTreasure']) {
          return -1
        } else if (b['isTreasure'] && !a['isTreasure']) {
          return 1
        } else if (a['isTreasure'] && b['isTreasure']) {
          return a['name'] < b['name'] ? -1 : 1
        }

        return a['name'] < b['name'] ? -1 : 1
      })
      return allCards
    },
    /**
     * Whether or not the player is displaying their own play area.
     */
    isPlayerDisplayed () {
      return this.player['displayedPlayer'] === this.playerIndex
    },

    moveCard: moveCard,
    saveGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_DOMINION_GAME_URL,
        {
          gameId: this.game.gameId,
          gameData: this.game,
          username: this.username
        },
        null,
        'Failed to save dominion game.')
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateDisplayWithLatestGame () {
      callAxiosAndSetButterBar(
        this,
        DOMINION_GET_LATEST_GAME_URL,
        { username: this.username },
        null,
        'Failed to save dominion game.',
        (response) => {
          if (response.data === null) {
            this.isInGame = false
            return
          }
          this.updateDisplayWithReceivedGameData(response.data.data)
        })
    },
    updateDisplayWithReceivedGameData (gameData) {
      let currentCardSelectionArrayPath
      if (this.games_currentCardSelection.exists) {
        currentCardSelectionArrayPath = findPath(this.games_currentCardSelection.array, this.game)
      }
      this.shouldSaveChanges = false
      this.isInGame = true
      this.game = gameData
      this.playerIndex = gameData.playerOrder[0] === this.username ? 0 : 1
      this.player = this.game.players[this.playerIndex]
      this.opponent = this.game.players[1 - this.playerIndex] // Only supports a 2 player game.

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
    deckToHand () {
      for (let i = 0; i < 5; ++i) {
        moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
      }
    },
    singleCardFromDeckToHand () {
      moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
    },
    endTurnAndCleanUp () {
      moveAllCards(this.player.hand, this.player.discard)
      moveAllCards(this.player.playArea, this.player.discard)
      if (this.games_currentCardSelection.array === this.player.hand || this.games_currentCardSelection.array === this.player.playArea) {
        clearCurrentCard(this)
      }
      this.player.numActions = 1
      this.player.numBuys = 1
      this.player.numCoins = 0
      this.player.displayedPlayer = 1 - this.playerIndex
      this.opponent.displayedPlayer = 1 - this.playerIndex
      this.endPlayerTurn()
      this.deckToHand()
    },
    incrementNumActions () { this.player.numActions++ },
    decrementNumActions () { this.player.numActions-- },
    incrementNumBuys () { this.player.numBuys++ },
    decrementNumBuys () { this.player.numBuys-- },
    incrementNumCoins () { this.player.numCoins++ },
    decrementNumCoins () { this.player.numCoins-- },
    incrementNumVP () { this.player.numVP++ },
    decrementNumVP () { this.player.numVP-- },
    incrementNumVillagers () { this.player.numVillagers++ },
    decrementNumVillagers () { this.player.numVillagers-- },
    incrementNumCoffers () { this.player.numCoffers++ },
    decrementNumCoffers () { this.player.numCoffers-- },
    incrementNumDebt () { this.player.numDebt++ },
    decrementNumDebt () { this.player.numDebt-- },
    handToPlayArea () {
      moveAllCards(this.player.hand, this.player.playArea)
      if (this.games_currentCardSelection.array === this.player.hand) {
        clearCurrentCard(this)
      }
    },
    endPlayerTurn () {
      this.game.currentPlayerTurn = 1 - this.playerIndex
    },
    toggledisplayedPlayer () {
      this.player.displayedPlayer = 1 - this.player.displayedPlayer
    },
    addGainToLog (card) {
      this.game.gameLog.push(this.player.name + ': +' + card.name)
    },
    handleKeyPress (event) {
      if (!this.isInGame) {
        return
      }
      switch (event.key) {
        case 'a': this.incrementNumActions(); break
        case 'b': this.incrementNumBuys(); break
        case 'c': this.incrementNumCoins(); break
        case 'A': this.decrementNumActions(); break
        case 'B': this.decrementNumBuys(); break
        case 'C': this.decrementNumCoins(); break
        case 'D': this.endTurnAndCleanUp(); return
        case 'H': this.deckToHand(); return
        case 'P': this.handToPlayArea(); return
        case 'Z': this.deckToDiscard(); return
        case 'w': this.singleCardFromDeckToHand(); return
      }
      if (!this.games_currentCardSelection.exists) {
        return
      }
      let destinationArray = null
      let reshufflePile = null
      switch (event.key) {
        case 'd': destinationArray = this.player.discard; break
        case 'u': destinationArray = this.player.durationArea; break
        case 'h': destinationArray = this.player.hand; break
        case 'k': destinationArray = this.player.deck; break
        case 'm': destinationArray = this.player.mats; break
        case 'p': destinationArray = this.player.playArea; break
        case 'n':
          let gamesCurrentCardSelectionCard = getCurrentCard(this)
          if (gamesCurrentCardSelectionCard == null) {
            return
          }
          let destinationPileType = gamesCurrentCardSelectionCard.pile_type
          let destinationPileIndex = gamesCurrentCardSelectionCard.pile_index
          if (!destinationPileType) {
            return
          }
          switch (destinationPileType) {
            case 'vp_cards':
              destinationArray = this.game.vpCards[destinationPileIndex]
              break
            case 'treasure_cards':
              destinationArray = this.game.treasureCards[destinationPileIndex]
              break
            case 'kingdom_cards':
              destinationArray = this.game.kingdomCards[destinationPileIndex]
              break
            case 'non_supply_cards':
              destinationArray = this.game.nonSupplyCards[destinationPileIndex]
              break
          }
          break
        case 's': this.shuffleDeck(); return
        case 't': destinationArray = this.game.trash; break
        case 'r': destinationArray = this.game.revealArea; break
        case 'o': destinationArray = this.opponent.hand; break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck) {
        reshufflePile = this.player.discard
      } else if (this.games_currentCardSelection.array === this.game.boonsDeck) {
        reshufflePile = this.game.boonsDiscard
      } else if (this.games_currentCardSelection.array === this.game.hexesDeck) {
        reshufflePile = this.game.hexesDiscard
      }
      moveCurrentCard(this, destinationArray, reshufflePile)
    }
  }
}
</script>
