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
import History from "./pages/History";
import Home from "./pages/Home";
import JobMatch from "./pages/JobMatch";
import Login from "./pages/Login";
import MockInterview from "./pages/MockInterview";
import Register from "./pages/Register";
import Resume from "./pages/Resume";
import SkillGap from "./pages/SkillGap";


function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* ============================================
            PUBLIC ROUTES
            ============================================ */}

        <Route
          path="/"
          element={
            <Home />
          }
        />


        <Route
          path="/login"
          element={
            <Login />
          }
        />


        <Route
          path="/register"
          element={
            <Register />
          }
        />


        {/* ============================================
            PROTECTED CAREERPILOT WORKSPACE
            ============================================ */}

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >

          {/* Dashboard */}

          <Route
            path="/dashboard"
            element={
              <Dashboard />
            }
          />


          {/* Resume */}

          <Route
            path="/resume"
            element={
              <Resume />
            }
          />


          {/* Career AI */}

          <Route
            path="/career-ai"
            element={
              <CareerAI />
            }
          />


          {/* Job Match */}

          <Route
            path="/job-match"
            element={
              <JobMatch />
            }
          />


          {/* Skill Gap */}

          <Route
            path="/skill-gap"
            element={
              <SkillGap />
            }
          />


          {/* Career Plan */}

          <Route
            path="/career-plan"
            element={
              <CareerPlan />
            }
          />


          {/* Mock Interview */}

          <Route
            path="/mock-interview"
            element={
              <MockInterview />
            }
          />


          {/* Analysis History */}

          <Route
            path="/history"
            element={
              <History />
            }
          />

        </Route>

      </Routes>

    </BrowserRouter>
  );
}


export default App;