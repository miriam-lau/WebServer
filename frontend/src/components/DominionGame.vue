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
      <button @click="showKingdom">Kingdom</button>
      <button v-if="game.nonSupplyCards.length > 0" @click="showOtherCardPage">Non Supply</button>
      <button v-if="game.hasBane" @click="showBane">Bane</button>
      <button v-if="game.hasBoons" @click="showBoons">Boons</button>
      <button v-if="game.hasHexes" @click="showHexes">Hexes</button>
      <button @click="showYourMats">Your Mats</button>
      <button @click="showDiscard">Your Discard</button>
      <button @click="showOpponentMats">Opponent Mats</button>
      <button @click="showRevealArea">Revealed</button>
      <button @click="showTrash">Trash</button>
      <button @click="showNotes">Notes</button>
      <button @click="showAllYourCards">All your cards</button>
      <button @click="showShortcuts">Shortcuts</button>
      <div v-if="game.player.shownPage === 'kingdom'">
        <div class="vp-treasure">
          <div class="card-container" :key="'treasure' + index" v-for="(cardArray, index) in game.treasureCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
          <div class="c"></div>
          <div class="card-container" :key="'vp' + index" v-for="(cardArray, index) in game.vpCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
        </div>
        <div class="kingdom">
          <div class="card-container" :key="index" v-for="(cardArray, index) in game.kingdomCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
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
          <div class="card-container" :key="index" v-for="(cardArray, index) in game.nonSupplyCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'bane'">
        <div class="bane">
          <div class="card-container">
            <div class="card-counter-container">{{game.bane.length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['discard'])"
                v-on:mouseover="setCurrentSelection(game.bane)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(game.bane)"/>
          </div>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'boons'">
        <div class="boons-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.boonsDeck.length}}</div>
            <img
                v-on:click="moveCard(boonsDeck, undefined, boonsReveal)"
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
                v-on:click="moveCard(game.hexesDeck, undefined, game.hexesReveal)"
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
          <img
              v-for="(card, index) in game.player['mats']"
              :key="index"
              v-on:click="moveCurrentSelection(game.player['discard'])"
              v-on:mouseover="setCurrentSelection(game.player['mats'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
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
          <img
              v-for="(card, index) in game.trash"
              :key="index"
              v-on:mouseover="setCurrentSelection(game.trash, index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="game.player.shownPage === 'reveal'">
        <div class="reveal-area">
          <img
              v-for="(card, index) in game.revealArea"
              :key="index"
              v-on:mouseover="setCurrentSelection(game.revealArea, index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
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
          <img
              v-for="(card, index) in game.player['discard']"
              :key="index"
              v-on:mouseover="setCurrentSelection(game.player['discard'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
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
      <img class="preview" v-if="currentSelection['exists']" :src="getImageForCurrentSelection()"/>
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
          <img
              v-for="(card, index) in game.player['playArea']"
              :key="index"
              v-on:click="moveCurrentSelection(game.player['discard'])"
              v-on:mouseover="setCurrentSelection(game.player['playArea'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
        <div v-else>
          <img
              v-for="(card, index) in game.opponent['playArea']"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
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
          <div class="card-container">
            <div class="card-counter-container">{{game.player['deck'].length}}</div>
            <img
                v-on:click="moveCurrentSelection(game.player['hand'])"
                v-on:mouseover="setCurrentSelection(game.player['deck'])"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(game.player['deck'])"/>
          </div>
        </div>
        <div class="discard">
          <div class="card-container">
            <div class="card-counter-container">{{game.player['discard'].length}}</div>
            <img
                v-on:mouseover="setCurrentSelection(game.player['discard'])"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(game.player['discard'])"/>
          </div>
        </div>
        <div class="hand">
          <img
              v-for="(card, index) in game.player['hand']"
              :key="index"
              v-on:click="moveCurrentSelection(game.player['playArea'])"
              v-on:mouseover="setCurrentSelection(game.player['hand'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
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
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const SAVE_DOMINION_GAME_URL = getFullBackendUrlForPath('/save_dominion_game')

export default {
  name: 'DominionGame',
  data () {
    return {
      currentSelection: {}, // Object with keys 'array', and 'index', and 'exists'
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
    ButterBar
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
      this.clearCurrentSelection()
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
    getImageForCurrentSelection () {
      if (!this.currentSelection.exists) {
        return
      }
      if (this.currentSelection.array === this.game.players['deck']) {
        return '/static/dominion/card_images/backside_blue.jpg'
      }
      let index = this.currentSelection.index
      if (index === undefined) {
        index = this.currentSelection.array.length - 1
      }
      if (index < 0) {
        return '/static/dominion/card_images/_blank.jpg'
      } else if (this.currentSelection.array.length <= index) {
        return ''
      } else {
        return this.getImageForCard(this.currentSelection.array[index])
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
    getCurrentSelectionCard () {
      let cardIndex = this.currentSelection['index']
      let cardArray = this.currentSelection['array']
      if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= cardArray.length)) {
        return null
      }
      if (cardIndex === undefined) {
        cardIndex = cardArray.length - 1
      }
      return cardArray[cardIndex]
    },
    moveCard (originalPile, cardIndex, destinationPile) {
      if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= originalPile.length)) {
        return false
      }
      if (cardIndex === undefined) {
        if (originalPile === this.game.player['deck'] && this.game.player['deck'].length === 0 && this.game.player['discard'].length !== 0) {
          this.game.player['deck'].push(...this.shuffle(this.game.player['discard']))
          this.emptyArray(this.game.player['discard'])
        } else if (originalPile === this.game.boonsDeck && this.game.boonsDeck.length === 0 && this.game.boonsDiscard.length !== 0) {
          this.game.boonsDeck.push(...this.shuffle(this.game.boonsDiscard))
          this.emptyArray(this.game.boonsDiscard)
        } else if (originalPile === this.game.hexesDeck && this.game.hexesDeck.length === 0 && this.game.hexesDiscard.length !== 0) {
          this.game.hexesDeck.push(...this.shuffle(this.game.hexesDiscard))
          this.emptyArray(this.game.hexesDiscard)
        }
        cardIndex = originalPile.length - 1
      }
      if (cardIndex < 0 || cardIndex >= originalPile.length) {
        return
      }
      let card = originalPile[cardIndex]
      destinationPile.push(card)
      originalPile.splice(cardIndex, 1)
      return true
    },
    emptyArray (arr) {
      for (let i = arr.length; i > 0; --i) {
        arr.pop()
      }
    },
    moveCurrentSelection (destinationPile) {
      if (!this.currentSelection.exists) {
        return
      }
      let success = this.moveCard(this.currentSelection['array'], this.currentSelection['index'], destinationPile)
      if (!success) {
        return
      }
      if (this.currentSelection.index !== undefined) {
        if (this.currentSelection.array.length > this.currentSelection.index) {
          this.setCurrentSelection(this.currentSelection.array, this.currentSelection.index)
        } else {
          this.clearCurrentSelection()
        }
      }
    },
    shuffleDeck () {
      this.shuffle(this.game.player['deck'])
    },
    deckToDiscard () {
      this.game.player['discard'].push(...this.game.player['deck'])
      this.emptyArray(this.game.player['deck'])
    },
    deckToHand () {
      for (let i = 0; i < 5; ++i) {
        this.moveCard(this.game.player['deck'], undefined, this.game.player['hand'])
      }
    },
    singleCardFromDeckToHand () {
      this.moveCard(this.game.player['deck'], undefined, this.game.player['hand'])
    },
    endTurnAndCleanUp () {
      this.game.player['discard'].push(...this.game.player['hand'])
      this.game.player['discard'].push(...this.game.player['playArea'])
      this.emptyArray(this.game.player['hand'])
      this.emptyArray(this.game.player['playArea'])
      if (this.currentSelection['array'] === this.game.player['hand'] || this.currentSelection['array'] === this.game.player['playArea']) {
        this.clearCurrentSelection()
      }
      this.game.player['numActions'] = 1
      this.game.player['numBuys'] = 1
      this.game.player['numCoins'] = 0
      this.game.player['displayedPlayArea'] = 1 - this.playerIndex
      this.game.opponent['displayedPlayArea'] = 1 - this.playerIndex
      this.endPlayerTurn()
    },
    incrementNumActions () {
      this.game.player['numActions']++
    },
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
      if (this.currentSelection['array'] === this.game.player['hand']) {
        this.clearCurrentSelection()
      }
    },
    shuffle (array) { // Taken from https://gomakethings.com/how-to-shuffle-an-array-with-vanilla-js/
      var currentIndex = array.length
      var temporaryValue, randomIndex

      while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex)
        currentIndex -= 1

        temporaryValue = array[currentIndex]
        array[currentIndex] = array[randomIndex]
        array[randomIndex] = temporaryValue
      }
      return array
    },
    /**
     * If index is undefined, then show the default card. i.e. the topmost card in most cases or a card back for the deck.
     */
    setCurrentSelection (cardArray, index) {
      if (index < 0 || index >= cardArray.length) {
        this.clearCurrentSelection()
        return
      }
      this.currentSelection = {
        array: cardArray,
        index: index,
        exists: true
      }
    },
    clearCurrentSelection () {
      this.currentSelection = {}
    },
    showOtherCardPage () {
      this.game.player.shownPage = 'nonSupply'
    },
    showKingdom () {
      this.game.player.shownPage = 'kingdom'
    },
    showBane () {
      this.game.player.shownPage = 'bane'
    },
    showBoons () {
      this.game.player.shownPage = 'boons'
    },
    showHexes () {
      this.game.player.shownPage = 'hexes'
    },
    showYourMats () {
      this.game.player.shownPage = 'yourMats'
    },
    showOpponentMats () {
      this.game.player.shownPage = 'opponentMats'
    },
    showTrash () {
      this.game.player.shownPage = 'trash'
    },
    showRevealArea () {
      this.game.player.shownPage = 'reveal'
    },
    showDiscard () {
      this.game.player.shownPage = 'discard'
    },
    showAllYourCards () {
      this.game.player.shownPage = 'allYourCards'
    },
    showNotes () {
      this.game.player.shownPage = 'notes'
    },
    showShortcuts () {
      this.game.player.shownPage = 'shortcuts'
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
      if (!this.currentSelection['exists']) {
        return
      }
      let destinationArray = null
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
          let currentSelectionCard = this.getCurrentSelectionCard()
          if (currentSelectionCard == null) {
            return
          }
          let destinationPileType = currentSelectionCard.pile_type
          let destinationPileIndex = currentSelectionCard.pile_index
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
      this.moveCurrentSelection(destinationArray)
    }
  }
}
</script>
