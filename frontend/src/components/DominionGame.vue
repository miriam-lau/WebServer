<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="new-game">
      Invite:
          <input v-model="playerToInvite" class="dominion-player-to-invite"/>
          <button v-on:click="newGame">New Game</button>
    </div>
    <div v-if="isInGame">
      <button @click="game.player.shownPage = 'kingdom'">Kingdom</button>
      <button v-if="game.nonSupplyCards.length > 0" @click="game.player.shownPage = 'nonSupply'">Non Supply</button>
      <button v-if="game.hasBane" @click="game.player.shownPage = 'bane'">Bane</button>
      <button v-if="game.hasBoons" @click="game.player.shownPage = 'boons'">Boons</button>
      <button v-if="game.hasHexes" @click="game.player.shownPage = 'hexes'">Hexes</button>
      <button @click="game.player.shownPage = 'yourMats'">Your Mats</button>
      <button @click="game.player.shownPage = 'discard'">Your Discard</button>
      <button @click="game.player.shownPage = 'opponentMats'">Opponent Mats</button>
      <button @click="game.player.shownPage = 'reveal'">Revealed</button>
      <button @click="game.player.shownPage = 'trash'">Trash</button>
      <button @click="game.player.shownPage = 'notes'">Notes</button>
      <button @click="game.player.shownPage = 'allYourCards'">All your cards</button>
      <button @click="game.player.shownPage = 'shortcuts'">Shortcuts</button>
      <div v-if="game.player.shownPage === 'kingdom'">
        <div class="vp-treasure">
          <CardStack
            :key="'treasure' + index" v-for="(cardArray, index) in game.treasureCards"
            :defaultMoveArray="game.player['discard']"
            :cardArray="cardArray"/>
          <div class="c"></div>
          <CardStack
            :key="'vp' + index" v-for="(cardArray, index) in game.vpCards"
            :defaultMoveArray="game.player['discard']"
            :cardArray="cardArray"/>
        </div>
        <div class="kingdom">
          <CardStack
            :key="'vp' + index" v-for="(cardArray, index) in game.kingdomCards"
            :defaultMoveArray="game.player['discard']"
            :cardArray="cardArray"/>
        </div>
        <div class="events">
          <img
              v-for="(card, index) in game.sidewaysCards"
              class="sideways-card"
              :key="index"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'nonSupply'">
        <div class="non-supply">
          <CardStack
            :key="index" v-for="(cardArray, index) in game.nonSupplyCards"
            :defaultMoveArray="game.player['discard']"
            :cardArray="cardArray"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'bane'">
        <div class="bane">
          <CardStack
            :defaultMoveArray="game.player['discard']"
            :cardArray="game.bane"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'boons'">
        <div class="boons-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.boonsDeck.length}}</div>
            <img
                v-on:click="moveCard(game.boonsDeck, undefined, game.boonsReveal, game.boonsDiscard)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.boonsDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.boonsDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.boonsDiscard)"/>
          </div>
        </div>
        <div class="boons-reveal">
          <img
              v-for="(card, index) in game.boonsReveal"
              :key="index"
              v-on:click="moveCard(game.boonsReveal, index, game.boonsDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'hexes'">
        <div class="hexes-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.hexesDeck.length}}</div>
            <img
                v-on:click="moveCard(game.hexesDeck, undefined, game.hexesReveal, game.hexesDiscard)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.hexesDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.hexesDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.hexesDiscard)"/>
          </div>
        </div>
        <div class="hexes-reveal">
          <img
              v-for="(card, index) in game.hexesReveal"
              :key="index"
              v-on:click="moveCard(game.hexesReveal, index, game.hexesDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'yourMats'">
        <div class="your-mats">
          <CardList
              :cardArray="game.player['mats']"
              :defaultMoveArray="game.player['discard']"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'opponentMats'">
        <div class="opponent-mats">
          <img
              v-for="(card, index) in game.opponent['mats']"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'trash'">
        <div class="trash">
          <CardList :cardArray="game.trash"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'reveal'">
        <div class="reveal-area">
          <CardList :cardArray="game.revealArea"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'notes'">
        <div class="notes">
          <textarea class="note" v-model="game.player['notes']"></textarea>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'shortcuts'">
        <div class="shortcuts">
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
      <div v-else-if="game.player.shownPage === 'discard'">
        <div class="discard-area">
          <CardList :cardArray="game.player['discard']"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'allYourCards'">
        <div class="all-your-cards">
          <img
              v-for="(card, index) in [].concat(game.player['deck'], game.player['discard'], game.player['playArea'], game.player['hand'], game.player['mats'])"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <img class="preview" v-if="games_currentCardSelection['exists']" :src="getImageForGames_CurrentCardSelection()"/>
      <div class="c">
      </div>
      <div v-if="game.player['displayedPlayArea'] === playerIndex">
      Your play area
      </div>
      <div v-else>
      {{game.players[game.player['displayedPlayArea']].name}}'s play area
      </div>
      <div class="play-area">
        <div v-if="game.player['displayedPlayArea'] === playerIndex">
          <CardList
              :cardArray="game.player['playArea']"
              :defaultMoveArray="game.player['discard']"/>
        </div>
        <div v-else>
          <CardList :cardArray="game.opponent['playArea']"/>
        </div>
      </div>
      <div class="c">
      </div>
      <div class="stats">
        <span class="stat-item">Actions: <button @click="decrementNumActions">-</button><input class="counter" v-model="game.player['numActions']"/><button @click="incrementNumActions">+</button></span>
        <span class="stat-item">Buys: <button @click="decrementNumBuys">-</button><input class="counter" v-model="game.player['numBuys']"/><button @click="incrementNumBuys">+</button></span>
        <span class="stat-item">Coins: <button @click="decrementNumCoins">-</button><input class="counter" v-model="game.player['numCoins']"/><button @click="incrementNumCoins">+</button></span>
        <span class="stat-item">VP: <button @click="decrementNumVP">-</button><input class="counter" v-model="game.player['numVP']"/><button @click="incrementNumVP">+</button></span>
        <span class="stat-item">Coffers: <button @click="decrementNumCoffers">-</button><input class="counter" v-model="game.player['numCoffers']"/><button @click="incrementNumCoffers">+</button></span>
        <span class="stat-item">Villagers: <button @click="decrementNumVillagers">-</button><input class="counter" v-model="game.player['numVillagers']"/><button @click="incrementNumVillagers">+</button></span>
        <span class="stat-item">Debt: <button @click="decrementNumDebt">-</button><input class="counter" v-model="game.player['numDebt']"/><button @click="incrementNumDebt">+</button></span>
        <button @click="endPlayerTurn" v-if="game.currentPlayerTurn === playerIndex">End Turn</button>
        <button @click="toggleDisplayedPlayArea">Toggle Play Area</button>
        <span v-if="game.currentPlayerTurn === playerIndex">Your turn</span>
        <span v-else>{{game.opponent.name}}'s turn</span>
      </div>
      <div class="deck-and-hand">
        <div class="deck">
          <CardStack
            :reshufflePileArray="game.player['discard']"
            :defaultMoveArray="game.player['hand']"
            :cardArray="game.player['deck']"/>
        </div>
        <div class="discard">
          <CardStack
            :cardArray="game.player['discard']"/>
        </div>
        <div class="hand">
          <CardList
              :defaultMoveArray="game.player['playerArea']"
              :cardArray="game.player['hand']"/>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/dominion-game.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'
