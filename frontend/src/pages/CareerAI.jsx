import {
  useEffect,
  useState,
} from "react";

import {
  ArrowRight,
  Bot,
  Check,
  CheckCircle2,
  CircleDot,
  Clock3,
  Code2,
  FileText,
  Lightbulb,
  LoaderCircle,
  MessageSquareText,
  Play,
  Plus,
  Save,
  Search,
  Send,
  Sparkles,
  Target,
  Trash2,
  User,
  XCircle,
} from "lucide-react";

import api from "../services/api";

import {
  createChatRequestId,
  getChatErrorMessage,
} from "../utils/chatRequest";
import {
  cleanAgentGuidance,
} from "../utils/agentGuidance";

const PROMPT_SUGGESTIONS = [
  "How should I prepare for Java fresher interviews?",
  "What should I learn next for backend roles?",
  "Which portfolio project should I build next?",
  "How can I improve my software engineering profile?",
  "What should I focus on this month?",
  "What skills should I strengthen for my target role?",
];


function createUniqueId(
  prefix
) {
  if (
    typeof crypto !== "undefined" &&
    crypto.randomUUID
  ) {
    return `${prefix}-${crypto.randomUUID()}`;
  }

  return `${prefix}-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2, 9)}`;
}


function createThreadId() {
  return createUniqueId(
    "careerpilot"
  );
}


function createEmptyChat(
  threadId = createThreadId()
) {
  const now =
    new Date().toISOString();

  return {
    id: threadId,
    title: "New conversation",
    threadId,
    resumeId: null,
    messages: [],
    createdAt: now,
    updatedAt: now,
    persisted: false,
  };
}


function mapConversationSummary(
  conversation
) {
  return {
    id: conversation.thread_id,
    threadId:
      conversation.thread_id,
    title:
      conversation.title ||
      "New conversation",
    resumeId:
      conversation.resume_id ??
      null,
    messages: [],
    createdAt:
      conversation.created_at,
    updatedAt:
      conversation.updated_at,
    persisted: true,
  };
}


function mapConversationDetail(
  conversation
) {
  return {
    ...mapConversationSummary(
      conversation
    ),
    messages: Array.isArray(
      conversation.messages
    )
      ? conversation.messages.map(
          (item) => ({
            id: item.id,
            mode:
              item.mode ||
              "chat",
            role: item.role,
            content:
              parseAssistantContent(
                item.content
              ),
            createdAt:
              item.created_at,
          })
        )
      : [],
  };
}


function formatChatTime(
  value
) {
  if (!value) {
    return "";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  const now =
    new Date();

  const sameDay =
    date.toDateString() ===
    now.toDateString();

  if (sameDay) {
    return date.toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  }

  return date.toLocaleDateString(
    [],
    {
      month: "short",
      day: "numeric",
    }
  );
}


/* ==================================================
   RESPONSE PARSER
   ================================================== */

function parseAssistantContent(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return null;
  }

  if (
    typeof value === "object"
  ) {
    return value;
  }

  if (
    typeof value !== "string"
  ) {
    return value;
  }

  let cleaned =
    value.trim();

  cleaned = cleaned
    .replace(
      /^```(?:json|javascript|js)?\s*/i,
      ""
    )
    .replace(
      /\s*```$/,
      ""
    )
    .trim();

  try {
    return JSON.parse(
      cleaned
    );
  } catch {
    // Continue.
  }

  const firstBrace =
    cleaned.indexOf("{");

  const lastBrace =
    cleaned.lastIndexOf("}");

  if (
    firstBrace !== -1 &&
    lastBrace > firstBrace
  ) {
    const possibleJson =
      cleaned.slice(
        firstBrace,
        lastBrace + 1
      );

    try {
      return JSON.parse(
        possibleJson
      );
    } catch {
      // Fall back to natural text.
    }
  }

  return cleaned;
}


/* ==================================================
   MAIN COMPONENT
   ================================================== */

