import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";


function AppLayout() {
  return (
    <div className="min-h-screen bg-app-bg">
      <Sidebar />

      <div className="min-h-screen lg:pl-[260px]">
        <Topbar />

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