import {
  useEffect,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import {
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  FileText,
  ShieldCheck,
  UploadCloud,
  X,
  XCircle,
} from "lucide-react";

import api from "../services/api";


const MAX_FILE_SIZE =
  5 * 1024 * 1024;


function Resume() {
  const navigate = useNavigate();

  const [file, setFile] =
    useState(null);

  const [loading, setLoading] =
    useState(false);
  const [restoring, setRestoring] =
  useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");


  /* ==================================================
     RESTORE ACTIVE RESUME
     ================================================== */

  useEffect(() => {
    let cancelled = false;
    let activeResume = null;

    try {
      activeResume =
        JSON.parse(
          localStorage.getItem(
            "careerpilot_active_resume"
          ) || "null"
        );

    } catch {
      localStorage.removeItem(
        "careerpilot_active_resume"
      );

      localStorage.removeItem(
        "careerpilot_resume_id"
      );

      return undefined;
    }

    if (
      !activeResume?.resume_id
    ) {
      return undefined;
    }

    async function restoreResume() {
      setRestoring(true);

      try {
        const response =
          await api.get(
            `/api/resume/${encodeURIComponent(
              activeResume.resume_id
            )}`
          );

        if (cancelled) {
          return;
        }

        const resumeMetadata =
          response.data;

        const restoredResume = {
          resume_id:
            resumeMetadata.resume_id,

          thread_id:
            activeResume.thread_id,

          filename:
            resumeMetadata.filename,
        };

        localStorage.setItem(
          "careerpilot_active_resume",
          JSON.stringify(
            restoredResume
          )
        );

        localStorage.setItem(
          "careerpilot_resume_id",
          String(
            resumeMetadata.resume_id
          )
        );

        setResult({
          ...resumeMetadata,

          thread_id:
            activeResume.thread_id,
        });

      } catch (err) {
        if (cancelled) {
          return;
        }

        if (
          err.response?.status === 404
        ) {
          localStorage.removeItem(
            "careerpilot_active_resume"
          );

          localStorage.removeItem(
            "careerpilot_resume_id"
          );

          localStorage.removeItem(
            "careerpilot_thread_id"
          );

          localStorage.removeItem(
            "careerpilot_latest_job_match"
          );

          localStorage.removeItem(
            "careerpilot_latest_skill_gap"
          );

          localStorage.removeItem(
            "careerpilot_latest_career_plan"
          );

          setResult(null);

          return;
        }

        console.error(
          "CareerPilot resume restoration failed:",
          err
        );

        setError(
          "CareerPilot could not restore your "
          + "active resume. Please refresh or "
          + "upload it again."
        );

      } finally {
        if (!cancelled) {
          setRestoring(false);
        }
      }
    }

    restoreResume();

    return () => {
      cancelled = true;
    };
  }, []);

  /* ==================================================
     RESUME THREAD
     ================================================== */

  /*
   * Every new resume upload receives a fresh
   * conversation thread.
   *
   * This prevents a thread created by another
   * account/session/resume from being reused.
   *
   * The generated thread is intentionally NOT
   * persisted here. It is stored only after the
   * backend confirms that the upload succeeded.
   */

  function createFreshResumeThreadId() {
    return (
      typeof crypto !== "undefined" &&
      typeof crypto.randomUUID === "function"
        ? `careerpilot-${crypto.randomUUID()}`
        : `careerpilot-${Date.now()}-${Math.random()
            .toString(36)
            .slice(2)}`
    );
  }


  /* ==================================================
     FILE SELECTION
     ================================================== */

  function handleFileChange(event) {
    const selectedFile =
      event.target.files?.[0];


    setResult(null);
    setError("");


    if (!selectedFile) {
      setFile(null);

      return;
    }


    if (
      selectedFile.type !==
      "application/pdf"
    ) {
      setFile(null);


      setError(
        "Please choose a PDF resume."
      );


      event.target.value = "";


      return;
    }


    if (
      selectedFile.size >
      MAX_FILE_SIZE
    ) {
      setFile(null);


      setError(
        "Your resume must be 5 MB or smaller."
      );


      event.target.value = "";


      return;
    }


    setFile(
      selectedFile
    );
  }


  /* ==================================================
     REMOVE SELECTED FILE
     ================================================== */

  function handleRemoveFile() {
    setFile(null);
    setResult(null);
    setError("");
  }


  /* ==================================================
     UPLOAD RESUME
     ================================================== */

  async function handleUpload() {
    if (!file) {
      setError(
        "Choose a PDF resume before continuing."
      );

      return;
    }


    setLoading(true);
    setError("");
    setResult(null);


    try {
      /*
       * Create a completely fresh thread for this
       * resume upload.
       *
       * Do not reuse careerpilot_thread_id here.
       */

      const threadId =
        createFreshResumeThreadId();


      const formData =
        new FormData();


      formData.append(
        "file",
        file
      );


      const response =
        await api.post(
          `/api/resume/upload?thread_id=${encodeURIComponent(
            threadId
          )}`,
          formData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },
          }
        );


      const uploadResult =
        response.data;


      /*
       * Validate the identifiers returned by the
       * backend before changing workspace state.
       */

      if (!uploadResult?.resume_id) {
        throw new Error(
          "Resume upload completed without a resume ID."
        );
      }


      /*
       * The backend should normally return the same
       * thread ID that was supplied during upload.
       *
       * Falling back to threadId keeps the workspace
       * consistent if the response omits it.
       */

      const confirmedThreadId =
        uploadResult.thread_id ||
        threadId;


      /*
       * Read the previously active resume before
       * replacing it.
       */

      let previousResume =
        null;


      try {
        previousResume =
          JSON.parse(
            localStorage.getItem(
              "careerpilot_active_resume"
            ) || "null"
          );

      } catch {
        previousResume =
          null;
      }


      /*
       * Detect whether CareerPilot now has a
       * different active resume record.
       */

      const resumeChanged =
        Boolean(
          previousResume?.resume_id
        ) &&
        String(
          previousResume.resume_id
        ) !==
          String(
            uploadResult.resume_id
          );


      /*
       * Analysis generated for an older resume must
       * never remain attached to a newly uploaded
       * resume.
       *
       * Clear resume-scoped analysis state whenever
       * the resume record changes.
       */

      if (resumeChanged) {
        localStorage.removeItem(
          "careerpilot_latest_job_match"
        );

        localStorage.removeItem(
          "careerpilot_latest_skill_gap"
        );

        localStorage.removeItem(
          "careerpilot_latest_career_plan"
        );
      }


      /*
       * Store the newly active resume.
       *
       * resume_id and thread_id now represent the
       * same successful upload and are reused by
       * Job Match, Skill Gap, Career Plan and
       * Career AI Agent Mode.
       */

      const activeResume = {
        resume_id:
          uploadResult.resume_id,

        thread_id:
          confirmedThreadId,

        filename:
          uploadResult.filename ||
          file.name,
      };


      localStorage.setItem(
        "careerpilot_active_resume",
        JSON.stringify(
          activeResume
        )
      );


      /*
       * Keep the compatibility resume ID key used
       * by other CareerPilot screens.
       */

      localStorage.setItem(
        "careerpilot_resume_id",
        String(
          uploadResult.resume_id
        )
      );


      /*
       * Replace any old conversation thread only
       * AFTER the backend successfully accepts the
       * current resume upload.
       */

      localStorage.setItem(
        "careerpilot_thread_id",
        confirmedThreadId
      );


      /*
       * Use the normalized result so the UI and
       * localStorage contain identical identifiers.
       */

      setResult({
        ...uploadResult,
        thread_id:
          confirmedThreadId,
        filename:
          uploadResult.filename ||
          file.name,
      });

    } catch (err) {
      console.error(
        "CareerPilot resume upload failed:",
        err
      );


      setError(
        err.response?.data?.detail ||
        err.message ||
        "CareerPilot could not upload your resume. Please try again."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <section>

      {/* ================= PAGE HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          RESUME
        </p>


        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Your resume workspace
        </h1>


        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          Upload the resume you want CareerPilot
          to use for job matching, skill-gap
          analysis, and personalized career
          planning.
        </p>

      </div>


      {/* ================= MAIN GRID ================= */}

      <div className="mt-10 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">

        {/* ================= UPLOAD CARD ================= */}

        <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

          <div className="flex items-start justify-between gap-4">

            <div>
              <p className="text-xs font-bold tracking-[0.12em] text-brand">
                UPLOAD RESUME
              </p>


              <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                Choose your current resume
              </h2>


              <p className="mt-2 text-sm leading-6 text-text-muted">
                Use the version you would currently
                submit for applications.
              </p>
            </div>


            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">

              <UploadCloud
                size={21}
              />

            </div>

          </div>


          {/* ================= FILE SELECT ================= */}

          {!file && (
            <label className="mt-7 flex min-h-[230px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 bg-app-bg px-6 text-center transition hover:border-emerald-300 hover:bg-emerald-50/40">

              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-brand shadow-sm">

                <FileText
                  size={25}
                />

              </div>


              <p className="mt-5 font-semibold text-midnight">
                Choose a PDF resume
              </p>


              <p className="mt-2 max-w-sm text-sm leading-6 text-text-muted">
                Select a resume from your
                device to prepare it for
                CareerPilot analysis.
              </p>


              <span className="mt-4 rounded-full border border-border-soft bg-white px-3 py-1.5 text-xs font-medium text-text-muted">
                PDF · Maximum 5 MB
              </span>


              <input
  type="file"
  accept=".pdf,application/pdf"
  onChange={
    handleFileChange
  }
  disabled={
    restoring
  }
  className="hidden"
/>

            </label>
          )}


          {/* ================= SELECTED FILE ================= */}

          {file && (
            <div className="mt-7">

              <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-5">

                <div className="flex items-center gap-4">

                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white text-brand shadow-sm">

                    <FileText
                      size={22}
                    />

                  </div>


                  <div className="min-w-0 flex-1">

                    <p className="truncate text-sm font-semibold text-midnight">
                      {file.name}
                    </p>


                    <p className="mt-1 text-xs text-text-muted">
                      {(
                        file.size /
                        1024 /
                        1024
                      ).toFixed(2)}
                      {" "}MB · PDF
                    </p>

                  </div>


                  <button
                    type="button"
                    onClick={
                      handleRemoveFile
                    }
                    disabled={
                      loading
                    }
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-gray-400 transition hover:bg-white hover:text-midnight disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="Remove selected resume"
                  >
                    <X
                      size={18}
                    />
                  </button>

                </div>

              </div>


              <button
                type="button"
                onClick={
                  handleRemoveFile
                }
                disabled={
                  loading
                }
                className="mt-3 text-sm font-semibold text-brand transition hover:text-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                Choose a different file
              </button>

            </div>
          )}


          {/* ================= ERROR ================= */}

          {error && (
            <div className="mt-5 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">

              <XCircle
                size={18}
                className="mt-0.5 shrink-0"
              />


              <span>
                {error}
              </span>

            </div>
          )}


          {/* ================= UPLOAD BUTTON ================= */}

          <button
            type="button"
            disabled={
  loading ||
  restoring ||
  !file
}
            onClick={
              handleUpload
            }
            className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover focus:outline-none focus:ring-4 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >

            <UploadCloud
              size={18}
            />


            {restoring
  ? "Restoring your resume..."
  : loading
    ? "Preparing your resume..."
    : "Upload resume"}

          </button>


          <p className="mt-4 text-center text-xs leading-5 text-gray-400">
            Your uploaded resume is used
            to provide personalized CareerPilot
            analysis for your account.
          </p>

        </section>


        {/* ================= INFORMATION PANEL ================= */}

        <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-8">

          <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
            WHAT HAPPENS NEXT
          </p>


          <h2 className="mt-3 text-2xl font-semibold tracking-tight">
            One resume powers your CareerPilot workspace.
          </h2>


          <p className="mt-4 leading-7 text-gray-300">
            Once your resume is ready,
            CareerPilot can use it to provide
            role-specific insights and practical
            career guidance.
          </p>


          <div className="mt-8 space-y-5">

            <StatusStep
              icon={
                <FileCheck2
                  size={19}
                />
              }
              title="Prepare your resume"
              description="CareerPilot securely prepares the selected PDF for analysis."
            />


            <StatusStep
              icon={
                <ShieldCheck
                  size={19}
                />
              }
              title="Ground the analysis"
              description="Your resume becomes the evidence source for personalized recommendations."
            />


            <StatusStep
              icon={
                <ArrowRight
                  size={19}
                />
              }
              title="Move to your target role"
              description="Compare your profile with a job description and identify your next priorities."
            />

          </div>


          {/* ================= SUCCESS ================= */}

          {result && (
            <div className="mt-8 rounded-2xl border border-emerald-500/20 bg-emerald-400/10 p-5">

              <div className="flex items-start gap-3">

                <CheckCircle2
                  size={21}
                  className="mt-0.5 shrink-0 text-emerald-300"
                />


                <div>

                  <p className="font-semibold text-emerald-100">
                    Resume uploaded successfully
                  </p>


                  <p className="mt-2 break-all text-sm leading-6 text-gray-300">
                    {result.filename}
                  </p>


                  <p className="mt-2 text-sm leading-6 text-gray-400">
                    Your resume is ready to use
                    across CareerPilot.
                  </p>

                </div>

              </div>


              <button
                type="button"
                onClick={() =>
                  navigate(
                    "/job-match"
                  )
                }
                className="mt-5 flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover"
              >
                Continue to Job Match

                <ArrowRight
                  size={16}
                />
              </button>

            </div>
          )}

        </section>

      </div>

    </section>
  );
}


/* ==================================================
   STATUS STEP
   ================================================== */

function StatusStep({
  icon,
  title,
  description,
}) {
  return (
    <div className="flex gap-4">

      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/5 text-brand-accent">
        {icon}
      </div>


      <div>

        <p className="text-sm font-semibold text-white">
          {title}
        </p>


        <p className="mt-1 text-sm leading-6 text-gray-400">
          {description}
        </p>

      </div>

    </div>
  );
}


export default Resume;