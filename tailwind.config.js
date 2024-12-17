/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");

export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: colors.gray[200],
        active: colors.green[200],
        dim: colors.zinc[600],
        success: colors.green[400],
        background: colors.neutral[800],
        input: colors.neutral[700],
      },
    },
  },
  plugins: [],
};
