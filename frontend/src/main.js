import { createApp } from "vue";
import App from "./App.vue";
import router from "./appRouter";
import { installTypography } from "./utils/typography";
import "./styles/forms.css";

const app = createApp(App);

app.use(router);
app.mount("#app");

const appRoot = document.getElementById("app");
if (appRoot) {
  installTypography(appRoot);
}
