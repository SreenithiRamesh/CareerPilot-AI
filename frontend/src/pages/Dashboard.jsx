import {
  ArrowRight,
  CheckCircle2,
  Circle,
  FileText,
  Gauge,
  MessageSquare,
  Route,
  Sparkles,
} from "lucide-react";

import { useNavigate } from "react-router-dom";


/* =========================================================
   Local storage readers
   These read the SAME keys already written by Resume.jsx,
   JobMatch.jsx, SkillGap.jsx and CareerPlan.jsx.
   No keys are renamed or invented here.
   ========================================================= */

function readJSON(key) {
  const stored = localStorage.getItem(key);

  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}


function getActiveResume() {
  return readJSON("careerpilot_active_resume");
}


function getLatestJobMatch() {
  return readJSON("careerpilot_latest_job_match");
}


function getLatestSkillGap() {
  return readJSON("careerpilot_latest_skill_gap");
}


function getLatestCareerPlan() {
  return readJSON("careerpilot_latest_career_plan");
}


/*
  NOTE: the exact field name used for the job-match score has
  not been confirmed yet (JobMatch.jsx was not available when
  this file was written). This checks a few likely field names
  and simply omits the score if none are present, rather than
  guessing a number.
*/
function getMatchScore(latestJobMatch) {
  if (!latestJobMatch) {
    return null;
  }

  const candidate =
    latestJobMatch.match_score ??
    latestJobMatch.score ??
    latestJobMatch.overall_score ??
    null;

  return typeof candidate === "number" ? candidate : null;
}


