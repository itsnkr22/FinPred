export default defineEventHandler((event) => {
  // Proxy API requests to backend in development
  const config = useRuntimeConfig();
  const target = config.public.apiBase || "http://localhost:8000";
  const path = event.path;

  return proxyRequest(event, `${target}${path}`);
});
