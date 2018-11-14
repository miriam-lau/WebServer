<template>
  <div class="codenames">
    <div class="codenames-title">Codenames</div>
    <div class="codenames-new-game-line">
      Player to invite:
          <input v-model="playerToInvite" placeholder='Player to Invite'/>
          <button v-on:click="newGame">New Game</button>
    </div>
    <div class="codenames-gameboard">
      <div class="codenames-codeword-row" :key="rowIndex" v-for="(codewordRow, rowIndex) in codewords">
        <div :class="'codenames-word-status-' + codeword['status'] + ' codenames-codeword-item'" :key="colIndex" v-for="(codeword, colIndex) in codewordRow" @click="guess(codeword['word'])">
          {{ codeword['word'] }}
        </div>
      </div>
    </div>
    <div class="codenames-location-board">
      <div class="codenames-location-row" :key="rowIndex" v-for="(locationRow, rowIndex) in locations">
        <div :class="'codenames-locationtype-' + location + ' codenames-location-item'" :key="colIndex" v-for="(location, colIndex) in locationRow">

        </div>
      </div>
    </div>
    <div class="codenames-status-line">
      <span>Time tokens used: {{timeTokensUsed}}.</span>&nbsp;
      <span v-if="assassinFound && gameOver">Assassin found. You lose.</span>
      <span v-else-if="!assassinFound && gameOver">All agents found. You win!</span>
    </div>
    <div v-if="turnType == 'guess'" class="codenames-given-hint">Given hint: {{ currentHintWord }}. Number of words: {{ currentHintNumber }}</div>
    <div v-if="!gameOver" class="codenames-action-line">
      <div v-if="isCurrentPlayerTurn && turnType == 'guess'">
        <div>Click on the words to make guesses or here when finished. <button @click="endGuesses">Done</button></div>
      </div>
      <div v-else-if="isCurrentPlayerTurn && turnType == 'give_hint'">
        Give a hint: <input v-model="newHintWord" placeholder='Hint word'/>
        Number of words: <input v-model="newHintNumber" placeholder="Hint number"/>
        <button @click="giveHint">Give Hint</button>
      </div>
      <div v-else-if="!isCurrentPlayerTurn && turnType == 'guess'">
        Waiting for {{otherPlayer}} to guess words.
      </div>
      <div v-else-if="!isCurrentPlayerTurn && turnType == 'give_hint'">
        Waiting for {{otherPlayer}} to give a hint.
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/codenames.css"
</style>
<script>
import { mapGetters } from 'vuex'
import axios from 'axios'
import * as io from 'socket.io-client'
window.io = io

const CODENAMES_CREATE_GAME_URL = 'http://' + window.location.hostname + ':5000/codenames_create_game'
const CODENAMES_GET_LATEST_GAME_URL = 'http://' + window.location.hostname + ':5000/codenames_get_latest_game'
const CODENAMES_GIVE_HINT_URL = 'http://' + window.location.hostname + ':5000/codenames_give_hint'
const CODENAMES_END_GUESSES_URL = 'http://' + window.location.hostname + ':5000/codenames_end_guesses'
const CODENAMES_GUESS_URL = 'http://' + window.location.hostname + ':5000/codenames_guess'

export default {
  name: 'Codenames',
  data () {
    return {
      assassinFound: false,
      gameOver: false,
      gameId: 0,
      player1: '',
      player2: '',
      turnNumber: 0,
      turnType: '',
      locations: [],
      codewords: [],
      currentHintWord: '',
      currentHintNumber: 0,
      newHintWord: '',
      newHintNumber: ''
    }
  },
  computed: {
    isCurrentPlayerTurn () {
      var isCurrentUserPlayer1 = this.getUsername() === this.player1
      var isPlayer1Turn = this.turnNumber % 2 === 0
      return isCurrentUserPlayer1 === isPlayer1Turn
    },
    timeTokensUsed () {
      var timeTokens = this.turnNumber - 1
      if (this.turnType === 'give_hint') {
        timeTokens += 1
      }
      return timeTokens
    },
    playerToInvite () {
      if (this.getUsername() === 'James') {
        return 'Miriam'
      }
      return 'James'
    },
    otherPlayer () {
      if (this.player1 === this.getUsername()) {
        return this.player2
      }
      return this.player1
    }
  },
  created () {
    this.getCodenamesLatestGame()
  },
  mounted () {
    var socket = io.connect('http://' + window.location.hostname + ':5000')
    var that = this
    // message handler for the 'join_room' channel
    socket.on('update_game_message', function (msg) {
      that.getCodenamesLatestGame()
    })
  },
  methods: {
    ...mapGetters(['getUsername']),
    newGame () {
      var randomizedPlayers = [this.getUsername(), this.playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })

      axios.post(CODENAMES_CREATE_GAME_URL, {
        username: this.getUsername(),
        player1: randomizedPlayers[0],
        player2: randomizedPlayers[1]
      })
    },
    endGuesses () {
      axios.post(
        CODENAMES_END_GUESSES_URL,
        {
          game_id: this.gameId,
          username: this.getUsername()
        })
    },
    guess (word) {
      axios.post(CODENAMES_GUESS_URL, {
        game_id: this.gameId,
        username: this.getUsername(),
        word: word
      })
    },
    giveHint () {
      axios.post(
        CODENAMES_GIVE_HINT_URL,
        {
          game_id: this.gameId,
          username: this.getUsername(),
          hint_word: this.newHintWord,
          hint_number: this.newHintNumber
        })
    },
    getCodenamesLatestGame () {
      axios.post(CODENAMES_GET_LATEST_GAME_URL, {username: this.getUsername()}).then(response => {
        if (response.data === null) {
          // TODO: Handle this better.
          return
        }
        var game = response.data['game']
        this.assassinFound = game['assassin_found']
        this.gameId = game['id']
        this.gameOver = game['game_over']
        this.player1 = game['player1']
        this.player2 = game['player2']
        this.turnNumber = game['turn_number']
        this.turnType = game['turn_type']

        var locations = response.data['locations_owned_by_player']
        var newLocations = []
        var locationRow = []
        for (let i in locations) {
          if (i !== 0 && i % 5 === 0) {
            newLocations.push(locationRow)
            locationRow = []
          }
          locationRow.push(locations[i]['location_type'])
        }
        newLocations.push(locationRow)
        this.locations = newLocations

        var words = response.data['words_for_game']
        var newWords = []
        var wordRow = []
        for (let i in words) {
          if (i !== 0 && i % 5 === 0) {
            newWords.push(wordRow)
            wordRow = []
          }
          wordRow.push({'word': words[i]['word'], 'status': words[i]['word_status']})
        }
        newWords.push(wordRow)
        this.codewords = newWords

        var turnsToHints = response.data['turns_to_hints']
        if (turnsToHints.length !== 0) {
          var currentTurnToHint = turnsToHints[turnsToHints.length - 1]
          this.currentHintWord = currentTurnToHint['hint_word']
          this.currentHintNumber = currentTurnToHint['hint_number']
        }
      })
    }
  }
}
</script>
