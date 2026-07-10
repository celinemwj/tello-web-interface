import { createContext, useContext, useMemo, useState } from "react";

const PipelineContext = createContext(null);

const STORAGE_KEY = "tello_pipeline_session";

function loadStoredSession() {
  try {
    const storedSession = localStorage.getItem(STORAGE_KEY);

    if (!storedSession) {
      return {
        messages: [],
        latestResult: null,
      };
    }

    const parsedSession = JSON.parse(storedSession);

    return {
      messages: parsedSession.messages ?? [],
      latestResult: parsedSession.latestResult ?? null,
    };
  } catch {
    return {
      messages: [],
      latestResult: null,
    };
  }
}

function saveSession(session) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch {
    // Ignore localStorage errors
  }
}

export function PipelineProvider({ children }) {
  const initialSession = loadStoredSession();

  const [messages, setMessagesState] = useState(initialSession.messages);
  const [latestResult, setLatestResultState] = useState(
    initialSession.latestResult
  );

  function addMessage(message) {
    setMessagesState((currentMessages) => {
      const nextMessages = [...currentMessages, message];

      saveSession({
        messages: nextMessages,
        latestResult,
      });

      return nextMessages;
    });
  }

  function setLatestResult(result) {
    setLatestResultState(result);

    saveSession({
      messages,
      latestResult: result,
    });
  }

  function clearSession() {
    setMessagesState([]);
    setLatestResultState(null);

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore localStorage errors
    }
  }

  const value = useMemo(
    () => ({
      messages,
      latestResult,
      addMessage,
      setLatestResult,
      clearSession,
    }),
    [messages, latestResult]
  );

  return (
    <PipelineContext.Provider value={value}>
      {children}
    </PipelineContext.Provider>
  );
}

export function usePipeline() {
  const context = useContext(PipelineContext);

  if (!context) {
    throw new Error("usePipeline must be used inside PipelineProvider.");
  }

  return context;
}