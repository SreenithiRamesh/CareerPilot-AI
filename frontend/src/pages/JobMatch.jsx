import { useState } from "react";

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Download,
  FileSearch,
  Gauge,
  LoaderCircle,
  Target,
  XCircle,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import api from "../services/api";

import {
  exportJobMatchPDF,
} from "../utils/reportExport";


function JobMatch() {
  const [jobDescription, setJobDescription] =
    useState("");

  const navigate =
    useNavigate();

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [analysis, setAnalysis] =
    useState(null);


  function getActiveResume() {
    const storedResume =
      localStorage.getItem(
        "careerpilot_active_resume"
      );


    if (!storedResume) {
      return null;
    }


    try {
      return JSON.parse(
        storedResume
      );

    } catch {
      return null;
    }
  }


  /* ==================================================
     ANALYZE JOB MATCH
     ================================================== */

  async function handleAnalyze() {
    setError("");
    setAnalysis(null);


    const activeResume =
      getActiveResume();


    if (!activeResume) {
      setError(
        "Upload a resume before running a job match."
      );

      return;
    }


    if (!jobDescription.trim()) {
      setError(
        "Paste the job description you want to compare with your resume."
      );

      return;
    }


    setLoading(true);


    try {
      const response =
        await api.post(
          "/api/chat",
          {
            thread_id:
              activeResume.thread_id,

            resume_id:
              activeResume.resume_id,

            message:
              "Match my resume with this job description.",

            target_role:
              "Software Engineer",

            job_description:
              jobDescription.trim(),

            skills: [],

            history: [],
          }
        );


      if (
        response.data.intent !==
        "job_match"
      ) {
        throw new Error(
          "Unexpected CareerPilot response."
        );
      }


      if (
        !response.data.data
      ) {
        throw new Error(
          "Job Match analysis was not returned."
        );
      }


      setAnalysis(
        response.data.data
      );


      /*
       * Store the latest Job Match result
       * together with the resume that produced it.
       *
       * This lets CareerPilot detect stale analysis
       * if the active resume changes later.
       */

      localStorage.setItem(
        "careerpilot_latest_job_match",
        JSON.stringify({
          ...response.data.data,

          resume_id:
            activeResume.resume_id,

          thread_id:
            activeResume.thread_id,

          job_match_result_id:
            response.data
              .job_match_result_id,

          job_description_id:
            response.data
              .job_description_id,

          job_description:
            jobDescription.trim(),
        })
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "CareerPilot could not complete the job match."
      );

    } finally {
      setLoading(false);
    }
  }


  /* ==================================================
     DOWNLOAD JOB MATCH PDF
     ================================================== */

  function handleDownloadPDF() {
    if (!analysis) {
      setError(
        "Run a Job Match before downloading the report."
      );

      return;
    }


    try {
      exportJobMatchPDF({
        analysis,

        jobDescription:
          jobDescription.trim(),

        targetRole:
          "Software Engineer",
      });

    } catch  {
     
      setError(
        "CareerPilot could not generate the PDF report. Please try again."
      );
    }
  }


  return (
    <section>

      {/* ================= PAGE HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          JOB MATCH
        </p>


        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Compare your resume with a target role
        </h1>


        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          Paste a job description and CareerPilot
          will compare its requirements with the
          evidence available in your uploaded resume.
        </p>

      </div>


      {/* ================= INPUT + INFO ================= */}

      <div className="mt-10 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">

        {/* ================= JOB DESCRIPTION ================= */}

        <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

          <div className="flex items-start justify-between gap-4">

            <div>

              <p className="text-xs font-bold tracking-[0.12em] text-brand">
                TARGET ROLE
              </p>


              <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                Paste the job description
              </h2>


              <p className="mt-2 text-sm leading-6 text-text-muted">
                Use the complete role description
                whenever possible for a more useful
                comparison.
              </p>

            </div>


            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">

              <FileSearch
                size={21}
              />

            </div>

          </div>


          <textarea
            value={jobDescription}
            onChange={(event) =>
              setJobDescription(
                event.target.value
              )
            }
            placeholder="Paste the job description here..."
            rows={14}
            className="mt-7 w-full resize-y rounded-2xl border border-border-soft bg-app-bg p-4 text-sm leading-7 text-midnight outline-none transition placeholder:text-gray-400 focus:border-brand focus:ring-4 focus:ring-emerald-500/10"
          />


          <div className="mt-3 flex items-center justify-between gap-4 text-xs text-text-muted">

            <span>
              Include required skills,
              responsibilities, and qualifications.
            </span>


            <span className="shrink-0">
              {jobDescription.length} characters
            </span>

          </div>


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


          {/* ================= ANALYZE BUTTON ================= */}

          <button
            type="button"
            onClick={
              handleAnalyze
            }
            disabled={
              loading ||
              !jobDescription.trim()
            }
            className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover focus:outline-none focus:ring-4 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <>
                <LoaderCircle
                  size={18}
                  className="animate-spin"
                />

                Analyzing your match...
              </>
            ) : (
              <>
                <Target
                  size={18}
                />

                Analyze job match
              </>
            )}
          </button>

        </section>


        {/* ================= HOW IT WORKS ================= */}

        <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-8">

          <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
            WHAT YOU&apos;LL GET
          </p>


          <h2 className="mt-3 text-2xl font-semibold tracking-tight">
            A role-specific view of your current fit.
          </h2>


          <p className="mt-4 leading-7 text-gray-300">
            CareerPilot compares the role
            requirements with your resume evidence
            and separates strengths from areas that
            need more proof or preparation.
          </p>


          <div className="mt-8 space-y-5">

            <InfoStep
              icon={
                <CheckCircle2
                  size={19}
                />
              }
              title="Strong matches"
              description="Requirements clearly supported by your resume."
            />


            <InfoStep
              icon={
                <Gauge
                  size={19}
                />
              }
              title="Partial matches"
              description="Areas where related evidence exists but could be stronger."
            />


            <InfoStep
              icon={
                <AlertTriangle
                  size={19}
                />
              }
              title="Priority gaps"
              description="Important role requirements that need attention."
            />

          </div>

        </section>

      </div>


      {/* ================= LOADING ================= */}

      {loading &&
        !analysis && (
          <section className="mt-8">

            <div className="grid gap-6 xl:grid-cols-[300px_1fr]">

              <div className="flex min-h-[280px] flex-col items-center justify-center rounded-2xl bg-midnight p-8 text-center text-white">

                <div className="h-[152px] w-[152px] animate-pulse rounded-full border-[10px] border-white/10" />


                <p className="mt-6 text-sm leading-6 text-gray-400">
                  Comparing role requirements
                  with your resume evidence...
                </p>

              </div>


              <div className="grid gap-5 md:grid-cols-2">

                {[0, 1, 2, 3].map(
                  (key) => (
                    <div
                      key={key}
                      className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm"
                    >

                      <div className="h-4 w-32 animate-pulse rounded bg-app-bg" />


                      <div className="mt-6 space-y-3">

                        <div className="h-3 w-full animate-pulse rounded bg-app-bg" />

                        <div className="h-3 w-5/6 animate-pulse rounded bg-app-bg" />

                        <div className="h-3 w-2/3 animate-pulse rounded bg-app-bg" />

                      </div>

                    </div>
                  )
                )}

              </div>

            </div>

          </section>
        )}


      {/* ================= EMPTY STATE ================= */}

      {!loading &&
        !analysis &&
        !error && (
          <section className="mt-8 flex flex-col items-center justify-center rounded-2xl border border-dashed border-border-soft bg-white/60 px-8 py-14 text-center">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-soft text-brand">

              <Gauge
                size={22}
              />

            </div>


            <h3 className="mt-5 text-lg font-semibold tracking-tight text-midnight">
              Your match results will appear here
            </h3>


            <p className="mt-2 max-w-md text-sm leading-6 text-text-muted">
              Paste a job description above and run
              the analysis to see your score, strong
              and partial matches, gaps, and suggested
              resume improvements.
            </p>

          </section>
        )}


      {/* ================= RESULTS ================= */}

      {analysis && (
        <section className="mt-8">

          <div className="grid gap-6 xl:grid-cols-[300px_1fr]">

            {/* ================= SCORE ================= */}

            <div className="flex min-h-[280px] flex-col items-center justify-center rounded-2xl bg-midnight p-8 text-center text-white">

              <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
                JOB MATCH SCORE
              </p>


              <div className="mt-6">

                <ScoreRing
                  score={
                    analysis.match_score
                  }
                />

              </div>


              <p className="mt-5 max-w-[220px] text-sm leading-6 text-gray-300">
                Based on the requirements in
                this job description and the
                evidence in your resume.
              </p>

            </div>


            {/* ================= BREAKDOWN ================= */}

            <div className="grid gap-5 md:grid-cols-2">

              <ResultCard
                title="Strong matches"
                tone="success"
                items={
                  analysis.strong_matches
                }
              />


              <ResultCard
                title="Partial matches"
                tone="warning"
                items={
                  analysis.partial_matches
                }
              />


              <ResultCard
                title="Missing requirements"
                tone="danger"
                items={
                  analysis.missing_skills
                }
              />


              <ResultCard
                title="Priority actions"
                tone="brand"
                items={
                  analysis.priority_actions
                }
              />

            </div>

          </div>


          {/* ================= RESUME IMPROVEMENTS ================= */}

          {analysis.resume_improvements
            ?.length > 0 && (
            <div className="mt-6 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

              <p className="text-xs font-bold tracking-[0.14em] text-brand">
                RESUME IMPROVEMENTS
              </p>


              <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                Make the relevant evidence easier to see
              </h2>


              <div className="mt-6 space-y-4">

                {analysis.resume_improvements.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      key={`${item}-${index}`}
                      className="flex gap-4 rounded-xl bg-app-bg p-4"
                    >

                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-xs font-bold text-brand">
                        {index + 1}
                      </div>


                      <p className="text-sm leading-7 text-text-muted">
                        {item}
                      </p>

                    </div>
                  )
                )}

              </div>

            </div>
          )}


          {/* ================= REPORT ACTIONS ================= */}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

            {/* Download PDF */}

            <button
              type="button"
              onClick={
                handleDownloadPDF
              }
              className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-border-soft bg-white px-5 text-sm font-semibold text-midnight transition hover:border-emerald-200 hover:bg-emerald-50/50 focus:outline-none focus:ring-4 focus:ring-emerald-500/10"
            >
              <Download
                size={16}
              />

              Download PDF
            </button>


            {/* Continue */}

            <button
              type="button"
              onClick={() =>
                navigate(
                  "/skill-gap"
                )
              }
              className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover focus:outline-none focus:ring-4 focus:ring-emerald-500/20"
            >
              Continue to Skill Gap

              <ArrowRight
                size={16}
              />
            </button>

          </div>

        </section>
      )}

    </section>
  );
}


