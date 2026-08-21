import {
  FileSearch,
  FileText,
  Gauge,
  History,
  LayoutDashboard,
  MessageSquareText,
  MicVocal,
  Navigation,
  Route,
  Sparkles,
  X,
} from "lucide-react";

import {
  NavLink,
} from "react-router-dom";


const navigationItems = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Resume",
    path: "/resume",
    icon: FileText,
  },
  {
    label: "Career AI",
    path: "/career-ai",
    icon: MessageSquareText,
  },
  {
    label: "Job Match",
    path: "/job-match",
    icon: Gauge,
  },
  {
    label: "Skill Gap",
    path: "/skill-gap",
    icon: Sparkles,
  },
  {
    label: "Career Plan",
    path: "/career-plan",
    icon: Route,
  },
  {
    label: "Mock Interview",
    path: "/mock-interview",
    icon: MicVocal,
  },
  {
    label: "History",
    path: "/history",
    icon: History,
  },
];


function Sidebar({
  mobileOpen = false,
  onClose,
}) {
  return (
    <>
      {/* ================= MOBILE BACKDROP ================= */}

      {mobileOpen && (
        <button
          type="button"
          onClick={onClose}
          aria-label="Close navigation"
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-[1px] lg:hidden"
        />
      )}


      {/* ================= SIDEBAR ================= */}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50
          flex w-[260px] flex-col
          border-r border-gray-800
          bg-midnight text-white
          transition-transform duration-200 ease-out
          lg:z-40 lg:translate-x-0
          ${
            mobileOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }
        `}
        aria-label="CareerPilot navigation"
      >

        {/* ================= BRAND ================= */}

        <div className="flex h-[72px] items-center justify-between border-b border-gray-800 px-5 lg:px-6">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white">

              <Navigation
                size={18}
                strokeWidth={2.4}
              />

            </div>


            <div>

              <p className="text-sm font-bold tracking-tight">
                CareerPilot

                <span className="text-brand-accent">
                  {" "}AI
                </span>
              </p>


              <p className="mt-0.5 text-[11px] text-gray-500">
                Career workspace
              </p>

            </div>

          </div>


          {/* Mobile close */}

          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition hover:bg-gray-800 hover:text-white lg:hidden"
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>

        </div>


        {/* ================= NAVIGATION ================= */}

        <nav className="flex-1 overflow-y-auto px-3 py-5">

          <p className="mb-3 px-3 text-[10px] font-bold tracking-[0.14em] text-gray-500">
            WORKSPACE
          </p>


          <div className="space-y-1">

            {navigationItems.map(
              ({
                label,
                path,
                icon: Icon,
              }) => (
                <NavLink
                  key={path}
                  to={path}
                  end={
                    path ===
                    "/dashboard"
                  }
                  onClick={
                    onClose
                  }
                  className={({
                    isActive,
                  }) =>
                    [
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",

                      isActive
                        ? "bg-brand text-white shadow-sm"
                        : "text-gray-400 hover:bg-gray-800 hover:text-white",
                    ].join(" ")
                  }
                >

                  <Icon
                    size={18}
                    className="shrink-0"
                  />


                  <span>
                    {label}
                  </span>

                </NavLink>
              )
            )}

          </div>

        </nav>


        {/* ================= BOTTOM INFO ================= */}

        <div className="border-t border-gray-800 p-4">

          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">

            <div className="flex items-start gap-3">

              <FileSearch
                size={18}
                className="mt-0.5 shrink-0 text-brand-accent"
              />


              <div>

                <p className="text-xs font-semibold text-white">
                  Resume-driven guidance
                </p>


                <p className="mt-1 text-[11px] leading-5 text-gray-500">
                  CareerPilot grounds role analysis
                  in your selected resume.
                </p>

              </div>

            </div>

          </div>

        </div>

      </aside>
    </>
  );
}


export default Sidebar;