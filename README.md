# WebServer


## Build Setup

* git clone git@github.com:miriam-lau/WebServer.git
* install python
* install npm
* install postgres
* In postgres: 
  * create database webserver;
  * create user webserver with password <password>;
  * grant all privileges on database webserver to webserver;

## Setting up the backend server
Navigate to the /backend/ directory.
```
python3 -m pip install --user virtualenv
python3 -m virtualenv env
python3 -m pip install flask flask-socketio eventlet
python3 -m pip install psycopg2
python3 -m pip install -U flask-cors
python3 -m pip install pyyaml
python3 -m pip install beautifulsoup4
```

## Setting up the frontend server
Navigate to the /frontend/ directory.
```
npm install -g vue-cli
npm install vue-cookies --save
npm install vuex --save
npm install axios --save
npm i --save @fortawesome/fontawesome-svg-core
npm i --save @fortawesome/free-solid-svg-icons
npm install --save @fortawesome/vue-fontawesome
npm install vue-masonry --save
```

## Running the backend server
Navigate to /backend/src/

On windows:
```
flask run --reload --debugger --host=0.0.0.0
```
On all others:
```
flask run --debugger --host=0.0.0.0
```

## Running the frontend server
Navigate to /frontend/
```
npm run dev -- --hot --host 0.0.0.0
```

## Database setup

Copy the code below into the database cmd line to set up the database. 
```
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
drop table codenames_games cascade;
drop table codenames_turns_to_hints cascade;
drop table codenames_turns_to_guesses cascade;
drop table codenames_games_to_words cascade;
drop table codenames_games_to_locations cascade;
drop table grocery_list cascade;
drop table grocery_known_words cascade;
drop table pantry cascade;
drop table notes cascade;
drop table dominion_games cascade;
drop table lotr_games cascade;

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
  guessed_word varchar(50) not null,
  guess_outcome guess_outcome not null
);

CREATE TYPE word_status AS ENUM ('agent_found', 'player_1_hit_bystander', 'player_2_hit_bystander', 'both_players_hit_bystanders' , 'assassin_found', 'unchecked');

create table codenames_games_to_words (
  game_id integer references codenames_games,
  word_index integer,
  word varchar(50) not null,
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

create table grocery_stores (
  store varchar(150) primary key
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

create table dominion_games (
  id serial primary key,
  player1 varchar(50) references users not null,
  player2 varchar(50) references users not null
);

create table dominion_game_data (
  id serial primary key,
  game_id integer references dominion_games on DELETE CASCADE not null,
  data jsonb
);

create table lotr_games (
  id serial primary key,
  player1 varchar(50) references users not null,
  player2 varchar(50) references users not null
);

create table lotr_game_data (
  id serial primary key,
  game_id integer references lotr_games on DELETE CASCADE not null,
  data jsonb
);

create table lotr_most_recent_deck (
  player varchar(50) references users primary key,
  xml text
);

```
## [Optional] Copying the recipe/restaurant databases to Google Drive
This generates a spreadsheet with the entries in the recipes and restaurants databases.<br/><br/>

For Recipes: Run the following command in psql as the webserver user:
```
copy (select recipe_meals.date as "Date", cookbooks.name as "Cookbook", recipes.name as "Recipe", ROUND(CAST((recipe_meals.user_1_rating + recipe_meals.user_2_rating)/2 as numeric), 2) as "Average Rating", recipe_meals.user_1_rating as "Miriam's Rating", recipe_meals.user_2_rating as "James' Rating", recipes.category as "Category", recipes.notes as "Notes", recipe_meals.user_1_comments as "Miriam's Comments", recipe_meals.user_2_comments as "James' Comments", cookbooks.notes as "Cookbook Notes" from cookbooks,recipes,recipe_meals where recipes.parent_id = cookbooks.id and recipe_meals.parent_id = recipes.id) to '/home/webserver/Recipe Ratings.csv' with (format csv,header, delimiter ',');
scp webserver@192.168.86.100:"/home/webserver/Recipe\ Ratings.csv" .
```

For Restaurants: Run the following command in psql as the webserver user:
```
copy (select dish_meals.date as "Date", cities.name as "City", restaurants.name as "Restaurant", dishes.name as "Dish", ROUND(CAST((dish_meals.user_1_rating + dish_meals.user_2_rating)/2 as numeric), 2) as "Average Rating", dish_meals.user_1_rating as "Miriam's Rating", dish_meals.user_2_rating as "James' Rating", dishes.category as "Dish Category", restaurants.category as "Restaurant Category", dishes.notes as "Notes", dish_meals.user_1_comments as "Miriam's Comments", dish_meals.user_2_comments as "James' Comments", restaurants.address as "Address", cities.state as "State", cities.country as "Country", restaurants.notes as "Restaurant Notes" from cities,restaurants,dishes,dish_meals where restaurants.parent_id = cities.id and dishes.parent_id = restaurants.id and dish_meals.parent_id = dishes.id) to '/home/webserver/Restaurant Ratings.csv' with (format csv,header, delimiter ',');
scp webserver@192.168.86.100:"/home/webserver/Restaurant\ Ratings.csv" .
```

## [Optional] How to back up and restore the database in windows
https://stackoverflow.com/questions/28048412/how-to-backup-restore-postgresql-database-in-windows7