function CareerAI() {
  const [message, setMessage] =
    useState("");

  const [messages, setMessages] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [
    failedRequest,
    setFailedRequest,
  ] = useState(null);

  const [
    chatHistory,
    setChatHistory,
  ] =
    useState([]);

  const [
    activeChatId,
    setActiveChatId,
  ] =
    useState(null);

  const [
    searchQuery,
    setSearchQuery,
  ] =
    useState("");

  const [
    conversationLoading,
    setConversationLoading,
  ] =
    useState(true);

  const [
    saveNotice,
    setSaveNotice,
  ] =
    useState("");

  const [
    careerMode,
    setCareerMode,
  ] =
    useState("chat");

  const [
    agentLoading,
    setAgentLoading,
  ] =
    useState(false);

  const chatMessages =
    messages.filter(
      (item) =>
        item.mode !== "agent"
    );

  const agentMessages =
    messages.filter(
      (item) =>
        item.mode === "agent"
    );


  /* ==================================================
     BACKEND CONVERSATION INITIALIZATION
     ================================================== */

  useEffect(() => {
    let cancelled = false;

    async function initializeConversations() {
      try {
        const response =
          await api.get(
            "/api/conversations"
          );

        const conversations =
          Array.isArray(
            response.data
              ?.conversations
          )
            ? response.data
                .conversations
            : [];

        if (cancelled) {
          return;
        }

        if (
          conversations.length === 0
        ) {
          const draft =
            createEmptyChat();

          setChatHistory([
            draft,
          ]);
          setActiveChatId(
            draft.id
          );
          setMessages([]);
          return;
        }

        const summaries =
          conversations.map(
            mapConversationSummary
          );

        const firstThreadId =
          summaries[0].threadId;

        setChatHistory(
          summaries
        );
        setActiveChatId(
          firstThreadId
        );

        const detailResponse =
          await api.get(
            `/api/conversations/${encodeURIComponent(
              firstThreadId
            )}`
          );

        if (cancelled) {
          return;
        }

        const detail =
          mapConversationDetail(
            detailResponse.data
          );

        setMessages(
          detail.messages
        );
        setChatHistory(
          (previous) =>
            previous.map(
              (chat) =>
                chat.id ===
                detail.id
                  ? detail
                  : chat
            )
        );
      } catch (initializationError) {
        console.error(
          "Career AI conversations could not be loaded:",
          initializationError
        );

        if (!cancelled) {
          const draft =
            createEmptyChat();

          setChatHistory([
            draft,
          ]);
          setActiveChatId(
            draft.id
          );
          setMessages([]);
          setError(
            initializationError
              .response?.data
              ?.detail ||
              "Your saved conversations could not be loaded."
          );
        }
      } finally {
        if (!cancelled) {
          setConversationLoading(
            false
          );
        }
      }
    }

    void initializeConversations();

    return () => {
      cancelled = true;
    };
  }, []);


  /* ==================================================
     SAVE NOTICE TIMER
     ================================================== */

  useEffect(() => {
    if (!saveNotice) {
      return;
    }

    const timer =
      window.setTimeout(
        () => {
          setSaveNotice("");
        },
        1800
      );

    return () => {
      window.clearTimeout(
        timer
      );
    };
  }, [saveNotice]);


  /* ==================================================
     PROJECT HANDOFF FROM SKILL GAP
     ================================================== */

  useEffect(() => {
    const storedHandoff =
      localStorage.getItem(
        "careerpilot_project_handoff"
      );

    if (!storedHandoff) {
      return;
    }

    try {
      const project =
        JSON.parse(
          storedHandoff
        );

      const title =
        project?.project_title ||
        "the recommended project";

      const targetSkill =
        project?.target_skill ||
        "the identified skill gap";

      const goal =
        project?.project_goal ||
        "";

      const stack =
        Array.isArray(
          project?.suggested_stack
        )
          ? project.suggested_stack
              .filter(Boolean)
              .join(", ")
          : "";

      const promptParts = [
        `Help me build the "${title}" project to strengthen ${targetSkill}.`,
      ];

      if (goal) {
        promptParts.push(
          `Project goal: ${goal}`
        );
      }

      if (stack) {
        promptParts.push(
          `Recommended stack: ${stack}.`
        );
      }

      promptParts.push(
        `
Act as a fresher-friendly Project Coach.

IMPORTANT SCOPE:
- This project is for an entry-level / fresher software engineering portfolio.
- Keep the project achievable and practical.
- Use a maximum of 6 project stages total.
- Give only ONE stage at a time.
- Each stage should contain 3 to 5 realistic tasks.
- Prefer fundamentals and portfolio evidence over enterprise-scale complexity.
- Do not introduce unnecessary advanced production engineering.
- Never pretend the user implemented a feature or technology unless it is part of the project.
- Keep the project aligned with the recommended stack and stated project goal.

Avoid unless the user explicitly asks:
- Terraform
- Kubernetes
- Prometheus
- Grafana
- ELK stack
- HashiCorp Vault
- chaos engineering
- blue-green deployment
- canary deployment
- complex disaster recovery
- enterprise compliance
- advanced observability
- advanced rollback orchestration

The goal is NOT to make the user a DevOps, SRE, or senior engineer.
The goal is to create enough practical evidence for a strong fresher portfolio.

Return ONLY valid JSON.
Do not use Markdown.
Do not use code fences.
Do not add any text outside the JSON.

Use exactly this structure:

{
  "project_name": "${title}",
  "current_stage": "Stage 1: Stage Name",
  "project_complete": false,
  "why_this_matters": "Short beginner-friendly explanation.",
  "step_by_step_plan": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "actionable_next_step": "One clear thing the user should complete before continuing.",
  "interview_tip": "One simple interview point connected to this stage."
}

Start with Stage 1 only.
`.trim()
      );
// eslint-disable-next-line react-hooks/set-state-in-effect
      setMessage(
        promptParts.join(
          "\n\n"
        )
      );
    } catch (handoffError) {
      console.error(
        "Career AI project handoff could not be read:",
        handoffError
      );
    } finally {
      localStorage.removeItem(
        "careerpilot_project_handoff"
      );
    }
  }, []);


  /* ==================================================
     ACTIVE RESUME
     ================================================== */

  function getActiveResume() {
    const stored =
      localStorage.getItem(
        "careerpilot_active_resume"
      );

    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(
        stored
      );
    } catch {
      return null;
    }
  }


  /* ==================================================
     THREAD + CONVERSATION CONTROLS
     ================================================== */

  function getThreadId() {
    const activeChat =
      chatHistory.find(
        (chat) =>
          chat.id ===
          activeChatId
      );

    if (
      activeChat?.threadId
    ) {
      return activeChat.threadId;
    }

    const generated =
      createThreadId();

    const draft =
      createEmptyChat(
        generated
      );

    setChatHistory(
      (previous) => [
        draft,
        ...previous.filter(
          (chat) =>
            chat.persisted
        ),
      ]
    );
    setActiveChatId(
      generated
    );

    return generated;
  }


  function handleNewConversation() {
    if (
      loading ||
      agentLoading ||
      conversationLoading
    ) {
      return;
    }

    const newChat =
      createEmptyChat();

    setChatHistory(
      (previous) => [
        newChat,
        ...previous.filter(
          (chat) =>
            chat.persisted
        ),
      ]
    );

    setActiveChatId(
      newChat.id
    );

    setMessages([]);
    setMessage("");
    setError("");
    setSearchQuery("");
  }


  async function handleOpenConversation(
    chatId
  ) {
    if (
      loading ||
      agentLoading ||
      conversationLoading ||
      chatId === activeChatId
    ) {
      return;
    }

    const selectedChat =
      chatHistory.find(
        (chat) =>
          chat.id === chatId
      );

    if (!selectedChat) {
      return;
    }

    if (!selectedChat.persisted) {
      setActiveChatId(
        selectedChat.id
      );
      setMessages([]);
      setMessage("");
      setError("");
      return;
    }

    setConversationLoading(true);
    setError("");

    try {
      const response =
        await api.get(
          `/api/conversations/${encodeURIComponent(
            selectedChat.threadId
          )}`
        );

      const detail =
        mapConversationDetail(
          response.data
        );

      setChatHistory(
        (previous) =>
          previous.map(
            (chat) =>
              chat.id === detail.id
                ? detail
                : chat
          )
      );
      setActiveChatId(
        detail.id
      );
      setMessages(
        detail.messages
      );
      setMessage("");
    } catch (openError) {
      console.error(
        "Career AI conversation could not be opened:",
        openError
      );
      setError(
        openError.response?.data
          ?.detail ||
          "This conversation could not be opened."
      );
    } finally {
      setConversationLoading(false);
    }
  }


  async function refreshConversationHistory(
    activeThreadId
  ) {
    const response =
      await api.get(
        "/api/conversations"
      );

    const conversations =
      Array.isArray(
        response.data?.conversations
      )
        ? response.data
            .conversations
        : [];

    setChatHistory(
      conversations.map(
        mapConversationSummary
      )
    );

    if (activeThreadId) {
      setActiveChatId(
        activeThreadId
      );
    }
  }


  async function handleSaveChat() {
    const activeChat =
      chatHistory.find(
        (chat) =>
          chat.id ===
          activeChatId
      );

    if (!activeChat) {
      return;
    }

    if (!activeChat.persisted) {
      setSaveNotice(
        "Send a message first"
      );
      return;
    }

    const requestedTitle =
      window.prompt(
        "Rename this conversation:",
        activeChat.title ||
          "New conversation"
      );

    if (requestedTitle === null) {
      return;
    }

    const title =
      requestedTitle.trim();

    if (!title) {
      setError(
        "Conversation title cannot be empty."
      );
      return;
    }

    try {
      const response =
        await api.patch(
          `/api/conversations/${encodeURIComponent(
            activeChat.threadId
          )}`,
          { title }
        );

      const updated =
        mapConversationSummary(
          response.data
        );

      setChatHistory(
        (previous) =>
          previous.map(
            (chat) =>
              chat.id === updated.id
                ? {
                    ...chat,
                    ...updated,
                    messages:
                      chat.messages,
                  }
                : chat
          )
      );
      setError("");
      setSaveNotice("Renamed");
    } catch (renameError) {
      console.error(
        "Career AI conversation could not be renamed:",
        renameError
      );
      setError(
        renameError.response?.data
          ?.detail ||
          "This conversation could not be renamed."
      );
    }
  }


  async function handleClearChat() {
    if (
      loading ||
      agentLoading ||
      conversationLoading ||
      !activeChatId
    ) {
      return;
    }

    const activeChat =
      chatHistory.find(
        (chat) =>
          chat.id ===
          activeChatId
      );

    if (!activeChat) {
      return;
    }

    if (
      activeChat.persisted &&
      !window.confirm(
        "Delete this conversation and all of its messages?"
      )
    ) {
      return;
    }

    setConversationLoading(true);

    try {
      if (activeChat.persisted) {
        await api.delete(
          `/api/conversations/${encodeURIComponent(
            activeChat.threadId
          )}`
        );
      }

      const remaining =
        chatHistory.filter(
          (chat) =>
            chat.id !==
              activeChat.id &&
            chat.persisted
        );

      if (remaining.length > 0) {
        const nextChat =
          remaining[0];

        const response =
          await api.get(
            `/api/conversations/${encodeURIComponent(
              nextChat.threadId
            )}`
          );

        const detail =
          mapConversationDetail(
            response.data
          );

        setChatHistory(
          remaining.map(
            (chat) =>
              chat.id === detail.id
                ? detail
                : chat
          )
        );
        setActiveChatId(
          detail.id
        );
        setMessages(
          detail.messages
        );
      } else {
        const draft =
          createEmptyChat();

        setChatHistory([
          draft,
        ]);
        setActiveChatId(
          draft.id
        );
        setMessages([]);
      }

      setMessage("");
      setError("");
      setSaveNotice("Deleted");
    } catch (deleteError) {
      console.error(
        "Career AI conversation could not be deleted:",
        deleteError
      );
      setError(
        deleteError.response?.data
          ?.detail ||
          "This conversation could not be deleted."
      );
    } finally {
      setConversationLoading(false);
    }
  }


  /* ==================================================
     SEND MESSAGE
     ================================================== */

  async function handleSend(
    overrideMessage = null,
    overrideRequestId = null
  ) {
    const sourceMessage =
      typeof overrideMessage ===
        "string"
        ? overrideMessage
        : message;

    const trimmedMessage =
      sourceMessage.trim();

    if (
      !trimmedMessage ||
      loading ||
      agentLoading ||
      conversationLoading
    ) {
      return;
    }

    setError("");
    setFailedRequest(null);

    const requestId =
      overrideRequestId ||
      createChatRequestId();

    const temporaryMessageId =
      createUniqueId(
        "pending-message"
      );

    const userMessage = {
      id: temporaryMessageId,
      mode: "chat",
      role: "user",
      content: trimmedMessage,
    };

    setMessages(
      (previous) => [
        ...previous,
        userMessage,
      ]
    );

    setMessage("");
    setLoading(true);

    try {
      const threadId =
        getThreadId();

      const activeChat =
        chatHistory.find(
          (chat) =>
            chat.id ===
            activeChatId
        );

      const activeResume =
        getActiveResume();

      const resumeId =
        activeChat?.resumeId ??
        activeResume?.resume_id ??
        null;

      const response =
        await api.post(
          "/api/chat",
          {
            request_id:
              requestId,

            thread_id:
              threadId,

            resume_id:
              resumeId,

            message:
              trimmedMessage,

            skills: [],

            history: [],
          }
        );

      const apiData =
        response.data;

      setFailedRequest(null);

      console.log(
        "Career AI API response:",
        apiData
      );

      let assistantResponse =
        apiData.data ??
        apiData.response ??
        null;

      assistantResponse =
        parseAssistantContent(
          assistantResponse
        );

      if (
        assistantResponse === null ||
        assistantResponse === undefined ||
        assistantResponse === ""
      ) {
        assistantResponse =
          "CareerPilot completed the request, but no response content was returned.";
      }

      setMessages(
        (previous) => [
          ...previous,
          {
            mode: "chat",
            role: "assistant",
            content:
              assistantResponse,
          },
        ]
      );

      try {
        await refreshConversationHistory(
          threadId
        );
      } catch (refreshError) {
        console.error(
          "Career AI conversation list could not be refreshed:",
          refreshError
        );
      }
    } catch (err) {
      console.error(
        "Career AI request failed:",
        err
      );

      setError(
        getChatErrorMessage(
          err,
          "CareerPilot could not respond right now."
        )
      );

      const isRetryable =
        !err.response ||
        err.response.status === 503;

      if (isRetryable) {
        setFailedRequest({
          message: trimmedMessage,
          requestId,
        });

        setMessage(trimmedMessage);
      }

      setMessages(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !==
              temporaryMessageId
          )
      );
    } finally {
      setLoading(false);
    }
  }


  /* ==================================================
     AUTONOMOUS AGENT MODE
     ================================================== */

  async function handleAgentRun(
    overrideGoal = null,
    overrideRequestId = null
  ) {
    const sourceGoal =
      typeof overrideGoal ===
        "string"
        ? overrideGoal
        : message;

    const trimmedGoal =
      sourceGoal.trim();

    if (
      !trimmedGoal ||
      loading ||
      agentLoading ||
      conversationLoading
    ) {
      return;
    }

    setError("");
    setFailedRequest(null);
    setAgentLoading(true);

    const requestId =
      overrideRequestId ||
      createChatRequestId();

    const threadId =
      getThreadId();

    try {
      const activeResume =
        getActiveResume();

      const activeChat =
        chatHistory.find(
          (chat) =>
            chat.id ===
            activeChatId
        );

      const resumeId =
        activeChat?.resumeId ??
        activeResume?.resume_id;

      if (!resumeId) {
        throw new Error(
          "Select a resume before starting Agent Mode."
        );
      }

      const response =
        await api.post(
          "/api/agent/run",
          {
            request_id:
              requestId,
            resume_id: resumeId,
            thread_id:
              threadId,
            goal:
              trimmedGoal,
            max_iterations: 6,
          }
        );

      const result =
        response.data;

      console.log(
        "CareerPilot Agent response:",
        result
      );

      setMessage("");
      setFailedRequest(null);

      const detailResponse =
        await api.get(
          `/api/conversations/${encodeURIComponent(
            threadId
          )}`
        );

      const detail =
        mapConversationDetail(
          detailResponse.data
        );

      setMessages(
        detail.messages
      );

      setChatHistory(
        (previous) =>
          previous.map(
            (chat) =>
              chat.id === detail.id
                ? detail
                : chat
          )
      );

      try {
        await refreshConversationHistory(
          threadId
        );
      } catch (refreshError) {
        console.error(
          "Agent conversation list could not be refreshed:",
          refreshError
        );
      }
    } catch (err) {
      console.error(
        "CareerPilot Agent request failed:",
        err
      );

      setError(
        getChatErrorMessage(
          err,
          "CareerPilot Agent could not complete this goal."
        )
      );

      const isRetryable =
        err.response?.status === 503 ||
        err.code === "ERR_NETWORK";

      if (isRetryable) {
        setFailedRequest({
          mode: "agent",
          message: trimmedGoal,
          requestId,
        });

        setMessage(trimmedGoal);
      } else {
        setMessage("");
      }

      try {
        const detailResponse =
          await api.get(
            `/api/conversations/${encodeURIComponent(
              threadId
            )}`
          );

        const detail =
          mapConversationDetail(
            detailResponse.data
          );

        setMessages(
          detail.messages
        );

        setChatHistory(
          (previous) =>
            previous.map(
              (chat) =>
                chat.id === detail.id
                  ? detail
                  : chat
            )
        );
      } catch (historyError) {
        console.error(
          "Failed Agent turn could not be reloaded:",
          historyError
        );
      }
    } finally {
      setAgentLoading(false);
    }
  }


  function handleCareerSubmit(
    overrideMessage = null
  ) {
    if (
      careerMode === "agent"
    ) {
      return handleAgentRun(
        overrideMessage
      );
    }

    return handleSend(
      overrideMessage
    );
  }


  /* ==================================================
     KEYBOARD
     ================================================== */

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (
        !loading &&
        !agentLoading &&
        !conversationLoading
      ) {
        handleCareerSubmit();
      }
    }
  }


  /* ==================================================
     SUGGESTIONS
     ================================================== */

  function handleSuggestion(
    suggestion
  ) {
    setMessage(
      suggestion
    );
  }


  /* ==================================================
     PROJECT COACH CONTINUE
     ================================================== */

  function handleContinueProject(
    projectName,
    currentStage
  ) {
    const safeProjectName =
      projectName ||
      "this project";

    const safeStage =
      currentStage ||
      "the current stage";

    const stageNumber =
      getStageNumber(
        safeStage
      );

    const forceCompletion =
      stageNumber >= 5;

    const nextPrompt = `
I completed ${safeStage} for the "${safeProjectName}" project.

Continue to ONLY the next practical project stage.

This is a FRESHER / ENTRY-LEVEL portfolio project.

IMPORTANT PROJECT RULES:

- Maximum 6 stages total.
- Give only ONE stage.
- Keep the stage achievable for a fresher.
- Give 3 to 5 practical steps.
- Prefer simple implementation and visible portfolio proof.
- Do not turn this into an enterprise or senior DevOps project.
- Do not repeat previous stages.
- Do not repeat monitoring, rollback, deployment, or security topics.
- Preserve the same project name.
- Do not claim the user implemented technologies that were never part of the project.

DO NOT introduce these unless I explicitly ask:
- Kubernetes
- Terraform
- Prometheus
- Grafana
- ELK
- HashiCorp Vault
- blue-green deployment
- canary deployment
- chaos engineering
- complex disaster recovery
- advanced observability
- advanced security/compliance
- infrastructure-as-code
- enterprise rollback strategies

The expected fresher project lifecycle is roughly:

Stage 1:
Project setup and basic architecture

Stage 2:
Core feature / implementation

Stage 3:
Testing or quality validation

Stage 4:
Simple deployment / cloud integration if relevant

Stage 5:
Final integration and practical proof

Stage 6:
README, GitHub evidence, resume bullet and interview preparation

${forceCompletion
  ? `
You are now approaching the maximum project scope.

The next response MUST be the FINAL stage.

Set:
"project_complete": true

The final stage should focus only on:
- cleaning the repository
- README documentation
- screenshots / demo proof
- GitHub presentation
- resume-ready evidence
- simple interview preparation

Do NOT introduce any new technology.
`
  : `
If there is still essential fresher-level implementation work left:
set "project_complete": false.

If the project already has enough portfolio evidence:
you may set "project_complete": true early instead of inventing unnecessary work.
`
}

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
Do not add text before or after the JSON.

Use exactly:

{
  "project_name": "${safeProjectName}",
  "current_stage": "Stage N: Stage Name",
  "project_complete": false,
  "why_this_matters": "Short fresher-friendly explanation of why this stage matters.",
  "step_by_step_plan": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "actionable_next_step": "One realistic completion target for this stage.",
  "interview_tip": "One simple interview point relevant to a fresher."
}
`.trim();

    setMessage(
      nextPrompt
    );
  }


  /* ==================================================
     PROJECT COMPLETE FOLLOW-UP ACTIONS
     ================================================== */

  function handleProjectFollowUp(
    action,
    projectName
  ) {
    const safeProjectName =
      projectName ||
      "this project";

    if (
      action ===
      "interview"
    ) {
      setMessage(
        `
Prepare me for a fresher-level Software Engineer interview based specifically on my "${safeProjectName}" project.

Give me the 8 most likely interview questions.

IMPORTANT:
- Keep every question appropriate for an entry-level candidate.
- Base questions only on the project concepts and technologies I would reasonably have implemented.
- Do not assume I used technologies that were never part of the project.
- Do not introduce Redis, RabbitMQ, Kafka, Kubernetes, Terraform, Prometheus, Grafana, ELK, advanced distributed systems, enterprise scaling, or complex production architecture unless they were actually used.
- Do not pretend hypothetical features were implemented.
- Focus on architecture basics, implementation choices, APIs, database usage if relevant, testing, Git/GitHub, deployment basics if relevant, debugging, and what I learned.
- Keep answers concise and interview-ready.
- If you include one "future improvement" question, keep the suggested improvements realistic for a fresher.
- Use clear headings, numbered questions, and bullet points.
`.trim()
      );

      return;
    }

    if (
      action ===
      "resume"
    ) {
      setMessage(
        `
Create 2 concise ATS-friendly fresher resume bullet points for my "${safeProjectName}" project.

Requirements:
- Focus only on technologies actually used.
- Explain what I built and the practical outcome.
- Do not invent percentages, user counts, performance improvements, or other metrics.
- Keep each bullet concise enough for a one-page fresher resume.
`.trim()
      );

      return;
    }

    if (
      action ===
      "readme"
    ) {
      setMessage(
        `
Help me create a clean GitHub README structure for my "${safeProjectName}" project.

Keep it suitable for a fresher portfolio.

Include:
- Project overview
- Problem solved
- Features
- Tech stack
- Basic architecture
- Local setup
- How to run the project
- Screenshots or demo section
- Testing section if applicable
- What I learned
- Future improvements

Do not add technologies or features that were not actually implemented.
`.trim()
      );
    }
  }


  const normalizedSearch =
    searchQuery
      .trim()
      .toLowerCase();

  const filteredChats =
    chatHistory.filter(
      (chat) =>
        !normalizedSearch ||
        String(
          chat.title || ""
        )
          .toLowerCase()
          .includes(
            normalizedSearch
          )
    );


  return (
    <section>

      {/* ================= HEADER ================= */}

      <div className="max-w-3xl">

        <p className="text-xs font-bold tracking-[0.14em] text-brand">
          CAREER AI
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-[-0.035em] text-midnight sm:text-4xl">
          Ask CareerPilot about your next move
        </h1>

        <p className="mt-4 max-w-2xl leading-7 text-text-muted">
          Get practical guidance on roles,
          preparation priorities, projects,
          interview readiness, and career decisions.
        </p>

      </div>


      {/* ================= CHAT WORKSPACE ================= */}

      <div className="mt-10 grid overflow-hidden rounded-2xl border border-border-soft bg-white shadow-sm lg:grid-cols-[260px_minmax(0,1fr)]">

        {/* ================= CONVERSATION SIDEBAR ================= */}

        <aside className="border-b border-border-soft bg-app-bg/70 lg:min-h-[700px] lg:border-b-0 lg:border-r">

          <div className="p-4">

            <button
              type="button"
              onClick={
                handleNewConversation
              }
              disabled={
                loading ||
                agentLoading ||
                conversationLoading
              }
              className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Plus size={17} />

              New conversation
            </button>


            <div className="relative mt-4">

              <Search
                size={16}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              />

              <input
                type="search"
                value={searchQuery}
                onChange={(event) =>
                  setSearchQuery(
                    event.target.value
                  )
                }
                placeholder="Search chats..."
                className="h-10 w-full rounded-xl border border-border-soft bg-white pl-9 pr-3 text-sm text-midnight outline-none transition placeholder:text-gray-400 focus:border-brand focus:ring-4 focus:ring-emerald-500/10"
              />

            </div>

          </div>


          <div className="border-t border-border-soft px-3 pb-4 pt-4">

            <div className="flex items-center justify-between px-2">

              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-text-muted">
                Recent conversations
              </p>

              <Clock3
                size={14}
                className="text-gray-400"
              />

            </div>


            <div className="mt-3 max-h-[430px] space-y-1 overflow-y-auto pr-1">

              {conversationLoading ? (
                <div className="flex items-center justify-center gap-2 rounded-xl border border-border-soft bg-white p-4 text-xs text-text-muted">
                  <LoaderCircle
                    size={15}
                    className="animate-spin text-brand"
                  />
                  Loading conversations...
                </div>
              ) : filteredChats.length >
              0 ? (
                filteredChats.map(
                  (chat) => {
                    const isActive =
                      chat.id ===
                      activeChatId;

                    return (
                      <button
                        key={chat.id}
                        type="button"
                        onClick={() =>
                          handleOpenConversation(
                            chat.id
                          )
                        }
                        className={`w-full rounded-xl border px-3 py-3 text-left transition ${
                          isActive
                            ? "border-emerald-200 bg-emerald-50"
                            : "border-transparent hover:border-border-soft hover:bg-white"
                        }`}
                      >

                        <div className="flex items-start gap-2.5">

                          <MessageSquareText
                            size={15}
                            className={`mt-0.5 shrink-0 ${
                              isActive
                                ? "text-brand"
                                : "text-gray-400"
                            }`}
                          />


                          <div className="min-w-0 flex-1">

                            <p
                              className={`truncate text-sm font-medium ${
                                isActive
                                  ? "text-brand"
                                  : "text-midnight"
                              }`}
                            >
                              {chat.title ||
                                "New conversation"}
                            </p>

                            <p className="mt-1 text-[10px] text-text-muted">
                              {formatChatTime(
                                chat.updatedAt
                              )}
                            </p>

                          </div>

                        </div>

                      </button>
                    );
                  }
                )
              ) : (
                <div className="rounded-xl border border-dashed border-border-soft bg-white p-4 text-center">

                  <p className="text-xs leading-5 text-text-muted">
                    No conversations match your search.
                  </p>

                </div>
              )}

            </div>

          </div>

        </aside>


        {/* ================= CHAT PANEL ================= */}

        <section className="flex min-h-[700px] min-w-0 flex-col bg-white">

          {/* ================= CHAT HEADER ================= */}

          <div className="flex flex-col gap-4 border-b border-border-soft px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">

            <div className="flex items-center gap-3">

              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">

                <Bot size={20} />

                <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-emerald-500" />

              </div>


              <div>

                <p className="text-sm font-semibold text-midnight">
                  CareerPilot AI
                </p>

                <p className="text-xs text-text-muted">
                  {careerMode === "agent"
                    ? "Autonomous · Plan, execute, evaluate and replan"
                    : "Online · Career guidance assistant"}
                </p>

              </div>

            </div>


            <div className="flex rounded-xl border border-border-soft bg-app-bg p-1">

              <button
                type="button"
                onClick={() => {
                  if (
                    loading ||
                    agentLoading
                  ) {
                    return;
                  }

                  setCareerMode("chat");
                  setError("");
                }}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${
                  careerMode === "chat"
                    ? "bg-white text-brand shadow-sm"
                    : "text-text-muted hover:text-midnight"
                }`}
              >
                <MessageSquareText size={14} />
                Chat
              </button>

              <button
                type="button"
                onClick={() => {
                  if (
                    loading ||
                    agentLoading
                  ) {
                    return;
                  }

                  setCareerMode("agent");
                  setError("");
                }}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${
                  careerMode === "agent"
                    ? "bg-white text-brand shadow-sm"
                    : "text-text-muted hover:text-midnight"
                }`}
              >
                <Bot size={14} />
                Agent
              </button>

            </div>


            <div className="flex flex-wrap items-center gap-2">

              {saveNotice && (
                <span className="text-xs font-medium text-brand">
                  {saveNotice}
                </span>
              )}

              <button
                type="button"
                onClick={
                  handleSaveChat
                }
                disabled={
                  !activeChatId ||
                  loading ||
                  agentLoading ||
                  conversationLoading
                }
                className="inline-flex h-9 items-center gap-2 rounded-lg border border-border-soft bg-white px-3 text-xs font-semibold text-midnight transition hover:border-emerald-200 hover:bg-emerald-50/40 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Save size={15} />

                Rename chat
              </button>

              <button
                type="button"
                onClick={
                  handleClearChat
                }
                disabled={
                  loading ||
                  agentLoading ||
                  conversationLoading
                }
                className="inline-flex h-9 items-center gap-2 rounded-lg border border-border-soft bg-white px-3 text-xs font-semibold text-midnight transition hover:border-red-200 hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Trash2 size={15} />

                Delete chat
              </button>

            </div>

          </div>


          {/* ================= MESSAGES ================= */}

          <div className="flex-1 overflow-y-auto bg-app-bg/40 p-5 sm:p-6">


            {conversationLoading ? (

              <div className="flex min-h-[430px] items-center justify-center gap-3 text-sm text-text-muted">
                <LoaderCircle
                  size={20}
                  className="animate-spin text-brand"
                />
                Loading conversation...
              </div>

            ) : careerMode === "agent" ? (

              <AgentWorkspace
                messages={agentMessages}
                loading={agentLoading}
              />

            ) : chatMessages.length === 0 ? (

              <EmptyChat
                onSuggestion={
                  handleSuggestion
                }
              />

            ) : (

              <div className="space-y-5">

                {chatMessages.map(
                  (
                    chatMessage,
                    index
                  ) => (
                    <ChatBubble
                      key={index}
                      role={
                        chatMessage.role
                      }
                      content={
                        chatMessage.content
                      }
                      onContinueProject={
                        handleContinueProject
                      }
                      onProjectFollowUp={
                        handleProjectFollowUp
                      }
                    />
                  )
                )}

                {loading && (
                  <div className="flex gap-3">

                    <AssistantIcon />

                    <div className="rounded-2xl rounded-tl-sm border border-border-soft bg-white px-4 py-3 shadow-sm">

                      <div className="flex items-center gap-2 text-sm text-text-muted">

                        <LoaderCircle
                          size={16}
                          className="animate-spin"
                        />

                        CareerPilot is thinking...

                      </div>

                    </div>

                  </div>
                )}

              </div>
            )}

          </div>

          {/* ================= ERROR ================= */}

          {error && (
            <div className="mx-5 mt-4 flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 sm:mx-6">

              <XCircle
                size={18}
                className="mt-0.5 shrink-0"
              />

              <div className="flex-1">
                <p>
                  {error}
                </p>

                {failedRequest && (
                  <button
                    type="button"
                    onClick={() => {
                      if (
                        failedRequest.mode ===
                        "agent"
                      ) {
                        return handleAgentRun(
                          failedRequest.message,
                          failedRequest.requestId
                        );
                      }

                      return handleSend(
                        failedRequest.message,
                        failedRequest.requestId
                      );
                    }}
                    disabled={
                      loading ||
                      agentLoading ||
                      conversationLoading
                    }
                    className="mt-3 rounded-lg border border-red-300 bg-white px-3 py-1.5 text-xs font-semibold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Retry message
                  </button>
                )}
              </div>

            </div>
          )}


          {careerMode === "chat" && (
            <>
          {/* ================= SUGGESTED PROMPTS ================= */}

          <div className="border-t border-border-soft bg-white px-4 pt-4 sm:px-5">

            <div className="flex items-center gap-2">

              <Sparkles
                size={14}
                className="text-brand"
              />

              <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-text-muted">
                Suggested questions
              </p>

            </div>


            <div className="mt-3 flex flex-wrap gap-2">

              {PROMPT_SUGGESTIONS.map(
                (suggestion) => (
                  <PromptChip
                    key={suggestion}
                    onClick={() =>
                      handleSuggestion(
                        suggestion
                      )
                    }
                  >
                    {suggestion}
                  </PromptChip>
                )
              )}

            </div>

          </div>
            </>
          )}


          {/* ================= COMPOSER ================= */}

          <div className="bg-white p-4 sm:p-5">

            <div className="rounded-2xl border border-border-soft bg-app-bg p-2 transition focus-within:border-brand focus-within:bg-white focus-within:ring-4 focus-within:ring-emerald-500/10">

              <textarea
                value={message}
                disabled={
                  conversationLoading
                }
                onChange={(event) =>
                  setMessage(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleKeyDown
                }
                rows={3}
                placeholder={
                  careerMode === "agent"
                    ? "Give CareerPilot a goal, e.g. Prepare me for a DevOps role based on my current skill gaps..."
                    : "Ask about your target role, preparation, projects, or next career step..."
                }
                className="w-full resize-none bg-transparent px-3 py-2 text-sm leading-6 text-midnight outline-none placeholder:text-gray-400"
              />

              <div className="flex items-center justify-between gap-4 px-2 pb-1">

                <p className="hidden text-[11px] text-gray-400 sm:block">
                  Enter to send · Shift + Enter for a new line
                </p>

                <button
                  type="button"
                  onClick={() =>
                    handleCareerSubmit()
                  }
                  disabled={
                    loading ||
                    agentLoading ||
                    conversationLoading ||
                    !message.trim()
                  }
                  className="ml-auto flex h-10 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {careerMode === "agent" ? (
                    <>
                      <Play size={16} />
                      Run Agent
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Send
                    </>
                  )}
                </button>

              </div>

            </div>

          </div>

        </section>

      </div>

    </section>
  );
}



