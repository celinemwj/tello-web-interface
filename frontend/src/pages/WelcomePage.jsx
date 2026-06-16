import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  AppBar,
  Box,
  Button,
  Container,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";

import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import ChatRoundedIcon from "@mui/icons-material/ChatRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";

import DroneScene from "../components/three/DroneScene";


export default function WelcomePage() {
  const navigate = useNavigate();

  const [menuAnchor, setMenuAnchor] = useState(null);

  const isMenuOpen = Boolean(menuAnchor);

  function openMenu(event) {
    setMenuAnchor(event.currentTarget);
  }

  function closeMenu() {
    setMenuAnchor(null);
  }

  function goToPage(path) {
    closeMenu();
    navigate(path);
  }

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        bgcolor: "background.default",
        overflow: "hidden",
      }}
    >
      {/* Background glow behind the drone */}
      <Box
        sx={{
          position: "absolute",
          width: {
            xs: 500,
            md: 720,
          },
          height: {
            xs: 500,
            md: 720,
          },
          borderRadius: "50%",
          left: "50%",
          top: "52%",
          transform: "translate(-50%, -50%)",
          background:
            "radial-gradient(circle, rgba(158,184,179,0.36) 0%, rgba(111,120,157,0.16) 42%, rgba(244,245,248,0) 72%)",
          filter: "blur(10px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Top-right decorative circle */}
      <Box
        sx={{
          position: "absolute",
          width: 430,
          height: 430,
          borderRadius: "50%",
          right: -180,
          top: -130,
          bgcolor: "rgba(111,120,157,0.08)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Bottom-left decorative circle */}
      <Box
        sx={{
          position: "absolute",
          width: 360,
          height: 360,
          borderRadius: "50%",
          left: -180,
          bottom: -170,
          bgcolor: "rgba(158,184,179,0.12)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Header */}
      <AppBar
        position="relative"
        elevation={0}
        sx={{
          zIndex: 5,
          bgcolor: "transparent",
          color: "text.primary",
        }}
      >
        <Container
          maxWidth={false}
          sx={{
            px: {
              xs: 2,
              sm: 3,
              md: 4,
            },
          }}
        >
          <Toolbar
            disableGutters
            sx={{
              minHeight: 96,
              width: "100%",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            {/* Left side */}
            <Stack
              direction="row"
              alignItems="center"
              spacing={1.5}
            >
              <IconButton
                aria-label="Open navigation menu"
                onClick={openMenu}
                sx={{
                  width: 44,
                  height: 44,
                  color: "primary.dark",
                  border: "1px solid",
                  borderColor: "divider",
                  bgcolor: "rgba(255,255,255,0.72)",
                  backdropFilter: "blur(12px)",
                  boxShadow:
                    "0 14px 34px rgba(31,34,48,0.08)",

                  "&:hover": {
                    bgcolor: "background.paper",
                  },
                }}
              >
                <MenuRoundedIcon />
              </IconButton>

              <Menu
                anchorEl={menuAnchor}
                open={isMenuOpen}
                onClose={closeMenu}
                PaperProps={{
                  sx: {
                    mt: 1.2,
                    minWidth: 230,
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                    bgcolor: "rgba(255,255,255,0.92)",
                    backdropFilter: "blur(16px)",
                    boxShadow:
                      "0 24px 70px rgba(31,34,48,0.14)",
                    p: 0.8,
                  },
                }}
              >
                <MenuItem
                  onClick={() => goToPage("/command")}
                  sx={{
                    py: 1.4,
                    borderRadius: 2,
                    mb: 0.5,
                  }}
                >
                  <ListItemIcon>
                    <ChatRoundedIcon fontSize="small" />
                  </ListItemIcon>

                  <ListItemText
                    primary="AI command"
                    secondary="Send drone missions"
                    primaryTypographyProps={{
                      fontWeight: 750,
                    }}
                    secondaryTypographyProps={{
                      fontSize: "0.78rem",
                    }}
                  />
                </MenuItem>

                <MenuItem
                  onClick={() => goToPage("/monitoring")}
                  sx={{
                    py: 1.4,
                    borderRadius: 2,
                  }}
                >
                  <ListItemIcon>
                    <DashboardRoundedIcon fontSize="small" />
                  </ListItemIcon>

                  <ListItemText
                    primary="Monitoring"
                    secondary="View drone state"
                    primaryTypographyProps={{
                      fontWeight: 750,
                    }}
                    secondaryTypographyProps={{
                      fontSize: "0.78rem",
                    }}
                  />
                </MenuItem>
              </Menu>
            </Stack>

            {/* Right side */}
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
          </Toolbar>
        </Container>
      </AppBar>

      {/* Large centered title behind the drone */}
      <Box
        sx={{
          position: "absolute",
          top: 84,
          right: 0,
          bottom: 0,
          left: 0,
          zIndex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          pointerEvents: "none",
          px: 2,
          pb: {
            xs: 15,
            md: 8,
          },
          transform: "translateY(-200px)",
        }}
      >
        <Typography
          component="h1"
          sx={{
            width: "100%",
            maxWidth: 1250,
            fontSize: {
              xs: "3.1rem",
              sm: "4.8rem",
              md: "6.5rem",
              lg: "8rem",
              xl: "9rem",
            },
            lineHeight: 0.86,
            letterSpacing: "-0.065em",
            fontWeight: 900,
            color: "text.primary",
          }}
        >
          Drone control

          <Box
            component="span"
            sx={{
              display: "block",
              color: "primary.main",
            }}
          >
            with natural language.
          </Box>
        </Typography>
      </Box>

      {/* Interactive drone displayed in front of the title */}
      <Box
        sx={{
          position: "absolute",
          top: 84,
          right: 0,
          bottom: 0,
          left: 0,
          zIndex: 2,
          pointerEvents: "auto",
        }}
      >
        <DroneScene />
      </Box>

      {/* Buttons displayed in front */}
      <Box
        sx={{
          position: "absolute",
          left: "50%",
          bottom: {
            xs: 64,
            md: 50,
          },
          transform: "translateX(-50%)",
          zIndex: 3,
          width: {
            xs: "calc(100% - 32px)",
            md: "auto",
          },
          maxWidth: 760,
          pointerEvents: "none",
        }}
      >
        <Stack
          spacing={2.2}
          alignItems="center"
          textAlign="center"
        >
          <Stack
            direction={{
              xs: "column",
              sm: "row",
            }}
            spacing={2}
            justifyContent="center"
            alignItems="center"
            sx={{
              pointerEvents: "auto",
              width: "100%",
            }}
          >
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate("/command")}
              sx={{
                px: 3.5,
                py: 1.35,
                boxShadow:
                  "0 14px 30px rgba(89,103,138,0.24)",
              }}
            >
              Start a mission
            </Button>

            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate("/monitoring")}
              sx={{
                px: 3.5,
                py: 1.35,
                bgcolor: "rgba(255,255,255,0.72)",
                backdropFilter: "blur(12px)",
              }}
            >
              View monitoring
            </Button>
          </Stack>
        </Stack>
      </Box>
    </Box>
  );
}