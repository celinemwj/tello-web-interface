import { useNavigate } from "react-router-dom";

import {
  Box,
  Button,
  Chip,
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
import TerminalRoundedIcon from "@mui/icons-material/TerminalRounded";

import { usePipeline } from "../context/PipelineContext";


function TelemetryCard({ icon, label, value, unit }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2.2,
        borderRadius: 4,
        bgcolor: "rgba(255,255,255,0.68)",
        backdropFilter: "blur(18px)",
        borderColor: "rgba(217,220,229,0.82)",
        boxShadow: "0 18px 50px rgba(31,34,48,0.07)",
        height: "100%",
      }}
    >
      <Stack spacing={1.4}>
        <Box
          sx={{
            width: 42,
            height: 42,
            borderRadius: 2.4,
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
          variant="h5"
          fontWeight={900}
        >
          {value}

          {unit && (
            <Box
              component="span"
              sx={{
                ml: 0.7,
                fontSize: "0.9rem",
                fontWeight: 650,
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


function StatusRow({ label, value, chipColor = "default" }) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      spacing={2}
    >
      <Typography color="text.secondary">
        {label}
      </Typography>

      <Chip
        size="small"
        label={value}
        color={chipColor}
        variant="outlined"
        sx={{
          fontWeight: 750,
          bgcolor: "rgba(255,255,255,0.62)",
        }}
      />
    </Stack>
  );
}


export default function MonitoringPanel() {
  const navigate = useNavigate();
  const { latestResult } = usePipeline();

  const finalState =
    latestResult?.execution?.final_state ?? null;

  const executionLogs =
    latestResult?.execution?.logs ?? [];

  const hasState = Boolean(finalState);

  const telemetryCards = [
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

  return (
    <Stack spacing={3}>
      <Stack
        direction="row"
        justifyContent="flex-end"
        alignItems="center"
      >
        <Button
          variant="outlined"
          onClick={() => navigate("/command")}
          sx={{
            borderRadius: 3,
            fontWeight: 800,
            bgcolor: "rgba(255,255,255,0.65)",
            whiteSpace: "nowrap",
          }}
        >
          Back to command
        </Button>
      </Stack>

      {/* Main monitoring area */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "minmax(0, 1.5fr) minmax(320px, 0.7fr)",
            lg: "minmax(0, 1.55fr) minmax(380px, 0.7fr)",
          },
          gap: {
            xs: 2.5,
            md: 3,
          },
          alignItems: "stretch",
        }}
      >
        {/* Camera panel */}
        <Paper
          variant="outlined"
          sx={{
            position: "relative",
            minHeight: {
              xs: 340,
              md: 480,
            },
            borderRadius: 6,
            overflow: "hidden",
            bgcolor: "rgba(255,255,255,0.58)",
            backdropFilter: "blur(20px)",
            borderColor: "rgba(217,220,229,0.82)",
            boxShadow: "0 30px 90px rgba(31,34,48,0.11)",
          }}
        >
         

          <Chip
            label="Live camera"
            size="small"
            sx={{
              position: "absolute",
              top: 16,
              left: 16,
              fontWeight: 800,
              bgcolor: "rgba(255,255,255,0.75)",
              backdropFilter: "blur(12px)",
            }}
          />
        </Paper>

        {/* Status summary */}
        <Paper
          variant="outlined"
          sx={{
            p: {
              xs: 2.4,
              md: 3,
            },
            borderRadius: 6,
            bgcolor: "rgba(255,255,255,0.66)",
            backdropFilter: "blur(18px)",
            borderColor: "rgba(217,220,229,0.82)",
            boxShadow: "0 26px 80px rgba(31,34,48,0.09)",
          }}
        >
          <Stack spacing={2.5}>
            <Box>
              <Typography
                variant="h5"
                fontWeight={900}
              >
                Current state
              </Typography>
            </Box>

            <StatusRow
              label="State source"
              value={hasState ? "Tello" : "Unavailable"}
              chipColor={hasState ? "success" : "default"}
            />

            <StatusRow
              label="Drone status"
              value={
                finalState?.is_flying
                  ? "Flying"
                  : hasState
                    ? "Landed"
                    : "--"
              }
              chipColor={finalState?.is_flying ? "success" : "default"}
            />

            <StatusRow
              label="Video stream"
              value={finalState?.streaming ? "Active" : "Inactive"}
              chipColor={finalState?.streaming ? "success" : "default"}
            />

            <StatusRow
              label="Execution mode"
              value={latestResult?.execution_mode ?? "Mock"}
              chipColor="default"
            />

            <Box
              sx={{
                mt: 1,
                p: 2,
                borderRadius: 4,
                bgcolor: "rgba(244,245,248,0.72)",
                border: "1px solid",
                borderColor: "divider",
              }}
            >
              <Typography
                variant="body2"
                color="text.secondary"
              >
                Position
              </Typography>

              <Typography
                variant="h6"
                fontWeight={850}
                mt={0.5}
              >
                {finalState
                  ? `x=${finalState.x}, y=${finalState.y}, z=${finalState.z}`
                  : "--"}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      </Box>

      {/* Telemetry cards */}
      <Box>
        <Typography
          variant="h5"
          fontWeight={900}
        >
          Telemetry
        </Typography>
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, minmax(0, 1fr))",
            md: "repeat(4, minmax(0, 1fr))",
          },
          gap: 2.3,
        }}
      >
        {telemetryCards.map((card) => (
          <TelemetryCard
            key={card.label}
            {...card}
          />
        ))}
      </Box>

      {/* Logs */}
      <Paper
        variant="outlined"
        sx={{
          p: {
            xs: 2.4,
            md: 3,
          },
          borderRadius: 6,
          bgcolor: "rgba(255,255,255,0.66)",
          backdropFilter: "blur(18px)",
          borderColor: "rgba(217,220,229,0.82)",
          boxShadow: "0 24px 70px rgba(31,34,48,0.08)",
        }}
      >
        <Stack
          direction="row"
          spacing={1.2}
          sx={{
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box
            sx={{
              width: 42,
              height: 42,
              borderRadius: 2.4,
              display: "grid",
              placeItems: "center",
              bgcolor: "secondary.light",
              color: "primary.dark",
            }}
          >
            <TerminalRoundedIcon />
          </Box>

          <Box>
            <Typography
              variant="h6"
              fontWeight={900}
            >
              Execution logs
            </Typography>
          </Box>
        </Stack>

        {executionLogs.length > 0 ? (
          <Stack spacing={0.8}>
            {executionLogs.map((log, index) => (
              <Typography
                key={`${log}-${index}`}
                variant="body2"
                sx={{
                  fontFamily: "monospace",
                  px: 1.5,
                  py: 1,
                  borderRadius: 2,
                  bgcolor: "rgba(244,245,248,0.82)",
                }}
              >
                {log}
              </Typography>
            ))}
          </Stack>
        ) : (
          <Typography color="text.secondary">
            No execution logs available yet. Run a command from the AI mission
            console first.
          </Typography>
        )}
      </Paper>
    </Stack>
  );
}