/* ==================================================
   AGENT WORKSPACE
   ================================================== */


function AgentWorkspace({
  messages,
  loading,
}) {
  if (
    messages.length === 0 &&
    !loading
  ) {
    return (
      <div className="flex min-h-[430px] flex-col items-center justify-center px-6 text-center">

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-soft text-brand">
          <Bot size={25} />
        </div>

        <h2 className="mt-5 text-xl font-semibold tracking-tight text-midnight">
          Autonomous Career Agent
        </h2>

        <p className="mt-3 max-w-lg text-sm leading-7 text-text-muted">
          Give CareerPilot a career goal instead of
          asking a single question. The agent can
          create a plan, retrieve evidence, execute
          multiple tools, evaluate the results, and
          replan when required.
        </p>

        <div className="mt-6 grid w-full max-w-xl gap-3 sm:grid-cols-3">
          <AgentCapability
            icon={<Target size={17} />}
            title="Plan"
            description="Break down your goal"
          />
          <AgentCapability
            icon={<Play size={17} />}
            title="Execute"
            description="Use career tools"
          />
          <AgentCapability
            icon={<CheckCircle2 size={17} />}
            title="Evaluate"
            description="Verify the outcome"
          />
        </div>

      </div>
    );
  }

  return (
    <div className="space-y-5">

      {messages.map(
        (agentMessage) =>
          agentMessage.role ===
          "user" ? (
            <AgentSection
              key={agentMessage.id}
              title="Your Goal"
              icon={<Target size={16} />}
            >
              <p className="text-sm leading-7 text-text-muted">
                {agentMessage.content}
              </p>
            </AgentSection>
          ) : (
            <AgentSection
              key={agentMessage.id}
              title="CareerPilot Guidance"
              icon={<Sparkles size={16} />}
            >
              <RichTextResponse
                content={
                  cleanAgentGuidance(
                    agentMessage.content
                  )
                }
                showHeader={false}
              />
            </AgentSection>
          )
      )}

      {loading && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
          <div className="flex items-center gap-3">
            <LoaderCircle
              size={20}
              className="animate-spin text-brand"
            />

            <div>
              <h2 className="text-sm font-semibold text-midnight">
                CareerPilot Agent is working
              </h2>

              <p className="mt-1 text-xs leading-5 text-text-muted">
                Planning, executing, evaluating, and
                replanning your goal when required.
              </p>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}


function AgentCapability({
  icon,
  title,
  description,
}) {
  return (
    <div className="rounded-xl border border-border-soft bg-white p-4 text-left">
      <div className="text-brand">
        {icon}
      </div>
      <p className="mt-3 text-sm font-semibold text-midnight">
        {title}
      </p>
      <p className="mt-1 text-xs leading-5 text-text-muted">
        {description}
      </p>
    </div>
  );
}


function AgentSection({
  title,
  icon,
  children,
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-border-soft bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-border-soft px-5 py-4 text-brand">
        {icon}
        <p className="text-[11px] font-bold uppercase tracking-[0.14em]">
          {title}
        </p>
      </div>
      <div className="p-5">
        {children}
      </div>
    </div>
  );
}


/* ==================================================
   EMPTY CHAT
   ================================================== */

function EmptyChat({
  onSuggestion,
}) {
  const featuredPrompts =
    PROMPT_SUGGESTIONS.slice(
      0,
      4
    );

  return (
    <div className="flex min-h-[390px] flex-col items-center justify-center px-6 text-center">

      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-soft text-brand">
        <Bot size={25} />
      </div>

      <h2 className="mt-5 text-xl font-semibold tracking-tight text-midnight">
        Start a career conversation
      </h2>

      <p className="mt-3 max-w-md text-sm leading-7 text-text-muted">
        Ask CareerPilot about your target role,
        preparation priorities, projects, skills,
        or the next practical step in your journey.
      </p>

      <div className="mt-6 flex max-w-2xl flex-wrap justify-center gap-2">

        {featuredPrompts.map(
          (prompt) => (
            <PromptChip
              key={prompt}
              onClick={() =>
                onSuggestion?.(
                  prompt
                )
              }
            >
              {prompt}
            </PromptChip>
          )
        )}

      </div>

    </div>
  );
}



/* ==================================================
   CHAT BUBBLE
   ================================================== */

function ChatBubble({
  role,
  content,
  onContinueProject,
  onProjectFollowUp,
}) {
  const isUser =
    role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3">

        <div className="max-w-[78%] whitespace-pre-wrap rounded-2xl rounded-tr-sm bg-brand px-4 py-3 text-sm leading-7 text-white">
          {cleanDisplayText(
            content
          )}
        </div>

        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-midnight text-white">
          <User size={17} />
        </div>

      </div>
    );
  }


  /* ==================================================
     NATURAL / MARKDOWN-LIKE RESPONSE
     ================================================== */

  if (
    typeof content === "string"
  ) {
    return (
      <div className="flex gap-3">

        <AssistantIcon />

        <RichTextResponse
          content={content}
        />

      </div>
    );
  }


  /* ==================================================
     PROJECT COACH
     ================================================== */

  if (
    isProjectCoachResponse(
      content
    )
  ) {
    return (
      <div className="flex gap-3">

        <AssistantIcon />

        <ProjectCoachCard
          content={content}
          onContinue={
            onContinueProject
          }
          onFollowUp={
            onProjectFollowUp
          }
        />

      </div>
    );
  }


  /* ==================================================
     GENERIC STRUCTURED RESPONSE
     ================================================== */

  if (
    content &&
    typeof content === "object"
  ) {
    return (
      <div className="flex gap-3">

        <AssistantIcon />

        <div className="w-full max-w-[760px] overflow-hidden rounded-2xl rounded-tl-sm border border-border-soft bg-white shadow-sm">

          {content.next_learning_step && (
            <StructuredHeader
              eyebrow="RECOMMENDED NEXT STEP"
              title={
                content.next_learning_step
              }
            />
          )}

          {content.next_backend_focus && (
            <StructuredHeader
              eyebrow="NEXT BACKEND FOCUS"
              title={
                content.next_backend_focus
              }
            />
          )}

          {content.recommended_project && (
            <ObjectHeader
              eyebrow="RECOMMENDED PROJECT"
              value={
                content.recommended_project
              }
            />
          )}

          {content.project_kickoff_plan && (
            <StructuredHeader
              eyebrow="PROJECT KICKOFF PLAN"
              title={
                content.project_kickoff_plan
              }
            />
          )}

          <div className="space-y-6 p-5">

            <GenericFields
              content={
                content
              }
            />

          </div>

        </div>

      </div>
    );
  }

  return null;
}


