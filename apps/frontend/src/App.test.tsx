import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("shows the landing screen first, then the dashboard after entering", () => {
    render(<App />);

    const enterButton = screen.getByRole("button", { name: /Panele Git/i });
    expect(enterButton).toBeInTheDocument();

    fireEvent.click(enterButton);

    expect(screen.getByText("CarbonPilot AI")).toBeInTheDocument();
    expect(screen.getAllByText("No calculation yet")).toHaveLength(2);
    expect(screen.getByText("Agent audit trail")).toBeInTheDocument();
    expect(screen.getByLabelText("Document to extract")).toBeInTheDocument();
    expect(screen.getByLabelText("Solar transition")).toBeInTheDocument();
  });
});