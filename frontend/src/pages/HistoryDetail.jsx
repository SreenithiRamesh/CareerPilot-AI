import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Download,
  FileText,
  Gauge,
  LoaderCircle,
  Route,
  Sparkles,
  Target,
  XCircle,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import api from "../services/api";

import {
  generateCareerReadinessReport,
} from "../utils/careerReportExport";


function HistoryDetail() {
  const navigate =
    useNavigate();

  const {
    jobMatchId,
  } =
    useParams();


  const [
    metadata,
    setMetadata,
  ] =
    useState(null);

  const [
    jobMatch,
    setJobMatch,
  ] =
    useState(null);

  const [
    skillGap,
    setSkillGap,
  ] =
    useState(null);

  const [
    careerPlan,
    setCareerPlan,
  ] =
    useState(null);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    error,
    setError,
  ] =
    useState("");

  const [
    reportError,
    setReportError,
  ] =
    useState("");


  /* ==================================================
     LOAD HISTORICAL ANALYSIS
     ================================================== */

  useEffect(() => {
    loadHistoricalAnalysis();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobMatchId]);


  async function loadHistoricalAnalysis() {
    setLoading(true);
    setError("");
    setReportError("");

    try {
      /*
       * History.jsx stores the selected summary
       * before navigating here.
       */

      let selectedMetadata =
        getStoredHistoryMetadata();


      /*
       * Direct browser refresh / copied URL fallback:
       *
       * If the local selected-history metadata
       * does not belong to this Job Match ID,
       * retrieve /history and locate it again.
       */

      if (
        !selectedMetadata ||
        String(
          selectedMetadata
            .job_match_result_id
        ) !==
          String(
            jobMatchId
          )
      ) {
        const historyResponse =
          await api.get(
            "/api/analysis/history"
          );

        const historyItems =
          historyResponse
            .data?.items ||
          [];


        selectedMetadata =
          historyItems.find(
            (item) =>
              String(
                item
                  .job_match_result_id
              ) ===
              String(
                jobMatchId
              )
          ) ||
          null;


        if (
          selectedMetadata
        ) {
          localStorage.setItem(
            "careerpilot_selected_history",
            JSON.stringify(
              selectedMetadata
            )
          );
        }
      }


      if (
        !selectedMetadata
      ) {
        throw new Error(
          "The selected historical analysis could not be found."
        );
      }


      setMetadata(
        selectedMetadata
      );


      /*
       * Job Match always exists because it
       * is the primary ID used by this route.
       */

      const jobMatchRequest =
        api.get(
          `/api/analysis/job-match/${jobMatchId}`
        );


      /*
       * Skill Gap and Career Plan are optional.
       *
       * Some older history records may not have
       * completed every CareerPilot stage.
       */

      const skillGapRequest =
        selectedMetadata
          .skill_gap_report_id
          ? api.get(
              `/api/analysis/skill-gap/${selectedMetadata.skill_gap_report_id}`
            )
          : Promise.resolve(
              null
            );


      const careerPlanRequest =
        selectedMetadata
          .career_plan_id
          ? api.get(
              `/api/analysis/career-plan/${selectedMetadata.career_plan_id}`
            )
          : Promise.resolve(
              null
            );


      const [
        jobMatchResponse,
        skillGapResponse,
        careerPlanResponse,
      ] =
        await Promise.all([
          jobMatchRequest,
          skillGapRequest,
          careerPlanRequest,
        ]);


      setJobMatch(
        jobMatchResponse.data
      );


      setSkillGap(
        skillGapResponse?.data ||
        null
      );


      setCareerPlan(
        careerPlanResponse?.data ||
        null
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "CareerPilot could not load this saved analysis."
      );

    } finally {
      setLoading(false);
    }
  }


  /* ==================================================
     DOWNLOAD HISTORICAL PDF
     ================================================== */

  function handleDownloadReport() {
    setReportError("");


    const resumeFilename =
      jobMatch?.resume_filename ||
      metadata?.resume_filename ||
      "Resume";


    const roleTitle =
      jobMatch?.job_title ||
      metadata?.job_title ||
      "Saved Career Analysis";


    const analyzedAt =
      metadata?.analyzed_at ||
      jobMatch?.created_at ||
      null;


    const result =
      generateCareerReadinessReport({
        historical: true,

        resume: {
          resume_id:
            jobMatch?.resume_id ||
            metadata?.resume_id ||
            null,

          filename:
            resumeFilename,

          original_filename:
            resumeFilename,
        },

        jobMatch,

        skillGap,

        careerPlan,

        targetRole:
          roleTitle,

        analyzedAt,
      });


    if (
      !result.success
    ) {
      setReportError(
        result.reasons?.join(
          " "
        ) ||
        "CareerPilot could not generate this historical report."
      );
    }
  }


  /* ==================================================
     LOADING
     ================================================== */

  if (loading) {
    return (
      <section>

        <BackButton
          onClick={() =>
            navigate(
              "/history"
            )
          }
        />


        <div className="mt-8 flex min-h-[360px] items-center justify-center rounded-2xl border border-border-soft bg-white shadow-sm">

          <div className="flex items-center gap-3 text-sm text-text-muted">

            <LoaderCircle
              size={20}
              className="animate-spin text-brand"
            />

            Loading saved analysis...

          </div>

        </div>

      </section>
    );
  }


  /* ==================================================
     ERROR
     ================================================== */

  if (error) {
    return (
      <section>

        <BackButton
          onClick={() =>
            navigate(
              "/history"
            )
          }
        />


        <div className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-6">

          <div className="flex gap-3">

            <XCircle
              size={20}
              className="mt-0.5 shrink-0 text-red-600"
            />


            <div>

              <p className="font-semibold text-red-800">
                Could not load saved analysis
              </p>


              <p className="mt-2 text-sm leading-6 text-red-700">
                {error}
              </p>


              <button
                type="button"
                onClick={
                  loadHistoricalAnalysis
                }
                className="mt-5 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
              >
                Try again
              </button>

            </div>

          </div>

        </div>

      </section>
    );
  }


  const roleTitle =
    jobMatch?.job_title ||
    metadata?.job_title ||
    "Saved Career Analysis";


  const companyName =
    jobMatch?.company_name ||
    metadata?.company_name ||
    null;


  const resumeFilename =
    jobMatch?.resume_filename ||
    metadata?.resume_filename ||
    "Resume";


  const analyzedDate =
    formatDate(
      metadata?.analyzed_at ||
      jobMatch?.created_at
    );


  const reportAvailable =
    Boolean(
      jobMatch &&
      skillGap &&
      careerPlan
    );


  return (
    <section>

      {/* ==================================================
          TOP ACTIONS
          ================================================== */}

      <div className="flex flex-wrap items-center justify-between gap-4">

        <BackButton
          onClick={() =>
            navigate(
              "/history"
            )
          }
        />


        <button
          type="button"
          onClick={
            handleDownloadReport
          }
          disabled={
            !reportAvailable
          }
          className={`inline-flex h-10 items-center gap-2 rounded-lg px-4 text-sm font-semibold transition ${
            reportAvailable
              ? "bg-brand text-white hover:bg-brand-hover"
              : "cursor-not-allowed bg-gray-100 text-gray-400"
          }`}
          title={
            reportAvailable
              ? "Download this saved analysis as PDF"
              : "Job Match, Skill Gap, and Career Plan are required for the full PDF"
          }
        >
          <Download
            size={16}
          />

          Download PDF
        </button>

      </div>


      {/* ==================================================
          PDF ERROR
          ================================================== */}

      {reportError && (
        <div className="mt-5 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">

          <XCircle
            size={18}
            className="mt-0.5 shrink-0"
          />


          <div>

            <p className="font-semibold">
              Could not generate PDF
            </p>


            <p className="mt-1 leading-6">
              {reportError}
            </p>

          </div>

        </div>
      )}


      {/* ==================================================
          PAGE HEADER
          ================================================== */}

      <div className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">

        <div className="max-w-3xl">

          <p className="text-xs font-bold tracking-[0.14em] text-brand">
            SAVED ANALYSIS
          </p>


          <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
            {roleTitle}
          </h1>


          {companyName && (
            <p className="mt-2 text-sm font-semibold text-text-muted">
              {companyName}
            </p>
          )}


          <p className="mt-4 max-w-2xl leading-7 text-text-muted">
            Review the exact Job Match,
            Skill Gap, and Career Plan
            captured for this historical
            CareerPilot analysis.
          </p>

        </div>


        <MatchScore
          score={
            jobMatch?.match_score ??
            metadata?.match_score ??
            0
          }
        />

      </div>


      {/* ==================================================
          ANALYSIS META
          ================================================== */}

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <MetaCard
          icon={
            <FileText
              size={17}
            />
          }
          label="Resume"
          value={
            resumeFilename
          }
        />


        <MetaCard
          icon={
            <CalendarDays
              size={17}
            />
          }
          label="Analyzed"
          value={
            analyzedDate
          }
        />


        <MetaCard
          icon={
            <Gauge
              size={17}
            />
          }
          label="Job Match"
          value={
            jobMatch
              ? "Available"
              : "Unavailable"
          }
        />


        <MetaCard
          icon={
            <Route
              size={17}
            />
          }
          label="Career Plan"
          value={
            careerPlan
              ? "Available"
              : "Not generated"
          }
        />

      </div>


      {/* ==================================================
          JOB MATCH
          ================================================== */}

      {jobMatch && (
        <AnalysisSection
          eyebrow="JOB MATCH"
          title="How the resume matched the role"
          icon={
            <Gauge
              size={19}
            />
          }
        >

          <div className="grid gap-5 xl:grid-cols-3">

            <SkillListCard
              title="Strong Matches"
              items={
                jobMatch
                  .strong_matches
              }
              tone="success"
            />


            <SkillListCard
              title="Partial Matches"
              items={
                jobMatch
                  .partial_matches
              }
              tone="warning"
            />


            <SkillListCard
              title="Missing Skills"
              items={
                jobMatch
                  .missing_skills
              }
              tone="danger"
            />

          </div>


          {hasItems(
            jobMatch
              .priority_actions
          ) && (
            <NumberedSection
              title="Priority Actions"
              items={
                jobMatch
                  .priority_actions
              }
            />
          )}


          {hasItems(
            jobMatch
              .resume_improvements
          ) && (
            <ChecklistSection
              title="Resume Improvements"
              items={
                jobMatch
                  .resume_improvements
              }
            />
          )}

        </AnalysisSection>
      )}


      {/* ==================================================
          SKILL GAP
          ================================================== */}

      {skillGap && (
        <AnalysisSection
          eyebrow="SKILL GAP"
          title="Skills worth strengthening next"
          icon={
            <Sparkles
              size={19}
            />
          }
        >

          <div className="grid gap-5 xl:grid-cols-3">

            <SkillListCard
              title="High Priority"
              items={
                skillGap
                  .high_priority_gaps
              }
              tone="danger"
            />


            <SkillListCard
              title="Medium Priority"
              items={
                skillGap
                  .medium_priority_gaps
              }
              tone="warning"
            />


            <SkillListCard
              title="Low Priority"
              items={
                skillGap
                  .low_priority_gaps
              }
              tone="neutral"
            />

          </div>


          {hasItems(
            skillGap
              .recommended_learning_order
          ) && (
            <NumberedSection
              title="Recommended Learning Order"
              items={
                skillGap
                  .recommended_learning_order
              }
            />
          )}


          {hasItems(
            skillGap
              .practice_tasks
          ) && (
            <ChecklistSection
              title="Practice Tasks"
              items={
                skillGap
                  .practice_tasks
              }
            />
          )}


          {hasItems(
            skillGap
              .proof_of_skill_actions
          ) && (
            <ChecklistSection
              title="Proof of Skill"
              items={
                skillGap
                  .proof_of_skill_actions
              }
            />
          )}


          {hasItems(
            skillGap
              .portfolio_project_prompts
          ) && (
            <PortfolioProjects
              projects={
                skillGap
                  .portfolio_project_prompts
              }
            />
          )}


          {skillGap
            .readiness_summary && (
            <SummaryCard
              title="Skill Gap Readiness Summary"
              text={
                skillGap
                  .readiness_summary
              }
            />
          )}

        </AnalysisSection>
      )}


      {/* ==================================================
          CAREER PLAN
          ================================================== */}

      {careerPlan ? (
        <AnalysisSection
          eyebrow="CAREER PLAN"
          title="The saved preparation roadmap"
          icon={
            <Route
              size={19}
            />
          }
        >

          {careerPlan
            .readiness_summary && (
            <SummaryCard
              title="Readiness Summary"
              text={
                careerPlan
                  .readiness_summary
              }
            />
          )}


          {hasItems(
            careerPlan
              .top_priorities
          ) && (
            <ChecklistSection
              title="Top Priorities"
              items={
                careerPlan
                  .top_priorities
              }
            />
          )}


          {hasItems(
            careerPlan
              .recommended_learning_order
          ) && (
            <NumberedSection
              title="Learning Order"
              items={
                careerPlan
                  .recommended_learning_order
              }
            />
          )}


          {hasItems(
            careerPlan
              .practical_tasks
          ) && (
            <ChecklistSection
              title="Practical Tasks"
              items={
                careerPlan
                  .practical_tasks
              }
            />
          )}


          {hasItems(
            careerPlan
              .portfolio_evidence
          ) && (
            <ChecklistSection
              title="Portfolio Evidence"
              items={
                careerPlan
                  .portfolio_evidence
              }
            />
          )}


          {hasItems(
            careerPlan
              .interview_preparation_focus
          ) && (
            <ChecklistSection
              title="Interview Preparation"
              items={
                careerPlan
                  .interview_preparation_focus
              }
            />
          )}


          {hasItems(
            careerPlan
              .action_plan_30_days
          ) && (
            <RoadmapSection
              items={
                careerPlan
                  .action_plan_30_days
              }
            />
          )}

        </AnalysisSection>
      ) : (
        <div className="mt-8 rounded-2xl border border-dashed border-border-soft bg-white p-8 text-center">

          <Route
            size={24}
            className="mx-auto text-gray-300"
          />


          <h3 className="mt-4 font-semibold text-midnight">
            No Career Plan was saved
          </h3>


          <p className="mt-2 text-sm leading-6 text-text-muted">
            This historical analysis was
            completed before a Career Plan
            was generated.
          </p>

        </div>
      )}

    </section>
  );
}


