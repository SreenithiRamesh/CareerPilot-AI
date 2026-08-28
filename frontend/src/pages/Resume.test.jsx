import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import {
  MemoryRouter,
} from "react-router-dom";

import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import api from "../services/api";
import Resume from "./Resume";


vi.mock(
  "../services/api",
  () => ({
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  })
);


function renderResume() {
  return render(
    <MemoryRouter>
      <Resume />
    </MemoryRouter>
  );
}


describe(
  "Resume refresh restoration",
  () => {
    beforeEach(() => {
      vi.resetAllMocks();
      localStorage.clear();

      vi.spyOn(
        console,
        "error"
      ).mockImplementation(
        () => {}
      );
    });


    it(
      "restores the active resume after refresh",
      async () => {
        localStorage.setItem(
          "careerpilot_active_resume",
          JSON.stringify({
            resume_id: 42,
            thread_id:
              "careerpilot-resume-thread",
            filename:
              "cached-filename.pdf",
          })
        );

        localStorage.setItem(
          "careerpilot_resume_id",
          "42"
        );

        api.get.mockResolvedValue({
          data: {
            resume_id: 42,
            filename:
              "sreenithi-resume.pdf",
            processing_status:
              "completed",
            vector_collection_id:
              "resume_42",
            upload_timestamp:
              "2026-08-28T10:00:00",
          },
        });

        renderResume();

        expect(
          await screen.findByText(
            "Resume uploaded successfully"
          )
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "sreenithi-resume.pdf"
          )
        ).toBeInTheDocument();

        expect(
          api.get
        ).toHaveBeenCalledTimes(1);

        expect(
          api.get
        ).toHaveBeenCalledWith(
          "/api/resume/42"
        );

        expect(
          api.post
        ).not.toHaveBeenCalled();

        const restoredResume =
          JSON.parse(
            localStorage.getItem(
              "careerpilot_active_resume"
            )
          );

        expect(
          restoredResume
        ).toEqual({
          resume_id: 42,
          thread_id:
            "careerpilot-resume-thread",
          filename:
            "sreenithi-resume.pdf",
        });
      }
    );


    it(
      "does not request metadata without an active resume",
      async () => {
        renderResume();

        await waitFor(() => {
          expect(
            api.get
          ).not.toHaveBeenCalled();
        });

        expect(
          screen.queryByText(
            "Resume uploaded successfully"
          )
        ).not.toBeInTheDocument();

        expect(
          api.post
        ).not.toHaveBeenCalled();
      }
    );


    it(
      "clears stale resume state after a 404",
      async () => {
        localStorage.setItem(
          "careerpilot_active_resume",
          JSON.stringify({
            resume_id: 999,
            thread_id:
              "stale-resume-thread",
            filename:
              "stale-resume.pdf",
          })
        );

        localStorage.setItem(
          "careerpilot_resume_id",
          "999"
        );

        localStorage.setItem(
          "careerpilot_thread_id",
          "stale-resume-thread"
        );

        localStorage.setItem(
          "careerpilot_latest_job_match",
          JSON.stringify({
            resume_id: 999,
          })
        );

        localStorage.setItem(
          "careerpilot_latest_skill_gap",
          JSON.stringify({
            resume_id: 999,
          })
        );

        localStorage.setItem(
          "careerpilot_latest_career_plan",
          JSON.stringify({
            resume_id: 999,
          })
        );

        api.get.mockRejectedValue({
          response: {
            status: 404,
            data: {
              detail:
                "Resume not found.",
            },
          },
        });

        renderResume();

        await waitFor(() => {
          expect(
            api.get
          ).toHaveBeenCalledWith(
            "/api/resume/999"
          );
        });

        await waitFor(() => {
          expect(
            localStorage.getItem(
              "careerpilot_active_resume"
            )
          ).toBeNull();

          expect(
            localStorage.getItem(
              "careerpilot_resume_id"
            )
          ).toBeNull();

          expect(
            localStorage.getItem(
              "careerpilot_thread_id"
            )
          ).toBeNull();

          expect(
            localStorage.getItem(
              "careerpilot_latest_job_match"
            )
          ).toBeNull();

          expect(
            localStorage.getItem(
              "careerpilot_latest_skill_gap"
            )
          ).toBeNull();

          expect(
            localStorage.getItem(
              "careerpilot_latest_career_plan"
            )
          ).toBeNull();
        });

        expect(
          screen.queryByText(
            "Resume uploaded successfully"
          )
        ).not.toBeInTheDocument();

        expect(
          api.post
        ).not.toHaveBeenCalled();
      }
    );
  }
);