/* ==================================================
   RICH NATURAL TEXT RESPONSE
   ================================================== */

function RichTextResponse({
  content,
   showHeader = true,
}) {
  const blocks =
    parseRichTextBlocks(
      content
    );

  return (
    <div className="w-full max-w-[760px] overflow-hidden rounded-2xl rounded-tl-sm border border-border-soft bg-white shadow-sm">

            {showHeader && (
        <div className="border-b border-border-soft bg-white px-5 py-4">

          <div className="flex items-center gap-2">

            <Sparkles
              size={15}
              className="text-brand"
            />

            <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">
              CareerPilot Guidance
            </p>

          </div>

        </div>
      )}
      <div className="space-y-4 p-5 sm:p-6">

        {blocks.map(
          (
            block,
            index
          ) => (
            <RichTextBlock
              key={index}
              block={block}
            />
          )
        )}

      </div>

    </div>
  );
}


/* ==================================================
   RICH TEXT BLOCK
   ================================================== */

function RichTextBlock({
  block,
}) {
  if (
    block.type === "heading1"
  ) {
    return (
      <h2 className="pt-1 text-xl font-bold tracking-tight text-midnight">
        <InlineFormattedText
          text={block.text}
        />
      </h2>
    );
  }


  if (
    block.type === "heading2"
  ) {
    return (
      <div className="pt-3">

        <h3 className="text-base font-semibold text-midnight">
          <InlineFormattedText
            text={block.text}
          />
        </h3>

      </div>
    );
  }


  if (
    block.type === "heading3"
  ) {
    return (
      <div className="mt-2 rounded-xl border border-border-soft bg-app-bg p-4">

        <div className="flex gap-3">

          {block.number ? (
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
              {String(
                block.number
              ).padStart(
                2,
                "0"
              )}
            </div>
          ) : (
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
              <MessageSquareText
                size={15}
              />
            </div>
          )}

          <h4 className="pt-1 text-sm font-semibold leading-6 text-midnight">
            <InlineFormattedText
              text={block.text}
            />
          </h4>

        </div>

      </div>
    );
  }


  if (
    block.type === "numbered"
  ) {
    return (
      <div className="rounded-xl border border-border-soft bg-app-bg p-4">

        <div className="flex gap-3">

          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
            {String(
              block.number
            ).padStart(
              2,
              "0"
            )}
          </div>

          <p className="pt-1 text-sm font-medium leading-6 text-midnight">
            <InlineFormattedText
              text={block.text}
            />
          </p>

        </div>

      </div>
    );
  }


  if (
    block.type === "bullet"
  ) {
    const {
      label,
      description,
    } =
      splitBulletLabel(
        block.text
      );

    return (
      <div className="flex gap-3 pl-1">

        <CheckCircle2
          size={16}
          className="mt-1.5 shrink-0 text-brand"
        />

        <p className="text-sm leading-7 text-text-muted">

          {label ? (
            <>
              <span className="font-semibold text-midnight">
                <InlineFormattedText
                  text={label}
                />
              </span>

              {description && (
                <>
                  {": "}

                  <InlineFormattedText
                    text={
                      description
                    }
                  />
                </>
              )}
            </>
          ) : (
            <InlineFormattedText
              text={block.text}
            />
          )}

        </p>

      </div>
    );
  }


  if (
    block.type === "divider"
  ) {
    return (
      <div className="py-2">
        <div className="h-px bg-border-soft" />
      </div>
    );
  }


  if (
    block.type === "code"
  ) {
    return (
      <div className="overflow-x-auto rounded-xl bg-midnight p-4">

        <div className="mb-3 flex items-center gap-2 text-gray-400">

          <Code2 size={14} />

          <span className="text-[10px] font-semibold uppercase tracking-[0.12em]">
            Code
          </span>

        </div>

        <pre className="whitespace-pre-wrap font-mono text-xs leading-6 text-gray-200">
          {block.text}
        </pre>

      </div>
    );
  }


  return (
    <p className="text-sm leading-7 text-text-muted">
      <InlineFormattedText
        text={block.text}
      />
    </p>
  );
}