/* ==================================================
   BACK BUTTON
   ================================================== */

function BackButton({
  onClick,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-2 text-sm font-semibold text-text-muted transition hover:text-brand"
    >
      <ArrowLeft
        size={16}
      />

      Back to history
    </button>
  );
}


/* ==================================================
   MATCH SCORE
   ================================================== */

function MatchScore({
  score,
}) {
  return (
    <div className="flex w-fit items-center gap-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4">

      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white shadow-sm">

        <span className="text-xl font-bold text-brand">
          {score}
        </span>

      </div>


      <div>

        <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-brand">
          Match Score
        </p>


        <p className="mt-1 text-sm font-semibold text-midnight">
          {score}/100
        </p>

      </div>

    </div>
  );
}


/* ==================================================
   META CARD
   ================================================== */

function MetaCard({
  icon,
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-border-soft bg-white p-4 shadow-sm">

      <div className="flex gap-3">

        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
          {icon}
        </div>


        <div className="min-w-0">

          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-text-muted">
            {label}
          </p>


          <p
            title={value}
            className="mt-1 truncate text-sm font-semibold text-midnight"
          >
            {value}
          </p>

        </div>

      </div>

    </div>
  );
}


/* ==================================================
   ANALYSIS SECTION
   ================================================== */

function AnalysisSection({
  eyebrow,
  title,
  icon,
  children,
}) {
  return (
    <section className="mt-8 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-7">

      <div className="flex items-start gap-3">

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
          {icon}
        </div>


        <div>

          <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
            {eyebrow}
          </p>


          <h2 className="mt-1 text-xl font-semibold tracking-tight text-midnight">
            {title}
          </h2>

        </div>

      </div>


      <div className="mt-7 space-y-7">
        {children}
      </div>

    </section>
  );
}


