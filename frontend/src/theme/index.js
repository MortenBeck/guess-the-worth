import { createSystem, defaultConfig } from "@chakra-ui/react";

const customConfig = {
  ...defaultConfig,
  tokens: {
    colors: {
      primary: {
        50: "#f0f2ff",
        100: "#e5e7ff",
        200: "#d1d6ff",
        300: "#b8bfff",
        400: "#9ba0ff",
        500: "#6366f1",
        600: "#5855eb",
        700: "#4f46e5",
        800: "#4338ca",
        900: "#3730a3",
      },
      accent: {
        50: "#fdf2f8",
        100: "#fce7f3",
        200: "#fbcfe8",
        300: "#f9a8d4",
        400: "#f472b6",
        500: "#ec4899",
        600: "#db2777",
        700: "#be185d",
        800: "#9d174d",
        900: "#831843",
      },
      secondary: {
        50: "#fffbeb",
        100: "#fef3c7",
        200: "#fed7aa",
        300: "#fdba74",
        400: "#fb923c",
        500: "#f59e0b",
        600: "#d97706",
        700: "#b45309",
        800: "#92400e",
        900: "#78350f",
      },
      bg: {
        primary: "#0f172a",
        surface: "#1e293b",
        surfaceLight: "#334155",
      },
      text: {
        primary: "#f8fafc",
        muted: "#94a3b8",
      },
    },
    gradients: {
      primary: "linear-gradient(135deg, #6366f1 0%, #ec4899 100%)",
      hero: "radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 50%)",
    },
  },
  semanticTokens: {
    colors: {
      text: {
        _light: "#050315",
        _dark: "#f8fafc",
      },
      "text.muted": {
        _light: "#64748b",
        _dark: "#94a3b8",
      },
      bg: {
        _light: "#FFFFFF",
        _dark: "#0f172a",
      },
      "bg.surface": {
        _light: "#f8fafc",
        _dark: "#1e293b",
      },
      "bg.surface.light": {
        _light: "#f1f5f9",
        _dark: "#334155",
      },
      primary: "#6366f1",
      accent: "#ec4899",
      secondary: "#f59e0b",
      success: "#10b981",
      "gradient.primary": "linear-gradient(135deg, #6366f1 0%, #ec4899 100%)",
    },
  },
  globalCss: {
    "*": {
      margin: 0,
      padding: 0,
      boxSizing: "border-box",
    },
    "html, body": {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      lineHeight: 1.6,
      overflowX: "hidden",
    },
    body: {
      bg: "bg",
      color: "text",
      minHeight: "100vh",
    },
  },
};

export const system = createSystem(customConfig);
