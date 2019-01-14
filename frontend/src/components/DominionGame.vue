<template>
  <div class="dominion-game">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="card-games-new-game">
      Invite:
          <input v-model="games_playerToInvite" class="card-games-player-to-invite"/>
          <button v-on:click="newDominionGame">New Game</button>
    </div>
    <div v-if="games_isInGame">
      Debug sync: {{games_numExpectedResponses}}<br/>
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
          <div class="dominion-boons-and-hexes-reveal">
            <CardList
                :cardArray="game['boonsReveal']"
                :defaultMoveArray="game['boonsDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="sidewaysCardWidth"
                :cardMargin="cardMargin"
                :getImageForCard="getImageForCard" />
          </div>
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
          <div class="dominion-boons-and-hexes-reveal">
            <CardList
                :cardArray="game['hexesReveal']"
                :defaultMoveArray="game['hexesDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="sidewaysCardWidth"
                :cardMargin="cardMargin"
                :getImageForCard="getImageForCard" />
          </div>
        </div>
      </div>
      <div class="clearfix"/>
      <span v-if="isPlayerDisplayed()" class="card-games-text">Your display</span>
      <span v-else class="card-games-text">{{game['players'][player['displayedPlayer']]['name']}}'s display</span>
      <button @click="toggleDisplayedPlayer">Toggle</button>
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
            <span class="card-games-stat-item">(1) Actions: <span class="card-games-counter">{{player['numActions']}}</span></span>
            <span class="card-games-stat-item">(2) Coins: <span class="card-games-counter">{{player['numCoins']}}</span></span>
            <span class="card-games-stat-item">(3) VP: <span class="card-games-counter">{{player['numVP']}}</span></span>
            <span class="card-games-stat-item">(4) Coffers: <span class="card-games-counter">{{player['numCoffers']}}</span></span>
            <span class="card-games-stat-item">(5) Villagers: <span class="card-games-counter">{{player['numVillagers']}}</span></span>
            <span class="card-games-stat-item">(6) Debt: <span class="card-games-counter">{{player['numDebt']}}</span></span>
            <span class="card-games-stat-item">(7) Buys: <span class="card-games-counter">{{player['numBuys']}}</span></span>
            <span>Your turn</span>
          </div>
          <div v-else>
            <span class="card-games-stat-item">Actions: {{opponent['numActions']}}</span>
            <span class="card-games-stat-item">Coins: {{opponent['numCoins']}}</span>
            <span class="card-games-stat-item">VP: {{opponent['numVP']}}</span>
            <span class="card-games-stat-item">Coffers: {{opponent['numCoffers']}}</span>
            <span class="card-games-stat-item">Villagers: {{opponent['numVillagers']}}</span>
            <span class="card-games-stat-item">Debt: {{opponent['numDebt']}}</span>
            <span class="card-games-stat-item">Buys: {{opponent['numBuys']}}</span>
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
// TODO: Handle increment of Actions, Buys, VP, etc automatically.
import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'
import { moveCard, moveAllCards, moveCurrentCard, getImageForCard, getImageForCurrentCard,
  getCurrentCard, getImageForCardArray, handleComponentMount, handleComponentCreated, mutateProperty,
  updateDisplayWithLatestGame, newGame, saveGame }
  from '../common/card_games'

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const DOMINION_MUTATE_GAME_URL = getFullBackendUrlForPath('/dominion_mutate_game')