function Dashboard() {
  const navigate = useNavigate();

  const activeResume = getActiveResume();
  const latestJobMatch = getLatestJobMatch();
  const latestSkillGap = getLatestSkillGap();
  const latestCareerPlan = getLatestCareerPlan();

  const matchScore = getMatchScore(latestJobMatch);

  /* ================= WORKFLOW STAGES ================= */

  const stages = [
    {
      key: "resume",
      label: "Resume",
      route: "/resume",
      done: Boolean(activeResume),
    },
    {
      key: "job-match",
      label: "Job Match",
      route: "/job-match",
      done: Boolean(latestJobMatch),
    },
    {
      key: "skill-gap",
      label: "Skill Gap",
      route: "/skill-gap",
      done: Boolean(latestSkillGap),
    },
    {
      key: "career-plan",
      label: "Career Plan",
      route: "/career-plan",
      done: Boolean(latestCareerPlan),
    },
  ];

  const currentStageIndex = stages.findIndex((stage) => !stage.done);

  const activeStage =
    currentStageIndex === -1
      ? stages[stages.length - 1]
      : stages[currentStageIndex];

  const allComplete = currentStageIndex === -1;

  /* ================= NEXT BEST STEP COPY ================= */

  const nextStepCopy = {
    resume: {
      heading: "Start with your resume.",
      body: "CareerPilot uses your selected resume as the evidence base for role matching, skill-gap analysis, and personalized career planning.",
      cta: "Go to resume",
      route: "/resume",
    },
    "job-match": {
      heading: "Run your first Job Match.",
      body: "Compare your resume against a target job description to see strong matches, partial matches, and priority gaps.",
      cta: "Run job match",
      route: "/job-match",
    },
    "skill-gap": {
      heading: "Identify your skill gaps.",
      body: "CareerPilot will use your latest Job Match to prioritize the skills worth focusing on next.",
      cta: "Analyze skill gaps",
      route: "/skill-gap",
    },
    "career-plan": {
      heading: "Build your career plan.",
      body: "Turn your resume, Job Match, and Skill Gap analysis into a focused 30-day preparation roadmap.",
      cta: "Generate career plan",
      route: "/career-plan",
    },
  };

  const nextStep = allComplete
    ? {
        heading: "Your workspace is fully analyzed.",
        body: "Revisit any stage to refine your analysis, or ask Career AI for guidance on your next move.",
        cta: "Ask Career AI",
        route: "/career-ai",
      }
    : nextStepCopy[activeStage.key];

  /* ================= STATUS TEXT ================= */

  function resumeStatusText() {
    return activeResume
      ? "Uploaded and ready"
      : "Not uploaded yet";
  }

  function jobMatchStatusText() {
    if (!latestJobMatch) {
      return "Not started";
    }

    return matchScore !== null
      ? `${matchScore}/100 match score`
      : "Analysis complete";
  }

  function skillGapStatusText() {
    if (!latestSkillGap) {
      return "Not started";
    }

    const highPriorityCount =
      latestSkillGap.high_priority_gaps?.length || 0;

    return highPriorityCount > 0
      ? `${highPriorityCount} high-priority gap${
          highPriorityCount === 1 ? "" : "s"
        }`
      : "Analysis complete";
  }

  function careerPlanStatusText() {
    return latestCareerPlan
      ? "Plan generated"
      : "Not generated yet";
  }

  const hasAnyAnalysis =
    Boolean(latestJobMatch) ||
    Boolean(latestSkillGap) ||
    Boolean(latestCareerPlan);

  /* ================= TOP NEXT ACTION (for latest analysis panel) ================= */

  const topNextAction =
    latestCareerPlan?.top_priorities?.[0] ||
    latestSkillGap?.recommended_learning_order?.[0] ||
    (activeStage ? nextStepCopy[activeStage.key]?.body : null);


  return (
    <section>

      {/* ================= WELCOME ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.15em] text-brand">
          DASHBOARD
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Welcome back to CareerPilot.
        </h1>

        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          {allComplete
            ? "Every stage of your workspace has been analyzed. Revisit any stage to refine it, or check your latest results below."
            : "Continue from your resume, compare your profile against a target role, review skill gaps, or turn your analysis into a focused preparation plan."}
        </p>

      </div>


      {/* ================= WORKFLOW PROGRESS ================= */}

      <div className="mt-8 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-7">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          WORKFLOW
        </p>

        <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-0">

          {stages.map((stage, index) => {
            const isDone = stage.done;
            const isCurrent = index === currentStageIndex;

            return (
              <div
                key={stage.key}
                className="flex flex-1 items-center gap-3"
              >

                <button
                  type="button"
                  onClick={() => navigate(stage.route)}
                  className="flex items-center gap-2.5 text-left"
                >

                  {isDone ? (
                    <CheckCircle2
                      size={20}
                      className="shrink-0 text-brand"
                    />
                  ) : (
                    <Circle
                      size={20}
                      className={`shrink-0 ${
                        isCurrent
                          ? "text-brand"
                          : "text-gray-300"
                      }`}
                    />
                  )}

                  <span
                    className={`text-sm font-semibold ${
                      isDone || isCurrent
                        ? "text-midnight"
                        : "text-text-muted"
                    }`}
                  >
                    {stage.label}
                  </span>

                </button>

                {index < stages.length - 1 && (
                  <div className="hidden h-px flex-1 bg-border-soft sm:mx-4 sm:block" />
                )}

              </div>
            );
          })}

        </div>

      </div>


      {/* ================= QUICK ACTIONS ================= */}

      <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

        <DashboardCard
          icon={<FileText size={21} />}
          label="RESUME"
          title="Upload or review resume"
          description="Use your latest resume as the evidence base for CareerPilot analysis."
          action={activeResume ? "Update resume" : "Upload resume"}
          onClick={() => navigate("/resume")}
        />


        <DashboardCard
          icon={<Gauge size={21} />}
          label="JOB MATCH"
          title="Compare with a target role"
          description="Review strong matches, partial matches, missing requirements, and priority actions."
          action={latestJobMatch ? "Review job match" : "Run job match"}
          onClick={() => navigate("/job-match")}
        />


        <DashboardCard
          icon={<Sparkles size={21} />}
          label="SKILL GAP"
          title="Focus your learning"
          description="Identify the highest-priority gaps for the role you want to target."
          action={latestSkillGap ? "Review skill gaps" : "View skill gaps"}
          onClick={() => navigate("/skill-gap")}
        />


        <DashboardCard
          icon={<Route size={21} />}
          label="CAREER PLAN"
          title="Build your next-step plan"
          description="Turn your analysis into practical learning, portfolio, and interview-preparation actions."
          action={latestCareerPlan ? "Review career plan" : "Open career plan"}
          onClick={() => navigate("/career-plan")}
        />

      </div>


      {/* ================= WORKSPACE STATUS ================= */}

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">

        <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-7">

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

            <div>
              <p className="text-xs font-bold tracking-[0.14em] text-brand">
                CAREER READINESS
              </p>

              <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                Your CareerPilot workspace
              </h2>
            </div>


            <span
              className={`w-fit rounded-full px-3 py-1.5 text-xs font-semibold ${
                allComplete
                  ? "bg-brand-soft text-brand"
                  : "bg-app-bg text-text-muted"
              }`}
            >
              {allComplete ? "Fully analyzed" : "In progress"}
            </span>

          </div>


          <div className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatusItem
              title="Resume"
              value={resumeStatusText()}
              done={Boolean(activeResume)}
            />

            <StatusItem
              title="Job match"
              value={jobMatchStatusText()}
              done={Boolean(latestJobMatch)}
            />

            <StatusItem
              title="Skill gap"
              value={skillGapStatusText()}
              done={Boolean(latestSkillGap)}
            />

            <StatusItem
              title="Career plan"
              value={careerPlanStatusText()}
              done={Boolean(latestCareerPlan)}
            />

          </div>

        </section>


        {/* ================= NEXT BEST STEP ================= */}

        <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-7">

          <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
            NEXT BEST STEP
          </p>

          <h2 className="mt-3 text-2xl font-semibold tracking-tight">
            {nextStep.heading}
          </h2>

          <p className="mt-4 leading-7 text-gray-300">
            {nextStep.body}
          </p>


          <button
            type="button"
            onClick={() => navigate(nextStep.route)}
            className="mt-6 inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover"
          >
            {nextStep.cta}

            <ArrowRight size={16} />
          </button>

        </section>

      </div>


      {/* ================= LATEST ANALYSIS ================= */}

      <div className="mt-8 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          LATEST ANALYSIS
        </p>

        {hasAnyAnalysis ? (
          <>

            <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
              Where things stand right now
            </h2>


            <div className="mt-6 grid gap-5 md:grid-cols-3">

              {matchScore !== null && (
                <AnalysisTile
                  label="Latest match score"
                  value={`${matchScore}/100`}
                />
              )}

              {latestSkillGap?.existing_skills?.length > 0 && (
                <AnalysisListTile
                  label="Strongest matching skills"
                  items={latestSkillGap.existing_skills.slice(0, 3)}
                  tone="success"
                />
              )}

              {latestSkillGap?.high_priority_gaps?.length > 0 && (
                <AnalysisListTile
                  label="Highest-priority gaps"
                  items={latestSkillGap.high_priority_gaps.slice(0, 3)}
                  tone="danger"
                />
              )}

            </div>


            {topNextAction && (
              <div className="mt-6 flex gap-4 rounded-xl border border-border-soft bg-app-bg p-5">

                <ArrowRight
                  size={18}
                  className="mt-0.5 shrink-0 text-brand"
                />

                <div>
                  <p className="text-xs font-bold tracking-[0.12em] text-brand">
                    TOP NEXT ACTION
                  </p>

                  <p className="mt-1.5 text-sm leading-6 text-text-muted">
                    {topNextAction}
                  </p>
                </div>

              </div>
            )}

          </>
        ) : (

          /* ================= EMPTY STATE ================= */

          <div className="mt-6 flex flex-col items-center rounded-xl border border-dashed border-border-soft bg-app-bg px-6 py-12 text-center">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-soft text-brand">
              <FileText size={22} />
            </div>

            <h3 className="mt-4 text-lg font-semibold tracking-tight text-midnight">
              No analysis yet
            </h3>

            <p className="mt-2 max-w-md text-sm leading-6 text-text-muted">
              Upload a resume to unlock Job Match, Skill Gap, and
              Career Plan analysis for your target role.
            </p>

            <button
              type="button"
              onClick={() => navigate("/resume")}
              className="mt-6 inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover"
            >
              Upload resume

              <ArrowRight size={16} />
            </button>

          </div>
        )}

      </div>


      {/* ================= ASK CAREER AI ================= */}

      <div className="mt-8 flex flex-col items-start justify-between gap-4 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:p-7">

        <div className="flex items-start gap-4">

          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
            <MessageSquare size={21} />
          </div>

          <div>
            <h3 className="font-semibold tracking-tight text-midnight">
              Have a specific question?
            </h3>

            <p className="mt-1.5 text-sm leading-6 text-text-muted">
              Ask Career AI about your resume, target role, or
              preparation plan directly.
            </p>
          </div>

        </div>


        <button
          type="button"
          onClick={() => navigate("/career-ai")}
          className="inline-flex h-11 shrink-0 items-center gap-2 rounded-lg border border-border-soft px-4 text-sm font-semibold text-midnight transition hover:border-emerald-200 hover:text-brand"
        >
          Ask Career AI

          <ArrowRight size={16} />
        </button>

      </div>

    </section>
  );
}