/* ==================================================
   INLINE TEXT FORMATTING
   ================================================== */

function InlineFormattedText({
  text,
}) {
  const value =
    String(
      text ?? ""
    );

  /*
   * Supports:
   * **bold**
   * `inline code`
   *
   * No external markdown dependency required.
   */

  const parts =
    value.split(
      /(\*\*[^*]+\*\*|`[^`]+`)/g
    );

  return (
    <>
      {parts.map(
        (
          part,
          index
        ) => {
          if (
            part.startsWith("**") &&
            part.endsWith("**")
          ) {
            return (
              <strong
                key={index}
                className="font-semibold text-midnight"
              >
                {part.slice(
                  2,
                  -2
                )}
              </strong>
            );
          }

          if (
            part.startsWith("`") &&
            part.endsWith("`")
          ) {
            return (
              <code
                key={index}
                className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[0.9em] text-midnight"
              >
                {part.slice(
                  1,
                  -1
                )}
              </code>
            );
          }

          return (
            <span key={index}>
              {cleanMathArtifacts(
                part
              )}
            </span>
          );
        }
      )}
    </>
  );
}


/* ==================================================
   NATURAL TEXT PARSER
   ================================================== */

function parseRichTextBlocks(
  content
) {
  const normalized =
    String(
      content ?? ""
    )
      .replace(
        /\r\n/g,
        "\n"
      )
      .trim();

  if (!normalized) {
    return [];
  }

  const lines =
    normalized.split("\n");

  const blocks = [];

  let codeBuffer = [];
  let inCodeBlock =
    false;

  let paragraphBuffer = [];


  function flushParagraph() {
    if (
      paragraphBuffer.length === 0
    ) {
      return;
    }

    blocks.push({
      type: "paragraph",
      text:
        paragraphBuffer
          .join(" ")
          .trim(),
    });

    paragraphBuffer = [];
  }


  function flushCode() {
    if (
      codeBuffer.length === 0
    ) {
      return;
    }

    blocks.push({
      type: "code",
      text:
        codeBuffer.join(
          "\n"
        ),
    });

    codeBuffer = [];
  }


  lines.forEach(
    (rawLine) => {
      const line =
        rawLine.trim();


      /* Code fence */

      if (
        line.startsWith("```")
      ) {
        flushParagraph();

        if (inCodeBlock) {
          flushCode();
          inCodeBlock =
            false;
        } else {
          inCodeBlock =
            true;
        }

        return;
      }


      if (inCodeBlock) {
        codeBuffer.push(
          rawLine
        );

        return;
      }


      /* Empty */

      if (!line) {
        flushParagraph();
        return;
      }


      /* Divider */

      if (
        /^-{3,}$/.test(
          line
        ) ||
        /^_{3,}$/.test(
          line
        )
      ) {
        flushParagraph();

        blocks.push({
          type: "divider",
        });

        return;
      }


      /* Heading 1 */

      if (
        /^#\s+/.test(
          line
        )
      ) {
        flushParagraph();

        blocks.push({
          type: "heading1",
          text:
            line.replace(
              /^#\s+/,
              ""
            ),
        });

        return;
      }


      /* Heading 2 */

      if (
        /^##\s+/.test(
          line
        )
      ) {
        flushParagraph();

        blocks.push({
          type: "heading2",
          text:
            line.replace(
              /^##\s+/,
              ""
            ),
        });

        return;
      }


      /* Heading 3 */

      if (
        /^###\s+/.test(
          line
        )
      ) {
        flushParagraph();

        const headingText =
          line.replace(
            /^###\s+/,
            ""
          );

        const numberedHeading =
          headingText.match(
            /^(\d+)\.\s*(.+)$/
          );

        blocks.push({
          type: "heading3",
          number:
            numberedHeading
              ? Number(
                  numberedHeading[1]
                )
              : null,
          text:
            numberedHeading
              ? numberedHeading[2]
              : headingText,
        });

        return;
      }


      /* Numbered item */

      const numberedMatch =
        line.match(
          /^(\d+)[.)]\s+(.+)$/
        );

      if (
        numberedMatch
      ) {
        flushParagraph();

        blocks.push({
          type: "numbered",
          number:
            Number(
              numberedMatch[1]
            ),
          text:
            numberedMatch[2],
        });

        return;
      }


      /* Bullet */

      const bulletMatch =
        line.match(
          /^[-*•]\s+(.+)$/
        );

      if (
        bulletMatch
      ) {
        flushParagraph();

        blocks.push({
          type: "bullet",
          text:
            bulletMatch[1],
        });

        return;
      }


      /*
       * Lines beginning with a bold label
       * are frequently AI-generated bullet-style
       * explanation lines even when the model
       * forgot the bullet marker.
       */

      if (
        /^\*\*[^*]+:\*\*/.test(
          line
        )
      ) {
        flushParagraph();

        blocks.push({
          type: "bullet",
          text: line,
        });

        return;
      }


      paragraphBuffer.push(
        line
      );
    }
  );

  flushParagraph();

  if (inCodeBlock) {
    flushCode();
  }

  return blocks;
}


