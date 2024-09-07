import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { Quasar, Notify } from "quasar";
import BackendService from "./services/backend-service";

// Import icon libraries
import "@quasar/extras/material-icons/material-icons.css";

// Import Quasar css
import "quasar/src/css/index.sass";

const app = createApp(App);

app.use(router);
app.use(Quasar, {
  plugins: { Notify }, // import Quasar plugins and add here
});

var backendService = new BackendService();
app.provide("backendService", backendService);

app.mount("#app");
