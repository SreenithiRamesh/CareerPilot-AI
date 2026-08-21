import { useEffect, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  Gauge,
  Navigation,
  Plus,
  Route,
  Sparkles,
} from "lucide-react";

import { Link } from "react-router-dom";


function Home() {
  return (
    <main className="min-h-screen bg-app-bg text-midnight">

      {/* ================= NAVBAR ================= */}

      <header className="sticky top-0 z-50 border-b border-border-soft bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-10">

          <Link
            to="/"
            className="flex items-center gap-3"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-midnight text-white shadow-sm">
              <Navigation
                size={19}
                strokeWidth={2.4}
              />
            </div>

            <span className="text-[15px] font-bold tracking-tight text-midnight sm:text-base">
              CareerPilot
              <span className="text-brand">
                {" "}AI
              </span>
            </span>
          </Link>


          <nav className="hidden items-center gap-8 text-sm font-medium text-gray-500 lg:flex">
            <a
              href="#how-it-works"
              className="transition hover:text-midnight"
            >
              How it works
            </a>

            <a
              href="#insights"
              className="transition hover:text-midnight"
            >
              Career insights
            </a>

            <a
              href="#freshers"
              className="transition hover:text-midnight"
            >
              For freshers
            </a>

            <a
              href="#faq"
              className="transition hover:text-midnight"
            >
              FAQ
            </a>
          </nav>


          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="hidden text-sm font-semibold text-midnight transition hover:text-brand sm:block"
            >
              Sign in
            </Link>

            <Link
              to="/register"
              className="rounded-lg bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-hover"
            >
              Analyze my resume
            </Link>
          </div>

        </div>
      </header>


      {/* ================= HERO ================= */}

      <section className="relative overflow-hidden bg-midnight text-white">

        <style>{`
          @media (prefers-reduced-motion: no-preference) {
            .cp-reveal-row {
              opacity: 0;
              animation: cpFadeSlideIn 0.55s ease forwards;
            }
            .cp-reveal-row:nth-child(1) { animation-delay: 0.7s; }
            .cp-reveal-row:nth-child(2) { animation-delay: 0.95s; }
            .cp-reveal-row:nth-child(3) { animation-delay: 1.2s; }

            .cp-hero-card {
              opacity: 0;
              animation: cpCardIn 0.6s ease forwards;
            }

            .cp-glow {
              animation: cpPulse 5s ease-in-out infinite;
            }
          }

          @keyframes cpFadeSlideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes cpCardIn {
            from { opacity: 0; transform: translateY(16px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
          }

          @keyframes cpPulse {
            0%, 100% { opacity: 0.35; transform: scale(1); }
            50% { opacity: 0.55; transform: scale(1.06); }
          }
        `}</style>


        {/* Ambient glow */}

        <div
          aria-hidden="true"
          className="cp-glow pointer-events-none absolute -right-40 -top-40 h-[560px] w-[560px] rounded-full bg-emerald-500/20 blur-[120px]"
        />

        <div
          aria-hidden="true"
          className="cp-glow pointer-events-none absolute -bottom-52 -left-32 h-[480px] w-[480px] rounded-full bg-emerald-400/10 blur-[120px]"
        />


        <div className="relative mx-auto grid min-h-[680px] max-w-[1440px] items-center gap-12 px-4 py-20 sm:px-6 sm:py-24 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-28 xl:gap-16 xl:px-10">

          <div className="max-w-[720px]">
            <p className="text-xs font-bold tracking-[0.18em] text-brand-accent">
              AGENTIC CAREER MENTOR
            </p>

            <h1 className="mt-5 text-5xl font-black leading-[0.98] tracking-[-0.04em] sm:text-6xl lg:text-7xl xl:text-[84px]">
              Stop guessing

              <span className="block text-emerald-300">
                if you're ready.
              </span>
            </h1>

            <p className="mt-7 max-w-[560px] text-base leading-8 text-gray-300 sm:text-lg">
              CareerPilot analyzes your resume against a real
              job description in seconds, then turns the gaps
              into a practical, prioritized action plan.
            </p>


            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/register"
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover"
              >
                Analyze my resume
                <ArrowRight size={17} />
              </Link>

              <a
                href="#how-it-works"
                className="inline-flex min-h-12 items-center justify-center rounded-lg border border-gray-700 px-5 text-sm font-semibold text-gray-100 transition hover:bg-gray-800"
              >
                See how it works
              </a>
            </div>


            <p className="mt-6 text-xs font-medium tracking-wide text-gray-500">
              BUILT FOR STUDENTS AND FRESH GRADUATES
            </p>
          </div>


          {/* HERO LIVE ANALYSIS PREVIEW */}

          <div className="cp-hero-card w-full rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl shadow-black/40 backdrop-blur-sm sm:p-7 lg:justify-self-end">

            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[11px] font-bold tracking-[0.14em] text-brand-accent">
                  LIVE RESUME ANALYSIS
                </p>

                <h2 className="mt-2 text-lg font-semibold">
                  Software Engineer
                </h2>
              </div>

              <span className="flex items-center gap-1.5 rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                Analyzing
              </span>
            </div>


            <div className="mt-8 flex items-center gap-6 border-b border-white/10 pb-7">

              <HeroScoreRing target={60} />

              <div>
                <p className="font-semibold">
                  Job Match Score
                </p>

                <p className="mt-1 text-xs leading-5 text-gray-400">
                  Sample output — based on resume
                  evidence and target-role requirements.
                </p>
              </div>

            </div>


            <div className="mt-5 space-y-3">

              <div className="cp-reveal-row grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-white/10 bg-black/20 p-4">
                <CheckCircle2
                  size={19}
                  className="row-span-2 text-emerald-400"
                />

                <span className="text-xs text-gray-400">
                  Strong matches
                </span>

                <strong className="mt-1 text-sm font-semibold">
                  Java · REST APIs · AWS · Git
                </strong>
              </div>


              <div className="cp-reveal-row grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-white/10 bg-black/20 p-4">
                <Gauge
                  size={19}
                  className="row-span-2 text-amber-400"
                />

                <span className="text-xs text-gray-400">
                  Partial matches
                </span>

                <strong className="mt-1 text-sm font-semibold">
                  SQL · Linux
                </strong>
              </div>


              <div className="cp-reveal-row grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-white/10 bg-black/20 p-4">
                <Sparkles
                  size={19}
                  className="row-span-2 text-emerald-400"
                />

                <span className="text-xs text-gray-400">
                  Priority gaps
                </span>

                <strong className="mt-1 text-sm font-semibold">
                  Spring Boot · Docker
                </strong>
              </div>

            </div>
          </div>

        </div>
      </section>


      {/* ================= HOW IT WORKS ================= */}

      <section
        id="how-it-works"
        className="scroll-mt-24"
      >
        <div className="mx-auto max-w-[1440px] px-4 py-20 sm:px-6 sm:py-24 lg:px-8 xl:px-10">

          <div className="max-w-3xl">
            <p className="text-xs font-bold tracking-[0.15em] text-brand">
              HOW IT WORKS
            </p>

            <h2 className="mt-4 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl lg:text-5xl">
              One resume.
              Four focused stages.
            </h2>

            <p className="mt-5 max-w-2xl leading-7 text-text-muted">
              Each stage answers a different career
              question, keeping the final recommendations
              focused, explainable, and actionable.
            </p>
          </div>


          <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

            <ProcessCard
              icon={<FileSearch size={21} />}
              number="01"
              label="PARSE"
              title="Understand your resume"
            >
              Extract the skills, projects, experience,
              and technical evidence available in your
              resume.
            </ProcessCard>


            <ProcessCard
              icon={<Gauge size={21} />}
              number="02"
              label="MATCH"
              title="Compare with your target role"
            >
              Evaluate your resume against the job
              description and identify strong and
              partial matches.
            </ProcessCard>


            <ProcessCard
              icon={<Sparkles size={21} />}
              number="03"
              label="DIAGNOSE"
              title="Identify the gaps"
            >
              Surface missing or weakly demonstrated
              skills and prioritize them by relevance.
            </ProcessCard>


            <ProcessCard
              icon={<Route size={21} />}
              number="04"
              label="PLAN"
              title="Build your next-step roadmap"
            >
              Turn the analysis into learning priorities,
              practical tasks, portfolio evidence, and
              interview preparation.
            </ProcessCard>

          </div>
        </div>
      </section>


      {/* ================= INSIGHTS ================= */}

      <section
        id="insights"
        className="scroll-mt-24 border-y border-border-soft bg-white"
      >
        <div className="mx-auto max-w-[1440px] px-4 py-20 sm:px-6 sm:py-24 lg:px-8 xl:px-10">

          <div className="max-w-3xl">
            <p className="text-xs font-bold tracking-[0.15em] text-brand">
              EXPLAINABLE CAREER INSIGHTS
            </p>

            <h2 className="mt-4 text-3xl font-bold tracking-[-0.035em] sm:text-4xl lg:text-5xl">
              Every result should tell you why.
            </h2>

            <p className="mt-5 max-w-2xl leading-7 text-text-muted">
              CareerPilot separates demonstrated strengths,
              partial evidence, missing requirements, and
              priority actions instead of returning only
              a standalone score.
            </p>
          </div>


          <div className="mt-12 overflow-hidden rounded-2xl border border-border-soft bg-white shadow-sm lg:grid lg:grid-cols-[300px_1fr]">

            <div className="flex min-h-60 flex-col items-center justify-center bg-midnight p-10 text-white">
              <span className="text-6xl font-bold tracking-tight text-emerald-300">
                60%
              </span>

              <p className="mt-3 text-sm text-gray-300">
                Current job match
              </p>
            </div>


            <div className="divide-y divide-border-soft px-6 sm:px-9 lg:px-12">

              <InsightRow
                label="Strong matches"
                value="Java · REST APIs · AWS · Git"
                type="success"
              />

              <InsightRow
                label="Partial matches"
                value="SQL · Linux"
                type="warning"
              />

              <InsightRow
                label="Priority gaps"
                value="Spring Boot · Docker"
                type="danger"
              />

            </div>
          </div>
        </div>
      </section>


      {/* ================= FAQ ================= */}

      <FAQSection />


      {/* ================= FRESHERS ================= */}

      <section
        id="freshers"
        className="scroll-mt-24"
      >
        <div className="mx-auto max-w-[1440px] px-4 py-20 sm:px-6 sm:py-24 lg:px-8 xl:px-10">

          <div className="flex flex-col gap-9 rounded-2xl bg-midnight px-6 py-10 text-white sm:px-10 lg:flex-row lg:items-center lg:justify-between lg:px-12 lg:py-14">

            <div className="max-w-3xl">
              <p className="text-xs font-bold tracking-[0.15em] text-brand-accent">
                BUILT FOR EARLY CAREERS
              </p>

              <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
                Turn uncertainty into a clear next step.
              </h2>

              <p className="mt-4 max-w-2xl leading-7 text-gray-300">
                Upload your resume, choose the role
                you're targeting, and build a focused
                preparation plan around the gaps that
                matter for that role.
              </p>
            </div>


            <Link
              to="/register"
              className="inline-flex min-h-12 shrink-0 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold transition hover:bg-brand-hover"
            >
              Start your analysis

              <ArrowRight size={17} />
            </Link>

          </div>
        </div>
      </section>


      {/* ================= FOOTER ================= */}

      <footer className="border-t border-border-soft bg-white">

        <div className="mx-auto flex max-w-[1440px] flex-col gap-7 px-4 py-8 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8 xl:px-10">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-midnight text-white">
              <Navigation
                size={17}
                strokeWidth={2.3}
              />
            </div>

            <div>
              <p className="font-semibold tracking-tight text-midnight">
                CareerPilot
                <span className="text-brand">
                  {" "}AI
                </span>
              </p>

              <p className="mt-1 text-xs text-text-muted">
                AI-assisted career guidance for
                students and fresh graduates.
              </p>
            </div>

          </div>


          <div className="text-sm text-text-muted md:text-right">
            <p>
              © 2026 CareerPilot AI. All rights reserved.
            </p>

            <p className="mt-1.5">
              Designed &amp; built by{" "}
              <span className="font-semibold text-midnight">
                Sreenithi Ramesh
              </span>
            </p>
          </div>

        </div>
      </footer>

    </main>
  );
}