/* ==================================================
   SKILL LIST CARD
   ================================================== */

function SkillListCard({
  title,
  items,
  tone,
}) {
  const values =
    Array.isArray(items)
      ? items
      : [];


  const styles = {
    success: {
      title:
        "text-brand",

      pill:
        "border-emerald-100 bg-emerald-50 text-emerald-700",
    },

    warning: {
      title:
        "text-amber-600",

      pill:
        "border-amber-100 bg-amber-50 text-amber-700",
    },

    danger: {
      title:
        "text-red-500",

      pill:
        "border-red-100 bg-red-50 text-red-600",
    },

    neutral: {
      title:
        "text-text-muted",

      pill:
        "border-border-soft bg-app-bg text-text-muted",
    },
  };


  const selected =
    styles[tone] ||
    styles.neutral;


  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-5">

      <p
        className={`text-[11px] font-bold uppercase tracking-[0.13em] ${selected.title}`}
      >
        {title}
      </p>


      {values.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">

          {values.map(
            (
              value,
              index
            ) => (
              <span
                key={`${value}-${index}`}
                className={`rounded-full border px-2.5 py-1 text-xs font-medium ${selected.pill}`}
              >
                {value}
              </span>
            )
          )}

        </div>
      ) : (
        <p className="mt-3 text-sm text-text-muted">
          None recorded.
        </p>
      )}

    </div>
  );
}


