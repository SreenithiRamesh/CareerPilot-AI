import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  FileText,
  Gauge,
  History as HistoryIcon,
  LoaderCircle,
  XCircle,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import api from "../services/api";


function History() {
  const navigate =
    useNavigate();

  const [items, setItems] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const response =
        await api.get(
          "/api/analysis/history"
        );

      setItems(
        response.data?.items ||
        []
      );

    } catch (err) {
   
      setError(
        err.response?.data?.detail ||
        err.message ||
        "CareerPilot could not load your analysis history."
      );
    }
      finally {
    setLoading(false);
  }

  
  }
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadHistory();
  }, []);





  return (
    <section>

      {/* ================= HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          ANALYSIS HISTORY
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Review your previous career analyses
        </h1>

        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          Revisit past Job Match, Skill Gap,
          and Career Plan results without
          rerunning the entire workflow.
        </p>

      </div>


      {/* ================= LOADING ================= */}

      {loading && (
        <div className="mt-10 flex min-h-[280px] items-center justify-center rounded-2xl border border-border-soft bg-white shadow-sm">

          <div className="flex items-center gap-3 text-sm text-text-muted">

            <LoaderCircle
              size={20}
              className="animate-spin text-brand"
            />

            Loading analysis history...

          </div>

        </div>
      )}


      {/* ================= ERROR ================= */}

      {!loading && error && (
        <div className="mt-8 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">

          <XCircle
            size={18}
            className="mt-0.5 shrink-0"
          />

          <div>

            <p className="font-semibold">
              Could not load history
            </p>

            <p className="mt-1">
              {error}
            </p>

          </div>

        </div>
      )}


      {/* ================= EMPTY STATE ================= */}

      {!loading &&
        !error &&
        items.length === 0 && (
          <div className="mt-10 flex flex-col items-center rounded-2xl border border-dashed border-border-soft bg-white px-6 py-14 text-center shadow-sm">

            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-soft text-brand">
              <HistoryIcon
                size={24}
              />
            </div>

            <h2 className="mt-5 text-xl font-semibold tracking-tight text-midnight">
              No analysis history yet
            </h2>

            <p className="mt-3 max-w-md text-sm leading-7 text-text-muted">
              Run a Job Match and Skill Gap
              analysis to begin building your
              CareerPilot history.
            </p>

            <button
              type="button"
              onClick={() =>
                navigate(
                  "/job-match"
                )
              }
              className="mt-6 inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover"
            >
              Run Job Match

              <ArrowRight
                size={16}
              />
            </button>

          </div>
        )}


      {/* ================= HISTORY GRID ================= */}

      {!loading &&
        !error &&
        items.length > 0 && (
          <>

            <div className="mt-8 flex items-center justify-between">

              <p className="text-sm text-text-muted">
                {items.length} saved analysis
                {items.length === 1
                  ? ""
                  : "es"}
              </p>

            </div>


            <div className="mt-5 grid gap-5 xl:grid-cols-2">

              {items.map(
                (item) => (
                  <HistoryCard
                    key={
                      `${item.resume_id}-${item.job_description_id}`
                    }
                    item={item}
                    onOpen={() =>
                      openHistoricalAnalysis(
                        item,
                        navigate
                      )
                    }
                  />
                )
              )}

            </div>

          </>
        )}

    </section>
  );
}


/* ==================================================
   HISTORY CARD
   ================================================== */