import { shuffle, moveCard, moveCurrentCardSelection, clearCurrentCardSelection } from '../common/card_games'

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const SAVE_DOMINION_GAME_URL = getFullBackendUrlForPath('/save_dominion_game')

export default {
  name: 'DominionGame',
  data () {
    return {
      games_currentCardSelection: {}, // Object with keys 'array', and 'index', and 'exists'
      shouldSaveChanges: false,
      playerToInvite: '',
      playerIndex: 0,
      butterBar_message: '',
      butterBar_css: '',
      isInGame: false,
      game: {
        playerOrder: [],
        currentPlayerTurn: 0,
        nonSupplyCards: [],
        kingdomCards: [],
        vpCards: [],
        treasureCards: [],
        sidewaysCards: [],
        trash: [],
        revealArea: [],
        players: [{
          name: '',
          notes: '',
          playArea: [],
          deck: [],
          mats: [],
          hand: [],
          discard: [],
          numActions: 1,
          numBuys: 1,
          numCoins: 0,
          numVP: 0,
          numCoffers: 0,
          numVillagers: 0,
          numDebt: 0,
          shownPage: 'kingdom',
          displayedPlayArea: 0
        }, {
          name: '',
          notes: '',
          playArea: [],
          deck: [],
          hand: [],
          mats: [],
          discard: [],
          numActions: 1,
          numBuys: 1,
          numCoins: 0,
          numVP: 0,
          numCoffers: 0,
          numVillagers: 0,
          numDebt: 0,
          shownPage: 'kingdom',
          displayedPlayArea: 1
        }],
        player: {},
        opponent: {},
        boonsDeck: [],
        boonsReveal: [],
        boonsDiscard: [],
        bane: [],
        hexes: [],
        hexesDeck: [],
        hexesReveal: [],
        hexesDiscard: [],
        hasBane: false,
        hasBoons: false,
        hasHexes: false
      }
    }
  },
  components: {
    ButterBar, CardStack, CardList
  },
  created () {
    this.updateDominionDisplayWithLatestGame()
    window.addEventListener('keyup', this.handleKeyPress)
    this.playerToInvite = this.defaultPlayerToInvite()
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  watch: {
    username () {
      this.updateDominionDisplayWithLatestGame()
    },
    game: {
      handler (val) {
        if (this.shouldSaveChanges) {
          this.saveDominionGame()
        } else {
          this.shouldSaveChanges = true
        }
      },
      deep: true
    }
  },
  mounted () {
    var that = this
    socket.on('refresh_dominion', function (data) {
      if (data['players'].includes(that.username) && data['player_triggering_update'] !== that.username) {
        that.updateDominionDisplayWithGameData(data['gameData'])
      }
    })
  },
  methods: {
    moveCard: moveCard,
    /*
     * The default player name to invite to a game.
     */
    defaultPlayerToInvite () {
      if (this.username === 'James') {
        return 'Miriam'
      } else if (this.username === 'Miriam') {
        return 'James'
      } else if (this.username === 'Angeline') {
        return 'Sujinda'
      } else if (this.username === 'Sujinda') {
        return 'Angeline'
      }
      return ''
    },
    newGame () {
      var randomizedPlayers = [this.username, this.playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })

      let that = this
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
        function (response) {
          let data = response['data']
          that.updateDominionDisplayWithGameData(data)
        })
    },
    getGameData () {
      let data = {}
      data['currentPlayerTurn'] = this.game.currentPlayerTurn
      data['revealArea'] = this.game.revealArea
      data['isInGame'] = this.isInGame
      data['players'] = this.game.players
      data['boonsDiscard'] = this.game.boonsDiscard
      data['hexesDiscard'] = this.game.hexesDiscard
      data['boonsDeck'] = this.game.boonsDeck
      data['boonsReveal'] = this.game.boonsReveal
      data['hexesDeck'] = this.game.hexesDeck
      data['hexesReveal'] = this.game.hexesReveal
      data['gameId'] = this.game.gameId

      data['playerOrder'] = this.game.playerOrder
      data['nonSupplyCards'] = this.game.nonSupplyCards
      data['kingdomCards'] = this.game.kingdomCards
      data['vpCards'] = this.game.vpCards
      data['treasureCards'] = this.game.treasureCards
      data['trash'] = this.game.trash
      data['bane'] = this.game.bane
      data['hexesDeck'] = this.game.hexesDeck
      data['boonsDeck'] = this.game.boonsDeck
      data['sidewaysCards'] = this.game.sidewaysCards
      data['hasBane'] = this.game.hasBane
      data['hasBoons'] = this.game.hasBoons
      data['hasHexes'] = this.game.hasHexes
      return data
    },
    saveDominionGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_DOMINION_GAME_URL,
        {
          gameId: this.game.gameId,
          gameData: this.getGameData(),
          username: this.username
        },
        null,
        'Failed to save dominion game.')
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateDominionDisplayWithLatestGame () {
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
          this.updateDominionDisplayWithGameData(response.data.data)
        })
    },
    updateDominionDisplayWithGameData (gameData) {
      clearCurrentCardSelection(this)
      this.shouldSaveChanges = false
      this.isInGame = gameData['isInGame']
      this.game.currentPlayerTurn = gameData['currentPlayerTurn']
      this.game.revealArea = gameData['revealArea']
      this.game.players = gameData['players']
      this.game.boonsDiscard = gameData['boonsDiscard']
      this.game.hexesDiscard = gameData['hexesDiscard']
      this.game.boonsDeck = gameData['boonsDeck']
      this.game.boonsReveal = gameData['boonsReveal']
      this.game.hexesDeck = gameData['hexesDeck']
      this.game.hexesReveal = gameData['hexesReveal']
      this.game.gameId = gameData['gameId']
      this.game.playerOrder = gameData['playerOrder']

      this.playerIndex = gameData['playerOrder'][0] === this.username ? 0 : 1
      this.game.nonSupplyCards = gameData['nonSupplyCards']
      this.game.kingdomCards = gameData['kingdomCards']
      this.game.vpCards = gameData['vpCards']
      this.game.treasureCards = gameData['treasureCards']
      this.game.trash = gameData['trash']
      this.game.player = this.game.players[this.playerIndex]
      this.game.opponent = this.game.players[1 - this.playerIndex] // Only supports a 2 player game.
      this.game.bane = gameData['bane']
      this.game.hexesDeck = gameData['hexesDeck']
      this.game.boonsDeck = gameData['boonsDeck']
      this.game.sidewaysCards = gameData['sidewaysCards']
      this.game.hasBane = gameData['hasBane']
      this.game.hasBoons = gameData['hasBoons']
      this.game.hasHexes = gameData['hasHexes']
    },
    getImageForGames_CurrentCardSelection () {
      if (!this.games_currentCardSelection.exists) {
        return
      }
      if (this.games_currentCardSelection.array === this.game.players['deck']) {
        return '/static/dominion/card_images/backside_blue.jpg'
      }
      let index = this.games_currentCardSelection.index
      if (index === undefined) {
        index = this.games_currentCardSelection.array.length - 1
      }
      if (index < 0) {
        return '/static/dominion/card_images/_blank.jpg'
      } else if (this.games_currentCardSelection.array.length <= index) {
        return ''
      } else {
        return this.getImageForCard(this.games_currentCardSelection.array[index])
      }
    },
    getImageForCardArrayOrBlank (cardArray) {
      if (cardArray.length === 0) {
        return '/static/dominion/card_images/_blank.jpg'
      } else if (cardArray === this.game.player['deck']) {
        return '/static/dominion/card_images/backside_blue.jpg'
      } else if (cardArray === this.game.boonsDeck) {
        return '/static/dominion/card_images/Boon-back.jpg'
      } else if (cardArray === this.game.hexesDeck) {
        return '/static/dominion/card_images/Hex-back.jpg'
      } else {
        return this.getImageForCard(cardArray[cardArray.length - 1])
      }
    },
    getImageForCard (card) {
      if (card.set === 'Renaissance') {
        return this.getOldImageForCard(card)
      } else {
        return this.getDigitalImageForCard(card)
      }
    },
    getOldImageForCard (card) {
      let imageName = card.set + '_'
      if (card.type !== 'card') {
        imageName += card.type + '_'
      }
      imageName += card.name
      imageName = imageName.toLowerCase()
      imageName = imageName.replace(/[-' /]/g, '')
      imageName = imageName.replace(/\(2nd\)/g, '2')
      imageName = '/static/dominion/card_images/' + imageName + '.jpg'
      return imageName
    },
    getDigitalImageForCard (card) {
      let imageName = card.name
      imageName = imageName.replace(/ /g, '_')
      imageName = '/static/dominion/card_images/' + imageName + 'Digital.jpg'
      return imageName
    },
    getDisplayForCardArray (cardArray) {
      if (cardArray.length === 0) {
        return ''
      } else {
        let cardName = cardArray[cardArray.length - 1].name
        if (cardName.length > 8) {
          cardName = cardName.substring(0, 8) + '...'
        }
        return cardName + '\n$' + cardArray[cardArray.length - 1].cost.treasure + ', ' + cardArray.length + ' left'
      }
    },
    getGames_CurrentCardSelectionCard () {
      let cardIndex = this.games_currentCardSelection['index']
      let cardArray = this.games_currentCardSelection['array']
      if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= cardArray.length)) {
        return null
      }
      if (cardIndex === undefined) {
        cardIndex = cardArray.length - 1
      }
      return cardArray[cardIndex]
    },
    shuffleDeck () {
      shuffle(this.game.player['deck'])
    },
    deckToDiscard () {
      this.game.player['discard'].push(...this.game.player['deck'])
      this.emptyArray(this.game.player['deck'])
    },
    deckToHand () {
      for (let i = 0; i < 5; ++i) {
        moveCard(this.game.player['deck'], undefined, this.game.player['hand'])
      }
    },
    singleCardFromDeckToHand () {
      moveCard(this.game.player['deck'], undefined, this.game.player['hand'])
    },
    endTurnAndCleanUp () {
      this.game.player['discard'].push(...this.game.player['hand'])
      this.game.player['discard'].push(...this.game.player['playArea'])
      this.emptyArray(this.game.player['hand'])
      this.emptyArray(this.game.player['playArea'])
      if (this.games_currentCardSelection['array'] === this.game.player['hand'] || this.games_currentCardSelection['array'] === this.game.player['playArea']) {
        clearCurrentCardSelection(this)
      }
      this.game.player['numActions'] = 1
      this.game.player['numBuys'] = 1
      this.game.player['numCoins'] = 0
      this.game.player['displayedPlayArea'] = 1 - this.playerIndex
      this.game.opponent['displayedPlayArea'] = 1 - this.playerIndex
      this.endPlayerTurn()
    },
    incrementNumActions () { this.game.player['numActions']++ },
    decrementNumActions () {
      this.game.player['numActions']--
    },
    incrementNumBuys () {
      this.game.player['numBuys']++
    },
    decrementNumBuys () {
      this.game.player['numBuys']--
    },
    incrementNumCoins () {
      this.game.player['numCoins']++
    },
    decrementNumCoins () {
      this.game.player['numCoins']--
    },
    incrementNumVP () {
      this.game.player['numVP']++
    },
    decrementNumVP () {
      this.game.player['numVP']--
    },
    incrementNumVillagers () {
      this.game.player['numVillagers']++
    },
    decrementNumVillagers () {
      this.game.player['numVillagers']--
    },
    incrementNumCoffers () {
      this.game.player['numCoffers']++
    },
    decrementNumCoffers () {
      this.game.player['numCoffers']--
    },
    incrementNumDebt () {
      this.game.player['numDebt']++
    },
    decrementNumDebt () {
      this.game.player['numDebt']--
    },
    handToPlayArea () {
      this.game.player['playArea'].push(...this.game.player['hand'])
      this.emptyArray(this.game.player['hand'])
      if (this.games_currentCardSelection['array'] === this.game.player['hand']) {
        clearCurrentCardSelection(this)
      }
    },
    endPlayerTurn () {
      this.game.currentPlayerTurn = 1 - this.playerIndex
    },
    toggleDisplayedPlayArea () {
      this.game.player.displayedPlayArea = 1 - this.game.player.displayedPlayArea
    },
    handleKeyPress (event) {
      if (!this.isInGame) {
        return
      }
      switch (event.key) {
        case 'a':
          this.incrementNumActions()
          break
        case 'b':
          this.incrementNumBuys()
          break
        case 'c':
          this.incrementNumCoins()
          break
        case 'A':
          this.decrementNumActions()
          break
        case 'B':
          this.decrementNumBuys()
          break
        case 'C':
          this.decrementNumCoins()
          break
        case 'D':
          this.endTurnAndCleanUp()
          return
        case 'H':
          this.deckToHand()
          return
        case 'P':
          this.handToPlayArea()
          return
        case 'Z': // For lack of a better letter
          this.deckToDiscard()
          return
        case 'e':
          this.endPlayerTurn()
          break
        case 'w':
          this.singleCardFromDeckToHand()
          return
      }
      if (!this.games_currentCardSelection['exists']) {
        return
      }
      let destinationArray = null
      let reshufflePile = null
      switch (event.key) {
        case 'd':
          destinationArray = this.game.player['discard']
          break
        case 'h':
          destinationArray = this.game.player['hand']
          break
        case 'k':
          destinationArray = this.game.player['deck']
          break
        case 'm':
          destinationArray = this.game.player['mats']
          break
        case 'p':
          destinationArray = this.game.player['playArea']
          break
        case 'r':
          let gamesCurrentCardSelectionCard = this.getGames_CurrentCardSelectionCard()
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
        case 's':
          this.shuffleDeck()
          return
        case 't':
          destinationArray = this.game.trash
          break
        case 'v':
          destinationArray = this.game.revealArea
          break
        case 'o':
          destinationArray = this.game.opponent['hand']
          break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.game.player['deck']) {
        reshufflePile = this.game.player['discard']
      } else if (this.games_currentCardSelection.array === this.game.boonsDeck) {
        reshufflePile = this.game.boonsDiscard
      } else if (this.games_currentCardSelection.array === this.game.hexesDeck) {
        reshufflePile = this.game.hexesDiscard
      }
      moveCurrentCardSelection(this, destinationArray, reshufflePile)
    }
  }
}
</script>
