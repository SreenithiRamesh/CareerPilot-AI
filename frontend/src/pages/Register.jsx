import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";
import {
  ArrowRight,
  LockKeyhole,
  Mail,
  Navigation,
  UserPlus,
} from "lucide-react";

import api from "../services/api";


function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }


  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await api.post(
        "/api/auth/register",
        form
      );

      navigate("/login");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to create your account. Please try again."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="min-h-screen bg-app-bg lg:grid lg:grid-cols-[1.05fr_0.95fr]">

      {/* ================= LEFT BRAND PANEL ================= */}

      <section className="relative hidden min-h-screen overflow-hidden bg-midnight px-10 py-10 text-white lg:flex lg:flex-col lg:justify-between xl:px-16 xl:py-12">

        <div className="pointer-events-none absolute -left-24 top-20 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />

        <div className="pointer-events-none absolute -bottom-32 right-0 h-96 w-96 rounded-full bg-emerald-400/10 blur-3xl" />


        <Link
          to="/"
          className="relative z-10 flex items-center gap-3"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-white">
            <Navigation
              size={19}
              strokeWidth={2.4}
            />
          </div>

          <span className="text-base font-bold tracking-tight">
            CareerPilot
            <span className="text-brand-accent">
              {" "}AI
            </span>
          </span>
        </Link>


        <div className="relative z-10 max-w-xl">
          <p className="text-xs font-bold tracking-[0.16em] text-brand-accent">
            START YOUR CAREER JOURNEY
          </p>

          <h1 className="mt-5 text-5xl font-bold leading-[1.05] tracking-[-0.045em] xl:text-6xl">
            Build your career with direction.
          </h1>

          <p className="mt-6 max-w-lg text-base leading-8 text-gray-300">
            Create your CareerPilot account, upload your
            resume, and turn role requirements into a
            focused preparation roadmap.
          </p>


          <div className="mt-10 grid gap-3 sm:grid-cols-2">

            <div className="rounded-xl border border-gray-700 bg-white/5 p-4">
              <p className="text-xs font-semibold text-gray-400">
                RESUME ANALYSIS
              </p>

              <p className="mt-2 text-sm font-medium text-white">
                Understand the evidence already present
                in your resume.
              </p>
            </div>


            <div className="rounded-xl border border-gray-700 bg-white/5 p-4">
              <p className="text-xs font-semibold text-gray-400">
                SKILL GAP
              </p>

              <p className="mt-2 text-sm font-medium text-white">
                Focus your learning on the gaps that
                matter for your target role.
              </p>
            </div>

          </div>
        </div>


        <p className="relative z-10 text-xs text-gray-500">
          © 2026 CareerPilot AI
        </p>
      </section>


      {/* ================= REGISTER PANEL ================= */}

      <section className="flex min-h-screen items-center justify-center px-5 py-10 sm:px-8 lg:px-12">

        <div className="w-full max-w-[440px]">

          {/* Mobile Brand */}

          <Link
            to="/"
            className="mb-10 flex items-center gap-3 lg:hidden"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-midnight text-white">
              <Navigation
                size={19}
                strokeWidth={2.4}
              />
            </div>

            <span className="font-bold tracking-tight text-midnight">
              CareerPilot
              <span className="text-brand">
                {" "}AI
              </span>
            </span>
          </Link>


          <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand">
            <UserPlus size={20} />
          </div>


          <p className="text-xs font-bold tracking-[0.15em] text-brand">
            CREATE YOUR ACCOUNT
          </p>

          <h2 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
            Start with CareerPilot
          </h2>

          <p className="mt-3 leading-7 text-text-muted">
            Create your account and begin building
            a more focused career preparation plan.
          </p>


          <form
            className="mt-8 space-y-5"
            onSubmit={handleSubmit}
          >

            {/* Email */}

            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-semibold text-midnight"
              >
                Email address
              </label>

              <div className="relative">

                <Mail
                  size={18}
                  className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={handleChange}
                  required
                  className="h-12 w-full rounded-lg border border-border-soft bg-white pl-11 pr-4 text-sm text-midnight outline-none transition placeholder:text-gray-400 focus:border-brand focus:ring-4 focus:ring-emerald-500/10"
                />

              </div>
            </div>


            {/* Password */}

            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-semibold text-midnight"
              >
                Password
              </label>

              <div className="relative">

                <LockKeyhole
                  size={18}
                  className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="Minimum 8 characters"
                  value={form.password}
                  onChange={handleChange}
                  minLength={8}
                  maxLength={72}
                  required
                  className="h-12 w-full rounded-lg border border-border-soft bg-white pl-11 pr-4 text-sm text-midnight outline-none transition placeholder:text-gray-400 focus:border-brand focus:ring-4 focus:ring-emerald-500/10"
                />

              </div>

              <p className="mt-2 text-xs leading-5 text-gray-400">
                Use at least 8 characters. Keep your
                password private and unique.
              </p>
            </div>


            {/* Error */}

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700">
                {error}
              </div>
            )}


            {/* Submit */}

            <button
              type="submit"
              disabled={loading}
              className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-hover focus:outline-none focus:ring-4 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Creating account..."
                : (
                  <>
                    Create account
                    <ArrowRight size={17} />
                  </>
                )
              }
            </button>

          </form>


          <div className="my-7 flex items-center gap-4">
            <div className="h-px flex-1 bg-border-soft" />

            <span className="text-xs font-medium text-gray-400">
              CAREERPILOT AI
            </span>

            <div className="h-px flex-1 bg-border-soft" />
          </div>


          <p className="text-center text-sm text-text-muted">
            Already have an account?{" "}

            <Link
              to="/login"
              className="font-semibold text-brand transition hover:text-brand-hover"
            >
              Sign in
            </Link>
          </p>


          <p className="mt-8 text-center text-xs leading-5 text-gray-400">
            CareerPilot provides AI-assisted guidance
            to support your preparation and career decisions.
          </p>

        </div>
      </section>

    </main>
  );
}


export default Register;