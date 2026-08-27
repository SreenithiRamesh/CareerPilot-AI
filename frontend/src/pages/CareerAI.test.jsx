import {
  act,
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


function createDeferredPromise() {
  let resolve;
  let reject;

  const promise =
    new Promise(
      (
        promiseResolve,
        promiseReject
      ) => {
        resolve =
          promiseResolve;

        reject =
          promiseReject;
      }
    );

  return {
    promise,
    reject,
    resolve,
  };
}


async function renderCareerAI() {
  render(
    <CareerAI />
  );

  const composer =
    await screen.findByPlaceholderText(
      /Ask about your target role/i
    );

  await waitFor(() => {
    expect(composer).toBeEnabled();
  });

  return composer;
}


describe(
  "CareerAI chat states",
  () => {
    beforeEach(() => {
      vi.resetAllMocks();

      api.get.mockResolvedValue({
        data: {
          conversations: [],
        },
      });

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
      "disables submission while a request is pending",
      async () => {
        const user =
          userEvent.setup();

        const pendingRequest =
          createDeferredPromise();

        api.post.mockReturnValue(
          pendingRequest.promise
        );

        const composer =
          await renderCareerAI();

        await user.type(
          composer,
          "Help me prepare for Java interviews."
        );

        const sendButton =
          screen.getByRole(
            "button",
            {
              name: "Send",
            }
          );

        await user.click(
          sendButton
        );

        await waitFor(() => {
          expect(
            api.post
          ).toHaveBeenCalledTimes(1);
        });

        expect(
          sendButton
        ).toBeDisabled();

        await user.click(
          sendButton
        );

        expect(
          api.post
        ).toHaveBeenCalledTimes(1);

        await act(
          async () => {
            pendingRequest.resolve({
              data: {
                response:
                  "Start with Java fundamentals.",
              },
            });

            await pendingRequest.promise;
          }
        );

        expect(
          await screen.findByText(
            "Start with Java fundamentals."
          )
        ).toBeInTheDocument();

        await waitFor(() => {
          expect(
            sendButton
          ).toBeDisabled();
        });
      }
    );


    it(
      "retries a 503 failure with the same request ID",
      async () => {
        const user =
          userEvent.setup();

        api.post
          .mockRejectedValueOnce({
            response: {
              status: 503,
              data: {
                detail:
                  "Career AI is temporarily unavailable.",
              },
            },
          })
          .mockResolvedValueOnce({
            data: {
              response:
                "Your retry succeeded.",
            },
          });

        const composer =
          await renderCareerAI();

        const question =
          "Suggest one backend portfolio project.";

        await user.type(
          composer,
          question
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Send",
            }
          )
        );

        expect(
          await screen.findByText(
            "Career AI is temporarily unavailable."
          )
        ).toBeInTheDocument();

        expect(
          composer
        ).toHaveValue(
          question
        );

        const firstRequestId =
          api.post.mock.calls[
            0
          ][1].request_id;

        const retryButton =
          screen.getByRole(
            "button",
            {
              name:
                "Retry message",
            }
          );

        await user.click(
          retryButton
        );

        await waitFor(() => {
          expect(
            api.post
          ).toHaveBeenCalledTimes(2);
        });

        const retryRequestId =
          api.post.mock.calls[
            1
          ][1].request_id;

        expect(
          retryRequestId
        ).toBe(
          firstRequestId
        );

        expect(
          await screen.findByText(
            "Your retry succeeded."
          )
        ).toBeInTheDocument();

        expect(
          screen.queryByRole(
            "button",
            {
              name:
                "Retry message",
            }
          )
        ).not.toBeInTheDocument();

        expect(
          screen.getAllByText(
            question
          )
        ).toHaveLength(1);
      }
    );


    it(
      "does not offer retry for a non-retryable API error",
      async () => {
        const user =
          userEvent.setup();

        api.post.mockRejectedValue({
          response: {
            status: 409,
            data: {
              detail:
                "Request ID conflicts with another message.",
            },
          },
        });

        const composer =
          await renderCareerAI();

        await user.type(
          composer,
          "Review my current learning plan."
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Send",
            }
          )
        );

        expect(
          await screen.findByText(
            "Request ID conflicts with another message."
          )
        ).toBeInTheDocument();

        expect(
          screen.queryByRole(
            "button",
            {
              name:
                "Retry message",
            }
          )
        ).not.toBeInTheDocument();

        expect(
          composer
        ).toHaveValue("");
      }
    );
  }
);