/* ==================================================
   NUMBERED SECTION
   ================================================== */

function NumberedSection({
  title,
  items,
}) {
  return (
    <ContentBlock
      title={title}
    >

      <div className="space-y-3">

        {items.map(
          (
            item,
            index
          ) => (
            <div
              key={`${item}-${index}`}
              className="flex gap-3 rounded-xl border border-border-soft bg-app-bg p-4"
            >

              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
                {String(
                  index + 1
                ).padStart(
                  2,
                  "0"
                )}
              </div>


              <p className="pt-1 text-sm leading-6 text-text-muted">
                {item}
              </p>

            </div>
          )
        )}

      </div>

    </ContentBlock>
  );
}


/* ==================================================
   CHECKLIST SECTION
   ================================================== */

function ChecklistSection({
  title,
  items,
}) {
  return (
    <ContentBlock
      title={title}
    >

      <div className="space-y-3">

        {items.map(
          (
            item,
            index
          ) => (
            <div
              key={`${item}-${index}`}
              className="flex gap-3"
            >

              <CheckCircle2
                size={17}
                className="mt-1 shrink-0 text-brand"
              />


              <p className="text-sm leading-7 text-text-muted">
                {item}
              </p>

            </div>
          )
        )}

      </div>

    </ContentBlock>
  );
}


