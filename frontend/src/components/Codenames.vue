<template>
  <div class="codenames">
    <div class="codenames-title">Codenames</div>
    <div class="codenames-gameboard">
      <div class="codenames-codeword-row" :key="rowIndex" v-for="(codewordRow, rowIndex) in codewords">
        <div class="codenames-codeword-item" :key="colIndex" v-for="(codeword, colIndex) in codewordRow">
          {{ codeword }}
        </div>
      </div>
    </div>
    <div class="codenames-agent-board">
      <div class="codenames-agent-row" :key="rowIndex" v-for="(agentRow, rowIndex) in agentLocations">
        <div class="codenames-agent-item" :key="colIndex" v-for="(agent, colIndex) in agentRow">
          {{ agent }}
        </div>
      </div>
    </div>
    <div class="codenames-action-line">
      <div v-if="playerTurn == this.getUsername() && turnType == 0">
        <div class="codenames-given-hint">Given hint: {{ receivedHintWord }}. Number of words: {{ receivedHintNumber }}</div>
        <div>Click on the words to make guesses or here when finished. <button v-on:click="endTurn">Done</button></div>
      </div>
      <div v-else-if="playerTurn == this.getUsername() && turnType == 1">
        Give a hint: <input v-model="newHintWord" placeholder='Hint word'/> Number of words: <input v-model="newHintNumber" placeholder="Hint number"/>
      </div>
      <div v-else-if="playerTurn != this.getUsername() && turnType == 0">
        Waiting for {{playerTurn}} to guess words.
      </div>
      <div v-else-if="playerTurn != this.getUsername() && turnType == 1">
        Waiting for {{playerTurn}} to give a hint.
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/codenames.css"
</style>
<script>
import { mapGetters } from 'vuex'

var LocationEnum = {
  BYSTANDER: 1,
  AGENT: 2,
  ASSASSIN: 3
}

export default {
  name: 'Codenames',
  data () {
    return {
      codewords: [['Hollywood', 'Screen', 'Play', 'Marble', 'Dinosaur'], ['Cat', 'Pitch', 'Bond', 'Greece', 'Deck'], ['Spike', 'Center', 'Vacuum', 'Unicorn', 'Undertaker'], ['Sock', 'Loch Ness', 'Horse', 'Berlin', 'Platypus'], ['Port', 'Chest', 'Box', 'Compound', 'Ship']],
      receivedHintWord: 'Bond',
      receivedHintNumber: 3,
      newHintWord: '',
      newHintNumber: '',
      agentLocations: [[LocationEnum.BYSTANDER, LocationEnum.AGENT, LocationEnum.AGENT, LocationEnum.ASSASSIN, LocationEnum.AGENT], [LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.AGENT], [LocationEnum.ASSASSIN, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER], [LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.AGENT], [LocationEnum.ASSASSIN, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER]],
      playerTurn: 'James',
      timeTokensUsed: 5,
      turnType: 1
    }
  },
  methods: {
    ...mapGetters(['getUsername'])
  }
}
</script>
