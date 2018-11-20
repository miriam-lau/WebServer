<template>
  <div>
    <div v-if="shouldDisplayGame">
      <div class="codenames-gameboard">
        <div class="codenames-codeword-row" :key="rowIndex" v-for="(codewordRow, rowIndex) in codewords">
          <div :class="generateWordStatusClass(codeword['status']) + ' codenames-codeword-item'" :key="colIndex"
              v-for="(codeword, colIndex) in codewordRow" @click="guess(codeword['word'])">
            {{ codeword['word'] }}
          </div>
        </div>
      </div>
      <div class="codenames-location-board">
        <div class="codenames-location-row" :key="rowIndex" v-for="(locationRow, rowIndex) in locations">
          <div :class="'codenames-locationtype-' + location + ' codenames-location-item'" :key="colIndex"
              v-for="(location, colIndex) in locationRow">
          </div>
        </div>
      </div>
      <div class="clearfix"></div>
      <div>
        <span v-if="assassinFound && gameOver">Assassin found. You lose.</span>
        <span v-else-if="!assassinFound && gameOver">All agents found. You win!</span>
        <span>Time tokens used: {{ timeTokensUsed }}</span>&nbsp;
      </div>
      <div v-if="turnType == 'guess'" class="codenames-given-hint">
        Given hint: {{ currentHintWord }}. Number of words: {{ currentHintNumber }}
      </div>
      <div v-if="!gameOver">
        <div v-if="isCurrentPlayerTurn && turnType == 'guess'">
          <div>Click on the words to make guesses or here when finished. <button @click="endGuesses">Done</button>
          </div>
        </div>
        <div v-else-if="isCurrentPlayerTurn && turnType == 'give_hint'">
          Hint: <input class="codenames-hint-input" v-model="newHintWord" placeholder="Hint word"/>
          Num Words: <input type="number" class="codenames-hint-num-words" v-model="newHintNumber" />
          <button @click="giveHint">Give Hint</button>
        </div>
        <div v-else-if="!isCurrentPlayerTurn && turnType == 'guess'">
          Waiting for {{otherPlayer}} to guess words.
        </div>
        <div v-else-if="!isCurrentPlayerTurn && turnType == 'give_hint'">
          Waiting for {{otherPlayer}} to give a hint.
        </div>
      </div>
      <div v-else>
        No game to display
      </div>
    </div>
    <div>
      Invite:
          <input v-model="playerToInvite" class="codenames-player-to-invite"/>
          <button v-on:click="newGame">New Game</button>
    </div>
    <div class="codenames-log">
      <div>Log:</div>
      <div class="codenames-log-inner">
        <div :key="index" v-for="(logMessage, index) in logs">{{ logMessage }}</div>
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/codenames.css"
</style>
<script>
import axios from 'axios'
import { store } from '../store/store'
import { playSound, getFullBackendUrlForPath, generateExpandIcon } from '../common/utils'
import * as io from 'socket.io-client'
window.io = io

// Todo: Make the CSS in this file less hacky. There's hardcoded widths everywhere.
const CODENAMES_CREATE_GAME_URL = getFullBackendUrlForPath('/codenames_create_game')
const CODENAMES_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/codenames_get_latest_game')
const CODENAMES_GIVE_HINT_URL = getFullBackendUrlForPath('/codenames_give_hint')
const CODENAMES_END_GUESSES_URL = getFullBackendUrlForPath('/codenames_end_guesses')
const CODENAMES_GUESS_URL = getFullBackendUrlForPath('/codenames_guess')

const SIGNAL_TURN_MP3 = '/static/signal-turn.mp3'

