<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <button @click="generateKingdom">New Game</button><br/>
    <div class="vp_treasure">
      <img v-on:click="moveToDiscard(cardArray, cardArray.length - 1); setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseover="setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseout="clearHoverCard()" :key="index" v-for="(cardArray, index) in treasureCards" class="card" :src="getImageForCardArrayOrBlank(cardArray)"/>
      <img v-on:click="moveToDiscard(cardArray, cardArray.length - 1); setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseover="setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseout="clearHoverCard()" :key="index" v-for="(cardArray, index) in vpCards" class="card" :src="getImageForCardArrayOrBlank(cardArray)"/>
    </div>
    <div class="kingdom">
      <img v-on:click="moveToDiscard(cardArray, cardArray.length - 1); setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseover="setHoverCard(cardArray, cardArray.length - 1)" v-on:mouseout="clearHoverCard()" :key="index" v-for="(cardArray, index) in kingdomCards" class="card" :src="getImageForCardArrayOrBlank(cardArray)"/>
    </div>
    <div class="non_kingdom">
      <img class="sideways_card" :key="index" v-for="(card, index) in sidewaysCards" :src="getImageForCard(card)"/>
    </div>
    <div class="preview" v-if="hasHoverCard">
      <img :src="getImageForCard(hoverCardArrayAndIndex['array'][hoverCardArrayAndIndex['index']])"/>
    </div>
    <div class="c">
    </div>
    <div class="play_area">
      <img v-on:click="moveToDiscard(players[playerIndex]['playArea'], index); clearHoverCard()" v-on:mouseover="setHoverCard(players[playerIndex]['playArea'], index)" v-on:mouseout="clearHoverCard()" class="card" :key="index" v-for="(card, index) in players[playerIndex]['playArea']" :src="getImageForCard(card)"/>
    </div>
    <div class="c">
    </div>
    <div class="stats">
      Actions: <button @click="players[playerIndex]['numActions']--">-</button><input class="counter" v-model="players[playerIndex]['numActions']"/><button @click="players[playerIndex]['numActions']++">+</button>
      Buys: <button @click="players[playerIndex]['numBuys']--">-</button><input class="counter" v-model="players[playerIndex]['numBuys']"/><button @click="players[playerIndex]['numBuys']++">+</button>
      Coins: <button @click="players[playerIndex]['numCoins']--">-</button><input class="counter" v-model="players[playerIndex]['numCoins']"/><button @click="players[playerIndex]['numCoins']++">+</button>
      Coffers: <button @click="players[playerIndex]['numCoffers']--">-</button><input class="counter" v-model="players[playerIndex]['numCoffers']"/><button @click="players[playerIndex]['numCoffers']++">+</button>
      Villagers: <button @click="players[playerIndex]['numVillagers']--">-</button><input class="counter" v-model="players[playerIndex]['numVillagers']"/><button @click="players[playerIndex]['numVillagers']++">+</button>
    </div>
    <div class="deck_and_hand">
      <div class="deck">
        <img v-if="players[playerIndex]['deck'].length > 0" v-on:click="moveCardFromDeckToHand()" class="card" src="/static/dominion/card_images/backside_blue.jpg"/>
        <img v-else class="card" v-on:click="moveCardFromDeckToHand()" src="/static/dominion/card_images/_blank.jpg"/>
      </div>
      <div class="discard">
        <img v-on:mouseover="setHoverCard(players[playerIndex]['discard'], players[playerIndex]['discard'].length - 1)" v-on:mouseout="clearHoverCard()" class="card" :src="getImageForCardArrayOrBlank(players[playerIndex]['discard'])"/>
      </div>
      <div class="hand">
        <img v-on:click="moveToPlayArea(players[playerIndex]['hand'], index); clearHoverCard()" v-on:mouseover="setHoverCard(players[playerIndex]['hand'], index)" v-on:mouseout="clearHoverCard()" class="card" :key="index" v-for="(card, index) in players[playerIndex]['hand']" :src="getImageForCard(card)"/>
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
# Deck to hand - left click
# Hand to Discard - d
# Hand to Trash - del
# Reveal all discard - r
# Reveal N cards from deck (or add to revealed area) - #
# Deck to discard - d
# Gain kingdom card on top of deck - t
# Gain kingdom card to discard - left click
# hand to play area - left click
# Revealed card to play area - p
# Revealed card to hand - h
# Revealed card to discard - d
# Revealed card to top of deck - t
# Gain kingdom card to hand - h
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
# Set aside cards to discard - d
# Set aside cards to hand - h
# Type in notes who has the flag and artifacts
*/