/* ==================================================
   SCORE RING
   ================================================== */

function ScoreRing({
  score,
}) {
  const safeScore =
    typeof score === "number" &&
    !Number.isNaN(score)
      ? Math.max(
          0,
          Math.min(
            100,
            score
          )
        )
      : 0;


  const size =
    152;

  const strokeWidth =
    10;

  const radius =
    (
      size -
      strokeWidth
    ) / 2;

  const circumference =
    2 *
    Math.PI *
    radius;


  const offset =
    circumference -
    (
      safeScore /
      100
    ) *
      circumference;


  return (
    <div
      className="relative flex items-center justify-center"
      style={{
        width: size,
        height: size,
      }}
    >

      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
      >

        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={
            strokeWidth
          }
        />


        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          className="text-emerald-400"
          strokeWidth={
            strokeWidth
          }
          strokeLinecap="round"
          strokeDasharray={
            circumference
          }
          strokeDashoffset={
            offset
          }
          style={{
            transition:
              "stroke-dashoffset 0.6s ease",
          }}
        />

      </svg>


      <div className="absolute flex flex-col items-center">

        <span className="text-4xl font-bold tracking-tight text-emerald-300">
          {typeof score ===
          "number"
            ? score
            : "--"}
        </span>


        <span className="mt-1 text-xs font-medium text-gray-400">
          out of 100
        </span>

      </div>

    </div>
  );
}