export default {
  name: 'Codenames',
  data () {
    return {
      shouldDisplayGame: false,
      assassinFound: false,
      gameOver: false,
      gameId: 0,
      player1: '',
      player2: '',
      turnNumber: 0,
      timeTokensUsed: 0,
      turnType: '',
      locations: [],
      codewords: [],
      currentHintWord: '',
      currentHintNumber: 0,
      newHintWord: '',
      newHintNumber: 0,
      logs: [],
      isExpanded: true
    }
  },
  computed: {
    /*
     * Whether it's the turn of the currently signed in user or not.
     */
    isCurrentPlayerTurn () {
      var isPlayer1Turn = this.turnNumber % 2 === 0
      return this.isCurrentUserPlayer1() === isPlayer1Turn
    },
    /*
     * The default player name to invite to a game.
     */
    playerToInvite () {
      if (this.username === 'James') {
        return 'Miriam'
      } else if (this.username === 'Miriam') {
        return 'James'
      }
      return ''
    },
    /*
     * The name of the other player in the current game. That is, the one playing with the current user.
     */
    otherPlayer () {
      if (this.player1 === this.username) {
        return this.player2
      }
      return this.player1
    },
    username () {
      return store.state.username
    },
    expandIcon () {
      return generateExpandIcon(this.isExpanded)
    }
  },
  watch: {
    username () {
      this.updateCodenamesDisplayWithLatestGame(null)
    }
  },
  created () {
    this.updateCodenamesDisplayWithLatestGame(null)
  },
  mounted () {
    var socket = io.connect('http://' + window.location.hostname + ':5000')
    var that = this
    socket.on('refresh_codenames', function (data) {
      if (data['players'].includes(that.username)) {
        that.updateCodenamesDisplayWithLatestGame(data['player_triggering_update'])
      }
    })
  },
  methods: {
    toggleExpand () {
      this.isExpanded = !this.isExpanded
    },
    isCurrentUserPlayer1 () {
      return this.username === this.player1
    },
    /**
     * Generates the html class used to render the word in the game board.
     */
    generateWordStatusClass (wordStatus) {
      var wordStatusClass = 'codenames-word-status-'
      var isPlayer1 = this.isCurrentUserPlayer1()
      if (wordStatus === 'player_1_hit_bystander') {
        if (isPlayer1) {
          wordStatus = 'current_player_hit_bystander'
        } else {
          wordStatus = 'other_player_hit_bystander'
        }
      } else if (wordStatus === 'player_2_hit_bystander') {
        if (isPlayer1) {
          wordStatus = 'other_player_hit_bystander'
        } else {
          wordStatus = 'current_player_hit_bystander'
        }
      }
      return wordStatusClass + wordStatus
    },
    /**
     * Creates a new game with the invited player.
     */
    newGame () {
      var randomizedPlayers = [this.username, this.playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })

      axios.post(CODENAMES_CREATE_GAME_URL, {
        username: this.username,
        player1: randomizedPlayers[0],
        player2: randomizedPlayers[1]
      })
    },
    endGuesses () {
      axios.post(
        CODENAMES_END_GUESSES_URL,
        {
          game_id: this.gameId,
          username: this.username
        })
    },
    guess (word) {
      axios.post(CODENAMES_GUESS_URL, {
        game_id: this.gameId,
        username: this.username,
        word: word
      })
    },
    giveHint () {
      axios.post(
        CODENAMES_GIVE_HINT_URL,
        {
          game_id: this.gameId,
          username: this.username,
          hint_word: this.newHintWord,
          hint_number: this.newHintNumber
        }).then(response => {
        this.newHintWord = ''
        this.newHintNumber = 0
      })
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateCodenamesDisplayWithLatestGame (playerTriggeringUpdate) {
      axios.post(CODENAMES_GET_LATEST_GAME_URL, {username: this.username}).then(response => {
        if (response.data === null) {
          this.shouldDisplayGame = false
          return
        }
        this.shouldDisplayGame = true
        var game = response.data['game']
        this.assassinFound = game['assassin_found']
        this.gameId = game['id']
        this.gameOver = game['game_over']
        this.player1 = game['player1']
        this.player2 = game['player2']
        this.turnNumber = game['turn_number']
        this.turnType = game['turn_type']
        this.timeTokensUsed = game['time_tokens_used']

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

        var words = response['data']['words_for_game']
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

        var turnsToHints = response['data']['turns_to_hints']
        if (turnsToHints.length !== 0) {
          var currentTurnToHint = turnsToHints[turnsToHints.length - 1]
          this.currentHintWord = currentTurnToHint['hint_word']
          this.currentHintNumber = currentTurnToHint['hint_number']
        }

        // Assumes data for turns comes in order and starts with turn 1.
        var turnsToGuesses = response.data['turns_to_guesses']
        var turnsToGuessesArray = []
        turnsToGuessesArray.push([]) // There are no guesses in turn 0.
        var currentTurn = 1
        var guessStringsForCurrentTurn = []
        var i = 0
        while (i < turnsToGuesses.length) {
          var guess = turnsToGuesses[i]
          if (guess['turn_number'] === currentTurn) {
            var guessString = guess['player'] + ' went to ' + guess['guessed_word'] + ' '
            switch (guess['guess_outcome']) {
              case 'agent_found':
                guessString += 'and rescued an agent.'
                break
              case 'hit_bystander':
                guessString += 'and clobbered an innocent bystander.'
                break
              case 'assassin_found':
                guessString += 'and was killed by an assassin. :('
                break
            }
            guessStringsForCurrentTurn.push(guessString)
            i++
          } else {
            turnsToGuessesArray.push(guessStringsForCurrentTurn)
            guessStringsForCurrentTurn = []
            currentTurn++
          }
        }
        if (guessStringsForCurrentTurn.length !== 0) {
          turnsToGuessesArray.push(guessStringsForCurrentTurn)
        }

        this.logs = []
        for (i = 0; i <= this.turnNumber; ++i) {
          if (i < turnsToGuessesArray.length) {
            for (var j = 0; j < turnsToGuessesArray[i].length; ++j) {
              this.logs.push('     ' + turnsToGuessesArray[i][j])
            }
          }
          if (i < turnsToHints.length) {
            var turnToHint = turnsToHints[i]
            this.logs.push(
              turnToHint.player + ' says \'' + turnToHint.hint_word + '\'. ' +
              turnToHint.hint_number + ' words.')
          }
        }

        if (this.gameOver) {
          if (this.assassinFound) {
            this.logs.push('Unfortunately, the terrorists succeed.')
          } else {
            this.logs.push('Congratulations, you rescued everyone!')
          }
        }

        if (playerTriggeringUpdate !== null && playerTriggeringUpdate !== this.username && this.isCurrentPlayerTurn) {
          playSound(SIGNAL_TURN_MP3)
        }
      })
    }
  }
}
</script>
