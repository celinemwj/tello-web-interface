import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  AppBar,
  Box,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";

import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";
import ChatRoundedIcon from "@mui/icons-material/ChatRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import ChevronLeftRoundedIcon from "@mui/icons-material/ChevronLeftRounded";

import PageBackground from "../common/PageBackground";


const DRAWER_WIDTH = 250;


const navigationItems = [
  {
    label: "Home",
    path: "/",
    icon: <HomeRoundedIcon />,
  },
  {
    label: "AI command",
    path: "/command",
    icon: <ChatRoundedIcon />,
  },
  {
    label: "Monitoring",
    path: "/monitoring",
    icon: <DashboardRoundedIcon />,
  },
];


export default function DashboardLayout({
  title,
  subtitle,
  headerAction,
  children,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  const [mobileOpen, setMobileOpen] = useState(false);

  function handleNavigation(path) {
    navigate(path);
    setMobileOpen(false);
  }

  const drawerContent = (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
      }}
    >
      <Stack
        direction="row"
        alignItems="center"
        spacing={1.3}
        sx={{
          minHeight: 82,
          px: 2.5,
        }}
      >
        <Box
          component="img"
          src="/assets/tello-ai-logo.png"
          alt="Tello AI logo"
          sx={{
            width: 48,
            height: 48,
            objectFit: "contain",
          }}
        />

        <Box sx={{ flexGrow: 1 }}>
          <Typography fontWeight={850}>
            Tello AI
          </Typography>

          <Typography
            variant="caption"
            color="text.secondary"
          >
            Robotics platform
          </Typography>
        </Box>

        <IconButton
          onClick={() => setMobileOpen(false)}
          sx={{
            display: {
              xs: "inline-flex",
              lg: "none",
            },
          }}
        >
          <ChevronLeftRoundedIcon />
        </IconButton>
      </Stack>

      <Divider />

      <List
        sx={{
          px: 1.5,
          py: 2,
        }}
      >
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <ListItemButton
              key={item.path}
              selected={isActive}
              onClick={() => handleNavigation(item.path)}
              sx={{
                mb: 0.8,
                borderRadius: 2.5,
                minHeight: 48,

                "&.Mui-selected": {
                  bgcolor: "rgba(111,120,157,0.14)",
                  color: "primary.dark",
                },

                "&.Mui-selected:hover": {
                  bgcolor: "rgba(111,120,157,0.2)",
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 42,
                  color: isActive
                    ? "primary.main"
                    : "text.secondary",
                }}
              >
                {item.icon}
              </ListItemIcon>

              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontWeight: isActive ? 800 : 600,
                }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Box sx={{ flexGrow: 1 }} />

      <Divider />

      <Box sx={{ p: 2.5 }}>
        <Box
          component="img"
          src="/assets/logo-ibisc.png"
          alt="IBISC logo"
          sx={{
            width: "100%",
            maxHeight: 70,
            objectFit: "contain",
          }}
        />
      </Box>
    </Box>
  );

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <PageBackground />

      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          ml: {
            lg: `${DRAWER_WIDTH}px`,
          },
          width: {
            lg: `calc(100% - ${DRAWER_WIDTH}px)`,
          },
          bgcolor: "rgba(244,245,248,0.9)",
          color: "text.primary",
          backdropFilter: "blur(14px)",
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Toolbar
          sx={{
            minHeight: 78,
            gap: 2,
          }}
        >
          <IconButton
            aria-label="Open navigation"
            onClick={() => setMobileOpen(true)}
            sx={{
              display: {
                lg: "none",
              },
              border: "1px solid",
              borderColor: "divider",
              bgcolor: "background.paper",
            }}
          >
            <MenuRoundedIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h6"
              fontWeight={850}
            >
              {title}
            </Typography>

            {subtitle && (
              <Typography
                variant="body2"
                color="text.secondary"
              >
                {subtitle}
              </Typography>
            )}
          </Box>

          {headerAction}
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: {
            lg: DRAWER_WIDTH,
          },
          flexShrink: {
            lg: 0,
          },
        }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: {
              xs: "block",
              lg: "none",
            },

            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        <Drawer
          variant="permanent"
          open
          sx={{
            display: {
              xs: "none",
              lg: "block",
            },

            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              borderRight: "1px solid",
              borderColor: "divider",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          ml: {
            lg: `${DRAWER_WIDTH}px`,
          },
          pt: "78px",
          minHeight: "100vh",
          position: "relative",
          zIndex: 1,
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            py: {
              xs: 2.5,
              md: 4,
            },
          }}
        >
          {children}
        </Container>
      </Box>
    </Box>
  );
}