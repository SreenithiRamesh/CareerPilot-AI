import {
  useRef,
  useState,
} from "react";

import {
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ClipboardList,
  Download,
  LoaderCircle,
  Route,
  Sparkles,
  Target,
  XCircle,
} from "lucide-react";

import api from "../services/api";

import {
  completeChatRequest,
  getChatErrorMessage,
  getRetryableChatRequestId,
} from "../utils/chatRequest";

import {
  generateCareerReadinessReport,
} from "../utils/careerReportExport";


function readJSON(key) {
  const stored =
    localStorage.getItem(key);

  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored);

  } catch {
    return null;
  }
}


function CareerPlan() {
  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [reportError, setReportError] =
    useState("");

  const [plan, setPlan] =
    useState(null);

  const [planId, setPlanId] =
    useState(null);

  const pendingRequestRef =
    useRef(null);

  const [
    checkedItems,
    setCheckedItems,
  ] = useState({});

  const [
    activeWeek,
    setActiveWeek,
  ] = useState(0);


  function getActiveResume() {
    return readJSON(
      "careerpilot_active_resume"
    );
  }


  function getLatestJobMatch() {
    return readJSON(
      "careerpilot_latest_job_match"
    );
  }


  function getLatestSkillGap() {
    return readJSON(
      "careerpilot_latest_skill_gap"
    );
  }


  /* ================= CHECKLIST PERSISTENCE ================= */

  function checklistKey(id) {
    return `careerpilot_career_plan_checklist_${id}`;
  }


  function toggleChecklistItem(
    itemKey
  ) {
    setCheckedItems(
      (prev) => {
        const next = {
          ...prev,

          [itemKey]:
            !prev[itemKey],
        };


        if (planId) {
          localStorage.setItem(
            checklistKey(
              planId
            ),
            JSON.stringify(
              next
            )
          );
        }


        return next;
      }
    );
  }


  /* ================= GENERATE PLAN ================= */

  async function handleGeneratePlan() {
    setError("");
    setReportError("");
    setPlan(null);
    setCheckedItems({});
    setActiveWeek(0);


    const activeResume =
      getActiveResume();

    const latestJobMatch =
      getLatestJobMatch();

    const latestSkillGap =
      getLatestSkillGap();


    if (!activeResume) {
      setError(
        "Upload a resume before generating a career plan."
      );

      return;
    }


    if (
      !latestJobMatch?.job_description
    ) {
      setError(
        "Run a Job Match first so CareerPilot can build a role-specific career plan."
      );

      return;
    }


    if (
      latestJobMatch.resume_id &&
      String(
        latestJobMatch.resume_id
      ) !==
        String(
          activeResume.resume_id
        )
    ) {
      setError(
        "Your latest Job Match was created using a different resume. Run Job Match again before generating a career plan."
      );

      return;
    }


    if (!latestSkillGap) {
      setError(
        "Run a Skill Gap analysis before generating your career plan."
      );

      return;
    }


    if (
      latestSkillGap.resume_id &&
      String(
        latestSkillGap.resume_id
      ) !==
        String(
          activeResume.resume_id
        )
    ) {
      setError(
        "Your latest Skill Gap analysis was created using a different resume. Run Skill Gap again before generating a career plan."
      );

      return;
    }


    if (
      latestSkillGap.job_match_result_id &&
      latestJobMatch.job_match_result_id &&
      String(
        latestSkillGap.job_match_result_id
      ) !==
        String(
          latestJobMatch.job_match_result_id
        )
    ) {
      setError(
        "Your Skill Gap analysis belongs to a different Job Match. Run Skill Gap again before generating your career plan."
      );

      return;
    }


    const requestFingerprint =
      JSON.stringify({
        threadId:
          activeResume.thread_id,
        resumeId:
          activeResume.resume_id,
        jobMatchResultId:
          latestJobMatch.job_match_result_id ??
          null,
        skillGapReportId:
          latestSkillGap.skill_gap_report_id ??
          null,
      });

    const requestId =
      getRetryableChatRequestId(
        pendingRequestRef,
        requestFingerprint
      );

    setLoading(true);


    try {
      const response =
        await api.post(
          "/api/chat",
          {
            request_id:
              requestId,

            thread_id:
              activeResume.thread_id,

            resume_id:
              activeResume.resume_id,

            message:
              "Analyze my readiness and create a career plan for this role.",

            target_role:
              "Software Engineer",

            job_description:
              latestJobMatch.job_description,

            skills: [],

            history: [],
          }
        );


      if (
        response.data.intent !==
        "career_plan"
      ) {
        throw new Error(
          "Unexpected CareerPilot response."
        );
      }


      if (
        !response.data.data
      ) {
        throw new Error(
          "Career plan was not returned."
        );
      }


      setPlan(
        response.data.data
      );

      const newPlanId =
        response.data
          .career_plan_id;


      setPlanId(
        newPlanId
      );


      setCheckedItems(
        (
          newPlanId &&
          readJSON(
            checklistKey(
              newPlanId
            )
          )
        ) || {}
      );


      /*
       * Persist complete provenance chain:
       *
       * Resume
       * -> Job Match
       * -> Skill Gap
       * -> Career Plan
       */

      localStorage.setItem(
        "careerpilot_latest_career_plan",
        JSON.stringify({
          ...response.data.data,

          resume_id:
            activeResume.resume_id,

          thread_id:
            activeResume.thread_id,

          job_description:
            latestJobMatch.job_description,

          job_description_id:
            latestJobMatch.job_description_id,

          job_match_result_id:
            response.data
              .job_match_result_id ||
            latestJobMatch
              .job_match_result_id,

          skill_gap_report_id:
            response.data
              .skill_gap_report_id ||
            latestSkillGap
              .skill_gap_report_id,

          career_plan_id:
            response.data
              .career_plan_id,
        })
      );

      completeChatRequest(
        pendingRequestRef,
        requestId
      );

    } catch (err) {
      setError(
        getChatErrorMessage(
          err,
          "CareerPilot could not generate your career plan."
        )
      );

    } finally {
      setLoading(false);
    }
  }


  /* ================= DOWNLOAD FULL REPORT ================= */

  function handleDownloadReport() {
    setReportError("");


    const result =
      generateCareerReadinessReport();


    if (!result.success) {
      setReportError(
        result.reasons.join(
          " "
        )
      );
    }
  }


  /* ================= DERIVED DATA ================= */

  const checklistSections =
    plan
      ? [
          {
            key:
              "priorities",

            eyebrow:
              "TOP PRIORITIES",

            title:
              "What matters most",

            items:
              plan.top_priorities ||
              [],
          },
          {
            key:
              "learning",

            eyebrow:
              "LEARNING ORDER",

            title:
              "What to learn first",

            items:
              plan.recommended_learning_order ||
              [],
          },
          {
            key:
              "practical",

            eyebrow:
              "PRACTICAL TASKS",

            title:
              "Turn learning into evidence",

            items:
              plan.practical_tasks ||
              [],
          },
          {
            key:
              "portfolio",

            eyebrow:
              "PORTFOLIO EVIDENCE",

            title:
              "Make your progress visible",

            items:
              plan.portfolio_evidence ||
              [],
          },
          {
            key:
              "interview",

            eyebrow:
              "INTERVIEW PREPARATION",

            title:
              "What to be ready to explain",

            items:
              plan.interview_preparation_focus ||
              [],
          },
        ].filter(
          (section) =>
            section.items.length >
            0
        )
      : [];


  const actionDays =
    plan?.action_plan_30_days ||
    [];


  const weekCount =
    actionDays.length > 0
      ? 4
      : 0;


  const daysPerWeek =
    weekCount > 0
      ? Math.ceil(
          actionDays.length /
            weekCount
        )
      : 0;


  const weeks =
    Array.from(
      {
        length:
          weekCount,
      },
      (
        _,
        weekIndex
      ) => {
        const start =
          weekIndex *
          daysPerWeek;

        const end =
          start +
          daysPerWeek;


        return {
          label:
            `Week ${
              weekIndex + 1
            }`,

          items:
            actionDays
              .slice(
                start,
                end
              )
              .map(
                (
                  item,
                  index
                ) => ({
                  item,

                  index:
                    start +
                    index,
                })
              ),
        };
      }
    ).filter(
      (week) =>
        week.items.length >
        0
    );


  const totalChecklistItems =
    checklistSections.reduce(
      (
        sum,
        section
      ) =>
        sum +
        section.items.length,
      0
    ) +
    actionDays.length;


  const completedChecklistItems =
    checklistSections.reduce(
      (
        sum,
        section
      ) =>
        sum +
        section.items.filter(
          (
            _,
            index
          ) =>
            checkedItems[
              `${section.key}-${index}`
            ]
        ).length,
      0
    ) +
    actionDays.filter(
      (
        _,
        index
      ) =>
        checkedItems[
          `day-${index}`
        ]
    ).length;


  const overallProgress =
    totalChecklistItems > 0
      ? Math.round(
          (
            completedChecklistItems /
            totalChecklistItems
          ) *
            100
        )
      : 0;


  return (
    <section>

      {/* ================= HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          CAREER PLAN
        </p>


        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Turn analysis into a practical roadmap
        </h1>


        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          CareerPilot combines your resume, Job Match,
          and Skill Gap analysis to create a focused
          preparation plan for your target role.
        </p>

      </div>


      {/* ================= GENERATE PANEL ================= */}

      {!plan && (
        <div className="mt-10 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">

          <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

            <div className="flex items-start justify-between gap-4">

              <div>

                <p className="text-xs font-bold tracking-[0.12em] text-brand">
                  ROLE PREPARATION
                </p>


                <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                  Generate your career plan
                </h2>


                <p className="mt-2 text-sm leading-6 text-text-muted">
                  CareerPilot will reuse your latest
                  resume and target-role analysis automatically.
                </p>

              </div>


              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">

                <Route
                  size={21}
                />

              </div>

            </div>


            <div className="mt-7 rounded-2xl border border-border-soft bg-app-bg p-5">

              <div className="flex gap-4">

                <Target
                  size={20}
                  className="mt-0.5 shrink-0 text-brand"
                />


                <div>

                  <p className="font-semibold text-midnight">
                    Built from your existing analysis
                  </p>


                  <p className="mt-2 text-sm leading-6 text-text-muted">
                    No need to re-enter your resume
                    or job description.
                  </p>

                </div>

              </div>

            </div>


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


            <button
              type="button"
              onClick={
                handleGeneratePlan
              }
              disabled={
                loading
              }
              className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <>
                  <LoaderCircle
                    size={18}
                    className="animate-spin"
                  />

                  Building your plan...
                </>
              ) : (
                <>
                  <Route
                    size={18}
                  />

                  Generate career plan
                </>
              )}
            </button>

          </section>


          <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-8">

            <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
              WHAT YOU&apos;LL GET
            </p>


            <h2 className="mt-3 text-2xl font-semibold tracking-tight">
              A focused preparation roadmap.
            </h2>


            <p className="mt-4 leading-7 text-gray-300">
              The plan organizes your next steps
              around the highest-value gaps instead
              of giving you a long list of unrelated skills.
            </p>


            <div className="mt-8 space-y-5">

              <InfoStep
                icon={
                  <Sparkles
                    size={19}
                  />
                }
                title="Top priorities"
                description="The most important areas to improve first."
              />


              <InfoStep
                icon={
                  <ClipboardList
                    size={19}
                  />
                }
                title="Practical tasks"
                description="Concrete work that helps you build evidence, tracked as you complete it."
              />


              <InfoStep
                icon={
                  <BriefcaseBusiness
                    size={19}
                  />
                }
                title="Interview preparation"
                description="Focus areas aligned with the target role."
              />

            </div>

          </section>

        </div>
      )}


      {/* ================= PLAN RESULTS ================= */}

      {plan && (
        <section className="mt-10">

          {/* ================= READINESS ================= */}

          <div className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-8">

            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">

              <div>

                <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
                  READINESS SUMMARY
                </p>


                <h2 className="mt-3 text-2xl font-semibold tracking-tight">
                  Where you stand today
                </h2>


                <p className="mt-4 max-w-2xl leading-8 text-gray-300">
                  {plan.readiness_summary}
                </p>

              </div>


              {totalChecklistItems >
                0 && (
                <div className="w-full shrink-0 rounded-xl bg-white/5 p-4 sm:w-48">

                  <p className="text-xs font-medium text-gray-400">
                    Overall progress
                  </p>


                  <p className="mt-1 text-2xl font-bold tracking-tight">
                    {overallProgress}%
                  </p>


                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">

                    <div
                      className="h-full rounded-full bg-brand-accent transition-all"
                      style={{
                        width:
                          `${overallProgress}%`,
                      }}
                    />

                  </div>

                </div>
              )}

            </div>

          </div>


          {/* ================= CHECKLIST SECTIONS ================= */}

          {checklistSections.length >
            0 && (
            <div className="mt-6 grid gap-6 xl:grid-cols-2">

              {checklistSections.map(
                (section) => (
                  <ChecklistPanel
                    key={
                      section.key
                    }
                    eyebrow={
                      section.eyebrow
                    }
                    title={
                      section.title
                    }
                    items={
                      section.items
                    }
                    checkedItems={
                      checkedItems
                    }
                    sectionKey={
                      section.key
                    }
                    onToggle={
                      toggleChecklistItem
                    }
                  />
                )
              )}

            </div>
          )}


          {/* ================= 30 DAY PLAN ================= */}

          {weeks.length > 0 && (
            <div className="mt-6 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                <div>

                  <p className="text-xs font-bold tracking-[0.14em] text-brand">
                    30-DAY ACTION PLAN
                  </p>


                  <h2 className="mt-2 text-2xl font-semibold tracking-tight text-midnight">
                    Your next month, structured
                  </h2>

                </div>


                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">

                  <Route
                    size={21}
                  />

                </div>

              </div>


              {/* ================= WEEK TABS ================= */}

              <div className="mt-6 flex flex-wrap gap-2">

                {weeks.map(
                  (
                    week,
                    index
                  ) => (
                    <button
                      key={
                        week.label
                      }
                      type="button"
                      onClick={() =>
                        setActiveWeek(
                          index
                        )
                      }
                      className={`rounded-full px-4 py-2 text-xs font-semibold transition ${
                        activeWeek ===
                        index
                          ? "bg-midnight text-white"
                          : "border border-border-soft bg-white text-text-muted hover:border-emerald-200 hover:text-midnight"
                      }`}
                    >
                      {week.label}
                    </button>
                  )
                )}

              </div>


              {/* ================= WEEK ITEMS ================= */}

              <div className="mt-6 space-y-4">

                {(
                  weeks[
                    activeWeek
                  ]?.items ||
                  []
                ).map(
                  ({
                    item,
                    index,
                  }) => {

                    const itemKey =
                      `day-${index}`;


                    const isChecked =
                      Boolean(
                        checkedItems[
                          itemKey
                        ]
                      );


                    return (
                      <button
                        key={
                          itemKey
                        }
                        type="button"
                        onClick={() =>
                          toggleChecklistItem(
                            itemKey
                          )
                        }
                        className={`flex w-full items-start gap-4 rounded-2xl border p-5 text-left transition ${
                          isChecked
                            ? "border-emerald-200 bg-emerald-50/60"
                            : "border-border-soft bg-app-bg hover:border-emerald-200"
                        }`}
                      >

                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand text-sm font-bold text-white">
                          {isChecked ? (
                            <Check
                              size={16}
                            />
                          ) : (
                            index +
                            1
                          )}
                        </span>


                        <p
                          className={`pt-1 text-sm leading-7 ${
                            isChecked
                              ? "text-text-muted line-through"
                              : "text-text-muted"
                          }`}
                        >
                          {item}
                        </p>

                      </button>
                    );
                  }
                )}

              </div>

            </div>
          )}


          {/* ================= COMPLETION + PDF ================= */}

          <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 sm:p-8">

            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">

              <div className="flex items-start gap-4">

                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-emerald-600 shadow-sm">

                  <CheckCircle2
                    size={21}
                  />

                </div>


                <div>

                  <p className="font-semibold text-emerald-900">
                    Your CareerPilot roadmap is ready
                  </p>


                  <p className="mt-2 max-w-2xl text-sm leading-7 text-emerald-800">
                    Check off items as you complete them.
                    Your progress is saved automatically.
                    Download your consolidated Career
                    Readiness Report whenever you need a
                    clean copy of your analysis and roadmap.
                  </p>

                </div>

              </div>


              <button
                type="button"
                onClick={
                  handleDownloadReport
                }
                className="inline-flex h-11 shrink-0 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover focus:outline-none focus:ring-4 focus:ring-emerald-500/20"
              >
                <Download
                  size={16}
                />

                Download Full Report
              </button>

            </div>


            {reportError && (
              <div className="mt-5 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">

                <XCircle
                  size={18}
                  className="mt-0.5 shrink-0"
                />


                <span>
                  {reportError}
                </span>

              </div>
            )}

          </div>

        </section>
      )}

    </section>
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
   CHECKLIST PANEL
   ================================================== */

