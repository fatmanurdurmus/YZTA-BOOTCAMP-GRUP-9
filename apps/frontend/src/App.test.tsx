import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders the CarbonPilot dashboard", () => {
    render(<App />);

    expect(screen.getByText("CarbonPilot AI")).toBeInTheDocument();
    expect(screen.getAllByText("No calculation yet")).toHaveLength(2);
    expect(screen.getByText("Agent audit trail")).toBeInTheDocument();
    expect(screen.getByLabelText("Document to extract")).toBeInTheDocument();
    expect(screen.getByLabelText("Solar transition")).toBeInTheDocument();
  });
});