/* ==================================================
   SUMMARY CARD
   ================================================== */

function SummaryCard({
  title,
  text,
}) {
  return (
    <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-5">

      <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-brand">
        {title}
      </p>


      <p className="mt-3 text-sm leading-7 text-text-muted">
        {text}
      </p>

    </div>
  );
}


/* ==================================================
   PORTFOLIO PROJECTS
   ================================================== */

function PortfolioProjects({
  projects,
}) {
  return (
    <ContentBlock
      title="Portfolio Project Ideas"
    >

      <div className="grid gap-4 xl:grid-cols-2">

        {projects.map(
          (
            project,
            index
          ) => (
            <article
              key={
                project.project_title ||
                index
              }
              className="rounded-xl border border-border-soft bg-app-bg p-5"
            >

              <div className="flex items-center gap-2 text-brand">

                <Target
                  size={15}
                />


                <p className="text-[10px] font-bold uppercase tracking-[0.13em]">
                  {project.target_skill ||
                    "Portfolio Evidence"}
                </p>

              </div>


              <h4 className="mt-3 font-semibold text-midnight">
                {project.project_title ||
                  "Recommended Project"}
              </h4>


              {project.project_goal && (
                <p className="mt-2 text-sm leading-6 text-text-muted">
                  {project.project_goal}
                </p>
              )}


              {hasItems(
                project.suggested_stack
              ) && (
                <div className="mt-4 flex flex-wrap gap-2">

                  {project.suggested_stack.map(
                    (
                      technology,
                      technologyIndex
                    ) => (
                      <span
                        key={`${technology}-${technologyIndex}`}
                        className="rounded-full border border-border-soft bg-white px-2.5 py-1 text-[11px] font-medium text-midnight"
                      >
                        {technology}
                      </span>
                    )
                  )}

                </div>
              )}

            </article>
          )
        )}

      </div>

    </ContentBlock>
  );
}


/* ==================================================
   30-DAY ROADMAP
   ================================================== */

function RoadmapSection({
  items,
}) {
  return (
    <ContentBlock
      title="30-Day Action Plan"
    >

      <div className="grid gap-4 md:grid-cols-2">

        {items.map(
          (
            item,
            index
          ) => (
            <div
              key={`${item}-${index}`}
              className="rounded-xl border border-border-soft bg-app-bg p-5"
            >

              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-brand">
                Step {index + 1}
              </p>


              <p className="mt-2 text-sm leading-7 text-text-muted">
                {item}
              </p>

            </div>
          )
        )}

      </div>

    </ContentBlock>
  );
}


/* ==================================================
   CONTENT BLOCK
   ================================================== */

function ContentBlock({
  title,
  children,
}) {
  return (
    <section>

      <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-brand">
        {title}
      </p>


      <div className="mt-4">
        {children}
      </div>

    </section>
  );
}


/* ==================================================
   STORAGE
   ================================================== */

function getStoredHistoryMetadata() {
  const stored =
    localStorage.getItem(
      "careerpilot_selected_history"
    );


  if (!stored) {
    return null;
  }


  try {
    return JSON.parse(
      stored
    );

  } catch {
    return null;
  }
}


/* ==================================================
   HELPERS
   ================================================== */

function hasItems(value) {
  return (
    Array.isArray(value) &&
    value.length > 0
  );
}


function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }


  const date =
    new Date(value);


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "Unknown date";
  }


  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day:
        "2-digit",

      month:
        "short",

      year:
        "numeric",
    }
  ).format(date);
}


export default HistoryDetail;