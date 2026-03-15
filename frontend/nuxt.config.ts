export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
    },
  },

  css: ["~/assets/css/main.css"],

  app: {
    head: {
      title: "MiroFish FinPredict",
      meta: [
        {
          name: "description",
          content:
            "Multi-agent AI simulation engine for US market sentiment forecasting",
        },
      ],
    },
  },
});
