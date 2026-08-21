import { jsPDF } from "jspdf";


/* ============================================================
   CAREERPILOT CAREER READINESS REPORT
   ============================================================ */

const PAGE_MARGIN_X = 18;
const PAGE_TOP = 20;
const PAGE_BOTTOM = 22;

const CONTENT_WIDTH = 174;

const MIDNIGHT = [17, 24, 39];
const EMERALD = [5, 150, 105];
const MUTED = [90, 99, 112];
const LIGHT_BORDER = [225, 231, 239];
const LIGHT_BG = [248, 250, 252];


/* ============================================================
   DATA HELPERS
   ============================================================ */

function readJSON(key) {
  const stored =
    localStorage.getItem(key);

  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored);

  } catch {
    return null;
  }
}


function getActiveResume() {
  return readJSON(
    "careerpilot_active_resume"
  );
}


function getLatestJobMatch() {
  return readJSON(
    "careerpilot_latest_job_match"
  );
}


function getLatestSkillGap() {
  return readJSON(
    "careerpilot_latest_skill_gap"
  );
}


function getLatestCareerPlan() {
  return readJSON(
    "careerpilot_latest_career_plan"
  );
}


function safeArray(value) {
  return Array.isArray(value)
    ? value.filter(
        (item) =>
          item !== null &&
          item !== undefined &&
          item !== ""
      )
    : [];
}


function sameId(a, b) {
  /*
   * Missing provenance metadata should not
   * invalidate an otherwise valid report.
   */

  if (
    a === null ||
    a === undefined ||
    b === null ||
    b === undefined
  ) {
    return true;
  }

  return String(a) === String(b);
}


function getResumeFilename(
  resume
) {
  if (!resume) {
    return null;
  }

  return (
    resume.filename ||
    resume.original_filename ||
    resume.resume_filename ||
    null
  );
}


/* ============================================================
   LATEST REPORT VALIDATION
   ============================================================ */

function validateReportReadiness({
  resume,
  jobMatch,
  skillGap,
  careerPlan,
}) {
  const reasons = [];


  /* ------------------------------------------------------------
     REQUIRED DATA
     ------------------------------------------------------------ */

  if (!resume) {
    reasons.push(
      "No active resume is available."
    );
  }


  if (!jobMatch) {
    reasons.push(
      "Run Job Match before downloading the full report."
    );
  }


  if (!skillGap) {
    reasons.push(
      "Run Skill Gap before downloading the full report."
    );
  }


  if (!careerPlan) {
    reasons.push(
      "Generate your Career Plan before downloading the full report."
    );
  }


  if (
    !resume ||
    !jobMatch ||
    !skillGap ||
    !careerPlan
  ) {
    return {
      canExport: false,
      reasons,
    };
  }


  /* ------------------------------------------------------------
     ACTIVE RESUME VALIDATION
     ------------------------------------------------------------ */

  if (
    !sameId(
      resume.resume_id,
      jobMatch.resume_id
    )
  ) {
    reasons.push(
      "Your Job Match belongs to a previous resume. Run Job Match again."
    );
  }


  if (
    !sameId(
      resume.resume_id,
      skillGap.resume_id
    )
  ) {
    reasons.push(
      "Your Skill Gap belongs to a previous resume. Run Skill Gap again."
    );
  }


  if (
    !sameId(
      resume.resume_id,
      careerPlan.resume_id
    )
  ) {
    reasons.push(
      "Your Career Plan belongs to a previous resume. Generate it again."
    );
  }


  /* ------------------------------------------------------------
     JOB DESCRIPTION VALIDATION
     ------------------------------------------------------------ */

  if (
    jobMatch.job_description_id &&
    skillGap.job_description_id &&
    String(
      jobMatch.job_description_id
    ) !==
      String(
        skillGap.job_description_id
      )
  ) {
    reasons.push(
      "Your Skill Gap was generated for a different job description. Run Skill Gap again."
    );
  }


  if (
    jobMatch.job_description_id &&
    careerPlan.job_description_id &&
    String(
      jobMatch.job_description_id
    ) !==
      String(
        careerPlan.job_description_id
      )
  ) {
    reasons.push(
      "Your Career Plan was generated for a different job description."
    );
  }


  /*
   * IMPORTANT:
   *
   * Do not compare standalone:
   *
   * job_match_result_id
   * skill_gap_report_id
   *
   * against Career Plan IDs.
   *
   * Career Plan can create its own persistence
   * records during the workflow.
   */


  return {
    canExport:
      reasons.length === 0,

    reasons,
  };
}


