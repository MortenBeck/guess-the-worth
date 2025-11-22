import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Auth0Provider } from "@auth0/auth0-react";
import * as Sentry from "@sentry/react";
import { config } from "./config/env";
import socketService from "./services/socket";
import "./index.css";
import App from "./App.jsx";

// Initialize Sentry
if (config.SENTRY_DSN) {
  Sentry.init({
    dsn: config.SENTRY_DSN,
    integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
    tracesSampleRate: 0.1, // 10% of transactions for performance monitoring
    replaysSessionSampleRate: 0.1, // 10% session replays
    replaysOnErrorSampleRate: 1.0, // 100% replays when errors occur
    environment: import.meta.env.MODE,
  });
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

// Enable WebSocket connection for real-time bidding updates
socketService.enable();

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Auth0Provider
      domain={config.AUTH0_DOMAIN}
      clientId={config.AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: config.AUTH0_AUDIENCE,
      }}
    >
      <QueryClientProvider client={queryClient}>
        <ChakraProvider value={defaultSystem}>
          <App />
        </ChakraProvider>
      </QueryClientProvider>
    </Auth0Provider>
  </StrictMode>
);
