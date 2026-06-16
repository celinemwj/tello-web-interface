import {
  createContext,
  useContext,
  useMemo,
  useState,
} from "react";


const PipelineContext = createContext(null);


export function PipelineProvider({ children }) {
  const [latestResult, setLatestResult] = useState(null);

  const value = useMemo(
    () => ({
      latestResult,
      setLatestResult,
    }),
    [latestResult]
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
    throw new Error(
      "usePipeline must be used inside PipelineProvider."
    );
  }

  return context;
}