/* ============================================================
   HISTORICAL REPORT VALIDATION
   ============================================================ */

function validateHistoricalReport({
  resume,
  jobMatch,
  skillGap,
  careerPlan,
}) {
  const reasons = [];


  /*
   * Historical reports intentionally do NOT compare
   * against careerpilot_active_resume.
   *
   * An old analysis may correctly belong to an older
   * resume. That is exactly what History is designed
   * to preserve.
   */


  if (!resume) {
    reasons.push(
      "Resume information is unavailable for this saved analysis."
    );
  }


  if (!jobMatch) {
    reasons.push(
      "Job Match data is unavailable for this saved analysis."
    );
  }


  if (!skillGap) {
    reasons.push(
      "Skill Gap data is unavailable for this saved analysis."
    );
  }


  if (!careerPlan) {
    reasons.push(
      "Career Plan data is unavailable for this saved analysis."
    );
  }


  if (
    !jobMatch ||
    !skillGap ||
    !careerPlan
  ) {
    return {
      canExport: false,
      reasons,
    };
  }


  /*
   * Job Match and Skill Gap should still describe
   * the same saved Job Description.
   */

  if (
    jobMatch.job_description_id &&
    skillGap.job_description_id &&
    String(
      jobMatch.job_description_id
    ) !==
      String(
        skillGap.job_description_id
      )
  ) {
    reasons.push(
      "The saved Job Match and Skill Gap belong to different job descriptions."
    );
  }


  /*
   * Do not require careerPlan.job_description_id here.
   *
   * Historical Career Plan endpoint currently returns
   * its linked Job Match / Skill Gap IDs rather than
   * resume_id / job_description_id.
   */


  return {
    canExport:
      reasons.length === 0,

    reasons,
  };
}


/* ============================================================
   PAGE HELPERS
   ============================================================ */

function pageHeight(doc) {
  return doc.internal.pageSize.getHeight();
}


function checkPageBreak(
  doc,
  y,
  spaceNeeded = 20
) {
  if (
    y + spaceNeeded >
    pageHeight(doc) -
      PAGE_BOTTOM
  ) {
    doc.addPage();

    return PAGE_TOP;
  }

  return y;
}


function writeSectionDivider(
  doc,
  y
) {
  y = checkPageBreak(
    doc,
    y,
    8
  );

  doc.setDrawColor(
    ...LIGHT_BORDER
  );

  doc.setLineWidth(0.35);

  doc.line(
    PAGE_MARGIN_X,
    y,
    PAGE_MARGIN_X +
      CONTENT_WIDTH,
    y
  );

  return y + 8;
}


