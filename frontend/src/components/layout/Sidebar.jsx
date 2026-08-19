import {
  FileSearch,
  FileText,
  Gauge,
  LayoutDashboard,
  MessageSquareText,
  Navigation,
  Route,
  Sparkles,
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
];


function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[260px] border-r border-gray-800 bg-midnight text-white lg:flex lg:flex-col">

      {/* Brand */}

      <div className="flex h-[72px] items-center border-b border-gray-800 px-6">

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

      </div>


      {/* Navigation */}

      <nav className="flex-1 px-3 py-5">

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
                end={path === "/dashboard"}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
                    isActive
                      ? "bg-brand text-white shadow-sm"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white",
                  ].join(" ")
                }
              >
                <Icon size={18} />

                <span>
                  {label}
                </span>
              </NavLink>
            )
          )}

        </div>

      </nav>


      {/* Bottom info */}

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
  );
}


export default Sidebar;