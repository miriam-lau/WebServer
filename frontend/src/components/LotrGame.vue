<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="new-game">
      Invite: <input v-model="playerToInvite" class="lotr-player-to-invite"/>
      Scenario: <input v-model="scenarioName"/>
      Your deck: <textarea v-model="player1DeckXml"/>
      Partner's deck: <textarea v-model="player2DeckXml"/>
      <button v-on:click="newGame">New Game</button>
    </div>
    <div v-if="isInGame">
      <button @click="shownPage = 'main'">Kingdom</button>
      <button @click="shownPage = 'discard'">Your Discard</button>
      <button @click="shownPage = 'trash'"><u>T</u>rash</button>
      <button @click="shownPage = 'notes'">Notes</button>
      <button @click="shownPage = 'allYourCards'">All your cards</button>
      <button @click="shownPage = 'shortcuts'">Shortcuts</button>
      <button @click="shownPage = 'quest'">Quest</button>
      <button @click="shownPage = 'secondQuest'">Second Quest</button>
      <button @click="shownPage = 'encounter'">Encounter</button>
      <button @click="shownPage = 'victory'">Victory</button>
      <button @click="shownPage = 'special'">Special</button>
      <button @click="shownPage = 'secondSpecial'">Second Special</button>
      <button @click="shownPage = 'secondDeck'">Your Second Deck</button>
      <img class="preview" v-if="games_currentCardSelection.exists" :src="getImageForGames_CurrentCardSelection()"/>
      <div v-if="shownPage === 'main'">
        <div class="staging-area">
          <CardList
              :cardArray="game.stagingArea"
              :defaultMoveArray="game.encounterDiscard"/>
        </div>
        <div class="active-location">
          <CardList
              :cardArray="game.activeLocation"
              :defaultMoveArray="game.encounterDiscard"/>
        </div>
        <div class="quest">
          <CardStack
            :defaultMoveArray="game.questDiscard"
            :cardArray="game.questDeck"/>
        </div>
        <div class="encounter">
          <CardStack
            :defaultMoveArray="game.encounterDiscard"
            :cardArray="game.encounterDeck"/>
        </div>
        <div class="c"/>
        <div class="player-play-area">
          <div class="engaged-enemies">
            <CardList
                :cardArray="player.engagedEnemies"
                :defaultMoveArray="game.encounterDiscard"/>
          </div>
          <div class="characters">
            <CardList
                :cardArray="player.characters"
                :defaultMoveArray="player.discard"/>
          </div>
        </div>
        <div class="played">
          <CardList
              :cardArray="game.playedCards"
              :defaultMoveArray="player.discard"/>
        </div>
        <div class="player-play-area">
          <div class="engaged-enemies">
            <CardList
                :cardArray="partner.engagedEnemies"
                :defaultMoveArray="game.encounterDiscard"/>
          </div>
          <div class="characters">
            <CardList
                :cardArray="partner.characters"/>
          </div>
        </div>
      </div>
      <div class="c">
      </div>
      <div class="player-area">
        <div class="stats">
          <span class="stat-item">Threat Points: <button @click="decrementThreat">-</button><input class="counter" v-model="player.threat"/><button @click="incrementThreat">+</button></span>
        </div>
        <div class="deck-and-hand">
          <div class="single-pile">
            <div class="single-pile-cards">
              <CardStack
                :reshufflePileArray="player.discard"
                :defaultMoveArray="player.hand"
                :cardArray="player.deck"/>
            </div>
            Dec<u>k</u><br/>
          </div>
          <div class="single-pile">
            <div class="single-pile-cards">
              <CardStack
                :cardArray="player.discard"/>
            </div>
            <u>D</u>iscard<br/>
          </div>
          <div class="hand">
            <div class="hand-cards">
              <CardList
                  :defaultMoveArray="game.playedCards"
                  :cardArray="player.hand"/>
            </div>
            Your <u>H</u>and
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/lotr-game.css"
</style>
<script>
// TODO: Add this back.       <button v-if="game.revealArea.length > 0" @click="shownPage = 'reveal'"><u>R</u>evealed</button>

import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath, findPath, fetchFromPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'
import { shuffle, moveCard, moveAllCards, moveCurrentCardSelection, setCurrentCardSelection } from '../common/card_games'

const CREATE_LOTR_GAME_URL = getFullBackendUrlForPath('/create_lotr_game')
const LOTR_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/lotr_get_latest_game')
const SAVE_LOTR_GAME_URL = getFullBackendUrlForPath('/save_lotr_game')

