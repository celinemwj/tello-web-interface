import { useNavigate } from "react-router-dom";

import {
  Box,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";

import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";


export default function ImmersivePageLayout({
  title,
  subtitle,
  children,
}) {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        bgcolor: "background.default",
      }}
    >
      {/* Main central glow */}
      <Box
        sx={{
          position: "absolute",
          width: {
            xs: 520,
            md: 780,
          },
          height: {
            xs: 520,
            md: 780,
          },
          borderRadius: "50%",
          left: "50%",
          top: "48%",
          transform: "translate(-50%, -50%)",
          background:
            "radial-gradient(circle, rgba(158,184,179,0.28) 0%, rgba(111,120,157,0.12) 42%, rgba(244,245,248,0) 72%)",
          filter: "blur(12px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Top-right decorative circle */}
      <Box
        sx={{
          position: "absolute",
          width: {
            xs: 330,
            md: 460,
          },
          height: {
            xs: 330,
            md: 460,
          },
          borderRadius: "50%",
          right: {
            xs: -180,
            md: -190,
          },
          top: {
            xs: -130,
            md: -160,
          },
          bgcolor: "rgba(111,120,157,0.08)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Bottom-left decorative circle */}
      <Box
        sx={{
          position: "absolute",
          width: {
            xs: 300,
            md: 420,
          },
          height: {
            xs: 300,
            md: 420,
          },
          borderRadius: "50%",
          left: {
            xs: -170,
            md: -190,
          },
          bottom: {
            xs: -160,
            md: -190,
          },
          bgcolor: "rgba(158,184,179,0.13)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Header */}
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{
          position: "relative",
          zIndex: 5,
          px: {
            xs: 2,
            sm: 3,
            md: 4,
          },
          pt: {
            xs: 2,
            md: 2.5,
          },
        }}
      >
        <IconButton
          aria-label="Back to home"
          onClick={() => navigate("/")}
          sx={{
            width: 44,
            height: 44,
            color: "primary.dark",
            border: "1px solid",
            borderColor: "divider",
            bgcolor: "rgba(255,255,255,0.72)",
            backdropFilter: "blur(12px)",
            boxShadow: "0 14px 34px rgba(31,34,48,0.08)",

            "&:hover": {
              bgcolor: "background.paper",
            },
          }}
        >
          <ArrowBackRoundedIcon />
        </IconButton>

        <Box
          component="img"
          src="/assets/logo-ibisc.png"
          alt="IBISC logo"
          sx={{
            width: {
              xs: 120,
              sm: 170,
              md: 230,
            },
            height: {
              xs: 58,
              sm: 72,
              md: 88,
            },
            objectFit: "contain",
            objectPosition: "right center",
            flexShrink: 0,
          }}
        />
      </Stack>

      {/* Title */}
      <Box
        sx={{
          position: "relative",
          zIndex: 2,
          textAlign: "center",
          mt: {
            xs: 3,
            md: 1,
          },
          px: 2,
        }}
      >
        <Typography
          component="h1"
          sx={{
            fontSize: {
              xs: "2.7rem",
              sm: "4rem",
              md: "5.4rem",
              lg: "6.4rem",
            },
            lineHeight: 0.9,
            letterSpacing: "-0.065em",
            fontWeight: 900,
            color: "text.primary",
          }}
        >
          {title}
        </Typography>

        {subtitle && (
          <Typography
            sx={{
              mt: 1.5,
              mx: "auto",
              maxWidth: 700,
              color: "text.secondary",
              fontSize: {
                xs: "0.95rem",
                md: "1.05rem",
              },
            }}
          >
            {subtitle}
          </Typography>
        )}
      </Box>

      {/* Page content */}
      <Box
        sx={{
          position: "relative",
          zIndex: 3,
          width: "100%",
          maxWidth: 1500,
          mx: "auto",
          px: {
            xs: 2,
            sm: 3,
            md: 5,
          },
          pt: {
            xs: 4,
            md: 5,
          },
          pb: {
            xs: 4,
            md: 5,
          },
        }}
      >
        {children}
      </Box>
    </Box>
  );
}