function writeSectionHeading(
  doc,
  y,
  number,
  title,
  subtitle = null
) {
  y = checkPageBreak(
    doc,
    y,
    subtitle
      ? 24
      : 18
  );


  doc.setFillColor(
    ...EMERALD
  );

  doc.roundedRect(
    PAGE_MARGIN_X,
    y - 4,
    10,
    10,
    2,
    2,
    "F"
  );


  doc.setTextColor(
    255,
    255,
    255
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(9);

  doc.text(
    String(number).padStart(
      2,
      "0"
    ),
    PAGE_MARGIN_X + 5,
    y + 2.3,
    {
      align: "center",
    }
  );


  doc.setTextColor(
    ...MIDNIGHT
  );

  doc.setFontSize(15);

  doc.text(
    title,
    PAGE_MARGIN_X + 15,
    y + 3
  );


  let nextY =
    y + 12;


  if (subtitle) {
    doc.setTextColor(
      ...MUTED
    );

    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(8.5);


    const subtitleLines =
      doc.splitTextToSize(
        subtitle,
        155
      );


    doc.text(
      subtitleLines,
      PAGE_MARGIN_X + 15,
      nextY
    );


    nextY +=
      subtitleLines.length *
        4.5 +
      2;
  }


  return nextY;
}


function writeSubheading(
  doc,
  y,
  title
) {
  y = checkPageBreak(
    doc,
    y,
    10
  );


  doc.setTextColor(
    ...MIDNIGHT
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(9.5);

  doc.text(
    title.toUpperCase(),
    PAGE_MARGIN_X,
    y
  );


  return y + 6;
}


function writeParagraph(
  doc,
  y,
  text
) {
  if (!text) {
    return y;
  }


  doc.setTextColor(
    ...MUTED
  );

  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(9);


  const lines =
    doc.splitTextToSize(
      String(text),
      CONTENT_WIDTH
    );


  for (
    let index = 0;
    index < lines.length;
    index += 1
  ) {
    y = checkPageBreak(
      doc,
      y,
      6
    );


    doc.text(
      lines[index],
      PAGE_MARGIN_X,
      y
    );


    y += 5;
  }


  return y + 2;
}


function writeBulletList(
  doc,
  y,
  items
) {
  const values =
    safeArray(items);


  if (values.length === 0) {
    return y;
  }


  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(9);


  values.forEach(
    (item) => {
      const lines =
        doc.splitTextToSize(
          String(item),
          CONTENT_WIDTH - 8
        );


      y = checkPageBreak(
        doc,
        y,
        lines.length * 5 +
          4
      );


      doc.setTextColor(
        ...EMERALD
      );

      doc.setFont(
        "helvetica",
        "bold"
      );

      doc.text(
        "-",
        PAGE_MARGIN_X,
        y
      );


      doc.setTextColor(
        ...MUTED
      );

      doc.setFont(
        "helvetica",
        "normal"
      );


      doc.text(
        lines,
        PAGE_MARGIN_X + 6,
        y
      );


      y +=
        lines.length *
          5 +
        3;
    }
  );


  return y + 1;
}


function writeNumberedList(
  doc,
  y,
  items
) {
  const values =
    safeArray(items);


  if (values.length === 0) {
    return y;
  }


  values.forEach(
    (
      item,
      index
    ) => {
      const lines =
        doc.splitTextToSize(
          String(item),
          CONTENT_WIDTH - 14
        );


      y = checkPageBreak(
        doc,
        y,
        lines.length * 5 +
          6
      );


      doc.setFillColor(
        ...LIGHT_BG
      );

      doc.roundedRect(
        PAGE_MARGIN_X,
        y - 4,
        10,
        9,
        2,
        2,
        "F"
      );


      doc.setTextColor(
        ...EMERALD
      );

      doc.setFont(
        "helvetica",
        "bold"
      );

      doc.setFontSize(8);

      doc.text(
        String(
          index + 1
        ).padStart(
          2,
          "0"
        ),
        PAGE_MARGIN_X + 5,
        y + 1.4,
        {
          align: "center",
        }
      );


      doc.setTextColor(
        ...MUTED
      );

      doc.setFont(
        "helvetica",
        "normal"
      );

      doc.setFontSize(9);

      doc.text(
        lines,
        PAGE_MARGIN_X + 15,
        y
      );


      y +=
        lines.length *
          5 +
        5;
    }
  );


  return y + 1;
}


/* ============================================================
   REPORT HEADER
   ============================================================ */

function writeReportHeader(
  doc,
  y,
  {
    targetRole,
    generatedDate,
    filename,
    historical = false,
  }
) {
  doc.setFillColor(
    ...MIDNIGHT
  );

  doc.rect(
    0,
    0,
    210,
    55,
    "F"
  );


  doc.setTextColor(
    255,
    255,
    255
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(11);

  doc.text(
    "CAREERPILOT AI",
    PAGE_MARGIN_X,
    16
  );


  doc.setTextColor(
    110,
    231,
    183
  );

  doc.setFontSize(8);

  doc.text(
    historical
      ? "SAVED CAREER ANALYSIS"
      : "AI-ASSISTED CAREER GUIDANCE",
    PAGE_MARGIN_X,
    22
  );


  doc.setTextColor(
    255,
    255,
    255
  );

  doc.setFontSize(22);

  doc.text(
    "Career Readiness Report",
    PAGE_MARGIN_X,
    35
  );


  doc.setTextColor(
    209,
    213,
    219
  );

  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(8.5);


  doc.text(
    `Target Role: ${targetRole}`,
    PAGE_MARGIN_X,
    44
  );


  doc.text(
    historical
      ? `Analysis Date: ${generatedDate}`
      : `Generated: ${generatedDate}`,
    PAGE_MARGIN_X,
    49
  );


  if (filename) {
    const filenameLines =
      doc.splitTextToSize(
        `Resume: ${filename}`,
        75
      );

    doc.text(
      filenameLines[
        filenameLines.length - 1
      ],
      192,
      49,
      {
        align: "right",
      }
    );
  }


  return 66;
}


/* ============================================================
   JOB MATCH
   ============================================================ */

function writeJobMatchSection(
  doc,
  y,
  jobMatch
) {
  y = writeSectionHeading(
    doc,
    y,
    1,
    "Job Match Summary",
    "How the resume aligns with the target role."
  );


  const score =
    typeof jobMatch.match_score ===
    "number"
      ? jobMatch.match_score
      : Number(
          jobMatch.match_score ||
          0
        );


  y = checkPageBreak(
    doc,
    y,
    28
  );


  doc.setFillColor(
    ...LIGHT_BG
  );

  doc.roundedRect(
    PAGE_MARGIN_X,
    y,
    CONTENT_WIDTH,
    22,
    3,
    3,
    "F"
  );


  doc.setTextColor(
    ...EMERALD
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(22);

  doc.text(
    String(score),
    PAGE_MARGIN_X + 8,
    y + 14
  );


  doc.setFontSize(9);

  doc.setTextColor(
    ...MIDNIGHT
  );

  doc.text(
    "/ 100",
    PAGE_MARGIN_X + 25,
    y + 14
  );


  doc.setTextColor(
    ...MUTED
  );

  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.text(
    "JOB MATCH SCORE",
    PAGE_MARGIN_X + 45,
    y + 13.5
  );


  y += 31;


  if (
    safeArray(
      jobMatch.strong_matches
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Strong Matches"
    );

    y = writeBulletList(
      doc,
      y,
      jobMatch.strong_matches
    );
  }


  if (
    safeArray(
      jobMatch.partial_matches
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Partial Matches"
    );

    y = writeBulletList(
      doc,
      y,
      jobMatch.partial_matches
    );
  }


  if (
    safeArray(
      jobMatch.missing_skills
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Missing Requirements"
    );

    y = writeBulletList(
      doc,
      y,
      jobMatch.missing_skills
    );
  }


  if (
    safeArray(
      jobMatch.priority_actions
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Priority Actions"
    );

    y = writeNumberedList(
      doc,
      y,
      jobMatch.priority_actions
    );
  }


  if (
    safeArray(
      jobMatch.resume_improvements
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Resume Improvements"
    );

    y = writeBulletList(
      doc,
      y,
      jobMatch.resume_improvements
    );
  }


  return writeSectionDivider(
    doc,
    y
  );
}


/* ============================================================
   SKILL GAP
   ============================================================ */

function writePrioritySkillGapsSection(
  doc,
  y,
  skillGap
) {
  y = writeSectionHeading(
    doc,
    y,
    2,
    "Priority Skill Gaps",
    "The highest-value skills to strengthen for this role."
  );


  const groups = [
    {
      title:
        "High Priority",

      items:
        skillGap.high_priority_gaps,
    },
    {
      title:
        "Medium Priority",

      items:
        skillGap.medium_priority_gaps,
    },
    {
      title:
        "Low Priority",

      items:
        skillGap.low_priority_gaps,
    },
  ];


  groups.forEach(
    (group) => {
      if (
        safeArray(
          group.items
        ).length
      ) {
        y = writeSubheading(
          doc,
          y,
          group.title
        );

        y = writeBulletList(
          doc,
          y,
          group.items
        );
      }
    }
  );


  if (
    safeArray(
      skillGap.recommended_learning_order
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Focus Skills / Learning Order"
    );

    y = writeNumberedList(
      doc,
      y,
      skillGap.recommended_learning_order
    );
  }


  return writeSectionDivider(
    doc,
    y
  );
}


/* ============================================================
   BUILD EVIDENCE
   ============================================================ */

function writeProjectCard(
  doc,
  y,
  project,
  index
) {
  if (
    !project ||
    typeof project !==
      "object"
  ) {
    return y;
  }


  y = checkPageBreak(
    doc,
    y,
    44
  );


  doc.setFillColor(
    ...LIGHT_BG
  );

  doc.roundedRect(
    PAGE_MARGIN_X,
    y,
    CONTENT_WIDTH,
    13,
    3,
    3,
    "F"
  );


  doc.setTextColor(
    ...EMERALD
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(8);


  const skill =
    project.target_skill ||
    `Project ${index + 1}`;


  doc.text(
    String(skill).toUpperCase(),
    PAGE_MARGIN_X + 5,
    y + 8
  );


  y += 20;


  if (
    project.project_title
  ) {
    doc.setTextColor(
      ...MIDNIGHT
    );

    doc.setFont(
      "helvetica",
      "bold"
    );

    doc.setFontSize(12);


    const titleLines =
      doc.splitTextToSize(
        String(
          project.project_title
        ),
        CONTENT_WIDTH
      );


    doc.text(
      titleLines,
      PAGE_MARGIN_X,
      y
    );


    y +=
      titleLines.length *
        6 +
      1;
  }


  if (
    project.project_goal
  ) {
    y = writeParagraph(
      doc,
      y,
      project.project_goal
    );
  }


  if (
    safeArray(
      project.suggested_stack
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Suggested Stack"
    );


    y = writeParagraph(
      doc,
      y,
      project.suggested_stack.join(
        "  |  "
      )
    );
  }


  if (
    safeArray(
      project.implementation_steps
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "What To Build"
    );


    y = writeNumberedList(
      doc,
      y,
      project.implementation_steps
    );
  }


  if (
    safeArray(
      project.portfolio_evidence
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Portfolio Evidence"
    );


    y = writeBulletList(
      doc,
      y,
      project.portfolio_evidence
    );
  }


  return y + 5;
}


function writeBuildEvidenceSection(
  doc,
  y,
  skillGap
) {
  y = writeSectionHeading(
    doc,
    y,
    3,
    "Build Evidence",
    "Projects and practical work that can turn skill gaps into visible proof."
  );


  const projects =
    safeArray(
      skillGap.portfolio_project_prompts
    );


  projects.forEach(
    (
      project,
      index
    ) => {
      y = writeProjectCard(
        doc,
        y,
        project,
        index
      );
    }
  );


  if (
    safeArray(
      skillGap.practice_tasks
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Practice Tasks"
    );


    y = writeNumberedList(
      doc,
      y,
      skillGap.practice_tasks
    );
  }


  if (
    safeArray(
      skillGap.proof_of_skill_actions
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Proof Of Skill Actions"
    );


    y = writeBulletList(
      doc,
      y,
      skillGap.proof_of_skill_actions
    );
  }


  return writeSectionDivider(
    doc,
    y
  );
}


/* ============================================================
   CAREER ACTION PLAN
   ============================================================ */

function writeCareerActionPlanSection(
  doc,
  y,
  careerPlan
) {
  y = writeSectionHeading(
    doc,
    y,
    4,
    "Career Action Plan",
    "The practical priorities that move you closer to role readiness."
  );


  if (
    careerPlan.readiness_summary
  ) {
    y = writeSubheading(
      doc,
      y,
      "Readiness Summary"
    );


    y = writeParagraph(
      doc,
      y,
      careerPlan.readiness_summary
    );
  }


  if (
    safeArray(
      careerPlan.top_priorities
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Top Priorities"
    );


    y = writeNumberedList(
      doc,
      y,
      careerPlan.top_priorities
    );
  }


  if (
    safeArray(
      careerPlan.recommended_learning_order
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Recommended Learning Order"
    );


    y = writeNumberedList(
      doc,
      y,
      careerPlan.recommended_learning_order
    );
  }


  if (
    safeArray(
      careerPlan.practical_tasks
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Practical Tasks"
    );


    y = writeBulletList(
      doc,
      y,
      careerPlan.practical_tasks
    );
  }


  if (
    safeArray(
      careerPlan.portfolio_evidence
    ).length
  ) {
    y = writeSubheading(
      doc,
      y,
      "Portfolio Evidence"
    );


    y = writeBulletList(
      doc,
      y,
      careerPlan.portfolio_evidence
    );
  }


  return writeSectionDivider(
    doc,
    y
  );
}


/* ============================================================
   30 DAY ROADMAP
   ============================================================ */

function buildWeeks(
  actionItems
) {
  const items =
    safeArray(
      actionItems
    );


  if (
    items.length === 0
  ) {
    return [];
  }


  const weekCount =
    Math.min(
      4,
      items.length
    );


  const perWeek =
    Math.ceil(
      items.length /
        weekCount
    );


  return Array.from(
    {
      length:
        weekCount,
    },
    (
      _,
      weekIndex
    ) => {
      const start =
        weekIndex *
        perWeek;


      return {
        label:
          `Week ${weekIndex + 1}`,

        items:
          items.slice(
            start,
            start +
              perWeek
          ),
      };
    }
  ).filter(
    (week) =>
      week.items.length >
      0
  );
}


function writeRoadmapSection(
  doc,
  y,
  careerPlan
) {
  const weeks =
    buildWeeks(
      careerPlan.action_plan_30_days
    );


  if (
    weeks.length === 0
  ) {
    return y;
  }


  y = writeSectionHeading(
    doc,
    y,
    5,
    "30-Day Roadmap",
    "A simple four-stage structure for putting the plan into action."
  );


  weeks.forEach(
    (week) => {
      y = writeSubheading(
        doc,
        y,
        week.label
      );


      y = writeBulletList(
        doc,
        y,
        week.items
      );
    }
  );


  return writeSectionDivider(
    doc,
    y
  );
}


/* ============================================================
   INTERVIEW PREPARATION
   ============================================================ */

function writeInterviewPrepSection(
  doc,
  y,
  careerPlan
) {
  const items =
    safeArray(
      careerPlan.interview_preparation_focus
    );


  if (
    items.length === 0
  ) {
    return y;
  }


  y = writeSectionHeading(
    doc,
    y,
    6,
    "Interview Preparation",
    "Topics you should be ready to explain and discuss confidently."
  );


  y = writeBulletList(
    doc,
    y,
    items
  );


  return y;
}


/* ============================================================
   FOOTER
   ============================================================ */

function addPageFooters(
  doc
) {
  const pages =
    doc.getNumberOfPages();


  for (
    let page = 1;
    page <= pages;
    page += 1
  ) {
    doc.setPage(page);


    const height =
      pageHeight(doc);


    doc.setDrawColor(
      ...LIGHT_BORDER
    );

    doc.setLineWidth(0.3);

    doc.line(
      PAGE_MARGIN_X,
      height - 15,
      PAGE_MARGIN_X +
        CONTENT_WIDTH,
      height - 15
    );


    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(7.5);

    doc.setTextColor(
      ...MUTED
    );


    doc.text(
      "CareerPilot AI - AI-assisted career guidance",
      PAGE_MARGIN_X,
      height - 9
    );


    doc.text(
      `Page ${page} of ${pages}`,
      PAGE_MARGIN_X +
        CONTENT_WIDTH,
      height - 9,
      {
        align:
          "right",
      }
    );
  }
}


/* ============================================================
   DATE
   ============================================================ */

function getFormattedDate(
  value = null
) {
  const date =
    value
      ? new Date(value)
      : new Date();


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return new Intl.DateTimeFormat(
      "en-IN",
      {
        day:
          "2-digit",

        month:
          "short",

        year:
          "numeric",
      }
    ).format(
      new Date()
    );
  }


  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day:
        "2-digit",

      month:
        "short",

      year:
        "numeric",
    }
  ).format(date);
}


/* ============================================================
   FILE NAME
   ============================================================ */

function sanitizeFilename(
  value
) {
  const safe =
    String(
      value ||
      "Career_Readiness"
    )
      .trim()
      .replace(
        /[^a-zA-Z0-9-_]+/g,
        "_"
      )
      .replace(
        /_+/g,
        "_"
      )
      .replace(
        /^_+|_+$/g,
        ""
      );


  return (
    safe ||
    "Career_Readiness"
  );
}


/* ============================================================
   REPORT GENERATION CORE
   ============================================================ */

function createCareerReadinessPdf({
  resume,
  jobMatch,
  skillGap,
  careerPlan,
  targetRole,
  generatedDate,
  historical,
  outputFilename,
}) {
  const doc =
    new jsPDF({
      orientation:
        "portrait",

      unit:
        "mm",

      format:
        "a4",
    });


  let y =
    PAGE_TOP;


  y = writeReportHeader(
    doc,
    y,
    {
      targetRole:
        targetRole ||
        "Software Engineer",

      generatedDate:
        generatedDate ||
        getFormattedDate(),

      filename:
        getResumeFilename(
          resume
        ),

      historical:
        Boolean(
          historical
        ),
    }
  );


  y = writeJobMatchSection(
    doc,
    y,
    jobMatch
  );


  y =
    writePrioritySkillGapsSection(
      doc,
      y,
      skillGap
    );


  y = writeBuildEvidenceSection(
    doc,
    y,
    skillGap
  );


  y =
    writeCareerActionPlanSection(
      doc,
      y,
      careerPlan
    );


  y = writeRoadmapSection(
    doc,
    y,
    careerPlan
  );


  writeInterviewPrepSection(
    doc,
    y,
    careerPlan
  );


  addPageFooters(
    doc
  );


  doc.save(
    outputFilename ||
    "CareerPilot_Career_Readiness_Report.pdf"
  );
}


/* ============================================================
   PUBLIC EXPORTER
   ============================================================ */

/*
 * TWO SUPPORTED MODES
 *
 * ------------------------------------------------------------
 * MODE 1 — Latest Career Plan page
 * ------------------------------------------------------------
 *
 * generateCareerReadinessReport();
 *
 * Reads:
 *
 * careerpilot_active_resume
 * careerpilot_latest_job_match
 * careerpilot_latest_skill_gap
 * careerpilot_latest_career_plan
 *
 *
 * ------------------------------------------------------------
 * MODE 2 — History Detail
 * ------------------------------------------------------------
 *
 * generateCareerReadinessReport({
 *   historical: true,
 *   resume: {
 *     filename: "resume.pdf",
 *   },
 *   jobMatch,
 *   skillGap,
 *   careerPlan,
 *   targetRole: "Java Developer",
 *   analyzedAt: "2026-08-20T09:30:00",
 * });
 *
 */


export function generateCareerReadinessReport(
  options = {}
) {
  try {
    const historical =
      options.historical ===
      true;


    /* ------------------------------------------------------------
       HISTORICAL MODE
       ------------------------------------------------------------ */

    if (historical) {
      const resume =
        options.resume ||
        null;


      const jobMatch =
        options.jobMatch ||
        null;


      const skillGap =
        options.skillGap ||
        null;


      const careerPlan =
        options.careerPlan ||
        null;


      const readiness =
        validateHistoricalReport({
          resume,
          jobMatch,
          skillGap,
          careerPlan,
        });


      if (
        !readiness.canExport
      ) {
        return {
          success:
            false,

          reasons:
            readiness.reasons,
        };
      }


      const targetRole =
        options.targetRole ||
        jobMatch.job_title ||
        "Saved Career Analysis";


      const analyzedDate =
        options.generatedDate ||
        (
          options.analyzedAt
            ? getFormattedDate(
                options.analyzedAt
              )
            : getFormattedDate(
                jobMatch.created_at
              )
        );


      const safeRole =
        sanitizeFilename(
          targetRole
        );


      const outputFilename =
        options.outputFilename ||
        `CareerPilot_${safeRole}_Saved_Analysis.pdf`;


      createCareerReadinessPdf({
        resume,
        jobMatch,
        skillGap,
        careerPlan,

        targetRole,

        generatedDate:
          analyzedDate,

        historical:
          true,

        outputFilename,
      });


      return {
        success:
          true,

        reasons:
          [],
      };
    }


    /* ------------------------------------------------------------
       LATEST ANALYSIS MODE
       ------------------------------------------------------------ */

    const resume =
      getActiveResume();


    const jobMatch =
      getLatestJobMatch();


    const skillGap =
      getLatestSkillGap();


    const careerPlan =
      getLatestCareerPlan();


    const readiness =
      validateReportReadiness({
        resume,
        jobMatch,
        skillGap,
        careerPlan,
      });


    if (
      !readiness.canExport
    ) {
      return {
        success:
          false,

        reasons:
          readiness.reasons,
      };
    }


    const targetRole =
      options.targetRole ||
      jobMatch.job_title ||
      "Software Engineer";


    createCareerReadinessPdf({
      resume,
      jobMatch,
      skillGap,
      careerPlan,

      targetRole,

      generatedDate:
        getFormattedDate(),

      historical:
        false,

      outputFilename:
        options.outputFilename ||
        "CareerPilot_Career_Readiness_Report.pdf",
    });


    return {
      success:
        true,

      reasons:
        [],
    };

  } catch {
    
    return {
      success:
        false,

      reasons: [
        "CareerPilot could not generate the PDF report. Please try again.",
      ],
    };
  }
}