/* ==================================================
   BULLET LABEL PARSER
   ================================================== */

function splitBulletLabel(
  text
) {
  const cleaned =
    String(
      text ?? ""
    ).trim();

  /*
   * **Problem Solved:** explanation
   */

  const boldMatch =
    cleaned.match(
      /^\*\*([^*]+?):\*\*\s*(.*)$/
    );

  if (boldMatch) {
    return {
      label:
        boldMatch[1],
      description:
        boldMatch[2],
    };
  }


  /*
   * Problem Solved: explanation
   */

  const plainMatch =
    cleaned.match(
      /^([^:]{1,45}):\s+(.+)$/
    );

  if (plainMatch) {
    return {
      label:
        plainMatch[1],
      description:
        plainMatch[2],
    };
  }


  return {
    label: null,
    description: cleaned,
  };
}


/* ==================================================
   PROJECT COACH DETECTION
   ================================================== */

function isProjectCoachResponse(
  content
) {
  if (
    !content ||
    typeof content !== "object" ||
    Array.isArray(content)
  ) {
    return false;
  }

  const coachFields = [
    "project_name",
    "current_stage",
    "project_complete",
    "why_this_matters",
    "step_by_step_plan",
    "step_by_step_execution_plan",
    "actionable_next_step",
    "interview_tip",
  ];

  const matchedFields =
    coachFields.filter(
      (field) =>
        content[field] !== null &&
        content[field] !== undefined &&
        content[field] !== ""
    );

  return (
    Boolean(
      content.project_name
    ) &&
    matchedFields.length >= 3
  );
}


/* ==================================================
   PROJECT COACH CARD
   ================================================== */

