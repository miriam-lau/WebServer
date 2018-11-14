# WebServer


## Build Setup

git clone git@github.com:miriam-lau/WebServer.git
python3 -m pip install --user virtualenv
python3 -m virtualenv env
pip3 install flask flask-socketio eventlet
sudo apt install npm
sudo npm install -g vue-cli
sudo npm cache clean -f
sudo npm install -g n
sudo n stable
// sudo ln -s /usr/bin/nodejs /usr/bin/node - Might not need to do this either.
// vue init webpack frontend - Did this but don't need to anymore.
sudo npm install vue-cookies --save
sudo npm install vuex --save
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo pip3 install psycopg2
sudo npm install axios --save
sudo pip3 install -U flask-cors
sudo npm i --save @fortawesome/fontawesome-svg-core
sudo  npm i --save @fortawesome/free-solid-svg-icons
sudo  npm i --save @fortawesome/vue-fontawesome
sudo npm install --save @fortawesome/vue-fontawesome

## To run in dev mode:
from backend/src: flask run --reload --debugger --host=0.0.0.0
from frontend/: npm run dev -- --hot --host 0.0.0.0

## Database configuration

create table users (
  username varchar (50) primary key);

create table codenames_words ( 
  word varchar (50) primary key);

CREATE TYPE turn_type AS ENUM ('guess', 'give_hint');

create table codenames_games (
  id serial primary key,
  player1 varchar(50) references users,
  player2 varchar(50) references users,
  turn_number integer,
  turn_type turn_type,
  game_over boolean,
  assassin_found boolean
);

create table codenames_turns_to_hints (
  game_id integer references codenames_games,
  turn_number integer,
  player varchar(50) references users,
  hint_word varchar(150),
  hint_number integer,
  primary key (game_id, turn_number)
);

CREATE TYPE guess_outcome AS ENUM ('agent_found', 'assassin_found', 'hit_bystander');

create table codenames_turns_to_guesses (
  id serial primary key,
  game_id integer references codenames_games,
  turn_number integer,
  player varchar(50) references users,
  guessed_word varchar(50) references codenames_words,
  guess_outcome guess_outcome
);

CREATE TYPE word_status AS ENUM ('agent_found', 'player_1_hit_bystander', 'player_2_hit_bystander', 'both_players_hit_bystanders' , 'assassin_found', 'unchecked');

create table codenames_games_to_words (
  game_id integer references codenames_games,
  word_index integer,
  word varchar(50) references codenames_words,
  word_status word_status,
  primary key (game_id, word_index)
);

CREATE TYPE location_type AS ENUM ('agent', 'assassin', 'bystander');

create table codenames_games_to_locations (
  game_id integer references codenames_games,
  player_owning_location varchar(50) references users,
  location_index integer,
  location_type location_type,
  primary key (game_id, player_owning_location, location_index)
);
