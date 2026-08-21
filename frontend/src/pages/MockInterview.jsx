import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Gauge,
  LoaderCircle,
  MessageSquareText,
  RotateCcw,
  Sparkles,
  Target,
  Trophy,
  XCircle,
} from "lucide-react";

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

const INTERVIEW_TYPES = [
  {
    value: "technical",
    label: "Technical",
    description: "Practice role-relevant technical concepts and skills.",
  },
  {
    value: "behavioral",
    label: "Behavioral",
    description: "Practice project, teamwork, challenge, and learning questions.",
  },
  {
    value: "hr",
    label: "HR",
    description: "Practice motivation, communication, strengths, and career questions.",
  },
  {
    value: "mixed",
    label: "Mixed",
    description: "Practice a balanced mix of technical, behavioral, and HR questions.",
  },
];

const QUESTION_COUNTS = [3, 5, 7];

function MockInterview() {
  const navigate = useNavigate();

  /* ================= ANALYSIS CONTEXT ================= */
  const analysisContext = useMemo(() => getInterviewContext(), []);

  /* ================= SETUP STATE ================= */
  const [interviewType, setInterviewType] = useState("technical");
  const [totalQuestions, setTotalQuestions] = useState(5);

  /* ================= SESSION STATE ================= */
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState("setup");
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [nextQuestion, setNextQuestion] = useState(null);
  const [summary, setSummary] = useState(null);
  const [answeredCount, setAnsweredCount] = useState(0);

  /* ================= REQUEST STATE ================= */
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  /* ================= START INTERVIEW ================= */
  async function handleStartInterview() {
    setError("");
    setStarting(true);

    try {
      if (!analysisContext.resumeId) {
        throw new Error("Upload or select a resume before starting a Mock Interview.");
      }

      const payload = {
        resume_id: analysisContext.resumeId,
        job_description_id: analysisContext.jobDescriptionId || null,
        skill_gap_report_id: analysisContext.skillGapReportId || null,
        interview_type: interviewType,
        total_questions: totalQuestions,
      };

      const response = await api.post("/api/interview/start", payload);
      const data = response.data;

      setSessionId(data.session_id);
      setSessionStatus("in_progress");
      setCurrentQuestion(data.current_question);
      setAnswer("");
      setFeedback(null);
      setNextQuestion(null);
      setSummary(null);
      setAnsweredCount(0);
    } catch (err) {
      
      setError(
        err.response?.data?.detail ||
          err.message ||
          "CareerPilot could not start the Mock Interview."
      );
    } finally {
      setStarting(false);
    }
  }

  /* ================= SUBMIT ANSWER ================= */
  async function handleSubmitAnswer() {
    const cleanedAnswer = answer.trim();

    if (!cleanedAnswer) {
      setError("Enter your answer before submitting.");
      return;
    }

    if (!sessionId) {
      setError("Mock Interview session is unavailable.");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const response = await api.post("/api/interview/answer", {
        session_id: sessionId,
        answer: cleanedAnswer,
      });

      const data = response.data;

      setFeedback(data.feedback || null);
      setAnsweredCount(data.answered_question_number || answeredCount + 1);

      if (data.completed) {
        setSessionStatus("completed");
        setSummary(data.summary || null);
        setNextQuestion(null);
      } else {
        setNextQuestion(data.next_question || null);
      }
    } catch (err) {
      
      setError(
        err.response?.data?.detail ||
          err.message ||
          "CareerPilot could not evaluate this answer."
      );
    } finally {
      setSubmitting(false);
    }
  }

  /* ================= NEXT QUESTION ================= */
  function handleNextQuestion() {
    if (!nextQuestion) return;

    setCurrentQuestion(nextQuestion);
    setNextQuestion(null);
    setFeedback(null);
    setAnswer("");
    setError("");
  }

  /* ================= RESTART ================= */
  function handleRestart() {
    setSessionId(null);
    setSessionStatus("setup");
    setCurrentQuestion(null);
    setAnswer("");
    setFeedback(null);
    setNextQuestion(null);
    setSummary(null);
    setAnsweredCount(0);
    setError("");
  }

  /* ================================================================
     SETUP VIEW
     ================================================================ */
  if (sessionStatus === "setup") {
    return (
      <section>
        {/* HEADER */}
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-bold tracking-[0.14em] text-brand">MOCK INTERVIEW</p>
            <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
              Practice before the real interview
            </h1>
            <p className="mt-4 max-w-2xl leading-7 text-text-muted">
              CareerPilot generates fresher-level questions using your resume, target role
              context, and identified skill gaps.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/career-plan")}
            className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-text-muted transition hover:text-brand"
          >
            <ArrowLeft size={16} />
            Back to Career Plan
          </button>
        </div>

        {/* CONTEXT */}
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <ContextCard
            icon={<ClipboardCheck size={18} />}
            label="Resume"
            value={
              analysisContext.resumeFilename ||
              (analysisContext.resumeId ? "Selected" : "Not selected")
            }
            active={Boolean(analysisContext.resumeId)}
          />

          <ContextCard
            icon={<Target size={18} />}
            label="Job Description"
            value={analysisContext.jobDescriptionId ? "Tailored to role" : "Generic interview"}
            active={Boolean(analysisContext.jobDescriptionId)}
          />

          <ContextCard
            icon={<Sparkles size={18} />}
            label="Skill Gap"
            value={analysisContext.skillGapReportId ? "Targeting gaps" : "General preparation"}
            active={Boolean(analysisContext.skillGapReportId)}
          />
        </div>

        {error && <ErrorBanner message={error} />}

        {/* SETUP CARD */}
        <div className="mt-8 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-start gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
              <MessageSquareText size={20} />
            </div>

            <div>
              <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
                INTERVIEW SETUP
              </p>
              <h2 className="mt-1 text-xl font-semibold text-midnight">
                Choose how you want to practice
              </h2>
              <p className="mt-2 text-sm leading-6 text-text-muted">
                CareerPilot will ask one question at a time and provide feedback after every
                answer.
              </p>
            </div>
          </div>

          {/* INTERVIEW TYPES */}
          <div className="mt-8">
            <p className="text-sm font-semibold text-midnight">Interview type</p>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {INTERVIEW_TYPES.map((type) => {
                const selected = interviewType === type.value;

                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setInterviewType(type.value)}
                    aria-pressed={selected}
                    className={`group relative rounded-xl border p-4 text-left transition ${
                      selected
                        ? "border-brand bg-emerald-50/60 ring-2 ring-emerald-500/10"
                        : "border-border-soft bg-app-bg hover:border-emerald-200 hover:bg-emerald-50/30"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p
                        className={`font-semibold ${selected ? "text-brand" : "text-midnight"}`}
                      >
                        {type.label}
                      </p>

                      <div
                        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition ${
                          selected
                            ? "border-brand bg-brand text-white"
                            : "border-gray-300 bg-white text-transparent group-hover:border-emerald-300"
                        }`}
                      >
                        <CheckCircle2 size={13} strokeWidth={3} />
                      </div>
                    </div>

                    <p className="mt-2 text-sm leading-6 text-text-muted">{type.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* QUESTION COUNT */}
          <div className="mt-8">
            <p className="text-sm font-semibold text-midnight">Number of questions</p>

            <div className="mt-3 inline-flex rounded-lg border border-border-soft bg-app-bg p-1">
              {QUESTION_COUNTS.map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => setTotalQuestions(count)}
                  aria-pressed={totalQuestions === count}
                  className={`min-w-[52px] rounded-md px-4 py-2 text-sm font-semibold transition ${
                    totalQuestions === count
                      ? "bg-brand text-white shadow-sm"
                      : "text-text-muted hover:text-brand"
                  }`}
                >
                  {count}
                </button>
              ))}
            </div>

            <p className="mt-2 text-xs text-text-muted">
              Five questions is recommended for the MVP practice session.
            </p>
          </div>

          {/* START */}
          <div className="mt-8 flex flex-col gap-3 border-t border-border-soft pt-6 sm:flex-row sm:items-center sm:justify-between">
            <p className="max-w-xl text-sm leading-6 text-text-muted">
              Your answers are evaluated for clarity, relevance, and role-appropriate technical
              or behavioral quality.
            </p>

            <button
              type="button"
              onClick={handleStartInterview}
              disabled={starting || !analysisContext.resumeId}
              className={`inline-flex h-11 items-center justify-center gap-2 rounded-lg px-5 text-sm font-semibold transition ${
                starting || !analysisContext.resumeId
                  ? "cursor-not-allowed bg-gray-100 text-gray-400"
                  : "bg-brand text-white hover:bg-brand-hover"
              }`}
            >
              {starting ? (
                <LoaderCircle size={17} className="animate-spin" />
              ) : (
                <Sparkles size={17} />
              )}
              {starting ? "Starting..." : "Start Mock Interview"}
            </button>
          </div>
        </div>
      </section>
    );
  }

  /* ================================================================
     COMPLETE VIEW
     ================================================================ */
  if (sessionStatus === "completed") {
    return (
      <section>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => navigate("/career-plan")}
            className="inline-flex items-center gap-2 text-sm font-semibold text-text-muted transition hover:text-brand"
          >
            <ArrowLeft size={16} />
            Back to Career Plan
          </button>

          <button
            type="button"
            onClick={handleRestart}
            className="inline-flex items-center gap-2 rounded-lg border border-border-soft bg-white px-4 py-2 text-sm font-semibold text-midnight transition hover:bg-app-bg"
          >
            <RotateCcw size={16} />
            New Interview
          </button>
        </div>

        {/* COMPLETION HERO */}
        <div className="mt-8 rounded-2xl border border-emerald-100 bg-emerald-50/60 p-7 shadow-sm sm:p-9">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex items-center gap-2 text-brand">
                <Trophy size={20} />
                <p className="text-xs font-bold tracking-[0.14em]">INTERVIEW COMPLETE</p>
              </div>

              <h1 className="mt-4 text-3xl font-bold tracking-tight text-midnight">
                Mock Interview Summary
              </h1>

              <p className="mt-3 leading-7 text-text-muted">
                You completed {totalQuestions} questions in your {interviewType} interview
                session.
              </p>
            </div>

            <ScoreRing score={summary?.readiness_score ?? 0} />
          </div>
        </div>

        {/* SUMMARY */}
        {summary && (
          <div className="mt-8 grid gap-6">
            <SummaryPanel icon={<Gauge size={19} />} title="Overall Feedback">
              <p className="text-sm leading-7 text-text-muted">{summary.overall_feedback}</p>
            </SummaryPanel>

            <div className="grid gap-6 lg:grid-cols-2">
              <SummaryPanel icon={<CheckCircle2 size={19} />} title="Strengths">
                <BulletItems items={summary.strengths} tone="positive" />
              </SummaryPanel>

              <SummaryPanel icon={<Target size={19} />} title="Weak Areas">
                <BulletItems items={summary.weak_areas} tone="warning" />
              </SummaryPanel>
            </div>

            <SummaryPanel icon={<Sparkles size={19} />} title="Recommended Next Steps">
              <NumberedItems items={summary.recommended_next_steps} />
            </SummaryPanel>
          </div>
        )}
      </section>
    );
  }

  /* ================================================================
     ACTIVE INTERVIEW VIEW
     ================================================================ */
  const questionNumber = currentQuestion?.question_number || answeredCount + 1;

  const progress = Math.min(
    100,
    Math.round(((questionNumber - 1) / totalQuestions) * 100)
  );

  return (
    <section>
      {/* HEADER */}
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.14em] text-brand">MOCK INTERVIEW</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-midnight">
            {capitalize(interviewType)} Interview
          </h1>
          <p className="mt-2 text-sm text-text-muted">Session #{sessionId}</p>
        </div>

        <div className="min-w-[220px]">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-text-muted">
              Question {questionNumber} of {totalQuestions}
            </span>
            <span className="text-brand">{progress}%</span>
          </div>

          <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-brand transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {/* QUESTION CARD */}
      <div className="mt-8 rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
            <MessageSquareText size={20} />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
                QUESTION {questionNumber}
              </p>

              {currentQuestion?.skill_target && (
                <span className="rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700">
                  {currentQuestion.skill_target}
                </span>
              )}
            </div>

            <h2 className="mt-4 text-xl font-semibold leading-8 text-midnight">
              {currentQuestion?.question}
            </h2>
          </div>
        </div>

        {/* ANSWER */}
        {!feedback && (
          <div className="mt-8">
            <label htmlFor="mock-answer" className="text-sm font-semibold text-midnight">
              Your answer
            </label>

            <textarea
              id="mock-answer"
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
              rows={8}
              maxLength={5000}
              placeholder="Answer naturally, like you would in a real interview..."
              className="mt-3 w-full resize-y rounded-xl border border-border-soft bg-app-bg px-4 py-3 text-sm leading-7 text-midnight outline-none transition placeholder:text-gray-400 focus:border-brand focus:bg-white focus:ring-4 focus:ring-emerald-500/10"
            />

            <div className="mt-2 flex items-center justify-between gap-3">
              <p className="text-xs text-text-muted">
                Keep it clear and practical. You can use projects, internships, coursework, or
                academic examples.
              </p>

              <p className="shrink-0 text-xs text-gray-400">{answer.length}/5000</p>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={handleSubmitAnswer}
                disabled={submitting || !answer.trim()}
                className={`inline-flex h-11 items-center justify-center gap-2 rounded-lg px-5 text-sm font-semibold transition ${
                  submitting || !answer.trim()
                    ? "cursor-not-allowed bg-gray-100 text-gray-400"
                    : "bg-brand text-white hover:bg-brand-hover"
                }`}
              >
                {submitting ? (
                  <LoaderCircle size={17} className="animate-spin" />
                ) : (
                  <ClipboardCheck size={17} />
                )}
                {submitting ? "Evaluating..." : "Submit Answer"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* FEEDBACK */}
      {feedback && (
        <div className="mt-6 overflow-hidden rounded-2xl border border-border-soft bg-white shadow-sm">
          <div
            className={`h-1.5 w-full ${scoreBarColor(feedback.score)}`}
            aria-hidden="true"
          />

          <div className="p-6 sm:p-8">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
                  ANSWER FEEDBACK
                </p>
                <h2 className="mt-2 text-xl font-semibold text-midnight">
                  Here's how your answer performed
                </h2>
              </div>

              <div
                className={`rounded-xl border px-5 py-3 text-center ${scoreBadgeColor(
                  feedback.score
                )}`}
              >
                <p className="text-[10px] font-bold uppercase tracking-[0.12em]">Score</p>
                <p className="mt-1 text-2xl font-bold text-midnight">
                  {feedback.score}
                  <span className="text-sm font-semibold text-text-muted">/10</span>
                </p>
              </div>
            </div>

            <p className="mt-6 text-sm leading-7 text-text-muted">{feedback.feedback}</p>

            <div className="mt-7 grid gap-5 lg:grid-cols-2">
              <FeedbackBlock
                title="What You Did Well"
                items={feedback.strengths}
                tone="positive"
              />
              <FeedbackBlock
                title="What To Improve"
                items={feedback.improvements}
                tone="warning"
              />
            </div>

            {feedback.better_answer_approach && (
              <div className="mt-5 rounded-xl border border-border-soft bg-app-bg p-5">
                <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-brand">
                  Better Answer Approach
                </p>
                <p className="mt-3 text-sm leading-7 text-text-muted">
                  {feedback.better_answer_approach}
                </p>
              </div>
            )}

            {nextQuestion && (
              <div className="mt-7 flex justify-end border-t border-border-soft pt-6">
                <button
                  type="button"
                  onClick={handleNextQuestion}
                  className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover"
                >
                  Next Question
                  <ChevronRight size={17} />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

/* ================================================================
   CONTEXT CARD
   ================================================================ */

function ContextCard({ icon, label, value, active }) {
  return (
    <div className="rounded-xl border border-border-soft bg-white p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
            active ? "bg-brand-soft text-brand" : "bg-gray-100 text-gray-400"
          }`}
        >
          {icon}
        </div>

        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-text-muted">
            {label}
          </p>

          <p
            title={value}
            className={`mt-1 truncate text-sm font-semibold ${
              active ? "text-midnight" : "text-text-muted"
            }`}
          >
            {value}
          </p>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   ERROR BANNER
   ================================================================ */

function ErrorBanner({ message }) {
  return (
    <div className="mt-6 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      <XCircle size={18} className="mt-0.5 shrink-0" />
      <p className="leading-6">{message}</p>
    </div>
  );
}

/* ================================================================
   FEEDBACK BLOCK
   ================================================================ */

function FeedbackBlock({ title, items, tone }) {
  const values = Array.isArray(items) ? items : [];

  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-5">
      <p
        className={`text-[11px] font-bold uppercase tracking-[0.13em] ${
          tone === "positive" ? "text-brand" : "text-amber-600"
        }`}
      >
        {title}
      </p>

      {values.length > 0 ? (
        <div className="mt-4 space-y-3">
          {values.map((item, index) => (
            <div key={`${item}-${index}`} className="flex gap-3">
              {tone === "positive" ? (
                <CheckCircle2 size={16} className="mt-1 shrink-0 text-brand" />
              ) : (
                <Target size={16} className="mt-1 shrink-0 text-amber-600" />
              )}
              <p className="text-sm leading-6 text-text-muted">{item}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-text-muted">No items recorded.</p>
      )}
    </div>
  );
}

/* ================================================================
   SCORE RING (readiness score, 0-100)
   ================================================================ */

function ScoreRing({ score }) {
  const clamped = Math.max(0, Math.min(100, score));
  const ringColor =
    clamped >= 70 ? "#10b981" : clamped >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex w-fit items-center gap-4 rounded-2xl border border-emerald-100 bg-white px-6 py-5 shadow-sm">
      <div
        className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full"
        style={{
          background: `conic-gradient(${ringColor} ${clamped * 3.6}deg, #e5e7eb 0deg)`,
        }}
      >
        <div className="flex h-[62px] w-[62px] items-center justify-center rounded-full bg-white">
          <span className="text-xl font-bold text-midnight">{clamped}</span>
        </div>
      </div>

      <div>
        <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-brand">
          Readiness Score
        </p>
        <p className="mt-1 text-sm font-semibold text-midnight">{clamped}/100</p>
      </div>
    </div>
  );
}

/* ================================================================
   SUMMARY PANEL
   ================================================================ */

function SummaryPanel({ icon, title, children }) {
  return (
    <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">
          {icon}
        </div>
        <h2 className="font-semibold text-midnight">{title}</h2>
      </div>

      <div className="mt-5">{children}</div>
    </section>
  );
}

/* ================================================================
   BULLET ITEMS
   ================================================================ */

function BulletItems({ items, tone }) {
  const values = Array.isArray(items) ? items : [];

  if (values.length === 0) {
    return <p className="text-sm text-text-muted">No items recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {values.map((item, index) => (
        <div key={`${item}-${index}`} className="flex gap-3">
          {tone === "positive" ? (
            <CheckCircle2 size={17} className="mt-1 shrink-0 text-brand" />
          ) : (
            <Target size={17} className="mt-1 shrink-0 text-amber-600" />
          )}
          <p className="text-sm leading-7 text-text-muted">{item}</p>
        </div>
      ))}
    </div>
  );
}

/* ================================================================
   NUMBERED ITEMS
   ================================================================ */

function NumberedItems({ items }) {
  const values = Array.isArray(items) ? items : [];

  if (values.length === 0) {
    return <p className="text-sm text-text-muted">No recommendations recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {values.map((item, index) => (
        <div
          key={`${item}-${index}`}
          className="flex gap-3 rounded-xl border border-border-soft bg-app-bg p-4"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
            {String(index + 1).padStart(2, "0")}
          </div>
          <p className="pt-1 text-sm leading-6 text-text-muted">{item}</p>
        </div>
      ))}
    </div>
  );
}

/* ================================================================
   SCORE COLOR HELPERS (feedback score, 0-10)
   ================================================================ */

function scoreBarColor(score) {
  if (score >= 7) return "bg-emerald-500";
  if (score >= 4) return "bg-amber-500";
  return "bg-red-500";
}

function scoreBadgeColor(score) {
  if (score >= 7) return "border-emerald-100 bg-emerald-50";
  if (score >= 4) return "border-amber-100 bg-amber-50";
  return "border-red-100 bg-red-50";
}

/* ================================================================
   LOCAL STORAGE CONTEXT
   ================================================================ */

function getInterviewContext() {
  const resume = readStoredObject("careerpilot_active_resume");
  const jobMatch = readStoredObject("careerpilot_latest_job_match");
  const skillGap = readStoredObject("careerpilot_latest_skill_gap");
  const careerPlan = readStoredObject("careerpilot_latest_career_plan");

  const resumeId = firstAvailableId(
    resume?.resume_id,
    resume?.id,
    jobMatch?.resume_id,
    skillGap?.resume_id,
    careerPlan?.resume_id
  );

  const jobDescriptionId = firstAvailableId(
    jobMatch?.job_description_id,
    skillGap?.job_description_id,
    careerPlan?.job_description_id
  );

  const skillGapReportId = firstAvailableId(
    skillGap?.skill_gap_report_id,
    skillGap?.id,
    careerPlan?.skill_gap_report_id
  );

  const resumeFilename =
    resume?.original_filename ||
    resume?.filename ||
    resume?.resume_filename ||
    jobMatch?.resume_filename ||
    null;

  return {
    resumeId,
    jobDescriptionId,
    skillGapReportId,
    resumeFilename,
  };
}

/* ================================================================
   HELPERS
   ================================================================ */

function readStoredObject(key) {
  const value = localStorage.getItem(key);

  if (!value) return null;

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function firstAvailableId(...values) {
  const found = values.find(
    (value) => value !== null && value !== undefined && value !== ""
  );

  if (found === undefined) return null;

  const parsed = Number(found);

  return Number.isNaN(parsed) ? found : parsed;
}

function capitalize(value) {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default MockInterview;