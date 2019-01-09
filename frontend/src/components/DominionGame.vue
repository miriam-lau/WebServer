<template>
  <div class="dominion-game">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="new-game">
      Invite:
          <input v-model="playerToInvite" class="dominion-player-to-invite"/>
          <button v-on:click="newGame">New Game</button>
    </div>
    <div v-if="isInGame">
      <button @click="shownPage = 'kingdom'">Kingdom</button>
      <button v-if="game.nonSupplyCards.length > 0" @click="shownPage = 'nonSupply'">Non Supply</button>
      <button v-if="game.hasBane" @click="shownPage = 'bane'">Bane</button>
      <button v-if="game.hasBoons" @click="shownPage = 'boons'">Boons</button>
      <button v-if="game.hasHexes" @click="shownPage = 'hexes'">Hexes</button>
      <button v-if="player.mats.length > 0" @click="shownPage = 'yourMats'">Your Mats</button>
      <button @click="shownPage = 'discard'">Your Discard</button>
      <button v-if="opponent.mats.length > 0" @click="shownPage = 'opponentMats'">Opponent Mats</button>
      <button v-if="game.revealArea.length > 0" @click="shownPage = 'reveal'"><u>R</u>evealed</button>
      <button @click="shownPage = 'trash'"><u>T</u>rash</button>
      <button @click="shownPage = 'notes'">Notes</button>
      <button @click="shownPage = 'allYourCards'">All your cards</button>
      <button @click="shownPage = 'shortcuts'">Shortcuts</button>
      <div v-if="shownPage === 'kingdom'">
        <div class="vp-treasure">
          <CardStack
            :key="'treasure' + index" v-for="(cardArray, index) in game.treasureCards"
            :defaultMoveArray="player.discard"
            :cardArray="cardArray"
            :callback="addGainToLog"/>
          <div class="c"></div>
          <CardStack
            :key="'vp' + index" v-for="(cardArray, index) in game.vpCards"
            :defaultMoveArray="player.discard"
            :cardArray="cardArray"
            :callback="addGainToLog"/>
        </div>
        <div class="kingdom">
          <CardStack
            :key="'vp' + index" v-for="(cardArray, index) in game.kingdomCards"
            :defaultMoveArray="player.discard"
            :cardArray="cardArray"
            :callback="addGainToLog"/>
        </div>
        <div class="events">
          <img
              v-for="(card, index) in game.sidewaysCards"
              class="sideways-card"
              :key="index"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'nonSupply'">
        <div class="non-supply">
          <CardStack
            :key="index" v-for="(cardArray, index) in game.nonSupplyCards"
            :defaultMoveArray="player.discard"
            :cardArray="cardArray"
            :callback="addGainToLog"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'bane'">
        <div class="bane">
          <CardStack
            :defaultMoveArray="player.discard"
            :cardArray="cardArray"
            :callback="addGainToLog"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'boons'">
        <div class="boons-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.boonsDeck.length}}</div>
            <img
                v-on:click="moveCard(game.boonsDeck, undefined, game.boonsReveal, game.boonsDiscard)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.boonsDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.boonsDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.boonsDiscard)"/>
          </div>
        </div>
        <div class="boons-reveal">
          <img
              v-for="(card, index) in game.boonsReveal"
              :key="index"
              v-on:click="moveCard(game.boonsReveal, index, game.boonsDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'hexes'">
        <div class="hexes-deck-and-discard">
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.hexesDeck.length}}</div>
            <img
                v-on:click="moveCard(game.hexesDeck, undefined, game.hexesReveal, game.hexesDiscard)"
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.hexesDeck)"/>
          </div>
          <div class="sideways-card-container">
            <div class="card-counter-container">{{game.hexesDiscard.length}}</div>
            <img
                class="sideways-card card-in-container"
                :src="getImageForCardArrayOrBlank(game.hexesDiscard)"/>
          </div>
        </div>
        <div class="hexes-reveal">
          <img
              v-for="(card, index) in game.hexesReveal"
              :key="index"
              v-on:click="moveCard(game.hexesReveal, index, game.hexesDiscard)"
              class="sideways-card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'yourMats'">
        <div class="your-mats">
          <CardList
              :cardArray="player.mats"
              :defaultMoveArray="player.discard"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'opponentMats'">
        <div class="opponent-mats">
          <img
              v-for="(card, index) in opponent.mats"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'trash'">
        <div class="trash">
          <CardList :cardArray="game.trash"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'reveal'">
        <div class="reveal-area">
          <CardList :cardArray="game.revealArea"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'notes'">
        <div class="notes">
          <textarea class="note" v-model="notes"></textarea>
        </div>
      </div>
      <div v-else-if="shownPage === 'shortcuts'">
        <div class="shortcuts">
          a (A) - Increment num actions (Decrement num actions)<br/>
          b (B) - Increment num buys (Decrement num buys)<br/>
          c (C) - Increment num coins (Decrement num coins)<br/>
          d - Discard the card.<br/>
          D - Discard all cards in your hand and play area and end the turn.<br/>
          e - End the turn.
          h - Draw the card into your hand.<br/>
          H - Draw 5 new cards into your hand.<br/>
          k - Topdeck the card onto your deck.<br/>
          m - Move the card to your mat.<br/>
          o - Move the card to your opponent's hand.<br/>
          P - Play all cards in your hand.<br/>
          p - Play the card to your play area.<br/>
          r - Return the card to its original pile.<br/>
          s - Shuffle your deck.<br/><br/>
          t - Trash the card.<br/>
          w - Draw a single card from deck into your hand.<br/>
          v - Reveal the card in the revealed area.<br/>
        </div>
      </div>
      <div v-else-if="shownPage === 'discard'">
        <div class="discard-area">
          <CardList :cardArray="player.discard"/>
        </div>
      </div>
      <div v-else-if="shownPage === 'allYourCards'">
        <div class="all-your-cards">
          <img
              v-for="(card, index) in [].concat(player.deck, player.discard, player.playArea, player.hand, player.mats)"
              :key="index"
              class="card"
              :src="getImageForCard(card)"/>
        </div>
      </div>
      <img class="preview" v-if="games_currentCardSelection.exists" :src="getImageForGames_CurrentCardSelection()"/>
      <div class="c">
      </div>
      <span v-if="player.displayedPlayer === playerIndex">
      Your display
      </span>
      <span v-else>
      {{game.players[player.displayedPlayer].name}}'s display
      </span>
      <button @click="toggledisplayedPlayer">Toggle Display</button>
      <br/>
      <div class="game-log">
        <div class="game-log-inner">
          <div :key="index" v-for="(gameLogLine, index) in game.gameLog">
            {{gameLogLine}}<br/>
          </div>
        </div>
      </div>
      <div class="player-area">
        <div class="play-area">
          <div class="play-cards">
            <div v-if="player.displayedPlayer === playerIndex">
              <CardList
                  :cardArray="player.playArea"
                  :defaultMoveArray="player.discard"/>
            </div>
            <div v-else>
              <CardList :cardArray="opponent.playArea"/>
            </div>
          </div>
          <u>P</u>layed Cards
        </div>
        <div class="duration-area">
          <div class="duration-cards">
            <div v-if="player.displayedPlayer === playerIndex">
              <CardList
                  :cardArray="player.durationArea"
                  :defaultMoveArray="player.discard"/>
            </div>
            <div v-else>
              <CardList :cardArray="opponent.durationArea"/>
            </div>
          </div>
          D<u>u</u>ration
        </div>
        <div class="c">
        </div>
        <div class="stats">
          <div v-if="player.displayedPlayer === playerIndex">
            <span class="stat-item"><u>A</u>ctions: <button @click="decrementNumActions">-</button><input class="counter" v-model="player.numActions"/><button @click="incrementNumActions">+</button></span>
            <span class="stat-item"><u>B</u>uys: <button @click="decrementNumBuys">-</button><input class="counter" v-model="player.numBuys"/><button @click="incrementNumBuys">+</button></span>
            <span class="stat-item"><u>C</u>oins: <button @click="decrementNumCoins">-</button><input class="counter" v-model="player.numCoins"/><button @click="incrementNumCoins">+</button></span>
            <span class="stat-item">VP: <button @click="decrementNumVP">-</button><input class="counter" v-model="player.numVP"/><button @click="incrementNumVP">+</button></span>
            <span class="stat-item">Coffers: <button @click="decrementNumCoffers">-</button><input class="counter" v-model="player.numCoffers"/><button @click="incrementNumCoffers">+</button></span>
            <span class="stat-item">Villagers: <button @click="decrementNumVillagers">-</button><input class="counter" v-model="player.numVillagers"/><button @click="incrementNumVillagers">+</button></span>
            <span class="stat-item">Debt: <button @click="decrementNumDebt">-</button><input class="counter" v-model="player.numDebt"/><button @click="incrementNumDebt">+</button></span>
            <button @click="endPlayerTurn" v-if="game.currentPlayerTurn === playerIndex">End Turn</button>
            <span>Your turn</span>
          </div>
          <div v-else>
            <span class="stat-item">Actions: {{opponent.numActions}}</span>
            <span class="stat-item">Buys: {{opponent.numBuys}}</span>
            <span class="stat-item">Coins: {{opponent.numCoins}}</span>
            <span class="stat-item">VP: {{opponent.numVP}}</span>
            <span class="stat-item">Coffers: {{opponent.numCoffers}}</span>
            <span class="stat-item">Villagers: {{opponent.numVillagers}}</span>
            <span class="stat-item">Debt: {{opponent.numDebt}}</span>
            <span>{{opponent.name}}'s turn</span>
          </div>
        </div>
        <div class="deck-and-hand">
          <div class="single-pile">
            <div class="single-pile-cards">
              <div v-if="player.displayedPlayer === playerIndex">
                <CardStack
                  :reshufflePileArray="player.discard"
                  :defaultMoveArray="player.hand"
                  :cardArray="player.deck"/>
              </div>
              <div v-else>
                <CardStack
                  :cardArray="opponent.deck"/>
              </div>
            </div>
            <span v-if="player.displayedPlayer === playerIndex">
            Dec<u>k</u><br/>
            </span>
            <span v-else>
            {{game.players[player.displayedPlayer].name}}'s deck
            </span>

          </div>
          <div class="single-pile">
            <div class="single-pile-cards">
              <div v-if="player.displayedPlayer === playerIndex">
                <CardStack
                  :cardArray="player.discard"/>
              </div>
              <div v-else>
                <CardStack
                  :cardArray="opponent.discard"/>
              </div>
            </div>
            <span v-if="player.displayedPlayer === playerIndex">
            <u>D</u>iscard<br/>
            </span>
            <span v-else>
            {{game.players[player.displayedPlayer].name}}'s discard
            </span>
          </div>
          <div class="hand">
            <div class="hand-cards">
              <CardList
                  :defaultMoveArray="player.playArea"
                  :cardArray="player.hand"/>
            </div>
            Your <u>H</u>and
          </div>
        </div>
      </div>
    </div>
    <div class="c"/>
  </div>
