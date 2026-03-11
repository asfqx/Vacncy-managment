import { createApp } from "vue";
import App from "./App.vue";
import router from "./appRouter";
import "./styles/forms.css";

createApp(App).use(router).mount("#app");
