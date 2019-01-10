<template>
  <div>
    <div :style="'height:' + height(card)" class="outer-card-with-attachments" v-for="(card, index) in cardArray" :key="index">
      <div class="card-with-attachments">
        <div v-if="card.damage" :style="'top:' + damageVerticalPosition(card)" class="card-with-attachments-token">{{card.damage}}D</div>
        <div v-if="card.resources" :style="'top:' + resourceVerticalPosition(card)" class="card-with-attachments-token">{{card.resources}}R</div>
        <div v-if="card.progress" :style="'top:' + progressVerticalPosition(card)" class="card-with-attachments-token">{{card.progress}}P</div>
        <img v-for="(attachment, index) in card['attachments']" :key="index"
            v-on:click="handleClick()"
            v-on:mouseover="setCurrentCardSelection($parent, card['attachments'], index)"
            v-on:mouseout="clearCurrentCardSelection($parent)"
            class="card-attachment"
            :style="'top:' + getAttachmentVerticalPosition(index)"
            :src="$parent.getImageForCard(attachment)"/>
        <img
            v-on:click="handleClick()"
            v-on:mouseover="setCurrentCardSelection($parent, cardArray, index)"
            v-on:mouseout="clearCurrentCardSelection($parent)"
            class="card-attachment"
            :style="'top:' + getAttachmentVerticalPosition(card['attachments'].length)"
            :src="$parent.getImageForCard(card)"/>
      </div>
    </div>
  </div>
</template>
<script>
import { moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection } from '../../../common/card_games'

/**
 * Renders the cards represented by {@code card}.
 */
export default {
  name: 'CardWithAttachmentsList',
  props: {
    /**
     * Nullable. Where to move the top card of the card stack to on left click.
     */
    defaultMoveArray: Array,
    /**
     * The card array the current card belongs to.
     */
    cardArray: Array
  },
  methods: {
    height (card) {
      return 'calc(var(--card-height)*0.11 * ' + card['attachments'].length + ' + var(--card-height))'
    },
    damageVerticalPosition (card) {
      return 'calc(var(--card-height)*0.11*' + card['attachments'].length + ' + var(--card-height)/2 - 1.2vw)'
    },
    progressVerticalPosition (card) {
      return 'calc(var(--card-height)*0.11*' + card['attachments'].length + ' + var(--card-height)/2)'
    },
    resourceVerticalPosition (card) {
      return 'calc(var(--card-height)*0.11*' + card['attachments'].length + ' + var(--card-height)/2 + 1.2vw)'
    },
    getAttachmentVerticalPosition (index) {
      return 'calc(var(--card-height) * 0.11 * ' + index
    },
    setCurrentCardSelection: setCurrentCardSelection,
    clearCurrentCardSelection: clearCurrentCardSelection,
    handleClick () {
      if (this.defaultMoveArray) {
        moveCurrentCardSelection(this.$parent, this.defaultMoveArray)
      }
    }
  }
}
</script>
