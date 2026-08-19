import {
  ArrowRight,
  FileText,
  Gauge,
  LogOut,
  Navigation,
  Route,
  Sparkles,
} from "lucide-react";

import { useNavigate } from "react-router-dom";


function Dashboard() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem(
      "careerpilot_user"
    ) || "{}"
  );


  function handleLogout() {
    localStorage.removeItem(
      "careerpilot_token"
    );

    localStorage.removeItem(
      "careerpilot_user"
    );

    navigate(
      "/login",
      {
        replace: true,
      }
    );
  }


  return (
    <main className="min-h-screen bg-app-bg">

      {/* ================= TOP BAR ================= */}

      <header className="border-b border-border-soft bg-white">
        <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-10">

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-midnight text-white">
              <Navigation
                size={19}
                strokeWidth={2.4}
              />
            </div>

            <div>
              <p className="font-bold tracking-tight text-midnight">
                CareerPilot
                <span className="text-brand">
                  {" "}AI
                </span>
              </p>

              <p className="text-xs text-text-muted">
                Career workspace
              </p>
            </div>
          </div>


          <div className="flex items-center gap-4">

            <div className="hidden text-right sm:block">
              <p className="text-sm font-semibold text-midnight">
                {user.email || "CareerPilot user"}
              </p>

              <p className="text-xs text-text-muted">
                Signed in
              </p>
            </div>


            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-border-soft bg-white px-4 text-sm font-semibold text-midnight transition hover:border-gray-300 hover:bg-gray-50"
            >
              <LogOut size={16} />

              <span className="hidden sm:inline">
                Sign out
              </span>
            </button>

          </div>
        </div>
      </header>


      {/* ================= CONTENT ================= */}

      <section className="mx-auto max-w-[1440px] px-4 py-10 sm:px-6 lg:px-8 lg:py-14 xl:px-10">

        {/* Welcome */}

        <div className="max-w-3xl">

          <p className="text-xs font-bold tracking-[0.15em] text-brand">
            DASHBOARD
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
            Welcome back to CareerPilot.
          </h1>

          <p className="mt-4 max-w-2xl leading-7 text-text-muted">
            Your career workspace is ready.
            Continue from your resume, compare
            against a target role, or review your
            next preparation priorities.
          </p>

        </div>


        {/* Quick Actions */}

        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

          <DashboardCard
            icon={<FileText size={21} />}
            label="RESUME"
            title="Upload or review resume"
            description="Use your latest resume as the evidence base for CareerPilot analysis."
            action="Manage resume"
          />

          <DashboardCard
            icon={<Gauge size={21} />}
            label="JOB MATCH"
            title="Compare with a target role"
            description="See strong matches, partial matches, missing skills, and priority actions."
            action="Run job match"
          />

          <DashboardCard
            icon={<Sparkles size={21} />}
            label="SKILL GAP"
            title="Focus your learning"
            description="Identify the gaps that matter most for the role you want."
            action="View skill gaps"
          />

          <DashboardCard
            icon={<Route size={21} />}
            label="CAREER PLAN"
            title="Build your next-step plan"
            description="Turn analysis into a focused roadmap with practical tasks and preparation priorities."
            action="Open career plan"
          />

        </div>


        {/* Current Status */}

        <div className="mt-10 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">

          <section className="rounded-2xl border border-border-soft bg-white p-6 shadow-sm sm:p-7">

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div>
                <p className="text-xs font-bold tracking-[0.14em] text-brand">
                  CAREER STATUS
                </p>

                <h2 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
                  Your CareerPilot workspace
                </h2>
              </div>


              <span className="w-fit rounded-full bg-brand-soft px-3 py-1.5 text-xs font-semibold text-brand">
                Ready
              </span>

            </div>


            <div className="mt-7 grid gap-4 sm:grid-cols-3">

              <StatusItem
                title="Resume"
                value="Ready for analysis"
              />

              <StatusItem
                title="Job match"
                value="Choose a target role"
              />

              <StatusItem
                title="Career plan"
                value="Generated after analysis"
              />

            </div>

          </section>


          <section className="rounded-2xl bg-midnight p-6 text-white shadow-sm sm:p-7">

            <p className="text-xs font-bold tracking-[0.14em] text-brand-accent">
              NEXT BEST STEP
            </p>

            <h2 className="mt-3 text-2xl font-semibold tracking-tight">
              Start with your resume.
            </h2>

            <p className="mt-4 leading-7 text-gray-300">
              Upload or select your resume first.
              CareerPilot uses it as the foundation
              for role matching, skill-gap analysis,
              and career planning.
            </p>


            <button
              type="button"
              className="mt-6 inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover"
            >
              Go to resume

              <ArrowRight size={16} />
            </button>

          </section>

        </div>

      </section>

    </main>
  );
}


function DashboardCard({
  icon,
  label,
  title,
  description,
  action,
}) {
  return (
    <article className="group rounded-2xl border border-border-soft bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-950/5">

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand">
        {icon}
      </div>


      <p className="mt-6 text-[11px] font-bold tracking-[0.14em] text-brand">
        {label}
      </p>


      <h3 className="mt-2 text-lg font-semibold tracking-tight text-midnight">
        {title}
      </h3>


      <p className="mt-3 text-sm leading-7 text-text-muted">
        {description}
      </p>


      <button
        type="button"
        className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand transition group-hover:text-brand-hover"
      >
        {action}

        <ArrowRight size={15} />
      </button>

    </article>
  );
}


function StatusItem({
  title,
  value,
}) {
  return (
    <div className="rounded-xl border border-border-soft bg-app-bg p-4">

      <p className="text-xs font-medium text-text-muted">
        {title}
      </p>

      <p className="mt-2 text-sm font-semibold text-midnight">
        {value}
      </p>

    </div>
  );
}


export default Dashboard;