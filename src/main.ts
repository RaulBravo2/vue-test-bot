import { createApp, type Plugin } from "vue";
import { createPinia } from "pinia";
import { createNotivue } from "notivue";
import VueApexCharts from "vue3-apexcharts";
import axios from "axios";

// THIRD PARTY CSS
import "simplebar-vue/dist/simplebar.min.css";
import "notivue/notification.css";
import "notivue/animations.css";
import "nprogress/nprogress.css";

// MAIN CSS
import "@/assets/index.css";

// ROOT FILE
import App from "./App.vue";

// ROUTER
import router from "./router";

// Full-stack vs mock: con VITE_API_BASE_URL, axios pega a la API real y NO se carga el mock;
// sin ella, se mantiene el mock de src/__mock__ (comportamiento original del template).
const apiBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
if (apiBase) {
  axios.defaults.baseURL = apiBase;
}

async function bootstrap() {
  if (!apiBase) {
    await import("./__mock__");
  }

  const app = createApp(App);

  app.use(createPinia());
  // vue3-apexcharts trae tipos imperfectos para app.use(); el cast no cambia el runtime.
  app.use(VueApexCharts as unknown as Plugin);
  app.use(createNotivue());
  app.use(router);

  app.mount("#app");
}

bootstrap();