function HistoryCard({
  item,
  onOpen,
}) {
  const strongMatches =
    Array.isArray(
      item.strong_matches
    )
      ? item.strong_matches.slice(
          0,
          3
        )
      : [];

  const gaps =
    Array.isArray(
      item.high_priority_gaps
    )
      ? item.high_priority_gaps.slice(
          0,
          3
        )
      : [];

  const roleTitle =
    item.job_title ||
    "Career Analysis";

  const companyName =
    item.company_name ||
    null;

  const date =
    formatDate(
      item.analyzed_at
    );


  return (
    <article className="group flex h-full flex-col rounded-2xl border border-border-soft bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-950/5">

      {/* Top */}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

        <div className="min-w-0">

          <div className="flex items-center gap-2 text-brand">

            <HistoryIcon
              size={15}
            />

            <p className="text-[11px] font-bold tracking-[0.14em]">
              SAVED ANALYSIS
            </p>

          </div>

          <h2 className="mt-3 text-xl font-semibold tracking-tight text-midnight">
            {roleTitle}
          </h2>

          {companyName && (
            <p className="mt-1 text-sm text-text-muted">
              {companyName}
            </p>
          )}

        </div>


        <div className="flex h-16 w-16 shrink-0 flex-col items-center justify-center rounded-2xl bg-brand-soft">

          <p className="text-xl font-bold text-brand">
            {item.match_score}
          </p>

          <p className="text-[10px] font-semibold uppercase tracking-wide text-brand">
            Match
          </p>

        </div>

      </div>


      {/* Resume + date */}

      <div className="mt-5 grid gap-3 sm:grid-cols-2">

        <InfoRow
          icon={
            <FileText
              size={15}
            />
          }
          label="Resume"
          value={
            item.resume_filename
          }
        />

        <InfoRow
          icon={
            <CalendarDays
              size={15}
            />
          }
          label="Analyzed"
          value={date}
        />

      </div>


      {/* Skills */}

      <div className="mt-6 grid gap-5 sm:grid-cols-2">

        <div>

          <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-brand">
            Strong Matches
          </p>

          {strongMatches.length >
          0 ? (
            <div className="mt-3 flex flex-wrap gap-2">

              {strongMatches.map(
                (
                  skill,
                  index
                ) => (
                  <span
                    key={`${skill}-${index}`}
                    className="rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700"
                  >
                    {skill}
                  </span>
                )
              )}

            </div>
          ) : (
            <p className="mt-3 text-sm text-text-muted">
              No matching skills saved.
            </p>
          )}

        </div>


        <div>

          <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-red-500">
            Priority Gaps
          </p>

          {gaps.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">

              {gaps.map(
                (
                  skill,
                  index
                ) => (
                  <span
                    key={`${skill}-${index}`}
                    className="rounded-full border border-red-100 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-600"
                  >
                    {skill}
                  </span>
                )
              )}

            </div>
          ) : (
            <p className="mt-3 flex items-center gap-2 text-sm text-text-muted">

              <CheckCircle2
                size={15}
                className="text-brand"
              />

              No high-priority gaps

            </p>
          )}

        </div>

      </div>


      {/* Summary */}

      {item.readiness_summary && (
        <div className="mt-6 rounded-xl border border-border-soft bg-app-bg p-4">

          <p className="text-[11px] font-bold uppercase tracking-[0.13em] text-brand">
            Readiness Summary
          </p>

          <p className="mt-2 line-clamp-4 text-sm leading-6 text-text-muted">
            {item.readiness_summary}
          </p>

        </div>
      )}


      {/* Availability */}

      <div className="mt-5 flex flex-wrap gap-2">

        <StatusBadge
          label="Job Match"
          available={
            Boolean(
              item.job_match_result_id
            )
          }
        />

        <StatusBadge
          label="Skill Gap"
          available={
            Boolean(
              item.skill_gap_report_id
            )
          }
        />

        <StatusBadge
          label="Career Plan"
          available={
            Boolean(
              item.career_plan_id
            )
          }
        />

      </div>


      {/* Action */}

      <div className="mt-auto pt-6">

        <button
          type="button"
          onClick={onOpen}
          className="inline-flex items-center gap-2 text-sm font-semibold text-brand transition group-hover:text-brand-hover"
        >
          View analysis

          <ArrowRight
            size={15}
            className="transition-transform group-hover:translate-x-1"
          />
        </button>

      </div>

    </article>
  );
}


/* ==================================================
   INFO ROW
   ================================================== */

function InfoRow({
  icon,
  label,
  value,
}) {
  return (
    <div className="flex gap-3 rounded-xl border border-border-soft bg-app-bg p-3">

      <div className="mt-0.5 text-brand">
        {icon}
      </div>

      <div className="min-w-0">

        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-text-muted">
          {label}
        </p>

        <p
          title={value}
          className="mt-1 truncate text-xs font-semibold text-midnight"
        >
          {value}
        </p>

      </div>

    </div>
  );
}


/* ==================================================
   STATUS BADGE
   ================================================== */

function StatusBadge({
  label,
  available,
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ${
        available
          ? "bg-brand-soft text-brand"
          : "bg-gray-100 text-gray-400"
      }`}
    >

      {available ? (
        <CheckCircle2
          size={12}
        />
      ) : (
        <Gauge
          size={12}
        />
      )}

      {label}

    </span>
  );
}


/* ==================================================
   OPEN HISTORICAL ANALYSIS
   ================================================== */

function openHistoricalAnalysis(
  item,
  navigate
) {
  /*
   * For now we persist the selected history metadata.
   *
   * The next implementation step will add a dedicated
   * historical analysis detail view that loads the exact
   * Job Match / Skill Gap / Career Plan records by ID.
   */

  localStorage.setItem(
    "careerpilot_selected_history",
    JSON.stringify(
      item
    )
  );

  navigate(
    `/history/${item.job_match_result_id}`
  );
}


/* ==================================================
   DATE FORMATTER
   ================================================== */

function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "Unknown date";
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  ).format(date);
}


export default History;