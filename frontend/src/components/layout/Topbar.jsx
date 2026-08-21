import {
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Menu,
  UserRound,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";


function Topbar({
  onMenuClick,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  const profileMenuRef =
    useRef(null);

  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false);


  const user = JSON.parse(
    localStorage.getItem(
      "careerpilot_user"
    ) || "{}"
  );


  const email =
    user.email ||
    "CareerPilot user";


  const initial =
    email
      .charAt(0)
      .toUpperCase();


  /* ==================================================
     LOGOUT
     ================================================== */

  function handleLogout() {
    setProfileOpen(false);


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


  /* ==================================================
     DASHBOARD NAVIGATION
     ================================================== */

  function handleDashboard() {

    setProfileOpen(false);

    navigate(
      "/dashboard"
    );
  }


  /* ==================================================
     PROFILE TOGGLE
     ================================================== */

  function handleProfileToggle() {
    setProfileOpen(
      (current) =>
        !current
    );
  }


  /* ==================================================
     CLICK OUTSIDE PROFILE MENU
     ================================================== */

  useEffect(() => {
    function handleOutsideClick(
      event
    ) {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(
          event.target
        )
      ) {
        setProfileOpen(false);
      }
    }


    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );


    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);


  /* ==================================================
     ESCAPE KEY
     ================================================== */

  useEffect(() => {
    function handleEscape(
      event
    ) {
      if (
        event.key === "Escape"
      ) {
        setProfileOpen(false);
      }
    }


    document.addEventListener(
      "keydown",
      handleEscape
    );


    return () => {
      document.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, []);


  /* ==================================================
     CLOSE PROFILE MENU AFTER ROUTE CHANGE
     ================================================== */

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setProfileOpen(false);
  }, [location.pathname]);


  return (
    <header className="sticky top-0 z-30 h-[72px] border-b border-border-soft bg-white/95 backdrop-blur">

      <div className="mx-auto flex h-full max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-10">

        {/* ==================================================
            MOBILE MENU
            ================================================== */}

        <button
          type="button"
          onClick={onMenuClick}
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-border-soft text-midnight transition hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-emerald-500/10 lg:hidden"
          aria-label="Open navigation"
        >
          <Menu size={19} />
        </button>


        {/* ==================================================
            WORKSPACE LABEL
            ================================================== */}

        <div className="hidden lg:block">

          <p className="text-xs font-medium text-text-muted">
            CareerPilot workspace
          </p>

          <p className="mt-0.5 text-sm font-semibold text-midnight">
            Build your next career move
          </p>

        </div>


        {/* ==================================================
            PROFILE AREA
            ================================================== */}

        <div
          ref={profileMenuRef}
          className="relative"
        >

          <button
            type="button"
            onClick={
              handleProfileToggle
            }
            aria-label="Open profile menu"
            aria-haspopup="menu"
            aria-expanded={
              profileOpen
            }
            className="group flex items-center gap-3 rounded-xl px-2 py-1.5 text-left transition hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-emerald-500/10"
          >

            {/* Desktop email */}

            <div className="hidden min-w-0 text-right sm:block">

              <p className="max-w-[220px] truncate text-sm font-semibold text-midnight">
                {email}
              </p>

              <p className="text-xs text-text-muted">
                Signed in
              </p>

            </div>


            {/* Avatar */}

            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-soft text-sm font-bold text-brand ring-1 ring-emerald-100">
              {initial}
            </div>


            {/* Chevron */}

            <ChevronDown
              size={16}
              className={`hidden text-gray-400 transition-transform sm:block ${
                profileOpen
                  ? "rotate-180"
                  : ""
              }`}
            />

          </button>


          {/* ==================================================
              DROPDOWN
              ================================================== */}

          {profileOpen && (
            <div
              role="menu"
              className="absolute right-0 top-[calc(100%+10px)] z-50 w-[270px] overflow-hidden rounded-xl border border-border-soft bg-white shadow-xl shadow-gray-900/10"
            >

              {/* User identity */}

              <div className="border-b border-border-soft p-4">

                <div className="flex items-center gap-3">

                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-soft text-sm font-bold text-brand">
                    {initial}
                  </div>


                  <div className="min-w-0 flex-1">

                    <div className="flex items-center gap-1.5">

                      <UserRound
                        size={14}
                        className="shrink-0 text-brand"
                      />

                      <p className="text-sm font-semibold text-midnight">
                        Signed-in user
                      </p>

                    </div>


                    <p
                      title={email}
                      className="mt-1 truncate text-xs text-text-muted"
                    >
                      {email}
                    </p>

                  </div>

                </div>

              </div>


              {/* Navigation */}

              <div className="p-2">

                <button
                  type="button"
                  role="menuitem"
                  onClick={
                    handleDashboard
                  }
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-midnight transition hover:bg-app-bg focus:bg-app-bg focus:outline-none"
                >
                  <LayoutDashboard
                    size={17}
                    className="text-text-muted"
                  />

                  Dashboard
                </button>

              </div>


              {/* Logout */}

              <div className="border-t border-border-soft p-2">

                <button
                  type="button"
                  role="menuitem"
                  onClick={
                    handleLogout
                  }
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50 focus:bg-red-50 focus:outline-none"
                >
                  <LogOut
                    size={17}
                  />

                  Sign out
                </button>

              </div>

            </div>
          )}

        </div>

      </div>

    </header>
  );
}


export default Topbar;