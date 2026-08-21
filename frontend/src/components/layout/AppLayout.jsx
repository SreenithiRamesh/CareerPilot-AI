import {
  useEffect,
  useState,
} from "react";

import {
  Outlet,
  useLocation,
} from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";


function AppLayout() {
  const location =
    useLocation();

  const [
    mobileSidebarOpen,
    setMobileSidebarOpen,
  ] = useState(false);


  function openMobileSidebar() {
    setMobileSidebarOpen(true);
  }


  function closeMobileSidebar() {
    setMobileSidebarOpen(false);
  }


  /*
   * Close mobile navigation after route change.
   */

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    closeMobileSidebar();
  }, [location.pathname]);


  /*
   * Escape key closes sidebar.
   */

  useEffect(() => {
    function handleEscape(event) {
      if (
        event.key === "Escape"
      ) {
        closeMobileSidebar();
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


  /*
   * Prevent background scrolling
   * while mobile sidebar is open.
   */

  useEffect(() => {
    if (mobileSidebarOpen) {
      document.body.style.overflow =
        "hidden";
    } else {
      document.body.style.overflow =
        "";
    }


    return () => {
      document.body.style.overflow =
        "";
    };
  }, [mobileSidebarOpen]);


  return (
    <div className="min-h-screen bg-app-bg">

      <Sidebar
        mobileOpen={
          mobileSidebarOpen
        }
        onClose={
          closeMobileSidebar
        }
      />


      <div className="min-h-screen lg:pl-[260px]">

        <Topbar
          onMenuClick={
            openMobileSidebar
          }
        />


        <main className="px-4 py-6 sm:px-6 lg:px-8 xl:px-10">

          <div className="mx-auto max-w-[1440px]">
            <Outlet />
          </div>

        </main>

      </div>

    </div>
  );
}


export default AppLayout;