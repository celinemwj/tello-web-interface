import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";
import CodeRoundedIcon from "@mui/icons-material/CodeRounded";
import CheckCircleOutlineRoundedIcon from "@mui/icons-material/CheckCircleOutlineRounded";
import TerminalRoundedIcon from "@mui/icons-material/TerminalRounded";
import RouteRoundedIcon from "@mui/icons-material/RouteRounded";
import SensorsRoundedIcon from "@mui/icons-material/SensorsRounded";

import { executeCommand } from "../services/telloApi";


function SectionTitle({ icon, title, subtitle }) {
  return (
    <Stack direction="row" spacing={1.5} alignItems="center" mb={2}>
      <Box
        sx={{
          width: 38,
          height: 38,
          borderRadius: 2,
          bgcolor: "primary.light",
          color: "primary.dark",
          display: "grid",
          placeItems: "center",
        }}
      >
        {icon}
      </Box>

      <Box>
        <Typography variant="h3">{title}</Typography>

        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </Box>
    </Stack>
  );
}


function CodeBlock({ children }) {
  return (
    <Box
      component="pre"
      sx={{
        m: 0,
        p: 2.5,
        borderRadius: 2.5,
        bgcolor: "#1F2230",
        color: "#F4F5F8",
        overflowX: "auto",
        fontSize: "0.88rem",
        lineHeight: 1.7,
        whiteSpace: "pre-wrap",
      }}
    >
      <code>{children}</code>
    </Box>
  );
}


export default function CommandPanel() {
  const [command, setCommand] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setResult(null);
    setIsLoading(true);

    try {
      const apiResult = await executeCommand(command);
      setResult(apiResult);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  const interpretedCommands = result?.llm_output?.commands ?? [];
  const validationErrors = result?.validation?.errors ?? [];
  const executionLogs = result?.execution?.logs ?? [];
  const finalState = result?.execution?.final_state ?? null;

  return (
    <Stack spacing={3}>
      <Card>
        <CardContent sx={{ p: { xs: 2.5, md: 4 } }}>
          <SectionTitle
            icon={<RouteRoundedIcon />}
            title="Drone command"
            subtitle="Write a natural-language instruction for the DJI Tello."
          />

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              minRows={4}
              maxRows={8}
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              placeholder="Enter a natural-language command"
              disabled={isLoading}
            />

            <Stack
              direction={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "stretch", sm: "center" }}
              spacing={2}
              mt={2.5}
            >
              <Typography variant="body2" color="text.secondary">
                The command will be interpreted, validated, converted to Python,
                and tested with MockTello.
              </Typography>

              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={
                  isLoading ? (
                    <CircularProgress size={18} color="inherit" />
                  ) : (
                    <PlayArrowRoundedIcon />
                  )
                }
                disabled={isLoading || !command.trim()}
              >
                {isLoading ? "Processing..." : "Run command"}
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}

      {result && (
        <>
          <Alert severity={result.success ? "success" : "warning"}>
            {result.success
              ? "The complete pipeline finished successfully."
              : "The command was rejected or could not be executed."}
          </Alert>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 3 }}>
                  <SectionTitle
                    icon={<RouteRoundedIcon />}
                    title="Interpreted actions"
                    subtitle="Structured actions returned by the language model."
                  />

                  {interpretedCommands.length > 0 ? (
                    <Stack spacing={1.25}>
                      {interpretedCommands.map((item, index) => (
                        <Paper
                          key={`${item.action}-${index}`}
                          variant="outlined"
                          sx={{
                            p: 1.75,
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            gap: 2,
                          }}
                        >
                          <Box>
                            <Typography fontWeight={700}>
                              {index + 1}. {item.action}
                            </Typography>

                            {item.value !== undefined && (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Value: {item.value} {item.unit ?? ""}
                              </Typography>
                            )}
                          </Box>

                          <Chip
                            size="small"
                            label="Allowed action"
                            color="secondary"
                          />
                        </Paper>
                      ))}
                    </Stack>
                  ) : (
                    <Typography color="text.secondary">
                      No interpreted actions available.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 3 }}>
                  <SectionTitle
                    icon={<CodeRoundedIcon />}
                    title="Generated Python code"
                    subtitle="DJITelloPy code generated from validated actions."
                  />

                  {result.generated_code ? (
                    <CodeBlock>{result.generated_code}</CodeBlock>
                  ) : (
                    <Typography color="text.secondary">
                      No code was generated because validation failed.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 3 }}>
                  <SectionTitle
                    icon={<CheckCircleOutlineRoundedIcon />}
                    title="Validation"
                    subtitle="Safety and sequence checks."
                  />

                  <Stack spacing={2}>
                    <Chip
                      label={
                        result.validation?.valid
                          ? "Validation passed"
                          : "Validation failed"
                      }
                      color={
                        result.validation?.valid ? "success" : "error"
                      }
                      sx={{ alignSelf: "flex-start", fontWeight: 700 }}
                    />

                    {validationErrors.length > 0 ? (
                      <Stack spacing={1}>
                        {validationErrors.map((item, index) => (
                          <Alert key={index} severity="error">
                            {item}
                          </Alert>
                        ))}
                      </Stack>
                    ) : (
                      <Typography color="text.secondary">
                        All command checks passed successfully.
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 3 }}>
                  <SectionTitle
                    icon={<TerminalRoundedIcon />}
                    title="Mock execution logs"
                    subtitle="Software simulation of the drone execution."
                  />

                  {executionLogs.length > 0 ? (
                    <CodeBlock>{executionLogs.join("\n")}</CodeBlock>
                  ) : (
                    <Typography color="text.secondary">
                      No execution logs available.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {finalState && (
            <Card>
              <CardContent sx={{ p: 3 }}>
                <SectionTitle
                  icon={<SensorsRoundedIcon />}
                  title="Final simulated state"
                  subtitle="MockTello state after command execution."
                />

                <Divider sx={{ mb: 2.5 }} />

                <Grid container spacing={2}>
                  {Object.entries(finalState).map(([key, value]) => (
                    <Grid size={{ xs: 6, sm: 4, md: 3 }} key={key}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ textTransform: "uppercase" }}
                        >
                          {key.replaceAll("_", " ")}
                        </Typography>

                        <Typography variant="h6" mt={0.5}>
                          {String(value)}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </Stack>
  );
}