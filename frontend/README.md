# frontend

> A Vue.js project

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
sudo npm install socket.io-client vue-socket.io --save
sudo npm install socket.io --save

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).
