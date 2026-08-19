import {
  LogOut,
  Menu,
} from "lucide-react";

import { useNavigate } from "react-router-dom";


function Topbar() {
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


  const email =
    user.email ||
    "CareerPilot user";

  const initial =
    email
      .charAt(0)
      .toUpperCase();


  return (
    <header className="sticky top-0 z-30 h-[72px] border-b border-border-soft bg-white/95 backdrop-blur">

      <div className="mx-auto flex h-full max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-10">

        {/* Mobile placeholder */}

        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-border-soft text-midnight lg:hidden"
          aria-label="Open navigation"
        >
          <Menu size={19} />
        </button>


        <div className="hidden lg:block">
          <p className="text-xs font-medium text-text-muted">
            CareerPilot workspace
          </p>

          <p className="mt-0.5 text-sm font-semibold text-midnight">
            Build your next career move
          </p>
        </div>


        <div className="flex items-center gap-3">

          <div className="hidden text-right sm:block">
            <p className="max-w-[220px] truncate text-sm font-semibold text-midnight">
              {email}
            </p>

            <p className="text-xs text-text-muted">
              Signed in
            </p>
          </div>


          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-soft text-sm font-bold text-brand">
            {initial}
          </div>


          <button
            type="button"
            onClick={handleLogout}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border-soft bg-white text-text-muted transition hover:border-gray-300 hover:bg-gray-50 hover:text-midnight"
            aria-label="Sign out"
          >
            <LogOut size={17} />
          </button>

        </div>

      </div>

    </header>
  );
}


export default Topbar;