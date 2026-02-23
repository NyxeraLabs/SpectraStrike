/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
*/

import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bgPrimary: "#0B1020",
        surface: "#131A2E",
        surfaceElevated: "#1A2238",
        borderSubtle: "#222C4A",
        accentPrimary: "#7C5CFF",
        accentGlow: "#9D8CFF",
        accentHover: "#5E3FE6",
        accentFocus: "#B6A8FF",
        telemetry: "#00D4FF",
        telemetryDeep: "#0095B6",
        telemetryGlow: "#33E1FF",
        success: "#1ED760",
        warning: "#F5A524",
        critical: "#FF4D4F",
        info: "#3B82F6",
      },
      boxShadow: {
        accent: "0 0 12px rgba(124, 92, 255, 0.35)",
      },
      borderRadius: {
        panel: "12px",
      },
    }
  },
  plugins: []
};

export default config;
