import {
  Box,
  Chip,
  Grid,
  Paper,
  Stack,
  Typography,
} from "@mui/material";

import BatteryChargingFullRoundedIcon from "@mui/icons-material/BatteryChargingFullRounded";
import HeightRoundedIcon from "@mui/icons-material/HeightRounded";
import SpeedRoundedIcon from "@mui/icons-material/SpeedRounded";
import ExploreRoundedIcon from "@mui/icons-material/ExploreRounded";
import ThermostatRoundedIcon from "@mui/icons-material/ThermostatRounded";
import WifiRoundedIcon from "@mui/icons-material/WifiRounded";
import SensorsRoundedIcon from "@mui/icons-material/SensorsRounded";
import FlightTakeoffRoundedIcon from "@mui/icons-material/FlightTakeoffRounded";
import VideocamRoundedIcon from "@mui/icons-material/VideocamRounded";

import DashboardLayout from "../components/layout/DashboardLayout";
import { usePipeline } from "../context/PipelineContext";


function SensorCard({ icon, label, value, unit }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2.5,
        borderRadius: 3,
        height: "100%",
        bgcolor: "rgba(255,255,255,0.82)",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",

        "&:hover": {
          transform: "translateY(-3px)",
          boxShadow: "0 12px 30px rgba(31,34,48,0.08)",
        },
      }}
    >
      <Stack spacing={1.5}>
        <Box
          sx={{
            width: 42,
            height: 42,
            borderRadius: 2.5,
            display: "grid",
            placeItems: "center",
            bgcolor: "secondary.light",
            color: "primary.dark",
          }}
        >
          {icon}
        </Box>

        <Typography
          variant="body2"
          color="text.secondary"
        >
          {label}
        </Typography>

        <Typography
          variant="h4"
          fontWeight={850}
          color="text.primary"
        >
          {value}

          {unit && (
            <Box
              component="span"
              sx={{
                ml: 0.8,
                fontSize: "1rem",
                fontWeight: 600,
                color: "text.secondary",
              }}
            >
              {unit}
            </Box>
          )}
        </Typography>
      </Stack>
    </Paper>
  );
}