const FAQ_ITEMS = [
  {
    question: "How does Career AI work?",
    answer:
      "Career AI uses your selected resume as context so the guidance stays connected to your actual skills, projects, and experience. It helps you reason about roles, preparation priorities, projects, interview readiness, and practical next steps instead of giving only generic career advice.",
  },
  {
    question: "Can I run Job Match against any job description?",
    answer:
      "Yes. Paste a job description and CareerPilot compares it with your resume to surface a match score, strong matches, partial matches, missing skills, resume improvements, and the most important actions to take next.",
  },
  {
    question: "Does CareerPilot work if I do not have much experience yet?",
    answer:
      "Yes. CareerPilot is designed for students and fresh graduates. Recommendations are kept realistic for an entry-level portfolio, with practical learning tasks and projects you can actually complete, explain, and use as evidence in interviews.",
  },
  {
    question: "Is the Skill Gap analysis based on my actual resume?",
    answer:
      "Yes. Skill Gap analysis builds on your resume and Job Match results, then prioritizes missing or weakly demonstrated skills so you can focus on the areas that matter most for the role you are targeting.",
  },
  {
    question: "Can I download my Career Readiness report?",
    answer:
      "Yes. CareerPilot can export a consolidated Career Readiness report that brings together your Job Match, Skill Gap, Career Plan, learning priorities, practical actions, portfolio evidence, and interview preparation in one PDF.",
  },
  {
    question: "Does Mock Interview practice adapt to my skill gaps?",
    answer:
      "Yes. Mock Interview sessions can use your resume, target job description, and Skill Gap report as context. You receive question-by-question feedback, improvement suggestions, and a final readiness score at the end of the session.",
  },
];


