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
      <button v-if="nonSupplyCards.length > 0" @click="showOtherCardPage">Non Supply</button>
      <button v-if="hasBane" @click="showBane">Bane</button>
      <button v-if="hasBoons" @click="showBoons">Boons</button>
      <button v-if="hasHexes" @click="showHexes">Hexes</button>
      <button @click="showYourMats">Your Mats</button>
      <button @click="showDiscard">Your Discard</button>
      <button @click="showOpponentMats">Opponent Mats</button>
      <button @click="showRevealArea">Revealed</button>
      <button @click="showTrash">Trash</button>
      <button @click="showNotes">Notes</button>
      <button @click="showAllYourCards">All your cards</button>
      <button @click="showShortcuts">Shortcuts</button>
      <div v-if="player.shownPage === 'kingdom'">
        <div class="vp-treasure">
          <div class="card-container" :key="'treasure' + index" v-for="(cardArray, index) in treasureCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
          <div class="c"></div>
          <div class="card-container" :key="'vp' + index" v-for="(cardArray, index) in vpCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
        </div>
        <div class="kingdom">
          <div class="card-container" :key="index" v-for="(cardArray, index) in kingdomCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
        </div>
        <div class="events">
          <img
              v-for="(card, index) in sidewaysCards"
              class="sideways-card"
              :key="index"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'nonSupply'">
        <div class="non-supply">
          <div class="card-container" :key="index" v-for="(cardArray, index) in nonSupplyCards">
            <div class="card-counter-container">{{cardArray.length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['discard'])"
                v-on:mouseover="setCurrentSelection(cardArray)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(cardArray)"/>
          </div>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'bane'">
        <div class="bane">
          <div class="card-container">
            <div class="card-counter-container">{{bane.length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['discard'])"
                v-on:mouseover="setCurrentSelection(bane)"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(bane)"/>
          </div>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'boons'">
        <div class="boons-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{boonsDeck.length}}</div>
            <img
                v-on:click="moveCard(boonsDeck, undefined, boonsReveal)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(boonsDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{boonsDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(boonsDiscard)"/>
          </div>
        </div>
        <div class="boons-reveal">
          <img
              v-for="(card, index) in boonsReveal"
              :key="index"
              v-on:click="moveCard(boonsReveal, index, boonsDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'hexes'">
        <div class="hexes-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{hexesDeck.length}}</div>
            <img
                v-on:click="moveCard(hexesDeck, undefined, hexesReveal)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(hexesDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{hexesDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(hexesDiscard)"/>
          </div>
        </div>
        <div class="hexes-reveal">
          <img
              v-for="(card, index) in hexesReveal"
              :key="index"
              v-on:click="moveCard(hexesReveal, index, hexesDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'yourMats'">
        <div class="your-mats">
          <img
              v-for="(card, index) in player['mats']"
              :key="index"
              v-on:click="moveCurrentSelection(player['discard'])"
              v-on:mouseover="setCurrentSelection(player['mats'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'opponentMats'">
        <div class="opponent-mats">
          <img
              v-for="(card, index) in opponent['mats']"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'trash'">
        <div class="trash">
          <img
              v-for="(card, index) in trash"
              :key="index"
              v-on:mouseover="setCurrentSelection(trash, index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'reveal'">
        <div class="reveal-area">
          <img
              v-for="(card, index) in revealArea"
              :key="index"
              v-on:mouseover="setCurrentSelection(revealArea, index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'notes'">
        <div class="notes">
          <textarea class="note" v-model="player['notes']"></textarea>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'shortcuts'">
        <div class="shortcuts">
          D - Discard all cards in your hand and play area.<br/>
          H - Draw 5 new cards into your hand.<br/>
          P - Play all cards in your hand.<br/>
          s - Shuffle your deck.<br/><br/>
          d - Discard the card.<br/>
          h - Draw the card into your hand.<br/>
          k - Topdeck the card onto your deck.<br/>
          m - Move the card to your mat.<br/>
          p - Play the card to your play area.<br/>
          t - Trash the card.<br/>
          v - Reveal the card in the revealed area.<br/>
          o - Move the card to your opponent's hand.<br/>
          r - Return the card to its original pile.<br/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'discard'">
        <div class="discard-area">
          <img
              v-for="(card, index) in player['discard']"
              :key="index"
              v-on:mouseover="setCurrentSelection(player['discard'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'allYourCards'">
        <div class="all-your-cards">
          <img
              v-for="(card, index) in [].concat(player['deck'], player['discard'], player['playArea'], player['hand'], player['mats'])"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <img class="preview" v-if="currentSelection['exists']" :src="getImageForCurrentSelection()"/>
      <div class="c">
      </div>
      <div class="play-area">
        <img
            v-for="(card, index) in player['playArea']"
            :key="index"
            v-on:click="moveCurrentSelection(player['discard'])"
            v-on:mouseover="setCurrentSelection(player['playArea'], index)"
            v-on:mouseout="clearCurrentSelection()"
            class="card"
            :src="getImageForCard(card)"/>
      </div>
      <div class="c">
      </div>
      <div class="stats">
        <span class="stat-item">Actions: <button @click="player['numActions']--">-</button><input class="counter" v-model="player['numActions']"/><button @click="player['numActions']++">+</button></span>
        <span class="stat-item">Buys: <button @click="player['numBuys']--">-</button><input class="counter" v-model="player['numBuys']"/><button @click="player['numBuys']++">+</button></span>
        <span class="stat-item">Coins: <button @click="player['numCoins']--">-</button><input class="counter" v-model="player['numCoins']"/><button @click="player['numCoins']++">+</button></span>
        <span class="stat-item">VP: <button @click="player['numVP']--">-</button><input class="counter" v-model="player['numVP']"/><button @click="player['numVP']++">+</button></span>
        <span class="stat-item">Coffers: <button @click="player['numCoffers']--">-</button><input class="counter" v-model="player['numCoffers']"/><button @click="player['numCoffers']++">+</button></span>
        <span class="stat-item">Villagers: <button @click="player['numVillagers']--">-</button><input class="counter" v-model="player['numVillagers']"/><button @click="player['numVillagers']++">+</button></span>
        <button @click="changePlayerTurn" v-if="currentPlayerTurn === playerIndex">End Turn</button>
        <span v-if="currentPlayerTurn === playerIndex">Your turn</span>
        <span v-else>{{opponent.name}}'s turn</span>
      </div>
      <div class="deck-and-hand">
        <div class="deck">
          <div class="card-container">
            <div class="card-counter-container">{{player['deck'].length}}</div>
            <img
                v-on:click="moveCurrentSelection(player['hand'])"
                v-on:mouseover="setCurrentSelection(player['deck'])"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(player['deck'])"/>
          </div>
        </div>
        <div class="discard">
          <div class="card-container">
            <div class="card-counter-container">{{player['discard'].length}}</div>
            <img
                v-on:mouseover="setCurrentSelection(player['discard'])"
                v-on:mouseout="clearCurrentSelection()"
                class="card card-in-container"
                :src="getImageForCardArrayOrBlank(player['discard'])"/>
          </div>
        </div>
        <div class="hand">
          <img
              v-for="(card, index) in player['hand']"
              :key="index"
              v-on:click="moveCurrentSelection(player['playArea'])"
              v-on:mouseover="setCurrentSelection(player['hand'], index)"
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
import * as io from 'socket.io-client'
import axios from 'axios'
window.io = io

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const SAVE_DOMINION_GAME_URL = getFullBackendUrlForPath('/save_dominion_game')

export default {
  name: 'DominionGame',
  data () {
    return {
      currentSelection: {}, // Object with keys 'array', and 'index', and 'exists'
      gameId: 0,
      playerOrder: [],
      isInGame: false,
      playerIndex: 0,
      playerToInvite: '',
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
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numVP: 0,
        numCoffers: 0,
        numVillagers: 0,
        shownPage: 'kingdom'
      }, {
        name: '',
        notes: '',
        playArea: [],
        deck: [],
        hand: [],
        mats: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numVP: 0,
        numCoffers: 0,
        numVillagers: 0,
        shownPage: 'kingdom'
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
      hasHexes: false,

      butterBar_message: '',
      butterBar_css: ''
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
    }
  },
  mounted () {
    var socket = io.connect('http://' + window.location.hostname + ':5000')
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
          that.currentPlayerTurn = data['currentPlayerTurn']
          that.currentSelection = {}
          that.revealArea = data['revealArea']
          that.isInGame = data['isInGame']
          that.playerOrder = data['playerOrder']
          that.players = data['players']
          that.boonsDiscard = data['boonsDiscard']
          that.hexesDiscard = data['hexesDiscard']
          that.boonsDeck = data['boonsDeck']
          that.boonsReveal = data['boonsReveal']
          that.hexesDeck = data['hexesDeck']
          that.hexesReveal = data['hexesReveal']
          that.gameId = data['gameId']

          that.playerIndex = data['playerOrder'][0] === that.username ? 0 : 1
          that.nonSupplyCards = data['nonSupplyCards']
          that.kingdomCards = data['kingdomCards']
          that.vpCards = data['vpCards']
          that.treasureCards = data['treasureCards']
          that.trash = data['trash']
          that.player = that.players[that.playerIndex]
          that.opponent = that.players[1 - that.playerIndex] // Only supports a 2 player game.
          that.bane = data['bane']
          that.hexesDeck = data['hexesDeck']
          that.boonsDeck = data['boonsDeck']
          that.sidewaysCards = data['sidewaysCards']
          that.hasBane = data['hasBane']
          that.hasBoons = data['hasBoons']
          that.hasHexes = data['hasHexes']
        })
    },
    getGameData () {
      let data = {}
      data['currentPlayerTurn'] = this.currentPlayerTurn
      data['revealArea'] = this.revealArea
      data['isInGame'] = this.isInGame
      data['players'] = this.players
      data['boonsDiscard'] = this.boonsDiscard
      data['hexesDiscard'] = this.hexesDiscard
      data['boonsDeck'] = this.boonsDeck
      data['boonsReveal'] = this.boonsReveal
      data['hexesDeck'] = this.hexesDeck
      data['hexesReveal'] = this.hexesReveal
      data['gameId'] = this.gameId

      data['playerOrder'] = this.playerOrder
      data['nonSupplyCards'] = this.nonSupplyCards
      data['kingdomCards'] = this.kingdomCards
      data['vpCards'] = this.vpCards
      data['treasureCards'] = this.treasureCards
      data['trash'] = this.trash
      data['bane'] = this.bane
      data['hexesDeck'] = this.hexesDeck
      data['boonsDeck'] = this.boonsDeck
      data['sidewaysCards'] = this.sidewaysCards
      data['hasBane'] = this.hasBane
      data['hasBoons'] = this.hasBoons
      data['hasHexes'] = this.hasHexes
      return data
    },
    saveDominionGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_DOMINION_GAME_URL,
        {
          gameId: this.gameId,
          data: this.getGameData(),
          username: this.username
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        function (response) {})
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateDominionDisplayWithLatestGame () {
      let that = this
      axios.post(DOMINION_GET_LATEST_GAME_URL, {username: this.username}).then(response => {
        if (response.data === null) {
          this.isInGame = false
          return
        }
        that.updateDominionDisplayWithGameData(response.data.data)
      })
    },
    updateDominionDisplayWithGameData (gameData) {
      this.currentPlayerTurn = gameData['currentPlayerTurn']
      this.revealArea = gameData['revealArea']
      this.isInGame = gameData['isInGame']
      this.players = gameData['players']
      this.boonsDiscard = gameData['boonsDiscard']
      this.hexesDiscard = gameData['hexesDiscard']
      this.boonsDeck = gameData['boonsDeck']
      this.boonsReveal = gameData['boonsReveal']
      this.hexesDeck = gameData['hexesDeck']
      this.hexesReveal = gameData['hexesReveal']
      this.gameId = gameData['gameId']
      this.playerOrder = gameData['playerOrder']

      this.playerIndex = gameData['playerOrder'][0] === this.username ? 0 : 1
      this.nonSupplyCards = gameData['nonSupplyCards']
      this.kingdomCards = gameData['kingdomCards']
      this.vpCards = gameData['vpCards']
      this.treasureCards = gameData['treasureCards']
      this.trash = gameData['trash']
      this.player = this.players[this.playerIndex]
      this.opponent = this.players[1 - this.playerIndex] // Only supports a 2 player game.
      this.bane = gameData['bane']
      this.hexesDeck = gameData['hexesDeck']
      this.boonsDeck = gameData['boonsDeck']
      this.sidewaysCards = gameData['sidewaysCards']
      this.hasBane = gameData['hasBane']
      this.hasBoons = gameData['hasBoons']
      this.hasHexes = gameData['hasHexes']
    },
    getImageForCurrentSelection () {
      if (!this.currentSelection.exists) {
        return
      }
      if (this.currentSelection.array === this.players['deck']) {
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
      } else if (cardArray === this.player['deck']) {
        return '/static/dominion/card_images/backside_blue.jpg'
      } else if (cardArray === this.boonsDeck) {
        return '/static/dominion/card_images/Boon-back.jpg'
      } else if (cardArray === this.hexesDeck) {
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
        return false
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
        if (originalPile === this.player['deck'] && this.player['deck'].length === 0 && this.player['discard'].length !== 0) {
          this.player['deck'].push(...this.shuffle(this.player['discard']))
          this.emptyArray(this.player['discard'])
        } else if (originalPile === this.boonsDeck && this.boonsDeck.length === 0 && this.boonsDiscard.length !== 0) {
          this.boonsDeck.push(...this.shuffle(this.boonsDiscard))
          this.emptyArray(this.boonsDiscard)
        } else if (originalPile === this.hexesDeck && this.hexesDeck.length === 0 && this.hexesDiscard.length !== 0) {
          this.hexesDeck.push(...this.shuffle(this.hexesDiscard))
          this.emptyArray(this.hexesDiscard)
        }
        cardIndex = originalPile.length - 1
      }
      if (cardIndex < 0 || cardIndex >= originalPile.length) {
        return
      }
      let card = originalPile[cardIndex]
      destinationPile.push(card)
      originalPile.splice(cardIndex, 1)
      this.saveDominionGame()
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
      this.shuffle(this.player['deck'])
    },
    deckToDiscard () {
      this.player['discard'].push(...this.player['deck'])
      this.emptyArray(this.player['deck'])
    },
    deckToHand () {
      for (let i = 0; i < 5; ++i) {
        this.moveCard(this.player['deck'], undefined, this.player['hand'])
      }
    },
    handAndPlayAreaToDiscard () {
      this.player['discard'].push(...this.player['hand'])
      this.player['discard'].push(...this.player['playArea'])
      this.emptyArray(this.player['hand'])
      this.emptyArray(this.player['playArea'])
      if (this.currentSelection['array'] === this.player['hand'] || this.currentSelection['array'] === this.player['playArea']) {
        this.clearCurrentSelection()
      }
    },
    handToPlayArea () {
      this.player['playArea'].push(...this.player['hand'])
      this.emptyArray(this.player['hand'])
      if (this.currentSelection['array'] === this.player['hand']) {
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
      this.player.shownPage = 'nonSupply'
    },
    showKingdom () {
      this.player.shownPage = 'kingdom'
    },
    showBane () {
      this.player.shownPage = 'bane'
    },
    showBoons () {
      this.player.shownPage = 'boons'
    },
    showHexes () {
      this.player.shownPage = 'hexes'
    },
    showYourMats () {
      this.player.shownPage = 'yourMats'
    },
    showOpponentMats () {
      this.player.shownPage = 'opponentMats'
    },
    showTrash () {
      this.player.shownPage = 'trash'
    },
    showRevealArea () {
      this.player.shownPage = 'reveal'
    },
    showDiscard () {
      this.player.shownPage = 'discard'
    },
    showAllYourCards () {
      this.player.shownPage = 'allYourCards'
    },
    showNotes () {
      this.player.shownPage = 'notes'
    },
    showShortcuts () {
      this.player.shownPage = 'shortcuts'
    },
    changePlayerTurn () {
      this.currentPlayerTurn = 1 - this.currentPlayerTurn
    },
    handleKeyPress (event) {
      switch (event.key) {
        case 'D':
          this.handAndPlayAreaToDiscard()
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
      }
      if (!this.currentSelection['exists']) {
        return
      }
      let destinationArray = null
      switch (event.key) {
        case 'd':
          destinationArray = this.player['discard']
          break
        case 'h':
          destinationArray = this.player['hand']
          break
        case 'k':
          destinationArray = this.player['deck']
          break
        case 'm':
          destinationArray = this.player['mats']
          break
        case 'p':
          destinationArray = this.player['playArea']
          break
        case 'r':
          let currentSelectionCard = this.getCurrentSelectionCard()
          let destinationPileType = currentSelectionCard.pile_type
          let destinationPileIndex = currentSelectionCard.pile_index
          if (!destinationPileType) {
            return
          }
          switch (destinationPileType) {
            case 'vp_cards':
              destinationArray = this.vpCards[destinationPileIndex]
              break
            case 'treasure_cards':
              destinationArray = this.treasureCards[destinationPileIndex]
              break
            case 'kingdom_cards':
              destinationArray = this.kingdomCards[destinationPileIndex]
              break
            case 'non_supply_cards':
              destinationArray = this.nonSupplyCards[destinationPileIndex]
              break
          }
          break
        case 's':
          this.shuffleDeck()
          return
        case 't':
          destinationArray = this.trash
          break
        case 'v':
          destinationArray = this.revealArea
          break
        case 'o':
          destinationArray = this.opponent['hand']
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
