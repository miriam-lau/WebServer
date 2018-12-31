function Card (image) {
  this.image = image
}

function CardPile () {
  this.cards = []

  this.addCard = function (card) {
    this.cards.push(card)
  }
}

function PileManager () {
  // TODO: Implement
  // Map<String, CardPile>
  this.piles = {}

  this.reset = function () {
    this.piles = {}
  }

  this.addPile = function (pileName, pile) {
    this.piles[pileName] = pile
  }
}

export { Card, CardPile, PileManager }