/* ==================================================
   INFO STEP
   ================================================== */

function InfoStep({
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


/* ==================================================
   RESULT CARD
   ================================================== */

function ResultCard({
  title,
  items = [],
  tone,
}) {
  const toneStyles = {
    success: {
      border:
        "border-emerald-200",

      badge:
        "bg-emerald-50 text-emerald-700",

      icon:
        "text-emerald-600",

      ItemIcon:
        CheckCircle2,
    },


    warning: {
      border:
        "border-amber-200",

      badge:
        "bg-amber-50 text-amber-700",

      icon:
        "text-amber-600",

      ItemIcon:
        AlertTriangle,
    },


    danger: {
      border:
        "border-red-200",

      badge:
        "bg-red-50 text-red-700",

      icon:
        "text-red-600",

      ItemIcon:
        XCircle,
    },


    brand: {
      border:
        "border-emerald-200",

      badge:
        "bg-brand-soft text-brand",

      icon:
        "text-brand",

      ItemIcon:
        Target,
    },
  };


  const styles =
    toneStyles[tone] ||
    toneStyles.brand;


  const ItemIcon =
    styles.ItemIcon;


  return (
    <article
      className={`rounded-2xl border bg-white p-6 shadow-sm ${styles.border}`}
    >

      <div className="flex items-center justify-between gap-3">

        <h3 className="font-semibold text-midnight">
          {title}
        </h3>


        <span
          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${styles.badge}`}
        >
          {items?.length || 0}
        </span>

      </div>


      {items?.length > 0 ? (
        <ul className="mt-5 space-y-3">

          {items.map(
            (
              item,
              index
            ) => (
              <li
                key={`${item}-${index}`}
                className="flex gap-3 text-sm leading-6 text-text-muted"
              >

                <ItemIcon
                  size={17}
                  className={`mt-1 shrink-0 ${styles.icon}`}
                />


                <span>
                  {item}
                </span>

              </li>
            )
          )}

        </ul>
      ) : (
        <p className="mt-5 text-sm text-text-muted">
          No items were identified.
        </p>
      )}

    </article>
  );
}


export default JobMatch;