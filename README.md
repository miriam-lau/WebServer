# WebServer


## Build Setup

git clone git@github.com:miriam-lau/WebServer.git<br><br>
python3 -m pip install --user virtualenv<br>
python3 -m virtualenv env<br>
pip3 install flask flask-socketio eventlet<br>
sudo pip3 install psycopg2<br>
sudo pip3 install -U flask-cors<br>
sudo pip3 install pyyaml<br><br>

// navigate to "frontend" directory
sudo apt install npm<br>
sudo npm install -g vue-cli<br>
sudo npm install vue-cookies --save<br>
sudo npm install vuex --save<br>
sudo npm install axios --save<br>
sudo npm i --save @fortawesome/fontawesome-svg-core<br>
sudo  npm i --save @fortawesome/free-solid-svg-icons<br>
sudo npm install --save @fortawesome/vue-fontawesome<br>
sudo npm install vue-masonry --save<br><br>

sudo apt-get update<br>
sudo apt-get install postgresql postgresql-contrib<br>

## Restoring the database in windows
https://stackoverflow.com/questions/28048412/how-to-backup-restore-postgresql-database-in-windows7

## To run in dev mode:
from backend/src: flask run --reload --debugger --host=0.0.0.0<br>
from frontend/: npm run dev -- --hot --host 0.0.0.0

## Database configuration

# The table orders by app are:
# users
# current_documents
# hobby_tracker
# codenames
# recipes
# restaurants
# pantry

drop table users cascade;
drop table cookbooks cascade;
drop table recipes cascade;
drop table recipe_meals cascade;
drop table cities cascade;
drop table restaurants cascade;
drop table dishes cascade;
drop table dish_meals cascade;
drop table recipe_images cascade;
drop table dish_images cascade;
drop table current_documents cascade;
drop table hobby_tracker cascade;
drop table hobby_completed_hours_timestamped cascade;
drop table codenames_words cascade;
drop table codenames_games cascade;
drop table codenames_turns_to_hints cascade;
drop table codenames_turns_to_guesses cascade;
drop table codenames_games_to_words cascade;
drop table codenames_games_to_locations cascade;
drop table grocery_list cascade;
drop table grocery_known_words cascade;
drop table pantry cascade;
drop table notes cascade;

create table users (
  username varchar (50) primary key);

create table current_documents (
  id serial primary key,
  username varchar (50) references users not null,
  title varchar (500) not null,
  sort_order integer not null,
  url text,
  notes text
);

create table hobby_tracker (
  id serial primary key,
  username varchar (50) references users not null,
  hobby varchar (500) not null,
  sort_order integer not null,
  assigned_hours_per_week real not null
);

create table hobby_completed_hours_timestamped (
  id serial primary key,
  hobby_id integer references hobby_tracker ON DELETE CASCADE not null,
  timestamp timestamp default localtimestamp not null,
  completed_hours_for_week real not null
);

create table codenames_words (
  word varchar (50) primary key);

CREATE TYPE turn_type AS ENUM ('guess', 'give_hint');

create table codenames_games (
  id serial primary key,
  player1 varchar(50) references users not null,
  player2 varchar(50) references users not null,
  turn_number integer not null,
  turn_type turn_type not null,
  time_tokens_used integer not null,
  game_over boolean not null,
  assassin_found boolean not null
);

create table codenames_turns_to_hints (
  game_id integer references codenames_games,
  turn_number integer,
  player varchar(50) references users not null,
  hint_word varchar(150) not null,
  hint_number integer not null,
  primary key (game_id, turn_number)
);

CREATE TYPE guess_outcome AS ENUM ('agent_found', 'assassin_found', 'hit_bystander');

create table codenames_turns_to_guesses (
  id serial primary key,
  game_id integer references codenames_games not null,
  turn_number integer not null,
  player varchar(50) references users not null,
  guessed_word varchar(50) references codenames_words not null,
  guess_outcome guess_outcome not null
);

CREATE TYPE word_status AS ENUM ('agent_found', 'player_1_hit_bystander', 'player_2_hit_bystander', 'both_players_hit_bystanders' , 'assassin_found', 'unchecked');

create table codenames_games_to_words (
  game_id integer references codenames_games,
  word_index integer,
  word varchar(50) references codenames_words not null,
  word_status word_status not null,
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

CREATE TYPE recipe_restaurant_entity_type AS ENUM (
  'cookbook', 'recipe', 'recipe_meal', 'city', 'restaurant', 'dish', 'dish_meal');

create table cookbooks (
  id serial primary key,
  parent_id integer default 0 not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'cookbook' not null,
  name varchar(150) not null,
  notes text
);

create table recipes (
  id serial primary key,
  parent_id integer references cookbooks not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'recipe' not null,
  name varchar(500) not null,
  category varchar(150),
  notes text
);

create table recipe_meals (
  id serial primary key,
  parent_id integer references recipes not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'recipe_meal' not null,
  date date,
  user_1_rating real,
  user_2_rating real,
  user_1_comments text,
  user_2_comments text
);

create table cities (
  id serial primary key,
  parent_id integer default 0 not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'city' not null,
  name varchar(150) not null,
  state varchar(150),
  country varchar(150),
  notes text
);

create table restaurants (
  id serial primary key,
  parent_id integer references cities not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'restaurant' not null,
  name varchar(150) not null,
  category varchar(150),
  address text,
  notes text
);

create table dishes (
  id serial primary key,
  parent_id integer references restaurants not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'dish' not null,
  name varchar(150) not null,
  category varchar(150),
  notes text
);

create table dish_meals (
  id serial primary key,
  parent_id integer references dishes not null,
  entity_type recipe_restaurant_entity_type DEFAULT 'dish_meal' not null,
  date date,
  user_1_rating real,
  user_2_rating real,
  user_1_comments text,
  user_2_comments text
);

create table recipe_images (
  id serial primary key,
  recipe_id integer references recipes not nul,
  url text not null,
  caption text
);

create table dish_images (
  id serial primary key,
  dish_id integer references dishes not null,
  url text not null,
  caption text
);

create table grocery_lists (
  id serial primary key,
  title varchar(150) not null,
  date date,
  store varchar(150),
  imported boolean not null,
  list text not null
);

create table grocery_known_words (
  word varchar(150) primary key,
  category varchar(150),
  should_save boolean not null
);

create table grocery_store_categories (
  store varchar(150) not null,
  category varchar(150) not null,
  label varchar(150),
  primary key (store, category)
);

create table pantry (
  item varchar(150) primary key
);

create table notes (
  id serial primary key,
  title varchar(150) not null,
  text text not null,
  sort_order integer not null
);

create table inventory (
  id serial primary key,
  title varchar(150) not null,
  text text not null
);
