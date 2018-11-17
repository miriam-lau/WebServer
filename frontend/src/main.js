// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import VueCookies from 'vue-cookies'
import { store } from './store/store'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faPencilAlt, faSave, faTimes, faTrash, faLongArrowAltUp, faLongArrowAltDown } from
  '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faPencilAlt)
library.add(faSave)
library.add(faTimes)
library.add(faTrash)
library.add(faLongArrowAltUp)
library.add(faLongArrowAltDown)

Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.config.productionTip = false
Vue.use(VueCookies)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})