function FAQSection() {
  const [openIndex, setOpenIndex] =
    useState(0);

  return (
    <section
  id="faq"
  className="scroll-mt-24 border-y border-border-soft bg-app-bg"
>
      <div className="mx-auto max-w-[1440px] px-4 py-20 sm:px-6 sm:py-24 lg:px-8 xl:px-10">

        <div className="mx-auto max-w-3xl text-center">
          <p className="text-xs font-bold tracking-[0.15em] text-brand">
            FAQ
          </p>

          <h2 className="mt-4 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl lg:text-5xl">
            Questions before you get started.
          </h2>

          <p className="mx-auto mt-5 max-w-2xl leading-7 text-text-muted">
            A quick overview of how CareerPilot uses your
            resume, target role, skill gaps, and interview
            practice to create practical career guidance.
          </p>
        </div>


        <div className="mx-auto mt-12 max-w-4xl overflow-hidden rounded-2xl border border-border-soft bg-white shadow-sm">

          {FAQ_ITEMS.map(
            (item, index) => (
              <FAQItem
                key={item.question}
                item={item}
                isOpen={
                  openIndex === index
                }
                onToggle={() =>
                  setOpenIndex(
                    openIndex === index
                      ? -1
                      : index
                  )
                }
                isLast={
                  index ===
                  FAQ_ITEMS.length - 1
                }
              />
            )
          )}

        </div>


        <div className="mx-auto mt-8 flex max-w-4xl flex-col gap-4 rounded-2xl border border-emerald-100 bg-emerald-50/60 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">

          <div>
            <p className="text-sm font-semibold text-midnight">
              Still exploring what CareerPilot can do?
            </p>

            <p className="mt-1 text-sm leading-6 text-text-muted">
              Create an account, upload your resume, and start
              with a real role you are interested in.
            </p>
          </div>


          <Link
            to="/register"
            className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover"
          >
            Start free

            <ArrowRight size={16} />
          </Link>

        </div>

      </div>
    </section>
  );
}


