import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  Gauge,
  Navigation,
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

      <section className="bg-midnight text-white">
        <div className="mx-auto grid min-h-[650px] max-w-[1440px] items-center gap-10 px-4 py-20 sm:px-6 sm:py-24 lg:grid-cols-[1.08fr_0.92fr] lg:px-8 lg:py-28 xl:gap-14 xl:px-10">

          <div className="max-w-[760px]">
            <p className="text-xs font-bold tracking-[0.16em] text-brand-accent">
              AGENTIC CAREER MENTOR
            </p>

            <h1 className="mt-5 text-4xl font-bold leading-[1.04] tracking-[-0.045em] sm:text-5xl lg:text-6xl xl:text-[68px]">
              Know where your resume stands.

              <span className="mt-2 block text-emerald-100">
                Know what to improve next.
              </span>
            </h1>

            <p className="mt-7 max-w-[650px] text-base leading-8 text-gray-300 sm:text-lg">
              CareerPilot analyzes your resume, compares it
              with your target role, identifies skill gaps,
              and turns the findings into a practical career
              action plan.
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


            <p className="mt-6 text-xs font-medium tracking-wide text-gray-400">
              BUILT FOR STUDENTS AND FRESH GRADUATES
            </p>
          </div>


          {/* HERO REPORT PREVIEW */}

          <div className="w-full rounded-2xl border border-gray-700 bg-gray-800/80 p-5 shadow-2xl shadow-black/20 sm:p-7 lg:justify-self-end">

            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[11px] font-bold tracking-[0.14em] text-brand-accent">
                  RESUME ANALYSIS
                </p>

                <h2 className="mt-2 text-lg font-semibold">
                  Software Engineer
                </h2>
              </div>

              <span className="rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300">
                Analysis ready
              </span>
            </div>


            <div className="mt-8 flex items-center gap-5 border-b border-gray-700 pb-7">

              <div>
                <span className="text-5xl font-bold tracking-tight text-emerald-300">
                  60
                </span>

                <span className="ml-1 text-sm text-gray-400">
                  /100
                </span>
              </div>

              <div>
                <p className="font-semibold">
                  Job Match Score
                </p>

                <p className="mt-1 text-xs leading-5 text-gray-400">
                  Based on resume evidence and
                  target-role requirements.
                </p>
              </div>

            </div>


            <div className="mt-5 space-y-3">

              <div className="grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-gray-700 bg-midnight/60 p-4">
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


              <div className="grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-gray-700 bg-midnight/60 p-4">
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


              <div className="grid grid-cols-[auto_1fr] gap-x-3 rounded-xl border border-gray-700 bg-midnight/60 p-4">
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