export default {
  name: 'LotrGame',
  data () {
    return {
      games_currentCardSelection: {}, // Object with keys 'array', and 'index', and 'exists'
      shouldSaveChanges: false,
      scenarioName: '',
      playerToInvite: '',
      player1DeckXml: '',
      player2DeckXml: '',
      butterBar_message: '',
      butterBar_css: '',
      isInGame: false,
      player: {},
      partner: {},
      shownPage: 'main',
      notes: '',
      game: {}
    }
  },
  components: {
    ButterBar, CardStack, CardList
  },
  created () {
    this.updateLotrDisplayWithLatestGame()
    window.addEventListener('keyup', this.handleKeyPress)
    this.playerToInvite = this.defaultPlayerToInvite()
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  watch: {
    username () {
      this.updateLotrDisplayWithLatestGame()
    },
    game: {
      handler (val) {
        if (this.shouldSaveChanges) {
          this.saveLotrGame()
        } else {
          this.shouldSaveChanges = true
        }
      },
      deep: true
    }
  },
  mounted () {
    var that = this
    socket.on('refresh_lotr', function (data) {
      if (data.players.includes(that.username) && data.player_triggering_update !== that.username) {
        that.updateLotrDisplayWithGameData(data.gameData)
      }
    })
  },
  methods: {
    moveCard: moveCard,
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
      let that = this
      callAxiosAndSetButterBar(
        this,
        CREATE_LOTR_GAME_URL,
        {
          scenario: this.scenarioName,
          player1: this.username,
          player2: this.playerToInvite,
          player1Deck: this.player1DeckXml,
          player2Deck: this.player2DeckXml,
          username: this.username
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        function (response) {
          let data = response.data
          that.updateLotrDisplayWithGameData(data)
        })
    },
    saveLotrGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_LOTR_GAME_URL,
        {
          gameId: this.game.gameId,
          gameData: this.game,
          username: this.username
        },
        null,
        'Failed to save lotr game.')
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateLotrDisplayWithLatestGame () {
      callAxiosAndSetButterBar(
        this,
        LOTR_GET_LATEST_GAME_URL,
        { username: this.username },
        null,
        'Failed to save lotr game.',
        (response) => {
          if (response.data === null) {
            this.isInGame = false
            return
          }
          this.updateLotrDisplayWithGameData(response.data.data)
        })
    },
    updateLotrDisplayWithGameData (gameData) {
      let currentCardSelectionArrayPath
      if (this.games_currentCardSelection.exists) {
        currentCardSelectionArrayPath = findPath(this.games_currentCardSelection.array, this.game)
      }
      this.shouldSaveChanges = false
      this.isInGame = true
      this.game = gameData
      this.playerIndex = gameData.players[0].name === this.username ? 0 : 1
      this.player = this.game.players[this.playerIndex]
      this.opponent = this.game.players[1 - this.playerIndex] // Only supports a 2 player game.

      if (currentCardSelectionArrayPath) {
        setCurrentCardSelection(this, fetchFromPath(this.game, currentCardSelectionArrayPath), this.games_currentCardSelection.index)
      }
    },
    getImageForGames_CurrentCardSelection () {
      if (!this.games_currentCardSelection.exists) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck ||
          this.games_currentCardSelection.array === this.partner.deck) {
        return '/static/dominion/card_images/backside_blue.jpg'
      }
      let index = this.games_currentCardSelection.index
      if (index === undefined) {
        index = this.games_currentCardSelection.array.length - 1
      }
      if (index < 0) {
        return '/static/dominion/card_images/_blank.jpg'
      } else if (this.games_currentCardSelection.array.length <= index) {
        return ''
      } else {
        return '/static/dominion/card_images/_blank.jpg' // TODO: Fix this.
      }
    },
    getImageForCardArrayOrBlank (cardArray) {
      return '/static/dominion/card_images/_blank.jpg'
    },
    getImageForCard (card) {
      return '/static/dominion/card_images/_blank.jpg'
    },
    getGames_CurrentCardSelectionCard () {
      let cardIndex = this.games_currentCardSelection.index
      let cardArray = this.games_currentCardSelection.array
      if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= cardArray.length)) {
        return null
      }
      if (cardIndex === undefined) {
        cardIndex = cardArray.length - 1
      }
      return cardArray[cardIndex]
    },
    shuffleDeck () {
      shuffle(this.player.deck)
    },
    deckToDiscard () {
      moveAllCards(this.player.deck, this.player.discard)
    },
    singleCardFromDeckToHand () {
      moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
    },
    nextRound () {
      // TODO: Implement.
    },
    incrementThreat () { this.player.threat++ },
    decrementThreat () { this.player.threat-- },
    handleKeyPress (event) {
      if (!this.isInGame) {
        return
      }
      switch (event.key) {
        case 'a': this.incrementThreat(); break
        case 'A': this.decrementThreat(); break
        case 'w': this.singleCardFromDeckToHand(); return
      }
      if (!this.games_currentCardSelection.exists) {
        return
      }
      let destinationArray = null
      let reshufflePile = null
      switch (event.key) {
        case 'd': destinationArray = this.player.discard; break
        case 'h': destinationArray = this.player.hand; break
        case 'k': destinationArray = this.player.deck; break
        case 's': this.shuffleDeck(); return
        case 't': destinationArray = this.game.trash; break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck) {
        reshufflePile = this.player.discard
      }
      moveCurrentCardSelection(this, destinationArray, reshufflePile)
    }
  }
}
</script>