function FAQItem({
  item,
  isOpen,
  onToggle,
  isLast,
}) {
  return (
    <div
      className={
        isLast
          ? ""
          : "border-b border-border-soft"
      }
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className="group flex w-full items-center justify-between gap-5 px-5 py-5 text-left transition hover:bg-white sm:px-7 sm:py-6"
      >
        <span className="text-[15px] font-semibold leading-6 text-midnight transition group-hover:text-brand sm:text-base">
          {item.question}
        </span>

        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition ${
            isOpen
              ? "border-emerald-200 bg-brand-soft text-brand"
              : "border-border-soft bg-white text-text-muted group-hover:border-emerald-200 group-hover:text-brand"
          }`}
        >
          <Plus
            size={16}
            className={`transition-transform duration-300 ${
              isOpen
                ? "rotate-45"
                : ""
            }`}
          />
        </span>
      </button>


      <div
        className={`grid transition-all duration-300 ease-out ${
          isOpen
            ? "grid-rows-[1fr] opacity-100"
            : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <p className="px-5 pb-6 pr-16 text-sm leading-7 text-text-muted sm:px-7 sm:pr-20">
            {item.answer}
          </p>
        </div>
      </div>

    </div>
  );
}


function HeroScoreRing({ target }) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;

    if (prefersReducedMotion) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setValue(target);
      return;
    }

    let frameId;
    let start;
    const duration = 1200;
    const delay = 350;

    function tick(timestamp) {
      if (!start) start = timestamp;

      const elapsed = timestamp - start - delay;

      if (elapsed < 0) {
        frameId = requestAnimationFrame(tick);
        return;
      }

      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);

      setValue(Math.round(eased * target));

      if (progress < 1) {
        frameId = requestAnimationFrame(tick);
      }
    }

    frameId = requestAnimationFrame(tick);

    return () => cancelAnimationFrame(frameId);
  }, [target]);

  const size = 96;
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset =
    circumference - (value / 100) * circumference;

  return (
    <div
      className="relative flex shrink-0 items-center justify-center"
      style={{ width: size, height: size }}
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
          strokeWidth={strokeWidth}
        />

        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          className="text-emerald-300"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition:
              "stroke-dashoffset 0.15s linear",
          }}
        />

      </svg>


      <div className="absolute flex items-baseline">
        <span className="text-3xl font-bold tracking-tight text-emerald-300">
          {value}
        </span>

        <span className="ml-0.5 text-xs text-gray-500">
          /100
        </span>
      </div>

    </div>
  );
}


function ProcessCard({
  icon,
  number,
  label,
  title,
  children,
}) {
  return (
    <article className="rounded-2xl border border-border-soft bg-white p-6 transition duration-200 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-950/5">

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand">
        {icon}
      </div>

      <p className="mt-7 text-[11px] font-bold tracking-[0.14em] text-brand">
        {number} · {label}
      </p>

      <h3 className="mt-3 text-lg font-semibold tracking-tight text-midnight">
        {title}
      </h3>

      <p className="mt-3 text-sm leading-7 text-text-muted">
        {children}
      </p>

    </article>
  );
}


function InsightRow({
  label,
  value,
  type,
}) {
  const statusClasses = {
    success:
      "bg-emerald-50 text-emerald-700",

    warning:
      "bg-amber-50 text-amber-700",

    danger:
      "bg-red-50 text-red-700",
  };

  return (
    <div className="flex flex-col gap-3 py-7 sm:flex-row sm:items-center sm:justify-between">

      <span className="text-sm text-text-muted">
        {label}
      </span>

      <span
        className={`rounded-lg px-3 py-2 text-sm font-semibold ${
          statusClasses[type]
        }`}
      >
        {value}
      </span>

    </div>
  );
}


export default Home;