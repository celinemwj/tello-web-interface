import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import SendRoundedIcon from "@mui/icons-material/SendRounded";
import PersonOutlineRoundedIcon from "@mui/icons-material/PersonOutlineRounded";
import CodeRoundedIcon from "@mui/icons-material/CodeRounded";
import CheckCircleOutlineRoundedIcon from "@mui/icons-material/CheckCircleOutlineRounded";
import TerminalRoundedIcon from "@mui/icons-material/TerminalRounded";
import PsychologyRoundedIcon from "@mui/icons-material/PsychologyRounded";
import RouteRoundedIcon from "@mui/icons-material/RouteRounded";

import { executeCommand } from "../services/telloApi";
import { usePipeline } from "../context/PipelineContext";


function ChatMessage({ role, children }) {
  const isUser = role === "user";

  return (
    <Stack
      direction="row"
      spacing={1.2}
      sx={{
        justifyContent: isUser ? "flex-end" : "flex-start",
        alignItems: "flex-start",
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: {
            xs: "86%",
            md: "78%",
          },
          px: 2,
          py: 1.4,
          borderRadius: isUser
            ? "22px 22px 6px 22px"
            : "22px 22px 22px 6px",
          bgcolor: isUser
            ? "primary.main"
            : "rgba(255,255,255,0.76)",
          color: isUser
            ? "primary.contrastText"
            : "text.primary",
          border: isUser ? "none" : "1px solid",
          borderColor: "divider",
          backdropFilter: "blur(14px)",
          boxShadow: isUser
            ? "0 12px 28px rgba(89,103,138,0.22)"
            : "0 12px 30px rgba(31,34,48,0.06)",
        }}
      >
        {children}
      </Paper>

      {isUser && (
        <Box
          sx={{
            width: 38,
            height: 38,
            borderRadius: "50%",
            display: "grid",
            placeItems: "center",
            bgcolor: "secondary.light",
            color: "primary.dark",
            flexShrink: 0,
          }}
        >
          <PersonOutlineRoundedIcon fontSize="small" />
        </Box>
      )}
    </Stack>
  );
}


function ResultSection({ icon, title, subtitle, children }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2.4,
        borderRadius: 4,
        bgcolor: "rgba(255,255,255,0.72)",
        backdropFilter: "blur(16px)",
        borderColor: "rgba(217,220,229,0.8)",
        boxShadow: "0 18px 50px rgba(31,34,48,0.07)",
      }}
    >
      <Stack
        direction="row"
        spacing={1.3}
        sx={{
          alignItems: "center",
          mb: 2,
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2.3,
            display: "grid",
            placeItems: "center",
            bgcolor: "secondary.light",
            color: "primary.dark",
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>

        <Box>
          <Typography fontWeight={850}>
            {title}
          </Typography>

          {subtitle && (
            <Typography
              variant="caption"
              color="text.secondary"
            >
              {subtitle}
            </Typography>
          )}
        </Box>
      </Stack>

      {children}
    </Paper>
  );
}