export default {
  name: 'DominionGame',
  data () {
    return {
      hasHoverCard: false,
      hoverCardArrayAndIndex: {}, // Object with keys 'array', and 'index'
      playerIndex: 0,
      nonSupplyCards: [],
      kingdomCards: [],
      vpCards: [],
      treasureCards: [],
      sidewaysCards: [],
      trash: [],
      players: [{
        playArea: [],
        deck: [],
        hand: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numCoffers: 0,
        numVillagers: 0
      }, {
        playArea: [],
        deck: [],
        hand: [],
        discard: [],
        numActions: 0,
        numBuys: 0,
        numCoins: 0,
        numCoffers: 0,
        numVillagers: 0
      }],
      boons: [],
      boonsDiscard: [],
      bane: [],
      hexes: [],
      hexesDiscard: [],

      butterBar_message: '',
      butterBar_css: ''
    }
  },
  components: {
    ButterBar
  },
  created () {
    this.generateKingdom()
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
          let data = response['data']
          that.nonSupplyCards = data['non_supply_cards']
          that.kingdomCards = data['kingdom_cards']
          that.vpCards = data['vp_cards']
          that.treasureCards = data['treasure_cards']
          that.trash = data['trash']
          that.players[0]['deck'] = data['player_1_deck']
          that.players[1]['deck'] = data['player_2_deck']
          that.bane = data['bane']
          that.hexes = data['hexes']
          that.boons = data['boons']
          that.sidewaysCards = data['sideways_cards']
        })
    },
    getImageForCard (card) {
      if (card.set === 'Renaissance') {
        return this.getOldImageForCard(card)
      } else {
        return this.getDigitalImageForCard(card)
      }
    },
    getDigitalImageForCard (card) {
      let imageName = card.name
      imageName = imageName.replace(/ /g, '_')
      imageName = '/static/dominion/card_images/' + imageName + 'Digital.jpg'
      return imageName
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
    getImageForCardArrayOrBlank (cardArray) {
      if (cardArray.length === 0) {
        return '/static/dominion/card_images/_blank.jpg'
      } else {
        return this.getImageForCard(cardArray[cardArray.length - 1])
      }
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
    moveCard (originalPile, cardIndex, destinationPile) {
      if (cardIndex < 0) {
        return
      }
      let card = originalPile[cardIndex]
      destinationPile.push(card)
      this.$delete(originalPile, cardIndex)
    },
    moveToDiscard (originalPile, cardIndex) {
      this.moveCard(originalPile, cardIndex, this.players[this.playerIndex]['discard'])
    },
    moveToPlayArea (originalPile, cardIndex) {
      this.moveCard(originalPile, cardIndex, this.players[this.playerIndex]['playArea'])
    },
    moveToHand (originalPile, cardIndex) {
      this.moveCard(originalPile, cardIndex, this.players[this.playerIndex]['hand'])
    },
    moveCardFromDeckToHand () {
      if (this.players[this.playerIndex]['deck'].length === 0 && this.players[this.playerIndex]['discard'].length !== 0) {
        this.players[this.playerIndex]['deck'] = this.shuffle(this.players[this.playerIndex]['discard'])
        this.players[this.playerIndex]['discard'] = []
      }
      this.moveCard(this.players[this.playerIndex]['deck'], 0, this.players[this.playerIndex]['hand'])
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
    setHoverCard (cardArray, index) {
      if (index < 0) {
        this.clearHoverCard()
        return
      }
      this.hasHoverCard = true
      this.hoverCardArrayAndIndex = {
        array: cardArray,
        index: index
      }
    },
    clearHoverCard () {
      this.hoverCardArrayAndIndex = {}
      this.hasHoverCard = false
    }
  }
}
</script>
