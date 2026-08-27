import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import api from "../services/api";
import CareerAI from "./CareerAI";


vi.mock(
  "../services/api",
  () => ({
    default: {
      delete: vi.fn(),
      get: vi.fn(),
      patch: vi.fn(),
      post: vi.fn(),
    },
  })
);


function conversationDetail(
  threadId,
  messages
) {
  return {
    thread_id: threadId,
    title: "Java backend priorities",
    resume_id: 248,
    created_at:
      "2026-08-27T10:00:00",
    updated_at:
      "2026-08-27T10:05:00",
    messages,
  };
}


async function openAgentMode() {
  render(
    <CareerAI />
  );

  const chatComposer =
    await screen.findByPlaceholderText(
      /Ask about your target role/i
    );

  await waitFor(() => {
    expect(
      chatComposer
    ).toBeEnabled();
  });

  await userEvent.setup().click(
    screen.getByRole(
      "button",
      {
        name: "Agent",
      }
    )
  );

  return screen.getByPlaceholderText(
    /Give CareerPilot a goal/i
  );
}


describe(
  "CareerAI Agent conversation memory",
  () => {
    beforeEach(() => {
      vi.resetAllMocks();
      localStorage.clear();

      localStorage.setItem(
        "careerpilot_active_resume",
        JSON.stringify({
          resume_id: 248,
        })
      );

      vi.spyOn(
        console,
        "error"
      ).mockImplementation(
        () => {}
      );

      vi.spyOn(
        console,
        "log"
      ).mockImplementation(
        () => {}
      );
    });


    it(
      "keeps earlier Agent turns visible after a follow-up",
      async () => {
        const user =
          userEvent.setup();

        const persistedMessages = [];
        let activeThreadId = null;
        let nextMessageId = 1;

        api.get.mockImplementation(
          async (url) => {
            if (
              url ===
              "/api/conversations"
            ) {
              return {
                data: {
                  conversations:
                    activeThreadId
                      ? [
                          {
                            thread_id:
                              activeThreadId,
                            title:
                              "Java backend priorities",
                            resume_id: 248,
                            created_at:
                              "2026-08-27T10:00:00",
                            updated_at:
                              "2026-08-27T10:05:00",
                          },
                        ]
                      : [],
                },
              };
            }

            return {
              data: conversationDetail(
                activeThreadId,
                persistedMessages
              ),
            };
          }
        );

        api.post.mockImplementation(
          async (
            url,
            payload
          ) => {
            expect(url).toBe(
              "/api/agent/run"
            );

            activeThreadId =
              payload.thread_id;

            const answer =
              payload.goal.startsWith(
                "Give me"
              )
                ? "First, strengthen Spring Boot REST API fundamentals."
                : "The first priority means building controllers, services, and repositories.";

            persistedMessages.push(
              {
                id: nextMessageId++,
                mode: "agent",
                role: "user",
                content: payload.goal,
                created_at:
                  "2026-08-27T10:01:00",
              },
              {
                id: nextMessageId++,
                mode: "agent",
                role: "assistant",
                content: answer,
                created_at:
                  "2026-08-27T10:02:00",
              }
            );

            return {
              data: {
                agent_run_id:
                  nextMessageId,
                resume_id: 248,
                thread_id:
                  payload.thread_id,
                goal: payload.goal,
                plan: [],
                completed_steps: [],
                executed_steps: [],
                iterations: 1,
                run_outcome:
                  "completed",
                task_complete: true,
                final_response:
                  answer,
              },
            };
          }
        );

        const composer =
          await openAgentMode();

        const firstGoal =
          "Give me three Java backend priorities.";

        await user.type(
          composer,
          firstGoal
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Run Agent",
            }
          )
        );

        expect(
          await screen.findByText(
            "First, strengthen Spring Boot REST API fundamentals."
          )
        ).toBeInTheDocument();

        const secondGoal =
          "Explain the first priority in detail.";

        await user.type(
          composer,
          secondGoal
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Run Agent",
            }
          )
        );

        expect(
          await screen.findByText(
            "The first priority means building controllers, services, and repositories."
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            firstGoal
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            secondGoal
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "First, strengthen Spring Boot REST API fundamentals."
          )
        ).toBeInTheDocument();

        expect(
          api.post.mock.calls[0][1]
            .thread_id
        ).toBe(
          api.post.mock.calls[1][1]
            .thread_id
        );

        expect(
          api.post.mock.calls[0][1]
            .request_id
        ).not.toBe(
          api.post.mock.calls[1][1]
            .request_id
        );
      }
    );


    it(
      "restores persisted Agent turns after initialization",
      async () => {
        const threadId =
          "careerpilot-agent-history";

        const persistedMessages = [
          {
            id: 1,
            mode: "agent",
            role: "user",
            content:
              "Give me three Java backend priorities.",
            created_at:
              "2026-08-27T10:01:00",
          },
          {
            id: 2,
            mode: "agent",
            role: "assistant",
            content:
              "Spring Boot REST APIs should be your first priority.",
            created_at:
              "2026-08-27T10:02:00",
          },
          {
            id: 3,
            mode: "agent",
            role: "user",
            content:
              "Explain the first priority in detail.",
            created_at:
              "2026-08-27T10:03:00",
          },
          {
            id: 4,
            mode: "agent",
            role: "assistant",
            content:
              "Build one CRUD API with validation and tests.",
            created_at:
              "2026-08-27T10:04:00",
          },
        ];

        api.get.mockImplementation(
          async (url) => {
            if (
              url ===
              "/api/conversations"
            ) {
              return {
                data: {
                  conversations: [
                    {
                      thread_id:
                        threadId,
                      title:
                        "Java backend priorities",
                      resume_id: 248,
                      created_at:
                        "2026-08-27T10:00:00",
                      updated_at:
                        "2026-08-27T10:05:00",
                    },
                  ],
                },
              };
            }

            return {
              data: conversationDetail(
                threadId,
                persistedMessages
              ),
            };
          }
        );

        await openAgentMode();

        expect(
          screen.getByText(
            "Give me three Java backend priorities."
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Spring Boot REST APIs should be your first priority."
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Explain the first priority in detail."
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Build one CRUD API with validation and tests."
          )
        ).toBeInTheDocument();
      }
    );
  }
);
