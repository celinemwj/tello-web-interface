import { Box } from "@mui/material";

export default function PageBackground() {
  return (
    <>
      <Box
        sx={{
          position: "fixed",
          width: {
            xs: 520,
            md: 900,
          },
          height: {
            xs: 520,
            md: 900,
          },
          borderRadius: "50%",
          right: {
            xs: -300,
            md: -280,
          },
          top: {
            xs: -220,
            md: -300,
          },
          background:
            "radial-gradient(circle, rgba(111,120,157,0.28) 0%, rgba(158,184,179,0.18) 42%, rgba(244,245,248,0) 72%)",
          filter: "blur(6px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      <Box
        sx={{
          position: "fixed",
          width: {
            xs: 480,
            md: 760,
          },
          height: {
            xs: 480,
            md: 760,
          },
          borderRadius: "50%",
          left: {
            xs: -260,
            md: -280,
          },
          bottom: {
            xs: -260,
            md: -300,
          },
          background:
            "radial-gradient(circle, rgba(158,184,179,0.32) 0%, rgba(111,120,157,0.14) 44%, rgba(244,245,248,0) 72%)",
          filter: "blur(8px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      <Box
        sx={{
          position: "fixed",
          width: 520,
          height: 520,
          borderRadius: "50%",
          left: "48%",
          top: "48%",
          transform: "translate(-50%, -50%)",
          background:
            "radial-gradient(circle, rgba(193,222,219,0.22) 0%, rgba(244,245,248,0) 70%)",
          filter: "blur(12px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />
    </>
  );
}