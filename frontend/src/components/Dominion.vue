<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <button @click="generateKingdom">Generate Kingdom</button><br/>
    <div class="dominion_section" v-if="normalCards.length > 0">
      <h3>Kingdom Cards:</h3>
      <img class="dominion_card" :key="card.name" v-for="card in normalCards" :src="getImageForCard(card)"/>
    </div>
    <div class="clearfix"/>
    <div class="dominion_float dominion_section" v-if="bane != null">
      <h3>Bane:</h3>
      <img class="dominion_card" :src="getImageForCard(bane)"/>
    </div>
    <div class="dominion_float dominion_section" v-if="sidewaysCards.length > 0">
      <h3>Events, Landmarks, and Projects:</h3>
      <img class="dominion_sideways_card" :key="card.name" v-for="card in sidewaysCards" :src="getImageForCard(card)"/>
    </div>
    <div class="dominion_float dominion_section" v-if="supplementaryCards.length > 0">
      <h3>Supplementary Cards:</h3>
      <img class="dominion_card" :key="card.name" v-for="card in supplementaryCards" :src="getImageForCard(card)"/>
    </div>
    <div v-if="boons.length > 0">
      <div class="clearfix"/>
      <div class="dominion_float dominion_section">
        <h3>Boons:</h3>
        <img class="dominion_card" :key="card.name" v-for="card in boons" :src="getImageForCard(card)"/>
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/dominion.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath } from '../common/utils'

const GENERATE_KINGDOM_URL = getFullBackendUrlForPath('/generate_dominion_kingdom')

export default {
  name: 'Dominion',
  data () {
    return {
      normalCards: [],
      sidewaysCards: [],
      bane: null,
      supplementaryCards: {},
      boons: [],

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
          that.normalCards = data['normal_cards']
          that.sidewaysCards = data['sideways_cards']
          that.bane = data['bane']
          let supplementaryCards = []
          if (data['should_include_platinum_and_colony']) {
            supplementaryCards.push({name: 'Colonies / Platinums', type: 'card', set: 'Prosperity'})
          }
          if (data['should_include_shelters']) {
            supplementaryCards.push({name: 'Shelters', type: 'card', set: 'Dark Ages'})
          }
          if (data['should_include_potion']) {
            supplementaryCards.push({name: 'Potion', type: 'card', set: 'Alchemy'})
          }
          that.supplementaryCards = supplementaryCards
          that.boons = data['boons']
        })
    },
    getImageForCard (card) {
      if (card.set === 'Renaissance' || card.name === 'Shelters' || card.name.indexOf('/') !== -1) {
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
      imageName = '/static/dominion/old_card_images/' + imageName + '.jpg'
      return imageName
    },
    getDigitalImageForCard (card) {
      let imageName = card.name
      imageName = imageName.replace(/ /g, '_')
      imageName = '/static/dominion/card_images/' + imageName + 'Digital.jpg'
      return imageName
    }
  }
}

</script>
