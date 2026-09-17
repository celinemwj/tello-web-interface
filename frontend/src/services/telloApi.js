const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function executeCommand(command, executionMode = "mock") {
  const cleanedCommand = command.trim();

  if (!cleanedCommand) {
    throw new Error("Please enter a drone command.");
  }

  const response = await fetch(`${API_BASE_URL}/api/pipeline`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      command: cleanedCommand,
      execution_mode: executionMode,
    }),
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}.`);
  }

  return response.json();
}