function DashboardCard({
  icon,
  label,
  title,
  description,
  action,
  onClick,
}) {
  return (
    <article className="group flex h-full flex-col rounded-2xl border border-border-soft bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-950/5">

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand">
        {icon}
      </div>


      <p className="mt-6 text-[11px] font-bold tracking-[0.14em] text-brand">
        {label}
      </p>


      <h3 className="mt-2 text-lg font-semibold tracking-tight text-midnight">
        {title}
      </h3>


      <p className="mt-3 flex-1 text-sm leading-7 text-text-muted">
        {description}
      </p>


      <button
        type="button"
        onClick={onClick}
        className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand transition group-hover:text-brand-hover"
      >
        {action}

        <ArrowRight
          size={15}
          className="transition-transform group-hover:translate-x-1"
        />
      </button>

    </article>
  );
}


function StatusItem({
  title,
  value,
  done,
}) {
  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-4">

      <div className="flex items-center justify-between">

        <p className="text-xs font-medium text-text-muted">
          {title}
        </p>

        {done && (
          <CheckCircle2
            size={14}
            className="text-brand"
          />
        )}

      </div>

      <p className="mt-2 text-sm font-semibold text-midnight">
        {value}
      </p>

    </div>
  );
}


function AnalysisTile({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-5">

      <p className="text-xs font-medium text-text-muted">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold tracking-tight text-midnight">
        {value}
      </p>

    </div>
  );
}


function AnalysisListTile({
  label,
  items,
  tone,
}) {
  const dotClasses = {
    success: "text-brand",
    danger: "text-red-500",
  };

  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-5">

      <p className="text-xs font-medium text-text-muted">
        {label}
      </p>

      <ul className="mt-3 space-y-2">

        {items.map((item, index) => (
          <li
            key={`${item}-${index}`}
            className="flex items-start gap-2 text-sm leading-6 text-midnight"
          >

            <span
              className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-current ${
                dotClasses[tone] || "text-brand"
              }`}
            />

            <span>{item}</span>

          </li>
        ))}

      </ul>

    </div>
  );
}


export default Dashboard;