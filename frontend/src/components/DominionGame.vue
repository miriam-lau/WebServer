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
      <button @click="showOpponentMats">Opponent Mats</button>
      <button @click="showTrash">Trash</button>
      <button @click="showRevealArea">Revealed</button>
      <button @click="showDiscard">Discard</button>
      <button @click="showAllYourCards">All your cards</button>
      <button @click="showNotes">Notes</button>
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
              v-for="(card, index) in player['playArea']"
              :key="index"
              v-on:click="moveCurrentSelection(player['discard'])"
              v-on:mouseover="setCurrentSelection(player['playArea'], index)"
              v-on:mouseout="clearCurrentSelection()"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="player.shownPage === 'opponentMats'">
        <div class="opponent-mats">
          <img
              v-for="(card, index) in player['playArea']"
              :key="index"
              v-on:click="moveCurrentSelection(player['discard'])"
              v-on:mouseover="setCurrentSelection(player['playArea'], index)"
              v-on:mouseout="clearCurrentSelection()"
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
              v-for="(card, index) in [].concat(player['deck'], player['discard'], player['playArea'], player['hand'], player['mat'])"
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

const GENERATE_KINGDOM_URL = getFullBackendUrlForPath('/generate_dominion_kingdom_for_online_game')

export default {
  name: 'DominionGame',
  data () {
    return {
      currentSelection: {}, // Object with keys 'array', and 'index', and 'exists'
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
        mat: [],
        hand: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numCoffers: 0,
        numVillagers: 0,
        shownPage: 'kingdom'
      }, {
        name: '',
        notes: '',
        playArea: [],
        deck: [],
        hand: [],
        mat: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
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
    window.addEventListener('keyup', this.handleKeyPress)
    this.playerToInvite = this.defaultPlayerToInvite()
  },
  computed: {
    username () {
      return store.state.username
    }
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
        GENERATE_KINGDOM_URL,
        {
          player1: randomizedPlayers[0],
          player2: randomizedPlayers[1]
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        function (response) {
          that.currentPlayerTurn = 0
          that.currentSelection = {}
          that.revealArea = []
          that.isInGame = true
          that.players = [{
            name: '',
            notes: '',
            playArea: [],
            deck: [],
            hand: [],
            mat: [],
            discard: [],
            numActions: 0,
            numBuys: 0,
            numCoins: 0,
            numCoffers: 0,
            numVillagers: 0,
            shownPage: 'kingdom'
          }, {
            name: '',
            notes: '',
            playArea: [],
            deck: [],
            hand: [],
            mat: [],
            discard: [],
            numActions: 0,
            numBuys: 0,
            numCoins: 0,
            numCoffers: 0,
            numVillagers: 0,
            shownPage: 'kingdom'
          }]
          that.boonsDiscard = []
          that.hexesDiscard = []
          that.boonsDeck = []
          that.boonsReveal = []
          that.hexesDeck = []
          that.hexesReveal = []

          that.butterBar_message = ''
          that.butterBar_css = ''
          let data = response['data']
          that.playerIndex = data['player_order'][0] === that.username ? 0 : 1
          that.nonSupplyCards = data['non_supply_cards']
          that.kingdomCards = data['kingdom_cards']
          that.vpCards = data['vp_cards']
          that.treasureCards = data['treasure_cards']
          that.trash = data['trash']
          that.players[0]['deck'] = data['player_1_deck']
          that.players[1]['deck'] = data['player_2_deck']
          that.players[0]['name'] = data['player_order'][0]
          that.players[1]['name'] = data['player_order'][1]
          that.player = that.players[that.playerIndex]
          that.opponent = that.players[1 - that.playerIndex] // Only supports a 2 player game.
          that.bane = data['bane']
          that.hexesDeck = data['hexes']
          that.boonsDeck = data['boons']
          that.sidewaysCards = data['sideways_cards']
          that.hasBane = that.bane.length > 0
          that.hasBoons = that.boonsDeck.length > 0
          that.hasHexes = that.hexesDeck.length > 0
        })
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
    changePlayerTurn () {
      this.currentPlayerTurn = 1 - this.currentPlayerTurn
    },
    handleKeyPress (event) {
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
          destinationArray = this.player['mat']
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
        case 'z': // For lack of a better letter
          this.deckToDiscard()
          return
      }
      if (!destinationArray) {
        return
      }
      this.moveCurrentSelection(destinationArray)
    }
  }
}
</script>