export default function MonitoringPage() {
  const { latestResult } = usePipeline();

  const finalState =
    latestResult?.execution?.final_state ?? null;

  const executionLogs =
    latestResult?.execution?.logs ?? [];

  const isStateAvailable = Boolean(finalState);

  const sensors = [
    {
      label: "Battery",
      value: finalState?.battery ?? "--",
      unit: "%",
      icon: <BatteryChargingFullRoundedIcon />,
    },
    {
      label: "Height",
      value: finalState?.height ?? "--",
      unit: "cm",
      icon: <HeightRoundedIcon />,
    },
    {
      label: "Speed",
      value: finalState?.speed ?? "--",
      unit: "cm/s",
      icon: <SpeedRoundedIcon />,
    },
    {
      label: "Yaw",
      value: finalState?.yaw ?? "--",
      unit: "°",
      icon: <ExploreRoundedIcon />,
    },
    {
      label: "Temperature",
      value: finalState?.temperature ?? "--",
      unit: "°C",
      icon: <ThermostatRoundedIcon />,
    },
    {
      label: "ToF distance",
      value: finalState?.tof ?? "--",
      unit: "cm",
      icon: <SensorsRoundedIcon />,
    },
    {
      label: "Wi-Fi signal",
      value: finalState?.wifi_snr ?? "--",
      unit: "SNR",
      icon: <WifiRoundedIcon />,
    },
    {
      label: "Flight state",
      value:
        finalState === null
          ? "--"
          : finalState.is_flying
            ? "Flying"
            : "Landed",
      unit: "",
      icon: <FlightTakeoffRoundedIcon />,
    },
  ];

  const headerStatus = (
    <Chip
      label={
        isStateAvailable
          ? "Mock state available"
          : "No state available"
      }
      color={isStateAvailable ? "success" : "default"}
      variant="outlined"
      sx={{
        fontWeight: 700,
      }}
    />
  );

  return (
    <DashboardLayout
      title="Drone monitoring"
      subtitle="Camera stream, sensor values and current drone state"
      headerAction={headerStatus}
    >
      <Stack spacing={3}>
        {/* Camera and status area */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              lg: "minmax(0, 1.7fr) minmax(300px, 0.7fr)",
            },
            gap: 3,
          }}
        >
          {/* Camera placeholder */}
          <Paper
            variant="outlined"
            sx={{
              position: "relative",
              minHeight: {
                xs: 280,
                md: 420,
              },
              borderRadius: 4,
              overflow: "hidden",
              bgcolor: "#1F2230",
              display: "grid",
              placeItems: "center",
            }}
          >
            <Stack
              spacing={1.5}
              sx={{
                alignItems: "center",
                textAlign: "center",
                color: "#F4F5F8",
                px: 3,
              }}
            >
              <VideocamRoundedIcon
                sx={{
                  fontSize: 64,
                  color: "secondary.main",
                }}
              />

              <Typography
                variant="h6"
                fontWeight={800}
              >
                Camera stream unavailable
              </Typography>

              <Typography
                variant="body2"
                sx={{
                  maxWidth: 430,
                  color: "rgba(244,245,248,0.7)",
                }}
              >
                The live DJI Tello camera stream will appear here
                when the physical drone is connected.
              </Typography>

              <Chip
                label="Mock mode"
                sx={{
                  mt: 1,
                  bgcolor: "rgba(158,184,179,0.18)",
                  color: "#C1DEDB",
                  border: "1px solid rgba(193,222,219,0.35)",
                }}
              />
            </Stack>
          </Paper>

          {/* General state */}
          <Paper
            variant="outlined"
            sx={{
              p: 3,
              borderRadius: 4,
              bgcolor: "rgba(255,255,255,0.82)",
            }}
          >
            <Typography
              variant="h6"
              fontWeight={850}
            >
              Current status
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              mt={0.5}
              mb={3}
            >
              Summary of the latest MockTello execution.
            </Typography>

            <Stack spacing={2}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography color="text.secondary">
                  State source
                </Typography>

                <Chip
                  size="small"
                  label={
                    isStateAvailable
                      ? "MockTello"
                      : "Unavailable"
                  }
                  color={
                    isStateAvailable
                      ? "secondary"
                      : "default"
                  }
                />
              </Stack>

              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography color="text.secondary">
                  Drone
                </Typography>

                <Typography fontWeight={750}>
                  {finalState?.is_flying
                    ? "Flying"
                    : isStateAvailable
                      ? "Landed"
                      : "--"}
                </Typography>
              </Stack>

              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography color="text.secondary">
                  Video stream
                </Typography>

                <Typography fontWeight={750}>
                  {finalState?.streaming
                    ? "Active"
                    : "Inactive"}
                </Typography>
              </Stack>

              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography color="text.secondary">
                  Position
                </Typography>

                <Typography fontWeight={750}>
                  {finalState
                    ? `(${finalState.x}, ${finalState.y}, ${finalState.z})`
                    : "--"}
                </Typography>
              </Stack>
            </Stack>
          </Paper>
        </Box>

        {/* Sensor heading */}
        <Box>
          <Typography
            variant="h5"
            fontWeight={900}
          >
            Sensor information
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            mt={0.5}
          >
            Values returned by the most recent simulated execution.
          </Typography>
        </Box>

        {!finalState ? (
          <Paper
            variant="outlined"
            sx={{
              p: 5,
              borderRadius: 4,
              textAlign: "center",
              bgcolor: "rgba(255,255,255,0.72)",
            }}
          >
            <SensorsRoundedIcon
              sx={{
                fontSize: 56,
                color: "primary.main",
                mb: 1.5,
              }}
            />

            <Typography
              variant="h6"
              fontWeight={800}
            >
              No drone state available
            </Typography>

            <Typography
              color="text.secondary"
              mt={1}
            >
              Run a valid command from the AI command page first.
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={2.5}>
            {sensors.map((sensor) => (
              <Grid
                key={sensor.label}
                size={{
                  xs: 12,
                  sm: 6,
                  md: 4,
                  lg: 3,
                }}
              >
                <SensorCard {...sensor} />
              </Grid>
            ))}
          </Grid>
        )}

        {/* Logs */}
        {executionLogs.length > 0 && (
          <Paper
            variant="outlined"
            sx={{
              p: 3,
              borderRadius: 4,
              bgcolor: "#1F2230",
              color: "#F4F5F8",
            }}
          >
            <Typography
              fontWeight={800}
              mb={2}
            >
              Latest execution logs
            </Typography>

            <Stack spacing={0.8}>
              {executionLogs.map((log, index) => (
                <Typography
                  key={`${log}-${index}`}
                  variant="body2"
                  sx={{
                    fontFamily: "monospace",
                    color: "rgba(244,245,248,0.82)",
                  }}
                >
                  {log}
                </Typography>
              ))}
            </Stack>
          </Paper>
        )}
      </Stack>
    </DashboardLayout>
  );
}