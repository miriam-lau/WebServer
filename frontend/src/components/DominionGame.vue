<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <button @click="generateKingdom">New Game</button><br/><br/><br/>
    <button @click="showKingdom">Show Kingdom</button>
    <button v-if="nonSupplyCards.length > 0" @click="showOtherCardPage">Show More Cards</button>
    <button v-if="hasBane" @click="showBane">Show Bane</button>
    <button v-if="hasBoons" @click="showBoons">Show Boons</button>
    <button v-if="hasHexes" @click="showHexes">Show Hexes</button>
    <button @click="showYourMats">Show Your Mats</button>
    <button @click="showOpponentMats">Show Opponent Mats</button>
    <button @click="showTrash">Show Trash</button>
    <button @click="showRevealArea">Show Reveal Area</button>
    <div v-if="player.shownPage === 'kingdom'">
      <div class="vp-treasure">
        <div class="card-container" :key="'treasure' + index" v-for="(cardArray, index) in treasureCards">
          <div class="card-counter-container">{{cardArray.length}}</div>
          <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(cardArray)" v-on:mouseout="clearCurrentSelection()" class="card card-in-container" :src="getImageForCardArrayOrBlank(cardArray)"/>
        </div>
        <div class="c"></div>
        <div class="card-container" :key="'vp' + index" v-for="(cardArray, index) in vpCards">
          <div class="card-counter-container">{{cardArray.length}}</div>
          <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(cardArray)" v-on:mouseout="clearCurrentSelection()" class="card card-in-container" :src="getImageForCardArrayOrBlank(cardArray)"/>
        </div>
      </div>
      <div class="kingdom">
        <div class="card-container" :key="index" v-for="(cardArray, index) in kingdomCards">
          <div class="card-counter-container">{{cardArray.length}}</div>
          <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(cardArray)" v-on:mouseout="clearCurrentSelection()" class="card card-in-container" :src="getImageForCardArrayOrBlank(cardArray)"/>
        </div>
      </div>
      <div class="events">
        <img class="sideways-card" :key="index" v-for="(card, index) in sidewaysCards" :src="getImageForCard(card)"/>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'non-supply'">
      <div class="non-supply">
        <div class="card-container" :key="index" v-for="(cardArray, index) in nonSupplyCards">
          <div class="card-counter-container">{{cardArray.length}}</div>
          <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(cardArray)" v-on:mouseout="clearCurrentSelection()" class="card card-in-container" :src="getImageForCardArrayOrBlank(cardArray)"/>
        </div>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'bane'">
      <div class="bane">
        <div class="card-container">
          <div class="card-counter-container">{{bane.length}}</div>
          <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(bane)" v-on:mouseout="clearCurrentSelection()" class="card card-in-container" :src="getImageForCardArrayOrBlank(bane)"/>
        </div>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'boons'">
      <div class="boons">
      </div>
    </div>
    <div v-else-if="player.shownPage === 'hexes'">
      <div class="hexes">
      </div>
    </div>
    <div v-else-if="player.shownPage === 'yourMats'">
      <div class="yourMats">
        <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(player['playArea'], index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in player['playArea']" :src="getImageForCard(card)"/>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'opponentMats'">
      <div class="opponentMats">
        <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(player['playArea'], index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in player['playArea']" :src="getImageForCard(card)"/>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'trash'">
      <div class="trash">
        <img v-on:mouseover="setCurrentSelection(trash, index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in trash" :src="getImageForCard(card)"/>
      </div>
    </div>
    <div v-else-if="player.shownPage === 'reveal'">
      <div class="revealArea">
        <img v-on:mouseover="setCurrentSelection(revealArea, index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in revealArea" :src="getImageForCard(card)"/>
      </div>
    </div>
    <img class="preview" v-if="currentSelection['exists']" :src="getImageForCurrentSelection()"/>
    <div class="c">
    </div>
    <div class="play-area">
      <img v-on:click="moveCurrentSelection(player['discard'])" v-on:mouseover="setCurrentSelection(player['playArea'], index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in player['playArea']" :src="getImageForCard(card)"/>
    </div>
    <div class="c">
    </div>
    <div class="stats">
      <span class="stat-item">Actions: <button @click="player['numActions']--">-</button><input class="counter" v-model="player['numActions']"/><button @click="player['numActions']++">+</button></span>
      <span class="stat-item">Buys: <button @click="player['numBuys']--">-</button><input class="counter" v-model="player['numBuys']"/><button @click="player['numBuys']++">+</button></span>
      <span class="stat-item">Coins: <button @click="player['numCoins']--">-</button><input class="counter" v-model="player['numCoins']"/><button @click="player['numCoins']++">+</button></span>
      <span class="stat-item">Coffers: <button @click="player['numCoffers']--">-</button><input class="counter" v-model="player['numCoffers']"/><button @click="player['numCoffers']++">+</button></span>
      <span class="stat-item">Villagers: <button @click="player['numVillagers']--">-</button><input class="counter" v-model="player['numVillagers']"/><button @click="player['numVillagers']++">+</button></span>
    </div>
    <div class="deck-and-hand">
      <div class="deck">
        <img v-on:mouseover="setCurrentSelection(player['deck'])" v-on:mouseout="clearCurrentSelection()" v-on:click="moveCurrentSelection(player['hand'])" class="card" :src="getImageForCardArrayOrBlank(player['deck'])"/>
      </div>
      <div class="discard">
        <img v-on:mouseover="setCurrentSelection(player['discard'])" v-on:mouseout="clearCurrentSelection()" class="card" :src="getImageForCardArrayOrBlank(player['discard'])"/>
      </div>
      <div class="hand">
        <img v-on:click="moveCurrentSelection(player['playArea'])" v-on:mouseover="setCurrentSelection(player['hand'], index)" v-on:mouseout="clearCurrentSelection()" class="card" :key="index" v-for="(card, index) in player['hand']" :src="getImageForCard(card)"/>
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

const GENERATE_KINGDOM_URL = getFullBackendUrlForPath('/generate_dominion_kingdom_for_online_game')

/*
# Hand to Trash - del
# Reveal all discard - r
# Reveal N cards from deck (or add to revealed area) - #
# Gain kingdom card on top of deck - t
# Revealed card to play area - p
# Revealed card to top of deck - t
# Kingdom card to trash - del
# Reveal all trash - r
# Player hand to other player hand - z
# Unimplemented - Stash, Secret Passage - haven - just set aside face up. native village, island - set aside
#   philosopher's stone - need count of cards in deck and discard, coin of the realm - tavern mat, ratcatcher, gear, guide, miser, transmogrify, distant lands
#   type reason for set aside card, stash
# Reveal bottom card of deck - ?
# Shuffle deck - s
# Always display num cards in deck, buttons for actions, buttons for coffers, buttons for villagers
# Return kingdom card to the original pile? (page line, peasant line)
# Put whole deck in discard
# Implement notepad
# Reveal all cards you own together
# Move from play area to set aside - ?
# Type in notes who has the flag and artifacts
*/

export default {
  name: 'DominionGame',
  data () {
    return {
      currentSelection: {}, // Object with keys 'array', and 'index', and 'exists'
      playerIndex: 0,
      nonSupplyCards: [],
      kingdomCards: [],
      vpCards: [],
      treasureCards: [],
      sidewaysCards: [],
      trash: [],
      revealArea: [],
      players: [{
        playArea: [],
        deck: [],
        hand: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numCoffers: 0,
        numVillagers: 0,
        shownPage: 'kingdom'
      }, {
        playArea: [],
        deck: [],
        hand: [],
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
      boons: [],
      boonsDiscard: [],
      bane: [],
      hexes: [],
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
    this.generateKingdom()
    this.player = this.players[0]
  },
  methods: {
    generateKingdom () {
      let that = this
      callAxiosAndSetButterBar(
        this,
        GENERATE_KINGDOM_URL,
        {},
        'Generated Kingdom',
        'Failed to generate kingdom.',
        function (response) {
          that.currentSelection = {}
          that.revealArea = []
          that.playerIndex = 0
          that.players = [{
            playArea: [],
            deck: [],
            hand: [],
            discard: [],
            numActions: 0,
            numBuys: 0,
            numCoins: 0,
            numCoffers: 0,
            numVillagers: 0,
            shownPage: 'kingdom'
          }, {
            playArea: [],
            deck: [],
            hand: [],
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

          that.butterBar_message = ''
          that.butterBar_css = ''
          let data = response['data']
          that.nonSupplyCards = data['non_supply_cards']
          that.kingdomCards = data['kingdom_cards']
          that.vpCards = data['vp_cards']
          that.treasureCards = data['treasure_cards']
          that.trash = data['trash']
          that.players[0]['deck'] = data['player_1_deck']
          that.players[1]['deck'] = data['player_2_deck']
          that.player = that.players[that.playerIndex]
          that.opponent = that.players[1 - that.playerIndex] // Only supports a 2 player game.
          that.bane = data['bane']
          that.hexes = data['hexes']
          that.boons = data['boons']
          that.sidewaysCards = data['sideways_cards']
          that.hasBane = that.bane.length > 0
          that.hasBoons = that.boons.length > 0
          that.hasHexes = that.hexes.length > 0
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
          this.player['discard'] = []
        }
        cardIndex = originalPile.length - 1
      }
      let card = originalPile[cardIndex]
      destinationPile.push(card)
      originalPile.splice(cardIndex, 1)
      return true
    },
    moveCurrentSelection (destinationPile) {
      if (!this.currentSelection.exists) {
        return
      }
      let success = this.moveCard(this.currentSelection['array'], this.currentSelection['index'], destinationPile)
      if (!success) {
        return
      }
      if (this.currentSelection.index === undefined) {
        if (this.currentSelection.array.length > 0) {
          this.setCurrentSelection(this.currentSelection.array)
        } else {
          this.clearCurrentSelection()
        }
      } else {
        if (this.currentSelection.array.length > this.currentSelection.index) {
          this.setCurrentSelection(this.currentSelection.array, this.currentSelection.index)
        } else {
          this.clearCurrentSelection()
        }
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
      this.player.shownPage = 'non-supply'
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
        case 't':
          destinationArray = this.trash
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
        case 'v':
          destinationArray = this.revealArea
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
