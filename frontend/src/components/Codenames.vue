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
      <div v-if="playerTurn == username && turnType == 0">
        <div class="codenames-given-hint">Given hint: {{ receivedHintWord }}. Number of words: {{ receivedHintNumber }}</div>
        <div>Click on the words to make guesses or here when finished. <button v-on:click="endTurn">Done</button></div>
      </div>
      <div v-else-if="playerTurn == username && turnType == 1">
        Give a hint: <input v-model="newHintWord" placeholder='Hint word'/> Number of words: <input v-model="newHintNumber" placeholder="Hint number"/>
      </div>
      <div v-else-if="playerTurn != username && turnType == 0">
        Waiting for {{playerTurn}} to guess words.
      </div>
      <div v-else-if="playerTurn != username && turnType == 1">
        Waiting for {{playerTurn}} to give a hint.
      </div>
    </div>
  </div>
</template>

<script>

var LocationEnum = {
  BYSTANDER: 1,
  AGENT: 2,
  ASSASSIN: 3
}

export default {
  name: 'Codenames',
  data () {
    return {
      // TODO: Get username passed into Vuex so that this changes immediately when the username changes.
      username: this.$cookies.get('username'),
      codewords: [['Hollywood', 'Screen', 'Play', 'Marble', 'Dinosaur'], ['Cat', 'Pitch', 'Bond', 'Greece', 'Deck'], ['Spike', 'Center', 'Vacuum', 'Unicorn', 'Undertaker'], ['Sock', 'Loch Ness', 'Horse', 'Berlin', 'Platypus'], ['Port', 'Chest', 'Box', 'Compound', 'Ship']],
      receivedHintWord: 'Bond',
      receivedHintNumber: 3,
      newHintWord: '',
      newHintNumber: '',
      agentLocations: [[LocationEnum.BYSTANDER, LocationEnum.AGENT, LocationEnum.AGENT, LocationEnum.ASSASSIN, LocationEnum.AGENT], [LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.AGENT], [LocationEnum.ASSASSIN, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER], [LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.AGENT], [LocationEnum.ASSASSIN, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER, LocationEnum.BYSTANDER]],
      playerTurn: 'James',
      timeTokensUsed: 5,
      turnType: 0
    }
  }
}
</script>