function ChecklistPanel({
  eyebrow,
  title,
  items = [],
  checkedItems,
  sectionKey,
  onToggle,
}) {
  const doneCount =
    items.filter(
      (
        _,
        index
      ) =>
        checkedItems[
          `${sectionKey}-${index}`
        ]
    ).length;


  return (
    <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

      <div className="flex items-center justify-between">

        <div>

          <p className="text-xs font-bold tracking-[0.14em] text-brand">
            {eyebrow}
          </p>


          <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
            {title}
          </h2>

        </div>


        <span className="rounded-full bg-app-bg px-2.5 py-1 text-xs font-semibold text-text-muted">
          {doneCount}/{items.length}
        </span>

      </div>


      <div className="mt-6 space-y-3">

        {items.map(
          (
            item,
            index
          ) => {

            const itemKey =
              `${sectionKey}-${index}`;


            const isChecked =
              Boolean(
                checkedItems[
                  itemKey
                ]
              );


            return (
              <button
                key={
                  itemKey
                }
                type="button"
                onClick={() =>
                  onToggle(
                    itemKey
                  )
                }
                className={`flex w-full items-start gap-3 rounded-xl border p-4 text-left transition ${
                  isChecked
                    ? "border-emerald-200 bg-emerald-50/60"
                    : "border-transparent bg-app-bg hover:border-emerald-200"
                }`}
              >

                <span
                  className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border ${
                    isChecked
                      ? "border-brand bg-brand text-white"
                      : "border-gray-300 bg-white"
                  }`}
                >
                  {isChecked && (
                    <Check
                      size={13}
                    />
                  )}
                </span>


                <p
                  className={`text-sm leading-7 ${
                    isChecked
                      ? "text-text-muted line-through"
                      : "text-text-muted"
                  }`}
                >
                  {item}
                </p>

              </button>
            );
          }
        )}

      </div>

    </section>
  );
}


export default CareerPlan;
