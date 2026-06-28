import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders the CarbonPilot dashboard", () => {
    render(<App />);

    expect(screen.getByText("CarbonPilot AI")).toBeInTheDocument();
    expect(screen.getByText("45.25 tCO2e")).toBeInTheDocument();
    expect(screen.getByText("Agent audit trail")).toBeInTheDocument();
  });
});