function ProjectCoachCard({
  content,
  onContinue,
  onFollowUp,
}) {
  const projectName =
    content.project_name ||
    "CareerPilot Project";

  const currentStage =
    content.current_stage ||
    "Current stage";

  const stageNumber =
    getStageNumber(
      currentStage
    );

  const isComplete =
    content.project_complete ===
      true ||
    stageNumber >= 6;

  const whyThisMatters =
    content.why_this_matters ||
    content.why_it_matters ||
    null;

  const stagePlan =
    content.step_by_step_plan ||
    content.step_by_step_execution_plan ||
    content.execution_plan ||
    [];

  const actionableNextStep =
    content.actionable_next_step ||
    content.next_action ||
    null;

  const interviewTip =
    content.interview_tip ||
    content.interview_preparation_tip ||
    null;

  const ignoredKeys =
    new Set([
      "project_name",
      "current_stage",
      "project_complete",
      "why_this_matters",
      "why_it_matters",
      "step_by_step_plan",
      "step_by_step_execution_plan",
      "execution_plan",
      "actionable_next_step",
      "next_action",
      "interview_tip",
      "interview_preparation_tip",
    ]);

  const extraFields =
    Object.entries(
      content
    ).filter(
      ([key, value]) =>
        !ignoredKeys.has(key) &&
        value !== null &&
        value !== undefined &&
        value !== ""
    );

  return (
    <div className="w-full max-w-[780px] overflow-hidden rounded-2xl rounded-tl-sm border border-border-soft bg-white shadow-sm">

      <div className="border-b border-emerald-100 bg-emerald-50/70 p-5 sm:p-6">

        <div className="flex flex-wrap items-center justify-between gap-3">

          <div className="flex items-center gap-2 text-brand">

            <Sparkles
              size={16}
            />

            <p className="text-[11px] font-bold tracking-[0.15em]">
              PROJECT COACH
            </p>

          </div>

          {isComplete ? (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-white px-3 py-1 text-[11px] font-semibold text-emerald-700">

              <Check
                size={12}
              />

              Project complete

            </span>
          ) : (
            <span className="rounded-full border border-emerald-200 bg-white px-3 py-1 text-[11px] font-semibold text-brand">
              Stage {stageNumber || "•"} of 6
            </span>
          )}

        </div>

        <h3 className="mt-4 text-xl font-semibold tracking-tight text-midnight sm:text-2xl">
          {cleanDisplayText(
            projectName
          )}
        </h3>

        <div className="mt-4 flex items-start gap-3 rounded-xl border border-emerald-100 bg-white/80 p-3">

          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
            <Target
              size={16}
            />
          </div>

          <div className="min-w-0">

            <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-text-muted">
              {isComplete
                ? "Final Stage"
                : "Current Stage"}
            </p>

            <p className="mt-1 text-sm font-semibold leading-6 text-midnight">
              {cleanDisplayText(
                currentStage
              )}
            </p>

          </div>

        </div>

      </div>


      <div className="space-y-7 p-5 sm:p-6">

        {whyThisMatters && (
          <CoachSection
            icon={Lightbulb}
            title="Why This Matters"
          >

            <p className="text-sm leading-7 text-text-muted">
              {cleanDisplayText(
                whyThisMatters
              )}
            </p>

          </CoachSection>
        )}

        {hasContent(
          stagePlan
        ) && (
          <CoachSection
            icon={CircleDot}
            title={
              isComplete
                ? "Final Portfolio Tasks"
                : "Stage Tasks"
            }
          >

            <CoachSteps
              steps={
                normalizeSteps(
                  stagePlan
                )
              }
            />

          </CoachSection>
        )}

        {actionableNextStep && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 sm:p-5">

            <div className="flex gap-3">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand text-white">

                {isComplete ? (
                  <Check
                    size={17}
                  />
                ) : (
                  <Play
                    size={16}
                    fill="currentColor"
                  />
                )}

              </div>

              <div className="min-w-0">

                <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">
                  {isComplete
                    ? "Final Action"
                    : "Next Action"}
                </p>

                <p className="mt-2 text-sm leading-7 text-midnight">
                  {cleanDisplayText(
                    actionableNextStep
                  )}
                </p>

              </div>

            </div>

          </div>
        )}

        {interviewTip && (
          <div className="rounded-xl border border-border-soft bg-app-bg p-4 sm:p-5">

            <div className="flex gap-3">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-brand shadow-sm">
                <MessageSquareText
                  size={16}
                />
              </div>

              <div className="min-w-0">

                <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">
                  Interview Tip
                </p>

                <p className="mt-2 text-sm leading-7 text-text-muted">
                  {cleanDisplayText(
                    interviewTip
                  )}
                </p>

              </div>

            </div>

          </div>
        )}

        {extraFields.length > 0 && (
          <div className="space-y-6 border-t border-border-soft pt-6">

            {extraFields.map(
              (
                [key, value]
              ) => (
                <StructuredValue
                  key={key}
                  title={
                    formatLabel(
                      key
                    )
                  }
                  value={
                    value
                  }
                  numbered={
                    isNumberedField(
                      key
                    )
                  }
                />
              )
            )}

          </div>
        )}

        {!isComplete && (
          <div className="border-t border-border-soft pt-5">

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <p className="text-sm font-semibold text-midnight">
                  Finished this stage?
                </p>

                <p className="mt-1 text-xs leading-5 text-text-muted">
                  Complete the tasks first, then move
                  to the next fresher-friendly stage.
                </p>

              </div>

              <button
                type="button"
                onClick={() =>
                  onContinue?.(
                    projectName,
                    currentStage
                  )
                }
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-midnight px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-gray-800"
              >
                Continue to next stage

                <ArrowRight
                  size={16}
                />
              </button>

            </div>

          </div>
        )}

        {isComplete && (
          <div className="border-t border-border-soft pt-6">

            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">

              <div className="flex gap-4">

                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-emerald-600 shadow-sm">

                  <CheckCircle2
                    size={21}
                  />

                </div>

                <div>

                  <p className="font-semibold text-emerald-900">
                    Project journey complete
                  </p>

                  <p className="mt-2 text-sm leading-7 text-emerald-800">
                    You now have enough practical
                    project evidence for a fresher-level
                    portfolio. Focus on presenting it
                    clearly rather than adding unnecessary
                    advanced technologies.
                  </p>

                </div>

              </div>

            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-3">

              <ProjectFollowUpButton
                icon={
                  <MessageSquareText
                    size={16}
                  />
                }
                onClick={() =>
                  onFollowUp?.(
                    "interview",
                    projectName
                  )
                }
              >
                Interview Questions
              </ProjectFollowUpButton>

              <ProjectFollowUpButton
                icon={
                  <FileText
                    size={16}
                  />
                }
                onClick={() =>
                  onFollowUp?.(
                    "resume",
                    projectName
                  )
                }
              >
                Resume Bullets
              </ProjectFollowUpButton>

              <ProjectFollowUpButton
                icon={
                  <Sparkles
                    size={16}
                  />
                }
                onClick={() =>
                  onFollowUp?.(
                    "readme",
                    projectName
                  )
                }
              >
                Improve README
              </ProjectFollowUpButton>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}


/* ==================================================
   PROJECT FOLLOW-UP BUTTON
   ================================================== */

function ProjectFollowUpButton({
  icon,
  children,
  onClick,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center justify-center gap-2 rounded-xl border border-border-soft bg-white px-3 py-3 text-xs font-semibold text-midnight transition hover:border-emerald-200 hover:bg-emerald-50/40"
    >
      {icon}

      {children}
    </button>
  );
}


/* ==================================================
   COACH SECTION
   ================================================== */

function CoachSection({
  icon: Icon,
  title,
  children,
}) {
  return (
    <section>

      <div className="flex items-center gap-2">

        <Icon
          size={16}
          className="text-brand"
        />

        <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">
          {title}
        </p>

      </div>

      <div className="mt-3">
        {children}
      </div>

    </section>
  );
}


/* ==================================================
   COACH STEPS
   ================================================== */

function CoachSteps({
  steps = [],
}) {
  return (
    <div className="space-y-3">

      {steps.map(
        (
          step,
          index
        ) => (
          <div
            key={index}
            className="rounded-xl border border-border-soft bg-app-bg p-4"
          >

            <div className="flex gap-3">

              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
                {String(
                  index + 1
                ).padStart(
                  2,
                  "0"
                )}
              </div>

              <div className="min-w-0 flex-1">

                {step &&
                typeof step ===
                  "object" ? (
                  <StructuredObject
                    item={step}
                  />
                ) : (
                  <p className="text-sm leading-7 text-text-muted">
                    {cleanDisplayText(
                      step
                    )}
                  </p>
                )}

              </div>

            </div>

          </div>
        )
      )}

    </div>
  );
}


/* ==================================================
   STRUCTURED HEADER
   ================================================== */

function StructuredHeader({
  eyebrow,
  title,
}) {
  return (
    <div className="border-b border-border-soft bg-emerald-50/70 p-5">

      <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
        {eyebrow}
      </p>

      <h3 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
        {cleanDisplayText(
          title
        )}
      </h3>

    </div>
  );
}


/* ==================================================
   OBJECT HEADER
   ================================================== */

function ObjectHeader({
  eyebrow,
  value,
}) {
  if (
    !value ||
    typeof value !== "object"
  ) {
    return (
      <StructuredHeader
        eyebrow={eyebrow}
        title={
          cleanDisplayText(
            value
          )
        }
      />
    );
  }

  const title =
    value.project_name ||
    value.title ||
    value.name ||
    "CareerPilot recommendation";

  const description =
    value.description ||
    value.summary ||
    null;

  return (
    <div className="border-b border-border-soft bg-emerald-50/70 p-5">

      <p className="text-[11px] font-bold tracking-[0.14em] text-brand">
        {eyebrow}
      </p>

      <h3 className="mt-2 text-xl font-semibold tracking-tight text-midnight">
        {cleanDisplayText(
          title
        )}
      </h3>

      {description && (
        <p className="mt-3 text-sm leading-7 text-text-muted">
          {cleanDisplayText(
            description
          )}
        </p>
      )}

    </div>
  );
}


/* ==================================================
   ASSISTANT ICON
   ================================================== */

function AssistantIcon() {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
      <Bot size={17} />
    </div>
  );
}


/* ==================================================
   CAREER SECTION
   ================================================== */

function CareerSection({
  title,
  children,
}) {
  return (
    <section>

      <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">
        {title}
      </p>

      <div className="mt-3">
        {children}
      </div>

    </section>
  );
}


/* ==================================================
   GENERIC FIELDS
   ================================================== */

function GenericFields({
  content,
}) {
  const headerKeys =
    new Set([
      "next_learning_step",
      "next_backend_focus",
      "recommended_project",
      "project_kickoff_plan",
    ]);

  const remainingFields =
    Object.entries(
      content
    ).filter(
      ([key, value]) =>
        !headerKeys.has(key) &&
        value !== null &&
        value !== undefined &&
        value !== ""
    );

  if (
    remainingFields.length === 0
  ) {
    return null;
  }

  return (
    <>
      {remainingFields.map(
        (
          [key, value]
        ) => (
          <StructuredValue
            key={key}
            title={
              formatLabel(
                key
              )
            }
            value={
              value
            }
            numbered={
              isNumberedField(
                key
              )
            }
          />
        )
      )}
    </>
  );
}


/* ==================================================
   STRUCTURED VALUE
   ================================================== */

function StructuredValue({
  title,
  value,
  numbered = false,
}) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  if (
    Array.isArray(value)
  ) {
    return (
      <CareerList
        title={title}
        items={value}
        numbered={numbered}
      />
    );
  }

  if (
    typeof value === "object"
  ) {
    return (
      <CareerSection
        title={title}
      >

        <div className="rounded-xl bg-app-bg p-4">

          <StructuredObject
            item={value}
          />

        </div>

      </CareerSection>
    );
  }

  return (
    <CareerSection
      title={title}
    >

      <p className="text-sm leading-7 text-text-muted">
        {cleanDisplayText(
          value
        )}
      </p>

    </CareerSection>
  );
}


