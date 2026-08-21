import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";


function safeArray(value) {
  return Array.isArray(value)
    ? value.filter(Boolean)
    : [];
}


function addSectionTitle(
  doc,
  title,
  y
) {
  if (y > 265) {
    doc.addPage();
    y = 22;
  }

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(10);

  doc.text(
    title.toUpperCase(),
    18,
    y
  );

  return y + 7;
}


function addBulletSection(
  doc,
  title,
  items,
  startY
) {
  const cleanItems =
    safeArray(items);

  if (cleanItems.length === 0) {
    return startY;
  }


  let y = addSectionTitle(
    doc,
    title,
    startY
  );


  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(9.5);


  cleanItems.forEach(
    (item) => {
      const lines =
        doc.splitTextToSize(
          String(item),
          165
        );


      if (
        y +
          lines.length * 5 >
        280
      ) {
        doc.addPage();

        y = 22;
      }


      doc.text(
        "•",
        20,
        y
      );


      doc.text(
        lines,
        26,
        y
      );


      y +=
        lines.length * 5 +
        3;
    }
  );


  return y + 4;
}


function formatDate() {
  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  ).format(
    new Date()
  );
}


export function exportJobMatchPDF({
  analysis,
  jobDescription,
  targetRole = "Target Role",
}) {
  if (!analysis) {
    throw new Error(
      "Job Match analysis is required."
    );
  }


  const doc =
    new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    });


  const pageWidth =
    doc.internal.pageSize.getWidth();


  /* ================================================
     BRAND HEADER
     ================================================ */

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(16);

  doc.text(
    "CareerPilot AI",
    18,
    20
  );


  doc.setFontSize(9);

  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.text(
    "AI-assisted career guidance",
    18,
    26
  );


  doc.setDrawColor(
    220,
    220,
    220
  );

  doc.line(
    18,
    32,
    pageWidth - 18,
    32
  );


  /* ================================================
     REPORT TITLE
     ================================================ */

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(21);

  doc.text(
    "Job Match Report",
    18,
    45
  );


  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(9.5);

  doc.text(
    `Target role: ${targetRole}`,
    18,
    53
  );

  doc.text(
    `Generated: ${formatDate()}`,
    18,
    59
  );


  /* ================================================
     SCORE
     ================================================ */

  const score =
    typeof analysis.match_score ===
    "number"
      ? analysis.match_score
      : 0;


  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(30);

  doc.text(
    `${score}`,
    18,
    78
  );


  doc.setFontSize(11);

  doc.text(
    "/ 100",
    35,
    78
  );


  doc.setFontSize(9);

  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.text(
    "JOB MATCH SCORE",
    18,
    85
  );


  /* ================================================
     QUICK SUMMARY TABLE
     ================================================ */

  autoTable(
    doc,
    {
      startY: 94,

      head: [
        [
          "Category",
          "Count",
        ],
      ],

      body: [
        [
          "Strong matches",
          safeArray(
            analysis.strong_matches
          ).length,
        ],
        [
          "Partial matches",
          safeArray(
            analysis.partial_matches
          ).length,
        ],
        [
          "Missing requirements",
          safeArray(
            analysis.missing_skills
          ).length,
        ],
        [
          "Priority actions",
          safeArray(
            analysis.priority_actions
          ).length,
        ],
      ],

      theme:
        "grid",

      styles: {
        font:
          "helvetica",

        fontSize:
          9,

        cellPadding:
          3,
      },

      headStyles: {
        fillColor: [
          17,
          24,
          39,
        ],

        textColor:
          255,
      },
    }
  );


  let y =
    doc.lastAutoTable.finalY +
    12;


  /* ================================================
     REPORT SECTIONS
     ================================================ */

  y = addBulletSection(
    doc,
    "Strong Matches",
    analysis.strong_matches,
    y
  );


  y = addBulletSection(
    doc,
    "Partial Matches",
    analysis.partial_matches,
    y
  );


  y = addBulletSection(
    doc,
    "Missing Requirements",
    analysis.missing_skills,
    y
  );


  y = addBulletSection(
    doc,
    "Priority Actions",
    analysis.priority_actions,
    y
  );


  y = addBulletSection(
    doc,
    "Resume Improvements",
    analysis.resume_improvements,
    y
  );


  /* ================================================
     JOB DESCRIPTION SUMMARY
     ================================================ */

  if (
    jobDescription?.trim()
  ) {
    if (y > 245) {
      doc.addPage();

      y = 22;
    }


    y = addSectionTitle(
      doc,
      "Target Job Description",
      y
    );


    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(8.5);


    const description =
      doc.splitTextToSize(
        jobDescription.trim(),
        165
      );


    /*
     * Keep the export useful without
     * dumping an excessively long JD.
     */

    const limitedDescription =
      description.slice(
        0,
        35
      );


    doc.text(
      limitedDescription,
      18,
      y
    );
  }


  /* ================================================
     FOOTERS
     ================================================ */

  const pageCount =
    doc.getNumberOfPages();


  for (
    let page = 1;
    page <= pageCount;
    page += 1
  ) {
    doc.setPage(
      page
    );


    const pageHeight =
      doc.internal.pageSize.getHeight();


    doc.setDrawColor(
      230,
      230,
      230
    );

    doc.line(
      18,
      pageHeight - 16,
      pageWidth - 18,
      pageHeight - 16
    );


    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(7.5);


    doc.text(
      "CareerPilot AI · AI-assisted career guidance",
      18,
      pageHeight - 10
    );


    doc.text(
      `Page ${page} of ${pageCount}`,
      pageWidth - 18,
      pageHeight - 10,
      {
        align:
          "right",
      }
    );
  }


  /* ================================================
     DOWNLOAD
     ================================================ */

  doc.save(
    "CareerPilot_Job_Match_Report.pdf"
  );
}