export default function CommandPanel() {
  const navigate = useNavigate();

  const {
    messages,
    latestResult,
    addMessage,
    setLatestResult,
    clearSession,
  } = usePipeline();

  const [command, setCommand] = useState("");
  const [result, setResult] = useState(latestResult);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    const cleanedCommand = command.trim();

    if (!cleanedCommand || isLoading) {
      return;
    }

    setError("");
    setResult(null);

    addMessage({
      role: "user",
      content: cleanedCommand,
    });

    setCommand("");
    setIsLoading(true);

    try {
      const apiResult = await executeCommand(cleanedCommand);

      setResult(apiResult);
      setLatestResult(apiResult);

      const assistantMessage =
        apiResult.llm_output?.explanation ||
        apiResult.error ||
        "The command was processed.";

      addMessage({
        role: "assistant",
        content: assistantMessage,
      });
    } catch (requestError) {
      setError(requestError.message);

      addMessage({
        role: "assistant",
        content: "The backend could not process the command.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (!isLoading && command.trim()) {
        handleSubmit(event);
      }
    }
  }

  function handleClearSession() {
    clearSession();
    setResult(null);
    setError("");
    setCommand("");
  }

  const interpretedCommands =
    result?.llm_output?.commands ?? [];

  const validationErrors =
    result?.validation?.errors ?? [];

  const executionLogs =
    result?.execution?.logs ?? [];

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: {
          xs: "1fr",
          md: "minmax(0, 1.35fr) minmax(340px, 0.75fr)",
          lg: "minmax(0, 1.35fr) minmax(390px, 0.75fr)",
          xl: "minmax(0, 1.35fr) minmax(430px, 0.75fr)",
        },
        gap: {
          xs: 2.5,
          md: 3,
        },
        alignItems: "start",
      }}
    >
      <Paper
        variant="outlined"
        sx={{
          minHeight: {
            xs: 600,
            md: "calc(100vh - 270px)",
          },
          maxHeight: {
            md: "calc(100vh - 220px)",
          },
          display: "flex",
          flexDirection: "column",
          borderRadius: 6,
          overflow: "hidden",
          bgcolor: "rgba(255,255,255,0.64)",
          backdropFilter: "blur(18px)",
          borderColor: "rgba(217,220,229,0.8)",
          boxShadow: "0 28px 80px rgba(31,34,48,0.11)",
        }}
      >
        <Box
          sx={{
            px: {
              xs: 2.2,
              md: 3,
            },
            py: {
              xs: 2,
              md: 2.5,
            },
          }}
        >
          <Stack
            direction="row"
            spacing={1.5}
            sx={{
              alignItems: "center",
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 3,
                display: "grid",
                placeItems: "center",
                bgcolor: "primary.main",
                color: "primary.contrastText",
                boxShadow: "0 16px 34px rgba(89,103,138,0.24)",
              }}
            >
              <PsychologyRoundedIcon />
            </Box>

            <Box sx={{ flexGrow: 1 }}>
              <Typography
                variant="h5"
                fontWeight={900}
              >
                Mission assistant
              </Typography>
            </Box>

            <Button
              variant="text"
              onClick={handleClearSession}
              sx={{
                borderRadius: 3,
                fontWeight: 800,
                color: "text.secondary",
                whiteSpace: "nowrap",
              }}
            >
              Clear
            </Button>

            <Button
              variant="outlined"
              onClick={() => navigate("/monitoring")}
              sx={{
                borderRadius: 3,
                fontWeight: 800,
                bgcolor: "rgba(255,255,255,0.65)",
                whiteSpace: "nowrap",
              }}
            >
              View monitoring
            </Button>
          </Stack>
        </Box>

        <Divider />

        <Stack
          spacing={2}
          sx={{
            flexGrow: 1,
            overflowY: "auto",
            px: {
              xs: 2,
              md: 3,
            },
            py: 3,
            minHeight: 0,
          }}
        >
          {messages.length === 0 && (
            <ChatMessage role="assistant">
              <Typography>
                Enter a drone command. I will interpret the instruction,
                validate the sequence, generate the DJITelloPy code, and
                simulate the execution.
              </Typography>
            </ChatMessage>
          )}

          {messages.map((message, index) => (
            <ChatMessage
              key={`${message.role}-${index}`}
              role={message.role}
            >
              <Typography
                sx={{
                  whiteSpace: "pre-wrap",
                }}
              >
                {message.content}
              </Typography>
            </ChatMessage>
          ))}

          {isLoading && (
            <ChatMessage role="assistant">
              <Stack
                direction="row"
                spacing={1.2}
                sx={{
                  alignItems: "center",
                }}
              >
                <CircularProgress size={18} />

                <Typography>
                  Translating and validating the mission…
                </Typography>
              </Stack>
            </ChatMessage>
          )}
        </Stack>

        {error && (
          <Alert
            severity="error"
            sx={{
              mx: 2,
              mb: 1,
            }}
          >
            {error}
          </Alert>
        )}

        <Divider />

        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{
            p: {
              xs: 1.8,
              md: 2,
            },
            bgcolor: "rgba(255,255,255,0.46)",
          }}
        >
          <Stack
            direction="row"
            spacing={1.4}
            sx={{
              alignItems: "flex-end",
            }}
          >
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={command}
              onChange={(event) =>
                setCommand(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Write a command for the drone..."
              disabled={isLoading}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  bgcolor: "rgba(255,255,255,0.82)",
                },
              }}
            />

            <Button
              type="submit"
              variant="contained"
              disabled={isLoading || !command.trim()}
              sx={{
                minWidth: 56,
                width: 56,
                height: 56,
                px: 0,
                borderRadius: 3,
                boxShadow: "0 16px 34px rgba(89,103,138,0.22)",
              }}
            >
              <SendRoundedIcon />
            </Button>
          </Stack>
        </Box>
      </Paper>

      <Stack
        spacing={2.3}
        sx={{
          minWidth: 0,
        }}
      >
        <Stack
          direction="row"
          spacing={1.2}
          sx={{
            alignItems: "center",
          }}
        >
          <RouteRoundedIcon color="primary" />

          <Box>
            <Typography
              variant="h5"
              fontWeight={900}
            >
              Translation process
            </Typography>
          </Box>
        </Stack>

        {!result && (
          <Paper
            variant="outlined"
            sx={{
              minHeight: {
                xs: 260,
                md: 360,
              },
              display: "grid",
              placeItems: "center",
              textAlign: "center",
              borderRadius: 6,
              p: 4,
              bgcolor: "rgba(255,255,255,0.58)",
              backdropFilter: "blur(18px)",
              borderColor: "rgba(217,220,229,0.8)",
              boxShadow: "0 26px 70px rgba(31,34,48,0.08)",
            }}
          >
            <Box>
              <CodeRoundedIcon
                sx={{
                  fontSize: 58,
                  color: "primary.main",
                  mb: 1.5,
                }}
              />

              <Typography
                variant="h6"
                fontWeight={850}
              >
                No translation yet
              </Typography>
            </Box>
          </Paper>
        )}

        {result && (
          <>
            <ResultSection
              icon={<PsychologyRoundedIcon />}
              title="Interpreted actions"
              subtitle="Structured command sequence returned by the LLM"
            >
              {interpretedCommands.length > 0 ? (
                <Stack spacing={1}>
                  {interpretedCommands.map((item, index) => (
                    <Paper
                      key={`${item.action}-${index}`}
                      variant="outlined"
                      sx={{
                        px: 1.5,
                        py: 1.1,
                        borderRadius: 2.5,
                        bgcolor: "rgba(255,255,255,0.74)",
                      }}
                    >
                      <Stack
                        direction="row"
                        spacing={1}
                        sx={{
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Typography fontWeight={800}>
                          {index + 1}. {item.action}
                        </Typography>

                        {item.value !== undefined && (
                          <Chip
                            size="small"
                            label={`${item.value} ${item.unit ?? ""}`}
                          />
                        )}
                      </Stack>
                    </Paper>
                  ))}
                </Stack>
              ) : (
                <Typography color="text.secondary">
                  No action was returned.
                </Typography>
              )}
            </ResultSection>

            <ResultSection
              icon={<CheckCircleOutlineRoundedIcon />}
              title="Validation"
              subtitle="Safety, range and sequence verification"
            >
              <Chip
                label={
                  result.validation?.valid
                    ? "Validation passed"
                    : "Validation failed"
                }
                color={
                  result.validation?.valid
                    ? "success"
                    : "error"
                }
                sx={{
                  fontWeight: 750,
                  mb:
                    validationErrors.length > 0
                      ? 1.5
                      : 0,
                }}
              />

              {validationErrors.length > 0 && (
                <Stack spacing={1}>
                  {validationErrors.map((item, index) => (
                    <Alert
                      key={index}
                      severity="error"
                    >
                      {item}
                    </Alert>
                  ))}
                </Stack>
              )}
            </ResultSection>

            <ResultSection
              icon={<CodeRoundedIcon />}
              title="Generated Python code"
              subtitle="DJITelloPy code created from validated actions"
            >
              {result.generated_code ? (
                <Box
                  component="pre"
                  sx={{
                    m: 0,
                    p: 2,
                    overflowX: "auto",
                    borderRadius: 3,
                    bgcolor: "#1F2230",
                    color: "#F4F5F8",
                    fontSize: "0.84rem",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  <code>{result.generated_code}</code>
                </Box>
              ) : (
                <Typography color="text.secondary">
                  No code was generated.
                </Typography>
              )}
            </ResultSection>

            <ResultSection
              icon={<TerminalRoundedIcon />}
              title="Real execution"
              subtitle="Drone execution logs"
            >
              {executionLogs.length > 0 ? (
                <Stack spacing={0.8}>
                  {executionLogs.map((log, index) => (
                    <Typography
                      key={`${log}-${index}`}
                      variant="body2"
                      sx={{
                        fontFamily: "monospace",
                      }}
                    >
                      {log}
                    </Typography>
                  ))}
                </Stack>
              ) : (
                <Typography color="text.secondary">
                  No execution log available.
                </Typography>
              )}
            </ResultSection>
          </>
        )}
      </Stack>
    </Box>
  );
}