export default {
  name: 'DominionGame',
  components: { ButterBar, CardStack, CardList },
  computed: { username () { return store.state.username } },
  watch: {
    username () { updateDisplayWithLatestGame(this, DOMINION_GET_LATEST_GAME_URL) },
    games_mutations: { handler (val) { saveGame(this, DOMINION_MUTATE_GAME_URL) } }
  },
  created () {
    var style = getComputedStyle(document.body)
    this.cardHeight = style.getPropertyValue('--dominion-card-height')
    this.cardWidth = style.getPropertyValue('--dominion-card-width')
    this.cardMargin = style.getPropertyValue('--card-margin')
    this.sidewaysCardWidth = style.getPropertyValue('--dominion-sideways-card-width')
    updateDisplayWithLatestGame(this, DOMINION_GET_LATEST_GAME_URL)
    window.addEventListener('keyup', this.handleKeyPress)
    handleComponentCreated(this)
  },
  mounted () {
    handleComponentMount(this, 'refreshDominion')
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
       * Num expected responses
       */
      games_numExpectedResponses: 0,
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
       * pileType {string} the type of pile the card belongs to.
       * pileIndex {number} the index number of the pile the card originally belongs to.
       *      (corresponding to pileType)
       * type {string} the type of card it is (card, event, landmark, project, ...)
       */
      game: {},
      /**
       * Needed for card-games.js.
       */
      games_currentCardSelection: {'exists': false},
      /**
       * The name of the player to invite when creating a new game.
       */
      games_playerToInvite: '',
      /**
       * Whether there is a game to display or not.
       */
      games_isInGame: false,
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
       * The pending mutations to be sent to the server.
       */
      games_mutations: []
    }
  },
  methods: {
    newDominionGame () {
      let randomizedPlayers = [this.username, this.games_playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })
      newGame(this, randomizedPlayers, CREATE_DOMINION_GAME_URL)
    },
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
    games_callbackForUpdateDisplayWithReceivedGameData (gameData) {
      this.playerIndex = gameData['playerOrder'][0] === this.username ? 0 : 1
      this.player = this.game['players'][this.playerIndex]
      this.opponent = this.game['players'][1 - this.playerIndex] // Only supports a 2 player game.
    },
    handleKeyPress (event) {
      if (!this.games_isInGame) {
        return
      }
      switch (event.key) {
        case '1': this.incrementNumActions(); break
        case '!': this.decrementNumActions(); break
        case '2': this.incrementNumCoins(); break
        case '@': this.decrementNumCoins(); break
        case '3': this.incrementNumVP(); break
        case '#': this.decrementNumVP(); break
        case '4': this.incrementNumCoffers(); break
        case '$': this.decrementNumCoffers(); break
        case '5': this.incrementNumVillagers(); break
        case '%': this.decrementNumVillagers(); break
        case '6': this.incrementNumDebt(); break
        case '^': this.decrementNumDebt(); break
        case '7': this.incrementNumBuys(); break
        case '&': this.decrementNumBuys(); break
        case 'p': this.playTreasuresFromHand(); return
        case 'z': this.deckToDiscard(); return
        case 'e': this.endTurnAndCleanUp(); return
      }
      if (!this.games_currentCardSelection.exists) {
        return
      }
      let destinationArray
      let reshufflePile
      switch (event.key) {
        case 'd': destinationArray = this.player['discard']; break
        case 'u': destinationArray = this.player['durationArea']; break
        case 'h': destinationArray = this.player['hand']; break
        case 'k': destinationArray = this.player['deck']; break
        case 'm': destinationArray = this.player['mats']; break
        case 'n':
          let gamesCurrentCardSelectionCard = getCurrentCard(this)
          if (gamesCurrentCardSelectionCard == null) {
            return
          }
          let destinationPileType = gamesCurrentCardSelectionCard['pileType']
          let destinationPileIndex = gamesCurrentCardSelectionCard['pileIndex']
          if (!destinationPileType) {
            return
          }
          if (destinationPileIndex !== undefined) {
            destinationArray = this.game[destinationPileType][destinationPileIndex]
          } else {
            destinationArray = this.game[destinationPileType]
          }
          break
        case 't': destinationArray = this.game['trash']; break
        case 'r': destinationArray = this.game['revealArea']; break
        case 'o': destinationArray = this.opponent['hand']; break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection['array'] === this.player['deck']) {
        reshufflePile = this.player['discard']
      } else if (this.games_currentCardSelection['array'] === this.game['boonsDeck']) {
        reshufflePile = this.game['boonsDiscard']
      } else if (this.games_currentCardSelection['array'] === this.game['hexesDeck']) {
        reshufflePile = this.game['hexesDiscard']
      }
      moveCurrentCard(this, destinationArray, reshufflePile)
    },
    incrementNumActions () { mutateProperty(this, this.player, 'numActions', 'incrementProperty') },
    decrementNumActions () { mutateProperty(this, this.player, 'numActions', 'decrementProperty') },
    incrementNumBuys () { mutateProperty(this, this.player, 'numBuys', 'incrementProperty') },
    decrementNumBuys () { mutateProperty(this, this.player, 'numBuys', 'decrementProperty') },
    incrementNumCoins () { mutateProperty(this, this.player, 'numCoins', 'incrementProperty') },
    decrementNumCoins () { mutateProperty(this, this.player, 'numCoins', 'decrementProperty') },
    incrementNumVP () { mutateProperty(this, this.player, 'numVP', 'incrementProperty') },
    decrementNumVP () { mutateProperty(this, this.player, 'numVP', 'decrementProperty') },
    incrementNumVillagers () { mutateProperty(this, this.player, 'numVillagers', 'incrementProperty') },
    decrementNumVillagers () { mutateProperty(this, this.player, 'numVillagers', 'decrementProperty') },
    incrementNumCoffers () { mutateProperty(this, this.player, 'numCoffers', 'incrementProperty') },
    decrementNumCoffers () { mutateProperty(this, this.player, 'numCoffers', 'decrementProperty') },
    incrementNumDebt () { mutateProperty(this, this.player, 'numDebt', 'incrementProperty') },
    decrementNumDebt () { mutateProperty(this, this.player, 'numDebt', 'decrementProperty') },
    playTreasuresFromHand () {
      for (let i = this.player['hand'].length - 1; i >= 0; --i) {
        let card = this.player['hand'][i]
        if (card['isTreasure']) {
          moveCard(this, this.player['hand'], i, this.player['playArea'])
        }
      }
    },
    deckToDiscard () {
      moveAllCards(this, this.player['deck'], this.player['discard'])
    },
    endTurnAndCleanUp () {
      moveAllCards(this, this.player['hand'], this.player['discard'])
      moveAllCards(this, this.player['playArea'], this.player['discard'])
      moveAllCards(this, this.player['durationArea'], this.player['playArea'])
      mutateProperty(this, this.player, 'numActions', 'setProperty', 1)
      mutateProperty(this, this.player, 'numBuys', 'setProperty', 1)
      mutateProperty(this, this.player, 'numCoins', 'setProperty', 1)
      mutateProperty(this, this.player, 'displayedPlayer', 'setProperty', 1 - this.playerIndex)
      mutateProperty(this, this.opponent, 'displayedPlayer', 'setProperty', 1 - this.playerIndex)
      mutateProperty(this, this.game, 'currentPlayerTurn', 'setProperty', 1 - this.playerIndex)
      this.drawNewHand()
    },
    setNumberProperty (obj, propertyName, val) {
      if (obj[propertyName] === val) {
        return
      }
      if (obj[propertyName] > val) {
        while (obj[propertyName] > val) {
          mutateProperty(this, obj, propertyName, 'decrementProperty')
        }
        return
      }
      while (obj[propertyName] < val) {
        mutateProperty(this, obj, propertyName, 'incrementProperty')
      }
    },
    drawNewHand () {
      for (let i = 0; i < 5; ++i) {
        moveCard(this, this.player.deck, undefined, this.player.hand, this.player.discard)
      }
    },
    toggleDisplayedPlayer () {
      mutateProperty(this, this.player, 'displayedPlayer', 'setProperty', 1 - this.player['displayedPlayer'])
    },
    addGainToLog (card) {
      mutateProperty(this, this.game, 'gameLog', 'appendElement', this.player['name'] + ': +' + card['name'])
    }
  }
}
</script>
