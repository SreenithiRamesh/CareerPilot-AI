import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";

import CareerAI from "./pages/CareerAI";
import CareerPlan from "./pages/CareerPlan";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import JobMatch from "./pages/JobMatch";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Resume from "./pages/Resume";
import SkillGap from "./pages/SkillGap";


function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public */}

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />


        {/* Protected workspace */}

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/resume"
            element={<Resume />}
          />

          <Route
            path="/career-ai"
            element={<CareerAI />}
          />

          <Route
            path="/job-match"
            element={<JobMatch />}
          />

          <Route
            path="/skill-gap"
            element={<SkillGap />}
          />

          <Route
            path="/career-plan"
            element={<CareerPlan />}
          />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}


export default App;