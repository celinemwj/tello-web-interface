import { useState } from "react";

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

import DashboardLayout from "../components/layout/DashboardLayout";
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
      {!isUser && (
        <Box
          component="img"
          src="/assets/tello-ai-logo.png"
          alt="Tello AI"
          sx={{
            width: 38,
            height: 38,
            objectFit: "contain",
            flexShrink: 0,
          }}
        />
      )}

      <Paper
        elevation={0}
        sx={{
          maxWidth: {
            xs: "82%",
            md: "75%",
          },
          px: 2,
          py: 1.4,
          borderRadius: 3,
          bgcolor: isUser
            ? "primary.main"
            : "background.paper",
          color: isUser
            ? "primary.contrastText"
            : "text.primary",
          border: isUser ? "none" : "1px solid",
          borderColor: "divider",
          boxShadow: isUser
            ? "0 8px 20px rgba(89,103,138,0.18)"
            : "none",
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
            bgcolor: "secondary.main",
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


function ResultSection({
  icon,
  title,
  subtitle,
  children,
}) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2.5,
        borderRadius: 3,
        bgcolor: "rgba(255,255,255,0.82)",
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
            width: 38,
            height: 38,
            borderRadius: 2,
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


export default function CommandPage() {
  const { setLatestResult } = usePipeline();

  const [command, setCommand] = useState("");
  const [messages, setMessages] = useState([]);
  const [result, setResult] = useState(null);
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

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: cleanedCommand,
      },
    ]);

    setCommand("");
    setIsLoading(true);

    try {
      const apiResult = await executeCommand(cleanedCommand);

      setResult(apiResult);
      setLatestResult(apiResult);

      const assistantMessage =
        apiResult.llm_output?.explanation ||
        (apiResult.success
          ? "The command was interpreted and processed successfully."
          : "The command could not be executed.");

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: assistantMessage,
        },
      ]);
    } catch (requestError) {
      setError(requestError.message);

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content:
            "The backend could not process the command.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  const interpretedCommands =
    result?.llm_output?.commands ?? [];

  const validationErrors =
    result?.validation?.errors ?? [];

  const executionLogs =
    result?.execution?.logs ?? [];

  const headerStatus = (
    <Chip
      label="Mock mode"
      color="secondary"
      variant="outlined"
      sx={{
        fontWeight: 700,
      }}
    />
  );

  return (
    <DashboardLayout
      title="AI command"
      subtitle="Natural-language translation and safe drone execution"
      headerAction={headerStatus}
    >
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            xl: "minmax(0, 1.2fr) minmax(380px, 0.8fr)",
          },
          gap: 3,
        }}
      >
        {/* Chat workspace */}
        <Paper
          variant="outlined"
          sx={{
            minHeight: {
              xs: 640,
              xl: "calc(100vh - 150px)",
            },
            display: "flex",
            flexDirection: "column",
            borderRadius: 4,
            overflow: "hidden",
            bgcolor: "rgba(255,255,255,0.78)",
          }}
        >
          <Box
            sx={{
              px: 3,
              py: 2.5,
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
                  width: 44,
                  height: 44,
                  borderRadius: 2.5,
                  display: "grid",
                  placeItems: "center",
                  bgcolor: "primary.main",
                  color: "primary.contrastText",
                }}
              >
                <PsychologyRoundedIcon />
              </Box>

              <Box>
                <Typography
                  variant="h5"
                  fontWeight={900}
                >
                  Mission assistant
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Describe the mission using natural language.
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Divider />

          {/* Conversation */}
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
                  Enter a drone command. I will interpret the
                  instruction, validate the sequence, generate the
                  DJITelloPy code, and simulate the execution.
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
                    Interpreting the command…
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

          {/* Command input */}
          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
              p: 2,
              bgcolor: "background.paper",
            }}
          >
            <Stack
              direction="row"
              spacing={1.5}
              sx={{
                alignItems: "flex-end",
              }}
            >
              <TextField
                fullWidth
                multiline
                maxRows={5}
                value={command}
                onChange={(event) =>
                  setCommand(event.target.value)
                }
                placeholder="Write a command for the drone…"
                disabled={isLoading}
              />

              <Button
                type="submit"
                variant="contained"
                disabled={isLoading || !command.trim()}
                sx={{
                  minWidth: 54,
                  width: 54,
                  height: 54,
                  px: 0,
                  borderRadius: 2.5,
                }}
              >
                <SendRoundedIcon />
              </Button>
            </Stack>
          </Box>
        </Paper>

        {/* Translation workspace */}
        <Stack spacing={2.5}>
          <Box>
            <Typography
              variant="h5"
              fontWeight={900}
            >
              Translation process
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              mt={0.5}
            >
              Natural language → structured actions →
              validation → generated code.
            </Typography>
          </Box>

          {!result && (
            <Paper
              variant="outlined"
              sx={{
                minHeight: 300,
                display: "grid",
                placeItems: "center",
                textAlign: "center",
                borderRadius: 4,
                p: 4,
                bgcolor: "rgba(255,255,255,0.62)",
              }}
            >
              <Box>
                <CodeRoundedIcon
                  sx={{
                    fontSize: 56,
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

                <Typography
                  variant="body2"
                  color="text.secondary"
                  mt={0.8}
                >
                  Send a command to display its structured actions,
                  validation result and Python code.
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
                    {interpretedCommands.map(
                      (item, index) => (
                        <Paper
                          key={`${item.action}-${index}`}
                          variant="outlined"
                          sx={{
                            px: 1.6,
                            py: 1.2,
                            borderRadius: 2,
                          }}
                        >
                          <Stack
                            direction="row"
                            spacing={2}
                            sx={{
                              justifyContent:
                                "space-between",
                              alignItems: "center",
                            }}
                          >
                            <Typography fontWeight={750}>
                              {index + 1}. {item.action}
                            </Typography>

                            {item.value !== undefined && (
                              <Chip
                                size="small"
                                label={`${item.value} ${
                                  item.unit ?? ""
                                }`}
                              />
                            )}
                          </Stack>
                        </Paper>
                      )
                    )}
                  </Stack>
                ) : (
                  <Typography color="text.secondary">
                    No action was returned.
                  </Typography>
                )}
              </ResultSection>

              <ResultSection
                icon={
                  <CheckCircleOutlineRoundedIcon />
                }
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
                    {validationErrors.map(
                      (item, index) => (
                        <Alert
                          key={index}
                          severity="error"
                        >
                          {item}
                        </Alert>
                      )
                    )}
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
                      borderRadius: 2.5,
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
                title="Mock execution"
                subtitle="Simulated execution logs"
              >
                {executionLogs.length > 0 ? (
                  <Stack spacing={0.8}>
                    {executionLogs.map(
                      (log, index) => (
                        <Typography
                          key={`${log}-${index}`}
                          variant="body2"
                          sx={{
                            fontFamily: "monospace",
                          }}
                        >
                          {log}
                        </Typography>
                      )
                    )}
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
    </DashboardLayout>
  );
}