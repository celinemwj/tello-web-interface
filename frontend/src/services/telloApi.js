const API_BASE_URL = "http://127.0.0.1:8000";

export async function executeCommand(command) {
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
      execution_mode: "mock",
    }),
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}.`);
  }

  return response.json();
}