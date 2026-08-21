


import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  Code2,
  LoaderCircle,
  MessageSquareText,
  Sparkles,
  Target,
  XCircle,
} from "lucide-react";

import api from "../services/api";


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


function SkillGap() {
  const navigate =
    useNavigate();

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [analysis, setAnalysis] =
    useState(null);

  const [reportId, setReportId] =
    useState(null);

  const [
    checkedItems,
    setCheckedItems,
  ] = useState({});

  const [
    priorityFilter,
    setPriorityFilter,
  ] = useState("all");

  const [
    expandedCards,
    setExpandedCards,
  ] = useState({});


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


  /* ================= CHECKLIST PERSISTENCE ================= */

  function checklistKey(id) {
    return `careerpilot_skill_gap_checklist_${id}`;
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


        if (reportId) {
          localStorage.setItem(
            checklistKey(
              reportId
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


  /* ================= ANALYZE ================= */

  async function handleAnalyze() {
    setError("");
    setAnalysis(null);
    setCheckedItems({});
    setPriorityFilter("all");
    setExpandedCards({});


    const activeResume =
      getActiveResume();

    const latestJobMatch =
      getLatestJobMatch();


    if (!activeResume) {
      setError(
        "Upload a resume before running a skill-gap analysis."
      );

      return;
    }


    if (
      !latestJobMatch?.job_description
    ) {
      setError(
        "Run a Job Match first so CareerPilot can identify role-specific skill gaps."
      );

      return;
    }


    /*
     * Data-integrity safeguard:
     *
     * Skill Gap must use a Job Match generated
     * from the currently active resume.
     */

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
        "Your latest Job Match was created using a different resume. Run Job Match again before analyzing skill gaps."
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
              "What skills am I missing for this job?",

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
        "skill_gap"
      ) {
        throw new Error(
          "Unexpected CareerPilot response."
        );
      }


      if (
        !response.data.data
      ) {
        throw new Error(
          "Skill-gap analysis was not returned."
        );
      }


      setAnalysis(
        response.data.data
      );


      const newReportId =
        response.data
          .skill_gap_report_id;


      setReportId(
        newReportId
      );


      setCheckedItems(
        (
          newReportId &&
          readJSON(
            checklistKey(
              newReportId
            )
          )
        ) || {}
      );


      /*
       * Store analysis provenance.
       *
       * This lets downstream Career Plan logic
       * verify that Resume -> Job Match ->
       * Skill Gap all belong to the same chain.
       */

      localStorage.setItem(
        "careerpilot_latest_skill_gap",
        JSON.stringify({
          ...response.data.data,

          resume_id:
            activeResume.resume_id,

          thread_id:
            activeResume.thread_id,

          job_match_result_id:
            latestJobMatch
              .job_match_result_id,

          skill_gap_report_id:
            response.data
              .skill_gap_report_id,

          job_description_id:
            response.data
              .job_description_id,

          job_description:
            latestJobMatch
              .job_description,
        })
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "CareerPilot could not complete the skill-gap analysis."
      );

    } finally {
      setLoading(false);
    }
  }


  function toggleExpanded(
    cardKey
  ) {
    setExpandedCards(
      (prev) => ({
        ...prev,
        [cardKey]:
          !prev[cardKey],
      })
    );
  }


  /* ================= CAREER AI PROJECT HANDOFF ================= */

  function handleAskCareerAI(
    project
  ) {
    if (!project) {
      return;
    }


    localStorage.setItem(
      "careerpilot_project_handoff",
      JSON.stringify({
        target_skill:
          project.target_skill ||
          "",

        project_title:
          project.project_title ||
          "",

        project_goal:
          project.project_goal ||
          "",

        suggested_stack:
          Array.isArray(
            project.suggested_stack
          )
            ? project.suggested_stack
            : [],

        implementation_steps:
          Array.isArray(
            project.implementation_steps
          )
            ? project.implementation_steps
            : [],

        portfolio_evidence:
          Array.isArray(
            project.portfolio_evidence
          )
            ? project.portfolio_evidence
            : [],
      })
    );


    navigate(
      "/career-ai"
    );
  }


  /* ================= DERIVED DATA ================= */

  const priorityGroups =
    analysis
      ? [
          {
            key: "high",
            label:
              "High priority",
            items:
              analysis.high_priority_gaps ||
              [],
            tone:
              "danger",
          },
          {
            key: "medium",
            label:
              "Medium priority",
            items:
              analysis.medium_priority_gaps ||
              [],
            tone:
              "warning",
          },
          {
            key: "low",
            label:
              "Low priority",
            items:
              analysis.low_priority_gaps ||
              [],
            tone:
              "brand",
          },
        ]
      : [];


  const totalGapCount =
    priorityGroups.reduce(
      (
        sum,
        group
      ) =>
        sum +
        group.items.length,
      0
    );


  const visibleGroups =
    priorityGroups.filter(
      (group) =>
        priorityFilter ===
          "all" ||
        priorityFilter ===
          group.key
    );


  const portfolioProjects =
    analysis?.portfolio_project_prompts ||
    [];


  const actionChecklists =
    analysis
      ? [
          {
            key:
              "learning",
            eyebrow:
              "LEARNING ORDER",
            title:
              "What to work on first",
            items:
              analysis.recommended_learning_order ||
              [],
          },
          {
            key:
              "practice",
            eyebrow:
              "PRACTICE",
            title:
              "Build practical evidence",
            items:
              analysis.practice_tasks ||
              [],
          },
          {
            key:
              "proof",
            eyebrow:
              "PROOF OF SKILL",
            title:
              "Make your progress visible",
            items:
              analysis.proof_of_skill_actions ||
              [],
          },
        ].filter(
          (section) =>
            section.items.length >
            0
        )
      : [];


  const totalActionItems =
    actionChecklists.reduce(
      (
        sum,
        section
      ) =>
        sum +
        section.items.length,
      0
    );


  const completedActionItems =
    actionChecklists.reduce(
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
    );


  const progressPercent =
    totalActionItems > 0
      ? Math.round(
          (
            completedActionItems /
            totalActionItems
          ) *
            100
        )
      : 0;


  return (
    <section>

      {/* ================= HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          SKILL GAP
        </p>


        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Focus on the gaps that matter
        </h1>


        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          CareerPilot uses your latest Job Match
          to identify missing or weakly demonstrated
          skills and prioritize what to work on next.
        </p>

      </div>


      {/* ================= ACTION PANEL ================= */}

      {!analysis && (
        <div className="mt-10 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">

          <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

            <div className="flex items-start justify-between gap-4">

              <div>

                <p className="text-xs font-bold tracking-[0.12em] text-brand">
                  ROLE READINESS
                </p>


                <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                  Analyze your skill gaps
                </h2>


                <p className="mt-2 text-sm leading-6 text-text-muted">
                  CareerPilot will use the resume
                  and job description from your
                  latest Job Match automatically.
                </p>

              </div>


              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand">

                <Sparkles
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
                    Based on your latest Job Match
                  </p>


                  <p className="mt-2 text-sm leading-6 text-text-muted">
                    You do not need to paste the
                    job description again.
                  </p>

                </div>

              </div>

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

                  Analyzing skill gaps...
                </>
              ) : (
                <>
                  <Sparkles
                    size={18}
                  />

                  Analyze skill gaps
                </>
              )}
            </button>

          </section>


          {/* ================= EXPLANATION ================= */}

          <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-8">

            <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
              WHAT YOU'LL SEE
            </p>


            <h2 className="mt-3 text-2xl font-semibold tracking-tight">
              Priorities, not a random learning list.
            </h2>


            <p className="mt-4 leading-7 text-gray-300">
              CareerPilot separates demonstrated
              strengths from missing or partial skills
              and then ranks the gaps by importance.
            </p>


            <div className="mt-8 space-y-5">

              <InfoStep
                icon={
                  <CheckCircle2
                    size={19}
                  />
                }
                title="Existing skills"
                description="Capabilities already supported by your resume."
              />


              <InfoStep
                icon={
                  <AlertTriangle
                    size={19}
                  />
                }
                title="Priority gaps"
                description="Requirements that matter most for the target role."
              />


              <InfoStep
                icon={
                  <ArrowRight
                    size={19}
                  />
                }
                title="Learning order"
                description="A practical sequence for closing the important gaps, tracked as you go."
              />

            </div>

          </section>

        </div>
      )}


      {/* ================= RESULTS ================= */}

      {analysis && (
        <section className="mt-10">

          {/* ================= SKILL SNAPSHOT ================= */}

          <div className="grid gap-5 md:grid-cols-3">

            <SkillCard
              title="Existing skills"
              items={
                analysis.existing_skills
              }
              tone="success"
              expanded={
                expandedCards.existing
              }
              onToggle={() =>
                toggleExpanded(
                  "existing"
                )
              }
            />


            <SkillCard
              title="Missing skills"
              items={
                analysis.missing_skills
              }
              tone="danger"
              expanded={
                expandedCards.missing
              }
              onToggle={() =>
                toggleExpanded(
                  "missing"
                )
              }
            />


            <SkillCard
              title="Partially demonstrated"
              items={
                analysis.partially_demonstrated_skills
              }
              tone="warning"
              expanded={
                expandedCards.partial
              }
              onToggle={() =>
                toggleExpanded(
                  "partial"
                )
              }
            />

          </div>


          {/* ================= PRIORITY GAPS ================= */}

          {totalGapCount > 0 && (
            <section className="mt-6 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <p className="text-xs font-bold tracking-[0.14em] text-brand">
                    PRIORITY GAPS
                  </p>


                  <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                    What to close, ranked
                  </h2>

                </div>


                <div className="flex flex-wrap gap-2">

                  <FilterChip
                    label="All"
                    count={
                      totalGapCount
                    }
                    active={
                      priorityFilter ===
                      "all"
                    }
                    onClick={() =>
                      setPriorityFilter(
                        "all"
                      )
                    }
                  />


                  {priorityGroups.map(
                    (group) => (
                      <FilterChip
                        key={
                          group.key
                        }
                        label={
                          group.label.replace(
                            " priority",
                            ""
                          )
                        }
                        count={
                          group.items
                            .length
                        }
                        active={
                          priorityFilter ===
                          group.key
                        }
                        tone={
                          group.tone
                        }
                        onClick={() =>
                          setPriorityFilter(
                            group.key
                          )
                        }
                      />
                    )
                  )}

                </div>

              </div>


              {/* ================= DISTRIBUTION BAR ================= */}

              <div className="mt-6 flex h-2 overflow-hidden rounded-full bg-app-bg">

                {priorityGroups.map(
                  (group) =>
                    group.items.length >
                    0 ? (
                      <div
                        key={
                          group.key
                        }
                        className={
                          group.tone ===
                          "danger"
                            ? "bg-red-400"
                            : group.tone ===
                              "warning"
                            ? "bg-amber-400"
                            : "bg-emerald-400"
                        }
                        style={{
                          width: `${
                            (
                              group.items
                                .length /
                              totalGapCount
                            ) *
                            100
                          }%`,
                        }}
                      />
                    ) : null
                )}

              </div>


              {/* ================= PRIORITY CONTENT ================= */}

              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">

                {visibleGroups.map(
                  (group) =>
                    group.items.length >
                    0 ? (
                      <div
                        key={
                          group.key
                        }
                      >

                        <p
                          className={`text-xs font-bold tracking-[0.1em] ${
                            group.tone ===
                            "danger"
                              ? "text-red-600"
                              : group.tone ===
                                "warning"
                              ? "text-amber-600"
                              : "text-brand"
                          }`}
                        >
                          {group.label.toUpperCase()}
                        </p>


                        <ul className="mt-3 space-y-2.5">

                          {group.items.map(
                            (
                              item,
                              index
                            ) => (
                              <li
                                key={`${item}-${index}`}
                                className="flex items-start gap-2.5 text-sm leading-6 text-midnight"
                              >

                                <span
                                  className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${
                                    group.tone ===
                                    "danger"
                                      ? "bg-red-500"
                                      : group.tone ===
                                        "warning"
                                      ? "bg-amber-500"
                                      : "bg-emerald-500"
                                  }`}
                                />


                                <span>
                                  {item}
                                </span>

                              </li>
                            )
                          )}

                        </ul>

                      </div>
                    ) : null
                )}

              </div>

            </section>
          )}


          {/* ================= BUILD EVIDENCE ================= */}

          {portfolioProjects.length >
            0 && (
            <section className="mt-6 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                <div className="max-w-2xl">

                  <p className="text-xs font-bold tracking-[0.14em] text-brand">
                    BUILD EVIDENCE
                  </p>


                  <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                    Turn important gaps into portfolio proof
                  </h2>


                  <p className="mt-2 text-sm leading-6 text-text-muted">
                    These project ideas are based on your
                    current role gaps. Build one well, document
                    it clearly, and use the result as visible
                    evidence in GitHub, your portfolio, and future
                    resume updates.
                  </p>

                </div>


                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">

                  <Code2
                    size={21}
                  />

                </div>

              </div>


              <div className="mt-7 grid gap-5 xl:grid-cols-2">

                {portfolioProjects.map(
                  (
                    project,
                    index
                  ) => (
                    <PortfolioProjectCard
                      key={`${project.project_title || "project"}-${index}`}
                      project={project}
                      index={index}
                      onAskCareerAI={
                        handleAskCareerAI
                      }
                    />
                  )
                )}

              </div>

            </section>
          )}


          {/* ================= ACTION CHECKLISTS ================= */}

          {actionChecklists.length >
            0 && (
            <section className="mt-6 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <p className="text-xs font-bold tracking-[0.14em] text-brand">
                    YOUR ACTION PLAN
                  </p>


                  <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                    Track your progress
                  </h2>

                </div>


                <div className="flex items-center gap-3">

                  <div className="h-2 w-32 overflow-hidden rounded-full bg-app-bg">

                    <div
                      className="h-full rounded-full bg-brand transition-all"
                      style={{
                        width: `${progressPercent}%`,
                      }}
                    />

                  </div>


                  <span className="text-sm font-semibold text-midnight">
                    {progressPercent}%
                  </span>

                </div>

              </div>


              <div className="mt-7 grid gap-6 xl:grid-cols-3">

                {actionChecklists.map(
                  (section) => (
                    <div
                      key={
                        section.key
                      }
                    >

                      <p className="text-xs font-bold tracking-[0.12em] text-brand">
                        {section.eyebrow}
                      </p>


                      <h3 className="mt-1.5 text-sm font-semibold text-midnight">
                        {section.title}
                      </h3>


                      <div className="mt-4 space-y-2.5">

                        {section.items.map(
                          (
                            item,
                            index
                          ) => {
                            const itemKey =
                              `${section.key}-${index}`;

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
                                className={`flex w-full items-start gap-3 rounded-xl border p-3.5 text-left text-sm leading-6 transition ${
                                  isChecked
                                    ? "border-emerald-200 bg-emerald-50/60 text-text-muted line-through"
                                    : "border-border-soft bg-app-bg text-midnight hover:border-emerald-200"
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
                                      size={
                                        13
                                      }
                                    />
                                  )}
                                </span>


                                <span>
                                  {item}
                                </span>

                              </button>
                            );
                          }
                        )}

                      </div>

                    </div>
                  )
                )}

              </div>

            </section>
          )}


          {/* ================= READINESS SUMMARY ================= */}

          {analysis.readiness_summary && (
            <div className="mt-6 rounded-2xl bg-midnight p-6 text-white sm:p-8">

              <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
                READINESS SUMMARY
              </p>


              <p className="mt-4 max-w-4xl leading-8 text-gray-300">
                {
                  analysis.readiness_summary
                }
              </p>

            </div>
          )}


          {/* ================= CONTINUE ================= */}

          <div className="mt-6 flex justify-end">

            <button
              type="button"
              onClick={() =>
                navigate(
                  "/career-plan"
                )
              }
              className="inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover"
            >
              Continue to Career Plan

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
   PORTFOLIO PROJECT CARD
   ================================================== */

function PortfolioProjectCard({
  project,
  index,
  onAskCareerAI,
}) {
  const suggestedStack =
    Array.isArray(
      project?.suggested_stack
    )
      ? project.suggested_stack
      : [];

  const implementationSteps =
    Array.isArray(
      project?.implementation_steps
    )
      ? project.implementation_steps
      : [];

  const portfolioEvidence =
    Array.isArray(
      project?.portfolio_evidence
    )
      ? project.portfolio_evidence
      : [];


  return (
    <article className="flex h-full flex-col rounded-2xl border border-border-soft bg-app-bg p-5 transition hover:border-emerald-200 sm:p-6">

      <div className="flex items-start justify-between gap-4">

        <div className="min-w-0">

          <div className="flex flex-wrap items-center gap-2">

            <span className="rounded-full bg-brand-soft px-2.5 py-1 text-[11px] font-bold tracking-[0.08em] text-brand">
              {project?.target_skill ||
                `PROJECT ${index + 1}`}
            </span>

          </div>


          <h3 className="mt-3 text-lg font-semibold tracking-tight text-midnight">
            {project?.project_title ||
              "Portfolio project recommendation"}
          </h3>

        </div>


        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-brand shadow-sm">

          <Code2
            size={19}
          />

        </div>

      </div>


      {project?.project_goal && (
        <p className="mt-3 text-sm leading-7 text-text-muted">
          {project.project_goal}
        </p>
      )}


      {suggestedStack.length >
        0 && (
        <div className="mt-5">

          <p className="text-[11px] font-bold tracking-[0.12em] text-midnight/60">
            SUGGESTED STACK
          </p>


          <div className="mt-2 flex flex-wrap gap-2">

            {suggestedStack.map(
              (
                technology,
                stackIndex
              ) => (
                <span
                  key={`${technology}-${stackIndex}`}
                  className="rounded-lg border border-border-soft bg-white px-2.5 py-1.5 text-xs font-medium text-midnight"
                >
                  {technology}
                </span>
              )
            )}

          </div>

        </div>
      )}


      {implementationSteps.length >
        0 && (
        <div className="mt-6">

          <p className="text-[11px] font-bold tracking-[0.12em] text-midnight/60">
            WHAT TO BUILD
          </p>


          <div className="mt-3 space-y-3">

            {implementationSteps.map(
              (
                step,
                stepIndex
              ) => (
                <div
                  key={`${step}-${stepIndex}`}
                  className="flex gap-3"
                >

                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white text-[11px] font-bold text-brand shadow-sm">
                    {String(
                      stepIndex + 1
                    ).padStart(
                      2,
                      "0"
                    )}
                  </span>


                  <p className="pt-0.5 text-sm leading-6 text-text-muted">
                    {step}
                  </p>

                </div>
              )
            )}

          </div>

        </div>
      )}


      {portfolioEvidence.length >
        0 && (
        <div className="mt-6">

          <p className="text-[11px] font-bold tracking-[0.12em] text-midnight/60">
            PORTFOLIO EVIDENCE
          </p>


          <div className="mt-3 space-y-2.5">

            {portfolioEvidence.map(
              (
                evidence,
                evidenceIndex
              ) => (
                <div
                  key={`${evidence}-${evidenceIndex}`}
                  className="flex gap-2.5"
                >

                  <CheckCircle2
                    size={16}
                    className="mt-1 shrink-0 text-brand"
                  />


                  <p className="text-sm leading-6 text-text-muted">
                    {evidence}
                  </p>

                </div>
              )
            )}

          </div>

        </div>
      )}


      <div className="mt-auto pt-6">

        <button
          type="button"
          onClick={() =>
            onAskCareerAI(
              project
            )
          }
          className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm font-semibold text-brand transition hover:border-brand hover:bg-emerald-50"
        >
          <MessageSquareText
            size={16}
          />

          Ask Career AI to help build this

          <ArrowRight
            size={15}
          />
        </button>

      </div>

    </article>
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
   FILTER CHIP
   ================================================== */

function FilterChip({
  label,
  count,
  active,
  tone,
  onClick,
}) {
  const toneActiveClasses = {
    danger:
      "bg-red-500 border-red-500",

    warning:
      "bg-amber-500 border-amber-500",

    brand:
      "bg-emerald-500 border-emerald-500",
  };


  return (
    <button
      type="button"
      onClick={
        onClick
      }
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
        active
          ? `text-white ${
              toneActiveClasses[
                tone
              ] ||
              "bg-midnight border-midnight"
            }`
          : "border-border-soft bg-white text-text-muted hover:border-emerald-200 hover:text-midnight"
      }`}
    >
      {label}

      <span
        className={
          active
            ? "opacity-80"
            : "text-gray-400"
        }
      >
        {count}
      </span>

    </button>
  );
}


/* ==================================================
   SKILL CARD
   ================================================== */

function SkillCard({
  title,
  items = [],
  tone,
  expanded,
  onToggle,
}) {
  const styles = {
    success:
      "border-emerald-200 bg-emerald-50/40",

    warning:
      "border-amber-200 bg-amber-50/40",

    danger:
      "border-red-200 bg-red-50/40",
  };


  const dotStyles = {
    success:
      "text-brand",

    warning:
      "text-amber-500",

    danger:
      "text-red-500",
  };


  const visibleItems =
    items?.length > 0
      ? expanded
        ? items
        : items.slice(
            0,
            5
          )
      : [];


  const hiddenCount =
    (items?.length || 0) -
    visibleItems.length;


  return (
    <article
      className={`rounded-2xl border p-6 ${styles[tone]}`}
    >

      <div className="flex items-center justify-between">

        <h3 className="font-semibold text-midnight">
          {title}
        </h3>


        <span className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-text-muted">
          {items?.length || 0}
        </span>

      </div>


      {visibleItems.length > 0 ? (
        <>

          <ul className="mt-5 space-y-3">

            {visibleItems.map(
              (
                item,
                index
              ) => (
                <li
                  key={`${item}-${index}`}
                  className="flex gap-3 text-sm leading-6 text-text-muted"
                >

                  <CheckCircle2
                    size={16}
                    className={`mt-1 shrink-0 ${dotStyles[tone]}`}
                  />


                  <span>
                    {item}
                  </span>

                </li>
              )
            )}

          </ul>


          {hiddenCount >
            0 && (
            <button
              type="button"
              onClick={
                onToggle
              }
              className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-midnight/70 transition hover:text-midnight"
            >
              {expanded
                ? "Show less"
                : `Show ${hiddenCount} more`}

              <ChevronDown
                size={14}
                className={`transition-transform ${
                  expanded
                    ? "rotate-180"
                    : ""
                }`}
              />

            </button>
          )}

        </>
      ) : (
        <p className="mt-5 text-sm text-text-muted">
          No items identified.
        </p>
      )}

    </article>
  );
}


export default SkillGap;