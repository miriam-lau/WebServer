<template>
  <div>
    <div :style="'height:' + getHeight(card) + '; width: ' + cardWidth + '; margin:' + cardMargin" class="lotr-card-list-outer" v-for="(card, index) in cardArray" :key="index">
      <div v-if="card.resources" :style="'top:' + resourceVerticalPosition(card) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card.resources}}R</div>
      <div v-if="card.damage" :style="'top:' + damageVerticalPosition(card) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card.damage}}D</div>
      <div v-if="card.progress" :style="'top:' + progressVerticalPosition(card) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card.progress}}P</div>
      <img v-for="(attachment, index) in card['attachments']" :key="index"
          v-on:click="handleClick(attachment, true)"
          v-on:mouseover="handleMouseOver(card['attachments'], index)"
          v-on:mouseout="handleMouseOut()"
          class="lotr-card-list-inner"
          :style="getStyle(attachment, index)"
          :src="getImageForCard(attachment)"/>
      <img
          v-on:click="handleClick(card, false)"
          v-on:mouseover="handleMouseOver(cardArray, index)"
          v-on:mouseout="handleMouseOut()"
          class="lotr-card-list-inner"
          :style="getStyle(card, card['attachments'].length)"
          :src="getImageForCard(card)"/>
    </div>
  </div>
</template>
<script>
import { moveCurrentCard, setCurrentCard, clearCurrentCard } from '../../../common/card_games'

/**
 * Renders the cards represented by {@code cardArray} as a list. This is similar to CardList but can handle rendering
 * of attachments and tokens used in LOTR.
 * When a card is hovered over, the currently selected card is set to this card array and index of the card within it.
 * See the README.md file in this directory for more information on the currently selected card and usage.
 *
 * When the card is no longer hovered over, the currently selected card is cleared.
  */
export default {
  name: 'LotrCardList',
  props: {
    /**
     * The array of cards to render.
     */
    cardArray: Array,
    /**
     * The css width of the card.
     */
    cardWidth: String,
    /**
     * The css height of the card.
     */
    cardHeight: String,
    /**
     * The css margin of the outer container surrounding the card.
     */
    cardMargin: String,
    /**
     * This is called with a card from {@code cardArray} to get the image used to render the card.
     */
    getImageForCard: Function,
    /**
     * Nullable. If {@code defaultMoveArray} is passed in, when a card is clicked, it will be moved to that array. Only one
     *     of this or getMoveArray may be set.
     */
    defaultMoveArray: Array,
    /**
     * Nullable. If {@code getMoveArray} is passed in, when a card is clicked, the function will return the
     * array the card is to be moved to. Only one of this or defaultMoveArray may be set.
     */
    getMoveArray: Function,
    /**
     * Nullable. Passed to moveCard
     */
    afterMoveCallback: Function,
    /**
     * Nullable. Passed to moveCard.
     */
    beforeMoveCallback: Function,
    /**
     * Nullable. Whether or not to populate the currently selected card on mouseover.
     */
    shouldNotPopulateCurrentCard: Boolean
  },
  methods: {
    handleClick (card, isAttachment) {
      if (this.getMoveArray && this.defaultMoveArray) {
        throw new Error('Multiple move array conditions passed in.')
      }
      let array
      if (this.defaultMoveArray) {
        array = this.defaultMoveArray
      } else if (this.getMoveArray) {
        array = this.getMoveArray(card, isAttachment)
      }
      if (array) {
        moveCurrentCard(this.$parent, array, { beforeMoveCallback: this.beforeMoveCallback, afterMoveCallback: this.afterMoveCallback })
      }
    },
    getStyle (card, index) {
      let style = 'top:' + this.getCardVerticalPosition(index) + '; height: ' + this.cardHeight + '; width: ' + this.cardWidth
      if (card['exhausted']) {
        style += ';filter: brightness(0.5)'
      }
      return style
    },
    getHeight (card) {
      return 'calc(' + this.cardHeight + '*.11 * ' + card['attachments'].length + ' + ' + this.cardHeight + ')'
    },
    resourceVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '*0.11*' + card['attachments'].length + ' + ' + this.cardHeight + '/2 - 1.2vw)'
    },
    damageVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '*0.11*' + card['attachments'].length + ' + ' + this.cardHeight + '/2)'
    },
    progressVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '*0.11*' + card['attachments'].length + ' + ' + this.cardHeight + '/2 + 1.2vw)'
    },
    getCardVerticalPosition (index) {
      return 'calc(' + this.cardHeight + ' * 0.11 * ' + index + ')'
    },
    getTokenLeftPosition () {
      return 'calc(' + this.cardWidth + '/2 - 0.45vw)'
    },
    handleMouseOver (cardArray, index) {
      if (this.shouldNotPopulateCurrentCard) {
        return
      }
      setCurrentCard(this.$parent, cardArray, index)
    },
    handleMouseOut () {
      if (this.shouldNotPopulateCurrentCard) {
        return
      }
      clearCurrentCard(this.$parent)
    }
  }
}
</script>