/* ==================================================
   CAREER LIST
   ================================================== */

function CareerList({
  title,
  items = [],
  numbered = false,
}) {
  return (
    <CareerSection
      title={title}
    >

      <div className="space-y-3">

        {items.map(
          (
            item,
            index
          ) => {
            const isObject =
              item &&
              typeof item === "object" &&
              !Array.isArray(item);

            return (
              <div
                key={index}
                className="rounded-xl bg-app-bg p-4"
              >

                <div className="flex gap-3">

                  {numbered ? (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-xs font-bold text-white">
                      {getItemNumber(
                        item,
                        index
                      )}
                    </div>
                  ) : (
                    <CheckCircle2
                      size={17}
                      className="mt-1 shrink-0 text-brand"
                    />
                  )}

                  <div className="min-w-0 flex-1">

                    {isObject ? (
                      <StructuredObject
                        item={item}
                      />
                    ) : (
                      <p className="text-sm leading-6 text-text-muted">
                        {cleanDisplayText(
                          item
                        )}
                      </p>
                    )}

                  </div>

                </div>

              </div>
            );
          }
        )}

      </div>

    </CareerSection>
  );
}


/* ==================================================
   STRUCTURED OBJECT
   ================================================== */

function StructuredObject({
  item,
}) {
  const title =
    item.action ||
    item.topic ||
    item.project_name ||
    item.title ||
    item.name ||
    item.skill ||
    item.priority ||
    item.phase ||
    null;

  const description =
    item.details ||
    item.focus ||
    item.description ||
    item.summary ||
    item.reason ||
    item.explanation ||
    item.guidance ||
    null;

  const ignoredKeys =
    new Set([
      "step",
      "action",
      "topic",
      "project_name",
      "title",
      "name",
      "skill",
      "priority",
      "phase",
      "details",
      "focus",
      "description",
      "summary",
      "reason",
      "explanation",
      "guidance",
    ]);

  const remainingFields =
    Object.entries(
      item
    ).filter(
      ([key, value]) =>
        !ignoredKeys.has(key) &&
        value !== null &&
        value !== undefined &&
        value !== ""
    );

  return (
    <div>

      {title && (
        <p className="text-sm font-semibold text-midnight">
          {cleanDisplayText(
            title
          )}
        </p>
      )}

      {description && (
        <p className="mt-1 text-sm leading-6 text-text-muted">
          {cleanDisplayText(
            description
          )}
        </p>
      )}

      {remainingFields.length > 0 && (
        <div className="mt-3 space-y-3">

          {remainingFields.map(
            (
              [key, value]
            ) => (
              <NestedField
                key={key}
                label={
                  formatLabel(
                    key
                  )
                }
                value={
                  value
                }
              />
            )
          )}

        </div>
      )}

    </div>
  );
}


/* ==================================================
   NESTED FIELD
   ================================================== */

function NestedField({
  label,
  value,
}) {
  if (
    Array.isArray(value)
  ) {
    return (
      <div>

        <p className="text-xs font-semibold text-midnight">
          {label}
        </p>

        <div className="mt-2 space-y-2">

          {value.map(
            (
              item,
              index
            ) => (
              <div
                key={index}
                className="flex gap-2"
              >

                <ArrowRight
                  size={14}
                  className="mt-1 shrink-0 text-brand"
                />

                {item &&
                typeof item ===
                  "object" ? (
                  <StructuredObject
                    item={item}
                  />
                ) : (
                  <p className="text-sm leading-6 text-text-muted">
                    {cleanDisplayText(
                      item
                    )}
                  </p>
                )}

              </div>
            )
          )}

        </div>

      </div>
    );
  }

  if (
    value &&
    typeof value === "object"
  ) {
    return (
      <div>

        <p className="text-xs font-semibold text-midnight">
          {label}
        </p>

        <div className="mt-2 rounded-lg border border-border-soft bg-white p-3">

          <StructuredObject
            item={value}
          />

        </div>

      </div>
    );
  }

  return (
    <p className="text-sm leading-6">

      <span className="font-semibold text-midnight">
        {label}:
      </span>{" "}

      <span className="text-text-muted">
        {cleanDisplayText(
          value
        )}
      </span>

    </p>
  );
}


/* ==================================================
   HELPERS
   ================================================== */

function formatLabel(
  value
) {
  return value
    .replaceAll(
      "_",
      " "
    )
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


function cleanDisplayText(
  value
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  return String(value)
    .replace(
      /`([^`]+)`/g,
      "$1"
    )
    .replace(
      /\*\*([^*]+)\*\*/g,
      "$1"
    )
    .trim();
}


/* ==================================================
   CLEAN LATEX / AI FORMATTING ARTIFACTS
   ================================================== */

function cleanMathArtifacts(
  value
) {
  return String(
    value ?? ""
  )
    .replace(
      /\$\\rightarrow\$/g,
      "→"
    )
    .replace(
      /\\rightarrow/g,
      "→"
    )
    .replace(
      /\$([^$]+)\$/g,
      "$1"
    )
    .replace(
      /\\\*/g,
      "*"
    );
}


function getItemNumber(
  item,
  index
) {
  if (
    item &&
    typeof item === "object" &&
    item.step !== undefined
  ) {
    return item.step;
  }

  return index + 1;
}


function isNumberedField(
  key
) {
  return [
    "step_by_step_plan",
    "step_by_step_execution_plan",
    "step_by_step_execution",
    "execution_plan",
    "action_plan",
    "action_plan_30_days",
    "immediate_action_steps",
    "immediate_action_items",
    "next_immediate_steps",
    "recommended_learning_topics",
    "recommended_learning_order",
    "practical_tasks",
  ].includes(key);
}


function normalizeSteps(
  value
) {
  if (
    Array.isArray(value)
  ) {
    return value.filter(Boolean);
  }

  if (!value) {
    return [];
  }

  return [value];
}


function hasContent(
  value
) {
  if (
    Array.isArray(value)
  ) {
    return (
      value.length > 0
    );
  }

  return (
    value !== null &&
    value !== undefined &&
    value !== ""
  );
}


/* ==================================================
   STAGE NUMBER
   ================================================== */

function getStageNumber(
  currentStage
) {
  if (
    !currentStage
  ) {
    return 0;
  }

  const match =
    String(
      currentStage
    ).match(
      /stage\s*(\d+)/i
    );

  if (!match) {
    return 0;
  }

  const number =
    Number(
      match[1]
    );

  return Number.isNaN(
    number
  )
    ? 0
    : number;
}


/* ==================================================
   PROMPT SUGGESTION
   ================================================== */

function PromptChip({
  children,
  onClick,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-full border border-border-soft bg-white px-3.5 py-2 text-left text-xs font-medium leading-5 text-midnight transition hover:border-emerald-200 hover:bg-brand-soft hover:text-brand"
    >
      {children}
    </button>
  );
}



export default CareerAI;
