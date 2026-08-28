const GUIDANCE_HEADING_PATTERN =
  /^\s*(?:#{1,6}\s*)?(?:\*\*)?CareerPilot Guidance(?:\*\*)?\s*:?\s*/i;


function normalizeEscapedMarkdown(
  content
) {
  return content
    .replace(
    /\\+([#*_`>+-])/g,
    "$1"
    )
    .replace(
      /^\*{4}(.+?)\*{2}\s*:\s*(.+?)\*{2}\s*$/gm,
      "**$1: $2**"
    )
    .replace(
      /\*{4}/g,
      "**"
    );
}


export function cleanAgentGuidance(
  content
) {
  if (
    typeof content !== "string"
  ) {
    return content;
  }

  const normalizedContent =
    normalizeEscapedMarkdown(
      content.replace(
        /\r\n?/g,
        "\n"
      )
    );

  return normalizedContent
    .replace(
      GUIDANCE_HEADING_PATTERN,
      ""
    )
    .trim();
}