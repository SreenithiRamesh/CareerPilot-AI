import {
  describe,
  expect,
  it,
} from "vitest";

import {
  cleanAgentGuidance,
} from "./agentGuidance";


describe(
  "cleanAgentGuidance",
  () => {
    it(
      "removes a duplicate guidance heading",
      () => {
        const content = (
          "**CareerPilot Guidance**\n\n"
          + "Start with Core Java."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "Start with Core Java."
        );
      }
    );


    it(
      "removes an escaped duplicate guidance heading",
      () => {
        const content = (
          "\\*\\*CareerPilot Guidance"
          + "\\*\\*\n\n"
          + "Build a Spring Boot API."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "Build a Spring Boot API."
        );
      }
    );


    it(
      "normalizes escaped markdown headings",
      () => {
        const content = (
          "\\#### Why This Matters\n\n"
          + "Practical explanation."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "#### Why This Matters\n\n"
          + "Practical explanation."
        );
      }
    );


    it(
      "normalizes escaped emphasis",
      () => {
        const content = (
          "\\*Action:\\* Build one "
          + "REST endpoint."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "*Action:* Build one "
          + "REST endpoint."
        );
      }
    );


    it(
      "normalizes repeated markdown escapes",
      () => {
        const content = (
          "\\\\*Action:\\\\* Build a "
          + "Spring Boot endpoint."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "*Action:* Build a "
          + "Spring Boot endpoint."
        );
      }
    );


    it(
      "normalizes escaped project emphasis",
      () => {
        const content = (
          "Rebuild your "
          + "\\\\*Employee Hub\\\\* "
          + "backend using Java."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "Rebuild your "
          + "*Employee Hub* "
          + "backend using Java."
        );
      }
    );


    it(
      "normalizes duplicated bold markers",
      () => {
        const content = (
          "**\\*\\*Block 1**: Core "
          + "Java practice (2 Hours)\\*\\*"
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "**Block 1: Core Java "
          + "practice (2 Hours)**"
        );
      }
    );


    it(
      "preserves valid markdown",
      () => {
        const content = (
          "#### Day 1\n\n"
          + "**Focus:** Core Java\n\n"
          + "- Collections\n"
          + "- Streams\n\n"
          + "`HashMap<String, User>`"
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          content
        );
      }
    );


    it(
      "normalizes Windows line endings",
      () => {
        const content = (
          "#### Day 1\r\n\r\n"
          + "\\*Action:\\* Practice Java."
        );

        expect(
          cleanAgentGuidance(
            content
          )
        ).toBe(
          "#### Day 1\n\n"
          + "*Action:* Practice Java."
        );
      }
    );


    it(
      "returns non-string values unchanged",
      () => {
        expect(
          cleanAgentGuidance(null)
        ).toBeNull();

        expect(
          cleanAgentGuidance(undefined)
        ).toBeUndefined();
      }
    );
  }
);