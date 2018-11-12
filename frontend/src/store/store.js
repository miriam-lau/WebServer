import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    username: ''
  },
  getters: {
    getUsername: state => {
      return state.username
    }
  },
  mutations: {
    setUsername (state, username) {
      state.username = username
    }
  }
})
