import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",

    primary: {
      main: "#6F789D",
      light: "#A8AFCB",
      dark: "#3B455E",
      contrastText: "#FFFFFF",
    },

    secondary: {
      main: "#9EB8B3",
      light: "#C1DEDB",
      dark: "#5B6968",
      contrastText: "#111827",
    },

    background: {
      default: "#F4F5F8",
      paper: "#FFFFFF",
    },

    text: {
      primary: "#1F2230",
      secondary: "#6B7280",
    },

    success: {
      main: "#6F8F83",
    },

    warning: {
      main: "#C28A4A",
    },

    error: {
      main: "#B85C5C",
    },

    divider: "#D9DCE5",
  },

  typography: {
    fontFamily: [
      "Inter",
      "Roboto",
      "Arial",
      "sans-serif",
    ].join(","),

    h1: {
      fontSize: "2rem",
      fontWeight: 700,
    },

    h2: {
      fontSize: "1.4rem",
      fontWeight: 700,
    },

    h3: {
      fontSize: "1.05rem",
      fontWeight: 600,
    },

    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },

  shape: {
    borderRadius: 12,
  },

  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          paddingInline: 20,
          paddingBlock: 10,
        },
      },
    },

    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          border: "1px solid #D9DCE5",
          boxShadow: "0 8px 24px rgba(31, 34, 48, 0.06)",
        },
      },
    },
  },
});

export default theme;