</template>
<style>
  @import "../assets/style/dominion-game.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath, findPath, fetchFromPath } from '../common/utils'
import { store } from '../store/store'
import { socket } from '../common/socketio'
import { shuffle, moveCard, moveAllCards, moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection } from '../common/card_games'

const CREATE_DOMINION_GAME_URL = getFullBackendUrlForPath('/create_dominion_game')
const DOMINION_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/dominion_get_latest_game')
const SAVE_DOMINION_GAME_URL = getFullBackendUrlForPath('/save_dominion_game')

export default {
  name: 'DominionGame',
  data () {
    return {
      games_currentCardSelection: {}, // Object with keys 'array', and 'index', and 'exists'
      shouldSaveChanges: false,
      playerToInvite: '',
      playerIndex: 0,
      butterBar_message: '',
      butterBar_css: '',
      isInGame: false,
      player: {},
      opponent: {},
      shownPage: 'kingdom',
      notes: '',
      game: {}
    }
  },
  components: {
    ButterBar, CardStack, CardList
  },
  created () {
    this.updateDominionDisplayWithLatestGame()
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
      this.updateDominionDisplayWithLatestGame()
    },
    game: {
      handler (val) {
        if (this.shouldSaveChanges) {
          this.saveDominionGame()
        } else {
          this.shouldSaveChanges = true
        }
      },
      deep: true
    }
  },
  mounted () {
    var that = this
    socket.on('refresh_dominion', function (data) {
      if (data.players.includes(that.username) && data.player_triggering_update !== that.username) {
        that.updateDominionDisplayWithGameData(data.gameData)
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
      var randomizedPlayers = [this.username, this.playerToInvite]
      randomizedPlayers.sort(function (a, b) { return 0.5 - Math.random() })

      let that = this
      callAxiosAndSetButterBar(
        this,
        CREATE_DOMINION_GAME_URL,
        {
          player1: randomizedPlayers[0],
          player2: randomizedPlayers[1],
          username: this.username
        },
        'Generated Kingdom',
        'Failed to generate kingdom.',
        function (response) {
          let data = response.data
          that.updateDominionDisplayWithGameData(data)
        })
    },
    saveDominionGame () {
      callAxiosAndSetButterBar(
        this,
        SAVE_DOMINION_GAME_URL,
        {
          gameId: this.game.gameId,
          gameData: this.game,
          username: this.username
        },
        null,
        'Failed to save dominion game.')
    },
    /**
     * Fetches the latest game for the currently logged in user and displays it if any exists.
     * playerTriggeringUpdate may be null.
     */
    updateDominionDisplayWithLatestGame () {
      callAxiosAndSetButterBar(
        this,
        DOMINION_GET_LATEST_GAME_URL,
        { username: this.username },
        null,
        'Failed to save dominion game.',
        (response) => {
          if (response.data === null) {
            this.isInGame = false
            return
          }
          this.updateDominionDisplayWithGameData(response.data.data)
        })
    },
    updateDominionDisplayWithGameData (gameData) {
      let currentCardSelectionArrayPath
      if (this.games_currentCardSelection.exists) {
        currentCardSelectionArrayPath = findPath(this.games_currentCardSelection.array, this.game)
      }
      this.shouldSaveChanges = false
      this.isInGame = true
      this.game = gameData
      this.playerIndex = gameData.playerOrder[0] === this.username ? 0 : 1
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
          this.games_currentCardSelection.array === this.opponent.deck) {
        return '/static/dominion/card_images/backside_blue.jpg'
      }
      let index = this.games_currentCardSelection.index
      if (index === undefined) {
        index = this.games_currentCardSelection.array.length - 1
      }
      if (index < 0) {
        return '/static/blank-card.jpg'
      } else if (this.games_currentCardSelection.array.length <= index) {
        return ''
      } else {
        return this.getImageForCard(this.games_currentCardSelection.array[index])
      }
    },
    getImageForCardArrayOrBlank (cardArray) {
      if (cardArray.length === 0) {
        return '/static/blank-card.jpg'
      } else if (cardArray === this.player.deck || cardArray === this.opponent.deck) {
        return '/static/dominion/card_images/backside_blue.jpg'
      } else if (cardArray === this.game.boonsDeck) {
        return '/static/dominion/card_images/Boon-back.jpg'
      } else if (cardArray === this.game.hexesDeck) {
        return '/static/dominion/card_images/Hex-back.jpg'
      } else {
        return this.getImageForCard(cardArray[cardArray.length - 1])
      }
    },
    getImageForCard (card) {
      return card['image']
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
    deckToHand () {
      for (let i = 0; i < 5; ++i) {
        moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
      }
    },
    singleCardFromDeckToHand () {
      moveCard(this.player.deck, undefined, this.player.hand, this.player.discard)
    },
    endTurnAndCleanUp () {
      moveAllCards(this.player.hand, this.player.discard)
      moveAllCards(this.player.playArea, this.player.discard)
      if (this.games_currentCardSelection.array === this.player.hand || this.games_currentCardSelection.array === this.player.playArea) {
        clearCurrentCardSelection(this)
      }
      this.player.numActions = 1
      this.player.numBuys = 1
      this.player.numCoins = 0
      this.player.displayedPlayer = 1 - this.playerIndex
      this.opponent.displayedPlayer = 1 - this.playerIndex
      this.endPlayerTurn()
      this.deckToHand()
    },
    incrementNumActions () { this.player.numActions++ },
    decrementNumActions () { this.player.numActions-- },
    incrementNumBuys () { this.player.numBuys++ },
    decrementNumBuys () { this.player.numBuys-- },
    incrementNumCoins () { this.player.numCoins++ },
    decrementNumCoins () { this.player.numCoins-- },
    incrementNumVP () { this.player.numVP++ },
    decrementNumVP () { this.player.numVP-- },
    incrementNumVillagers () { this.player.numVillagers++ },
    decrementNumVillagers () { this.player.numVillagers-- },
    incrementNumCoffers () { this.player.numCoffers++ },
    decrementNumCoffers () { this.player.numCoffers-- },
    incrementNumDebt () { this.player.numDebt++ },
    decrementNumDebt () { this.player.numDebt-- },
    handToPlayArea () {
      moveAllCards(this.player.hand, this.player.playArea)
      if (this.games_currentCardSelection.array === this.player.hand) {
        clearCurrentCardSelection(this)
      }
    },
    endPlayerTurn () {
      this.game.currentPlayerTurn = 1 - this.playerIndex
    },
    toggledisplayedPlayer () {
      this.player.displayedPlayer = 1 - this.player.displayedPlayer
    },
    addGainToLog (card) {
      this.game.gameLog.push(this.player.name + ': +' + card.name)
    },
    handleKeyPress (event) {
      if (!this.isInGame) {
        return
      }
      switch (event.key) {
        case 'a': this.incrementNumActions(); break
        case 'b': this.incrementNumBuys(); break
        case 'c': this.incrementNumCoins(); break
        case 'A': this.decrementNumActions(); break
        case 'B': this.decrementNumBuys(); break
        case 'C': this.decrementNumCoins(); break
        case 'D': this.endTurnAndCleanUp(); return
        case 'H':
          this.deckToHand(); return
        case 'P': this.handToPlayArea(); return
        case 'Z': this.deckToDiscard(); return
        case 'e': this.endPlayerTurn(); break
        case 'w': this.singleCardFromDeckToHand(); return
      }
      if (!this.games_currentCardSelection.exists) {
        return
      }
      let destinationArray = null
      let reshufflePile = null
      switch (event.key) {
        case 'd': destinationArray = this.player.discard; break
        case 'u': destinationArray = this.player.durationArea; break
        case 'h': destinationArray = this.player.hand; break
        case 'k': destinationArray = this.player.deck; break
        case 'm': destinationArray = this.player.mats; break
        case 'p': destinationArray = this.player.playArea; break
        case 'n':
          let gamesCurrentCardSelectionCard = this.getGames_CurrentCardSelectionCard()
          if (gamesCurrentCardSelectionCard == null) {
            return
          }
          let destinationPileType = gamesCurrentCardSelectionCard.pile_type
          let destinationPileIndex = gamesCurrentCardSelectionCard.pile_index
          if (!destinationPileType) {
            return
          }
          switch (destinationPileType) {
            case 'vp_cards':
              destinationArray = this.game.vpCards[destinationPileIndex]
              break
            case 'treasure_cards':
              destinationArray = this.game.treasureCards[destinationPileIndex]
              break
            case 'kingdom_cards':
              destinationArray = this.game.kingdomCards[destinationPileIndex]
              break
            case 'non_supply_cards':
              destinationArray = this.game.nonSupplyCards[destinationPileIndex]
              break
          }
          break
        case 's': this.shuffleDeck(); return
        case 't': destinationArray = this.game.trash; break
        case 'r': destinationArray = this.game.revealArea; break
        case 'o': destinationArray = this.opponent.hand; break
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck) {
        reshufflePile = this.player.discard
      } else if (this.games_currentCardSelection.array === this.game.boonsDeck) {
        reshufflePile = this.game.boonsDiscard
      } else if (this.games_currentCardSelection.array === this.game.hexesDeck) {
        reshufflePile = this.game.hexesDiscard
      }
      moveCurrentCardSelection(this, destinationArray, reshufflePile)
    }
  }
}
</script>
