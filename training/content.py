"""Course content for the T1 "Simple Copilot Agent Builder" track (English).

English is the source language. Translations live in ``training/locales/``
and are keyed by the same module slugs, lesson slugs and question codes.
Run ``python app.py reseed`` after editing to push changes into the
database (learner progress is kept).

Product facts were checked against Microsoft Learn and Microsoft Support on
blocks.VERIFIED_DATE (see blocks.SOURCES). Microsoft UI labels and features
vary by tenant and licence, so lessons tell learners to follow the labels
they actually see.
"""

from .blocks import SOURCES, VERIFIED_DATE, callout, copy, src

EDITION_DATE = VERIFIED_DATE

TENANT_NOTE = callout(
    "<strong>Your screen may look different.</strong> Microsoft updates Copilot often, and features depend on "
    "your licence and your organization's settings. Microsoft's current guides use the label <em>New agent</em>; "
    "if your screen shows something else, follow the label you actually see.",
    "note",
)

EMAIL_COACH_INSTRUCTIONS = """You are my Email Clarity Coach.
Your only job is to help rewrite work email drafts in simple, polite English.
Keep the meaning unchanged. Provide a clear subject line if useful.
Offer two versions when requested: short and friendly, or formal and professional.
If facts are missing, ask one short question or show a placeholder.
Do not invent dates, names, approvals, decisions, or company policy.
If the user asks about unrelated subjects, politely suggest using normal Copilot Chat.
Use the format: Improved email / What I changed / What to double-check.
Do not request sensitive or confidential data that is not needed."""

EXPENSE_HELPER_INSTRUCTIONS = """You are my Expense Policy Helper.
Answer questions only about expense and reimbursement policy using the approved sources I attach.
Base answers on the available policy text and include a source reference or document section when possible.
If the answer is not in the source, say you cannot confirm it and suggest checking with Finance.
Never guess limits, exceptions, deadlines, legal rules, or approval authority.
Do not request or expose employee bank details, private claims, or other sensitive data.
When a question is not about expense policy, politely direct the user to normal Copilot Chat.
Respond in this format: Short answer / Source or policy section / What to check next."""

TEMPLATE_CHARTER = """AGENT NAME: [short and specific, max 30 characters]
ONE PURPOSE: This agent helps me [one clear task] for [audience].
IN SCOPE: [2-4 things it should do]
OUT OF SCOPE: [2-4 things it must not do]
KNOWLEDGE: [none / specific approved source(s)]
OUTPUT STYLE: [short answer / steps / table / example]
WHEN UNSURE: Say what is missing; ask or refer to an authorized source.
PRIVACY RULE: Do not request or expose unnecessary sensitive data.
STARTER PROMPTS: 1. ... 2. ... 3. ...
OWNER: [role; avoid exposing private identity in training copies]
REVIEW DATE: [date]"""

TEMPLATE_INSTRUCTIONS = """You are [Agent Name].
Your ONE purpose is [single, measurable task].
Help [type of user] by [allowed actions].
Use only [authorized sources] when facts must be grounded.
Reply with [requested output format] in simple English.
If information is unclear or missing, ask for clarification or say you cannot confirm it.
Never invent facts, policy limits, citations, or decisions.
Do not reveal sensitive data or bypass access rules.
If a request is outside [your purpose], briefly say so and recommend standard Copilot Chat or a suitable agent."""

TEMPLATE_TEST_CARD = """TEST 1 - ON TOPIC: [prompt]  Expected: completes the specific job correctly.
TEST 2 - UNCLEAR: [prompt]   Expected: requests clarification / states uncertainty.
TEST 3 - OFF TOPIC: [prompt] Expected: politely redirects rather than drifting.
FINAL CHECKS: source verified? no invented facts? safe data? correct permissions?
RESULT: PASS / REVISE
IMPROVEMENT MADE: [one clear edit to the agent instructions]"""

TEMPLATES = [
    {"slug": "charter", "title": "Template A: One-Purpose Agent Charter",
     "use": "Fill this in before you open the builder. It forces you to name one job.", "body": TEMPLATE_CHARTER},
    {"slug": "instructions", "title": "Template B: Copy-ready Agent Instructions",
     "use": "Paste into the Instructions box on the Configure tab and replace every [bracket]. Instructions can be up to 8,000 characters.",
     "body": TEMPLATE_INSTRUCTIONS},
    {"slug": "test-card", "title": "Template C: 3-Test Agent Quality Card",
     "use": "Run all three tests on the Try it tab every time you change the instructions.", "body": TEMPLATE_TEST_CARD},
    {"slug": "email-coach", "title": "Example A: Email Clarity Coach instructions",
     "use": "Name: Email Clarity Coach. Description: Helps me improve the clarity, tone and structure of work emails.",
     "body": EMAIL_COACH_INSTRUCTIONS},
    {"slug": "expense-helper", "title": "Example B: Expense Policy Helper instructions",
     "use": "Name: Expense Policy Helper. Description: Helps me find answers in my organization's approved expense policy.",
     "body": EXPENSE_HELPER_INSTRUCTIONS},
]

# Kept for backwards compatibility with earlier code.
_copy_block = copy


CASE_SOURCES = """
<h4>Source leads (verify before use)</h4>
<ul class="small">
<li><a href="https://www.microsoft.com/en/customers/story/25909-heineken-microsoft-copilot-studio" target="_blank" rel="noopener">HEINEKEN</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/25674-kantar-microsoft-copilot-studio" target="_blank" rel="noopener">Kantar (Copilot Studio)</a> &middot; <a href="https://www.microsoft.com/en/customers/story/24603-kantar-microsoft-365-copilot" target="_blank" rel="noopener">Kantar (Microsoft 365 Copilot)</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/23132-epiq-global-microsoft-power-platform" target="_blank" rel="noopener">Epiq Global</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/24130-peoplecert-hellas-ae-azure-openai" target="_blank" rel="noopener">PeopleCert</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/23332-games-global-microsoft-copilot-studio" target="_blank" rel="noopener">Games Global</a></li>
<li><a href="https://www.microsoft.com/en-us/power-platform/blog/power-apps/power-platform-stories/" target="_blank" rel="noopener">Power Platform stories (Komatsu Australia)</a></li>
<li><a href="https://news.microsoft.com/source/features/digital-transformation/accenture-is-rolling-out-copilot-to-a-workforce-the-size-of-denver/" target="_blank" rel="noopener">Accenture</a></li>
<li><a href="https://www.emiratesnbd.com/en/media-center/emirates-nbd-to-transform-business-operations-and-enhance-productivity-with-generative-ai" target="_blank" rel="noopener">Emirates NBD</a></li>
</ul>
"""


# ---------------------------------------------------------------------------
# Modules and lessons
# ---------------------------------------------------------------------------

MODULES = [
    {
        "slug": "welcome",
        "title": "1. Welcome and outcomes",
        "summary": "Why a personal agent can help you, and what you will be able to do by the end.",
        "minutes": 10,
        "lessons": [
            {
                "slug": "why-agents",
                "title": "Build your own helpful AI agent",
                "minutes": 4,
                "body": """
<p>Many associates repeat the same small tasks every week: tidying an email, finding a rule in a policy,
turning notes into a checklist. A <strong>Copilot agent</strong> is a small helper you set up once for one
of those jobs, so you do not have to explain the job again every time.</p>
""" + callout("<strong>Plain-English idea:</strong> An agent is Copilot with a job description.", "analogy") + """
<p>That is a way to picture it, not a technical guarantee. More precisely, an agent is a version of Copilot
that follows the <em>instructions</em> you wrote and, where you add them, uses the <em>knowledge sources</em>
you are allowed to use.</p>
<h3>Who this course is for</h3>
<ul>
<li>Any associate. No programming experience is needed.</li>
<li>People who want one focused helper for their own work.</li>
<li>People who will later move on to the advanced Copilot Studio training.</li>
</ul>
<h3>The tool we use</h3>
<p>This course covers <strong>Agent Builder in Microsoft 365 Copilot</strong> (we call it <strong>T1</strong>).
Microsoft describes it as a tool for quick, straightforward agents. You can open it in the Microsoft 365 Copilot app,
at microsoft365.com/chat, and in the Teams desktop and web apps. It is <em>not</em> available in the mobile apps.
This course does not cover the separate, more powerful Microsoft Copilot Studio.</p>
""" + src(["overview", "build_guide"]),
            },
            {
                "slug": "outcomes",
                "title": "What you will be able to do",
                "minutes": 3,
                "body": """
<p>By the end of the course you should be able to:</p>
<ol>
<li>Explain in plain words what an agent is, and when to use ordinary Copilot Chat instead.</li>
<li>Name <strong>one clear purpose</strong> for an agent and write what it should <strong>not</strong> do.</li>
<li>Create an agent on the <strong>Describe</strong> tab, on the <strong>Configure</strong> tab, or from a template.</li>
<li>Add a clear name, description, instructions, starter prompts and permitted knowledge sources.</li>
<li>Test a good prompt, a vague prompt and an unrelated prompt on the <strong>Try it</strong> tab, then improve the instructions.</li>
<li>Find your agent again and explain the difference between <strong>sharing an agent</strong> and
<strong>sharing a chat</strong>.</li>
<li>Tell apart chat history, Copilot memory and the agent's own instructions and knowledge.</li>
<li>Use a starter template to make a second narrow-purpose agent.</li>
</ol>
""",
            },
            {
                "slug": "how-course-works",
                "title": "How this course works",
                "minutes": 3,
                "body": """
<p>Each module follows the same rhythm: <strong>show, explain, try, check, reflect</strong>.</p>
<table class="grid">
<tr><th>Step</th><th>What you do in this app</th></tr>
<tr><td>Learn</td><td>Read each lesson and press <em>Mark lesson complete</em>.</td></tr>
<tr><td>Check</td><td>Take the short quiz at the end of each module. You can retry.</td></tr>
<tr><td>Practise</td><td>Work through the 12-step hands-on lab in Microsoft 365 Copilot and tick each step.</td></tr>
<tr><td>Plan</td><td>Fill in your own Agent Charter on the <em>My agent charter</em> page.</td></tr>
<tr><td>Prove</td><td>Pass the final assessment to unlock your certificate.</td></tr>
</table>
<h3>Six messages you will see again and again</h3>
<ul>
<li><strong>One agent = one purpose.</strong></li>
<li><strong>Use the right conversation for the right topic.</strong></li>
<li><strong>An agent is not permanently trained by every question.</strong></li>
<li><strong>Sharing the agent does not by itself share your personal chat history.</strong></li>
<li><strong>Knowledge access is permission-based.</strong></li>
<li><strong>Always verify important outputs.</strong></li>
</ul>
<p>The full course takes about 150 minutes including the lab. A 60-minute essentials route is: modules 2, 3, 4, 6 and 7, then lab steps 1 to 8.</p>
<p>The <a href="/quickref">Quick reference card</a>, <a href="/glossary">Glossary</a> and <a href="/resources">Microsoft references</a> pages are always available from the menu.</p>
""",
            },
        ],
    },
    {
        "slug": "basics",
        "title": "2. Agent basics",
        "summary": "Agent versus normal chat, the one-purpose principle, and T1 versus Copilot Studio.",
        "minutes": 15,
        "lessons": [
            {
                "slug": "agent-vs-chat",
                "title": "Agent or normal Copilot Chat?",
                "minutes": 5,
                "body": """
<p>Ordinary <strong>Copilot Chat</strong> is a general assistant: you can ask it almost anything, and you explain
the task each time. An <strong>agent</strong> is set up in advance for one job, with instructions, an answer format
and (optionally) approved knowledge.</p>
<table class="grid">
<tr><th>Use normal Copilot Chat when...</th><th>Use a purpose-built agent when...</th></tr>
<tr><td>The question is a one-off.</td><td>You do the same kind of task again and again.</td></tr>
<tr><td>The topic changes from question to question.</td><td>The topic stays inside one clear job.</td></tr>
<tr><td>You do not need a fixed answer format.</td><td>You want the same structure every time.</td></tr>
</table>
""" + callout("<strong>Plain-English idea:</strong> Instructions tell it <em>how</em> to help; knowledge sources tell it <em>what information</em> to use.", "analogy") + """
<h3>No code needed</h3>
<p>In Agent Builder you describe what you want in everyday language, then review and adjust the settings.
Microsoft gives examples such as a writing coach that follows your organization's standards, or a team onboarding helper.
You do not write code, call APIs or design workflows.</p>
""" + src(["overview"]),
            },
            {
                "slug": "one-purpose",
                "title": "One agent, one purpose",
                "minutes": 5,
                "body": callout("<strong>Plain-English idea:</strong> One agent, one job, like having a separate folder for each subject.", "analogy") + """
<p>When an agent has one narrow job, its instructions stay short and clear, and you can easily test whether it
does that job well. When an agent tries to do many unrelated things, the instructions become vague and the
results become less predictable.</p>
<div class="two-col">
<div class="good"><h4>Good: one purpose</h4><ul>
<li>"Rewrite my work email drafts in clear, polite English."</li>
<li>"Answer questions from our approved expense policy."</li>
<li>"Turn my meeting notes into a short action list."</li></ul></div>
<div class="bad"><h4>Not good: mixed jobs</h4><ul>
<li>"Help with expense policies, Spanish lessons and holiday planning."</li>
<li>"Help with anything."</li>
<li>"Be my HR, IT and finance assistant."</li></ul></div>
</div>
<p><strong>Use the right conversation for the right topic.</strong> If you have a question that is not about the
agent's job, open normal Copilot Chat or a more suitable agent. Unrelated questions make the current conversation
noisy, and where memory is turned on, Copilot may keep useful details from your chats.</p>
<p class="tag">Course best practice. It matches Microsoft's guidance that the description and instructions should clearly say what the agent is for.</p>
""" + src(["build", "memory"]),
            },
            {
                "slug": "t1-vs-studio",
                "title": "T1 Agent Builder versus Copilot Studio",
                "minutes": 5,
                "body": """
<table class="grid">
<tr><th></th><th>T1: Agent Builder in Microsoft 365 Copilot</th><th>Microsoft Copilot Studio</th></tr>
<tr><td>Who</td><td>Information workers building for themselves or a small team</td><td>Makers and developers building for a department, the whole organization or external customers</td></tr>
<tr><td>Typical use</td><td>Quick, no-code helpers that answer from existing content (FAQ, documentation, onboarding)</td><td>Workflows, approvals, custom connectors, autonomous agents, external publishing</td></tr>
<tr><td>Managed in</td><td>Microsoft 365 admin center</td><td>Power Platform admin center</td></tr>
<tr><td>In this course?</td><td>Yes</td><td>No, it is the next level</td></tr>
</table>
<p>Agent Builder cannot create actions that connect to outside services. When you need those, Microsoft lets you
<strong>copy an agent to Copilot Studio</strong> and keep its configuration. In this course we label such features
<strong>"Next-level capability, not covered by T1."</strong></p>
<h3>Licences</h3>
<p>According to Microsoft, both tools are included with a Microsoft 365 Copilot licence. Users without that licence may be able to use
Copilot Credits or pay-as-you-go, and Agent Builder can be used free of charge for agents that use web knowledge only.
What you can do depends on what your organization has enabled.</p>
""" + src(["compare_studio", "overview"]),
            },
        ],
    },
    {
        "slug": "plan",
        "title": "3. Plan your agent",
        "summary": "Write a one-sentence purpose, what it does and does not do, who it is for and what knowledge is safe.",
        "minutes": 15,
        "lessons": [
            {
                "slug": "purpose-sentence",
                "title": "Write a one-sentence purpose",
                "minutes": 5,
                "body": """
<p>Before you open the builder, finish this sentence:</p>
""" + callout("<strong>This agent helps me</strong> [one clear task] <strong>for</strong> [audience].") + """
<p>Examples:</p>
<ul>
<li>This agent helps me <em>rewrite my work email drafts in clear, polite English</em> for <em>my colleagues and customers</em>.</li>
<li>This agent helps me <em>find answers in our approved expense policy</em> for <em>my own expense claims</em>.</li>
</ul>
<p>If your sentence needs the word "and" to join two unrelated jobs, you probably need two agents.</p>
<p>Your purpose sentence becomes the agent's <strong>description</strong>. Microsoft notes that Copilot uses the description
to decide when to use the agent, and users see it too, so make it clear.</p>
""" + src(["build"]),
            },
            {
                "slug": "does-does-not",
                "title": "Does / does not",
                "minutes": 5,
                "body": """
<p>Write 2 to 4 things the agent <strong>should do</strong> and 2 to 4 things it <strong>must not do</strong>.
The "does not" list becomes the boundary rules in your instructions.</p>
<table class="grid">
<tr><th>Email Clarity Coach does</th><th>Email Clarity Coach does not</th></tr>
<tr><td>Rewrite my drafts in simple, polite English</td><td>Invent dates, names, approvals or policy</td></tr>
<tr><td>Suggest a subject line</td><td>Answer unrelated questions (it redirects to Copilot Chat)</td></tr>
<tr><td>Explain what it changed</td><td>Ask for confidential data it does not need</td></tr>
</table>
<h3>Who will use it and what will they type?</h3>
<p>Think about the <strong>audience</strong> (just you, or colleagues later) and the <strong>input</strong>
(a pasted draft, a question, a list of notes). This helps you write good starter prompts.</p>
""",
            },
            {
                "slug": "safe-knowledge",
                "title": "Choose safe knowledge",
                "minutes": 5,
                "body": """
<p>Some agents need no extra knowledge at all (the Email Clarity Coach works on the text you paste). Others should
answer from an approved source (the Expense Policy Helper uses the official policy).</p>
<p>Microsoft lists these knowledge types for Agent Builder. Which ones you see depends on your licence and your admin's settings:</p>
<table class="grid small">
<tr><th>Source</th><th>Limit per agent (Microsoft Learn)</th></tr>
<tr><td>Public websites</td><td>4 URLs (up to two path levels, no query strings)</td></tr>
<tr><td>SharePoint files, folders or sites</td><td>100 files</td></tr>
<tr><td>OneDrive files</td><td>50 files</td></tr>
<tr><td>Uploaded (embedded) files</td><td>20 files; Word, PDF, PowerPoint and text up to 512 MB, Excel up to 30 MB</td></tr>
<tr><td>Teams chats and meetings, Outlook email, people data</td><td>Depends on licence</td></tr>
<tr><td>Copilot connectors</td><td>Set up by your admin</td></tr>
</table>
<ul>
<li>Use <strong>approved, current</strong> documents owned by the right team.</li>
<li>Do not add files with personal, customer or confidential data unless your company policy allows it.
Files that are password-protected or have restrictive sensitivity-label permissions are not supported.</li>
<li><strong>Knowledge access is permission-based.</strong> The agent respects each user's permissions and sensitivity labels.
A colleague only gets content from sources they are allowed to open. If you add <em>My emails</em>, people you share
the agent with do not get access to your email.</li>
</ul>
<p>Write your plan down in <a href="/charter">My agent charter</a> before you build.</p>
""" + src(["knowledge", "share_manage"]),
            },
        ],
    },
    {
        "slug": "build",
        "title": "4. Build in Microsoft 365 Copilot",
        "summary": "Find Agent Builder, start on the Describe tab, from Configure or from a template, and review the draft.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "find-builder",
                "title": "Open Copilot and find Agent Builder",
                "minutes": 5,
                "body": TENANT_NOTE + """
<ol class="steps">
<li>Open Microsoft 365 Copilot (the Microsoft 365 Copilot app, microsoft365.com/chat, or Copilot in Teams on desktop or web) and sign in with your work account.</li>
<li>In the navigation pane, find <strong>Agents</strong>.</li>
<li>Select <strong>New agent</strong>.</li>
</ol>
<p>You now see three ways to start:</p>
<table class="grid">
<tr><th>Way to start</th><th>When to use it</th></tr>
<tr><td><strong>Describe</strong> tab: chat with the builder in everyday language</td><td>Recommended for beginners</td></tr>
<tr><td><strong>Skip to configure</strong>: fill in each field yourself</td><td>When you already have your charter and instructions ready</td></tr>
<tr><td><strong>Start with a template</strong></td><td>When a built-in template is close to your one purpose</td></tr>
</table>
<p>If you do not see <strong>New agent</strong>, it may not be enabled for your licence or organization.
Ask your Copilot champion or IT service desk. Do not try to work around it.</p>
<p class="facilitator">Facilitator: show your organization's own verified screenshots of these screens here, with the date you checked them.</p>
""" + src(["build", "build_guide", "overview"]),
            },
            {
                "slug": "describe",
                "title": "Describe your agent in plain language",
                "minutes": 8,
                "body": """
<p>On the <strong>Describe</strong> tab, type what you want in everyday language and select <strong>Send</strong>.
As you chat, the builder fills in the name, description and instructions for you. You can keep refining,
for example: "Also suggest a subject line."</p>
<p>Example description to type:</p>
""" + copy(
                    "Create an agent called Email Clarity Coach. Its only job is to help me rewrite my own work "
                    "email drafts in simple, polite English without changing the meaning. It should not invent facts "
                    "and should redirect unrelated questions to normal Copilot Chat."
                ) + """
<p>You can also add knowledge while describing: select the plus sign (<strong>+</strong>) in the chat box, or describe the source.</p>
<p>Read what the builder proposes. It is a draft, not a finished agent. You will check and tighten it on the Configure tab.</p>
""" + callout("Microsoft notes that the Describe tab only works when your Microsoft 365 language is one of the supported languages. If it is not available in your language, use <strong>Skip to configure</strong> and paste your instructions.", "note") + """
<p>With a <strong>template</strong>, the agent is created straight away. You then narrow it to your one purpose on Describe or Configure.</p>
""" + src(["build", "build_guide"]),
            },
            {
                "slug": "configure-tab",
                "title": "Review everything in Configure",
                "minutes": 7,
                "body": """
<p>Open the <strong>Configure</strong> tab. Here you can see and edit each setting directly:</p>
<table class="grid">
<tr><th>Setting</th><th>What to check</th><th>Limit</th></tr>
<tr><td>Name</td><td>Short and specific, e.g. "Email Clarity Coach"</td><td>30 characters</td></tr>
<tr><td>Icon</td><td>Generate, browse or upload (PNG with a transparent background works best)</td><td>192 x 192 px, 1 MB</td></tr>
<tr><td>Description</td><td>One sentence a colleague would understand</td><td>1,000 characters</td></tr>
<tr><td>Instructions</td><td>Role, allowed topics, answer format, what to do when unsure, off-topic rule</td><td>8,000 characters</td></tr>
<tr><td>Knowledge</td><td>Only approved sources you are allowed to use, or none</td><td>Depends on source type</td></tr>
<tr><td>Starter prompts</td><td>Three examples that match the one purpose (each has a title and the prompt text)</td><td>-</td></tr>
</table>
<p>Use the <strong>Try it</strong> tab to test before you create the agent. Microsoft enables Try it once the agent has a name, a description and instructions.</p>
""" + src(["build"]),
            },
        ],
    },
    {
        "slug": "configure",
        "title": "5. Configure well",
        "summary": "Name, description, scoped instructions, starter prompts, knowledge, capabilities, and creating the agent.",
        "minutes": 25,
        "lessons": [
            {
                "slug": "name-description",
                "title": "Name and description",
                "minutes": 4,
                "body": """
<p>A good name says what the agent does (up to 30 characters). A good description says who it helps and how.
Copilot uses the description to decide when the agent is relevant, and users read it.</p>
<div class="two-col">
<div class="good"><h4>Clear</h4><ul><li><strong>Email Clarity Coach</strong>: Helps me improve the clarity, tone and structure of work emails.</li></ul></div>
<div class="bad"><h4>Unclear</h4><ul><li><strong>My Bot</strong>: Helps with stuff.</li></ul></div>
</div>
""" + src(["build"]),
            },
            {
                "slug": "instructions",
                "title": "Write scoped instructions",
                "minutes": 8,
                "body": """
<p>Good instructions cover five things:</p>
<ol>
<li><strong>Role and one purpose</strong>: "You are my Email Clarity Coach. Your only job is..."</li>
<li><strong>Style</strong>: simple, polite language; short or formal versions.</li>
<li><strong>When unsure</strong>: ask one short question or say you cannot confirm it.</li>
<li><strong>Never</strong>: invent dates, names, approvals, policy or citations.</li>
<li><strong>Off-topic rule</strong>: politely suggest normal Copilot Chat.</li>
</ol>
<p>Plus an <strong>answer format</strong>, for example <em>Improved email / What I changed / What to double-check</em>.
You have up to 8,000 characters, but short and clear instructions are easier to test.</p>
<p>Start from Template B and replace each bracket:</p>
""" + copy(TEMPLATE_INSTRUCTIONS) + src(["build"]),
            },
            {
                "slug": "prompts-knowledge-save",
                "title": "Starter prompts, knowledge and creating the agent",
                "minutes": 8,
                "body": """
<h3>Starter prompts</h3>
<p>Add at least three. They show users what the agent is for. Each one should fit the one purpose.</p>
<h3>Knowledge sources</h3>
<ul>
<li>Add only approved files or sites you are permitted to use.</li>
<li>The <strong>Only use specified sources</strong> setting makes the agent prefer your sources for search questions.
Microsoft notes it does <em>not</em> fully block general AI knowledge (simple tasks such as translation still use it), so keep the
"say you cannot confirm it" rule in your instructions.</li>
<li>Sharing an agent is <strong>not</strong> a way around file permissions. Each user only gets content they can already access.</li>
<li>When answers are grounded in a source, ask the agent to name the source or section, and check it.</li>
</ul>
<h3>Create</h3>
<p>When your tests pass, select <strong>Create</strong>. Microsoft shows a confirmation that the agent is
<em>private and only available to you</em>. To find it later, use the agent list in the left pane (<strong>More ...</strong>
for recent agents, or <strong>All agents</strong>).</p>
<h3>Editing later</h3>
<p>To change an agent, choose <strong>Edit</strong> from its <strong>More</strong> menu. Changes save automatically, but
other users only see them after you select <strong>Update</strong>. Updates can take a few minutes.</p>
""" + src(["knowledge", "share_manage", "build_guide"]),
            },
            {
                "slug": "capabilities-limits",
                "title": "Capabilities, model choice and limits",
                "minutes": 5,
                "body": """
<h3>Optional capabilities</h3>
<ul>
<li><strong>Create documents, charts, and code</strong> (code interpreter)</li>
<li><strong>Create images</strong> (image generator)</li>
</ul>
<p>Turn on a capability only if your one purpose needs it. The Email Clarity Coach needs neither.</p>
<h3>Model</h3>
<p>On Configure you can set the default response mode: <strong>Auto</strong> (default), <strong>Quick response</strong> or
<strong>Think deeper</strong>. Users can change it while chatting.</p>
<h3>Limits to know</h3>
<ul>
<li>Agent Builder cannot create actions that connect to outside services. That needs Copilot Studio.</li>
<li>Agents built with Agent Builder cannot be used in Teams group chats or 1:1 chats.</li>
<li>Agent Builder is not available in the mobile apps.</li>
<li>Skills are a preview feature, only for organizations in Microsoft's Frontier program. They are out of scope for T1.</li>
</ul>
""" + src(["build", "overview"]),
            },
        ],
    },
    {
        "slug": "test",
        "title": "6. Test and improve",
        "summary": "Good, vague and off-topic tests; checking citations; handling wrong answers; one improvement loop.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "three-tests",
                "title": "The three tests",
                "minutes": 8,
                "body": """
<p>Run these on the <strong>Try it</strong> tab before you create the agent, and again after every change.</p>
<table class="grid">
<tr><th>Test</th><th>Example (Email Clarity Coach)</th><th>Pass when the agent...</th></tr>
<tr><td>1. On topic</td><td>Please improve this email: Hi team, we need the latest status by Friday. Thanks.</td><td>Returns a clearer email, keeps the facts, explains changes.</td></tr>
<tr><td>2. Vague</td><td>Make it better.</td><td>Asks for the draft or context instead of inventing one.</td></tr>
<tr><td>3. Off topic</td><td>Who won a sports match?</td><td>Says this is outside its purpose and suggests normal Copilot Chat.</td></tr>
</table>
<p>Record the results on Template C:</p>
""" + copy(TEMPLATE_TEST_CARD) + src(["build"]),
            },
            {
                "slug": "verify",
                "title": "Check facts and citations",
                "minutes": 6,
                "body": """
<p><strong>Always verify important outputs.</strong> AI answers can be incomplete, wrong, outdated or missing citations,
and a wrong answer can still sound confident.</p>
<ul>
<li>Ask: "Which document or section is that from?"</li>
<li>Open the source and check the exact wording.</li>
<li>If the agent cannot point to a source, treat the answer as unconfirmed.</li>
<li>For policy, legal, HR or financial decisions, the authorized team has the final word, not the agent.</li>
</ul>
""",
            },
            {
                "slug": "improve-loop",
                "title": "One improvement loop",
                "minutes": 6,
                "body": """
<ol class="steps">
<li>Run the three tests.</li>
<li>Find the first test that failed.</li>
<li>Make <strong>one</strong> clear edit to the instructions. For example, add: "If the user asks about unrelated subjects, politely suggest using normal Copilot Chat."</li>
<li>Run all three tests again.</li>
<li>Write down what changed on your test card.</li>
</ol>
<p>Changing one thing at a time tells you which edit actually helped. If the agent is already created and shared, remember to select <strong>Update</strong> so other users get the change.</p>
""" + src(["share_manage"]),
            },
        ],
    },
    {
        "slug": "safety",
        "title": "7. Sharing, chat history, memory and safety",
        "summary": "Agent sharing versus conversation sharing, permissions, chat history, Copilot memory, and data hygiene.",
        "minutes": 25,
        "lessons": [
            {
                "slug": "sharing",
                "title": "Sharing an agent versus sharing a chat",
                "minutes": 8,
                "body": callout("<strong>Plain-English idea:</strong> A shared agent is a shared helper, not a shared personal diary.", "analogy") + """
<h3>Sharing an agent</h3>
<ul>
<li>A new agent is <strong>private</strong>. Select <strong>Share</strong> to open the share dialog.</li>
<li>Add people or groups in <strong>Add a name, group, or email</strong>, then choose a role:
<strong>Can chat</strong> (can only use the agent) or <strong>Can edit</strong> (co-owner: can edit, share and delete). Groups can only get Can chat.</li>
<li><strong>Org-wide sharing for chat access</strong> lets anyone in your organization find the agent in the Agent Store. Your admin may turn this off.</li>
<li>You can also <strong>Copy chat link</strong>. People with the link can use the agent but cannot edit it.</li>
</ul>
<p>Sharing the agent shares its configuration (name, instructions, knowledge settings). It <strong>does not by itself share your personal conversations</strong> with it.</p>
<h3>Sharing a chat</h3>
<p>Sharing a conversation is a <strong>separate, deliberate action</strong>: <strong>Share</strong> &gt; <strong>Share chat</strong> for a whole
conversation, or <strong>More options (...)</strong> &gt; <strong>Share response</strong> for one answer. This creates a link that anyone
in your organization can open after signing in. It is a snapshot: later messages are not included. To stop, go to
<strong>Settings</strong> &gt; <strong>Data controls</strong> &gt; <strong>Shared links</strong> &gt; <strong>Stop sharing</strong>.</p>
<p>Your organization controls whether these features are available. Follow your company's rules before sharing anything.
In the lab you only <em>review</em> the share options; you do not need to share.</p>
""" + src(["share_manage", "share_agent", "share_chat"]),
            },
            {
                "slug": "permissions",
                "title": "Knowledge is permission-based",
                "minutes": 4,
                "body": """
<ul>
<li>The agent respects each user's permissions and sensitivity labels. If a user cannot open a source, the agent does not use it in their answers.</li>
<li>When you share with <strong>specific people or groups</strong>, the SharePoint files and folders you added can be shared with them automatically, but only if you are allowed to share those files. This does not happen with org-wide sharing.</li>
<li>Access to a whole SharePoint site is not granted automatically. A site admin must grant it.</li>
<li>Removing someone from the agent does not remove their access to the files. That is managed in SharePoint.</li>
<li>Sharing a chat link does not give access to files, emails or meetings mentioned in it.</li>
</ul>
<p>If a colleague says "the agent cannot answer", check whether they have permission to the source.</p>
""" + src(["share_manage", "share_chat"]),
            },
            {
                "slug": "memory",
                "title": "Chat history, memory and what the agent 'learns'",
                "minutes": 8,
                "body": callout("<strong>Plain-English idea:</strong> The agent is not a magic memory box that remembers every chat forever.", "analogy") + """
<table class="grid">
<tr><th>Thing</th><th>What it is</th></tr>
<tr><td>Agent configuration</td><td>The instructions, starter prompts and knowledge you set. This is what mainly shapes the agent, and it is what other users get when you share it.</td></tr>
<tr><td>Conversation context</td><td>What has been said in the current chat. It helps the current conversation.</td></tr>
<tr><td>Chat history</td><td>Your list of past chats (the <strong>Chats</strong> list in the left pane). Use <strong>... More</strong> to rename or delete a chat.</td></tr>
<tr><td>Copilot memory</td><td>Under <strong>Settings &gt; Personalization</strong>: <strong>Custom instructions</strong>, <strong>Saved memories</strong> and details from <strong>Chat history</strong>. Copilot keeps only details useful for personalization, not every detail.</td></tr>
</table>
<h3>What Microsoft says about memory</h3>
<ul>
<li>Memory is a <strong>preview</strong> feature and can change. It is on by default unless your admin turns it off.</li>
<li>You can turn off the <strong>Chat history</strong> toggle in Personalization (at work it may be called <em>Chat history &amp; work insights</em>). Details inferred from past chats are then deleted after 30 days.</li>
<li>Deleting a chat removes it from history, but <strong>does not delete saved memories</strong> created from it. Delete those in Settings &gt; Personalization.</li>
<li>Memories are stored in your Exchange mailbox and follow your organization's security and compliance policies. Admins can find them with eDiscovery.</li>
</ul>
<p>So: <strong>an agent is not permanently retrained by every question</strong>, and your chats do not become shared knowledge for other users.
Never promise colleagues that chats are "totally private": they are personal, but subject to your organization's compliance tools.</p>
""" + src(["memory", "chat_history"]),
            },
            {
                "slug": "data-hygiene",
                "title": "Data hygiene",
                "minutes": 5,
                "body": """
<ul>
<li>Do not paste passwords, secrets, bank details or customer records into an agent.</li>
<li>Use redacted or made-up examples when practising.</li>
<li>Follow your company's sensitivity labels and data policies.</li>
<li>Keep unrelated questions out of a purpose-built agent's chat.</li>
<li>Delete practice chats you do not need, and review your saved memories from time to time.</li>
</ul>
""" + src(["chat_history", "memory"]),
            },
        ],
    },
    {
        "slug": "examples",
        "title": "8. Two guided examples",
        "summary": "Email Clarity Coach (no knowledge needed) and Expense Policy Helper (grounded in an approved source).",
        "minutes": 20,
        "lessons": [
            {
                "slug": "email-coach",
                "title": "Example A: Email Clarity Coach",
                "minutes": 10,
                "body": """
<p class="tag">Illustrative training example, not a real company deployment.</p>
<p><strong>Challenge:</strong> You write many short work emails and want them clearer and more polite without changing the facts.</p>
<p><strong>Name:</strong> Email Clarity Coach<br><strong>Description:</strong> Helps me improve the clarity, tone and structure of work emails.<br><strong>Knowledge:</strong> none needed. <strong>Capabilities:</strong> none needed.</p>
<h3>Instructions</h3>
""" + copy(EMAIL_COACH_INSTRUCTIONS) + """
<h3>Tests</h3>
<ul>
<li><strong>Good:</strong> "Please improve this email: Hi team, we need the latest status by Friday. Thanks."</li>
<li><strong>Vague:</strong> "Make it better." Expected: asks for the draft or context.</li>
<li><strong>Off topic:</strong> "Who won a sports match?" Expected: explains this is outside its purpose and suggests normal Copilot Chat.</li>
</ul>
<p><strong>Proof of success:</strong> keeps the original facts, gives a readable email and subject, stays on topic and invents nothing.</p>
""",
            },
            {
                "slug": "expense-helper",
                "title": "Example B: Expense Policy Helper",
                "minutes": 10,
                "body": """
<p class="tag">Illustrative training example, not a real company deployment.</p>
<p><strong>Challenge:</strong> Associates often ask simple expense questions that are already answered in the approved policy.</p>
<p><strong>Name:</strong> Expense Policy Helper<br><strong>Description:</strong> Helps me find answers in my organization's approved expense policy.<br>
<strong>Knowledge:</strong> the approved expense policy file or SharePoint page only, with <strong>Only use specified sources</strong> turned on.
If no approved policy is available for training, upload a clearly labelled <em>fictional sample policy created for training</em>, and never present it as the real company policy.</p>
<h3>Instructions</h3>
""" + copy(EXPENSE_HELPER_INSTRUCTIONS) + """
<h3>Tests</h3>
<ul>
<li><strong>Good:</strong> "Where does the policy explain meal reimbursements? Please cite the section."</li>
<li><strong>Unsupported:</strong> "Can I claim an unlisted special expense?" Expected: explains it cannot confirm and suggests Finance; does not invent approval.</li>
<li><strong>Off topic:</strong> "Can you plan my holiday?" Expected: redirects to normal Copilot Chat.</li>
</ul>
<p><strong>Proof of success:</strong> stays in the policy domain, cites sources, separates known from unknown, and invents no policy facts.
Results vary with the knowledge, licence and features available to each user.</p>
""" + src(["knowledge"]),
            },
        ],
    },
    {
        "slug": "lab-intro",
        "title": "9. Hands-on lab briefing",
        "summary": "Prerequisites and pass criteria for the 12-step lab. Track the steps on the Lab page.",
        "minutes": 10,
        "lessons": [
            {
                "slug": "lab-brief",
                "title": "Lab: build, test, improve, verify",
                "minutes": 10,
                "body": """
<p><strong>Main lab:</strong> build the <em>Email Clarity Coach</em>. No code or risky data is needed.<br>
<strong>Optional stretch lab:</strong> the <em>Expense Policy Helper</em>, if approved knowledge and the right licence are available.</p>
<h3>Before you start</h3>
<ul>
<li>A work account where you can see <strong>Agents</strong> &gt; <strong>New agent</strong> in Microsoft 365 Copilot (desktop or web, not mobile).</li>
<li>Your completed Agent Charter (see <a href="/charter">My agent charter</a>).</li>
<li>Made-up or redacted example text only. No real confidential content.</li>
</ul>
<h3>To pass the lab</h3>
<ul>
<li>Complete steps 1 to 10 on the <a href="/lab">Lab page</a>.</li>
<li>Show a passing scope test, a useful answer and one improvement after testing.</li>
<li>Correctly explain the privacy and permission boundaries.</li>
<li>You do not have to actually share the agent if your company's policy or licence does not allow it.</li>
</ul>
<p><strong>Evidence for your facilitator:</strong> completed Agent Charter, three example prompts, your test card, and a safe screenshot of the finished agent's name and configuration.</p>
""",
            },
        ],
    },
    {
        "slug": "wrap-up",
        "title": "10. Common mistakes, real-world inspiration and next steps",
        "summary": "Quick fixes for common mistakes, what large organizations did (honestly labelled), and where to go next.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "mistakes",
                "title": "Common mistakes and quick fixes",
                "minutes": 7,
                "body": """
<table class="grid">
<tr><th>Mistake</th><th>Why it matters</th><th>Simple fix</th></tr>
<tr><td>One agent doing unrelated jobs</td><td>Vague instructions, unpredictable results</td><td>Give it one narrowly defined job</td></tr>
<tr><td>Asking random questions in the agent chat</td><td>The thread gets noisy; memory may pick up details where enabled</td><td>Use normal Copilot Chat or a new, relevant chat</td></tr>
<tr><td>Thinking every chat permanently retrains the agent</td><td>Factually misleading</td><td>Separate conversation context, configuration and Copilot memory</td></tr>
<tr><td>Expecting a shared agent to include your past chats</td><td>Confuses access with history</td><td>Share only the agent; chat sharing is separate</td></tr>
<tr><td>Using a source a colleague cannot access</td><td>The agent cannot answer from it for them</td><td>Check file and agent permissions</td></tr>
<tr><td>Editing a shared agent but forgetting Update</td><td>Colleagues still see the old version</td><td>Select Update after editing</td></tr>
<tr><td>Accepting a confident answer without checking</td><td>Wrong answers can sound convincing</td><td>Ask for the source and verify it</td></tr>
<tr><td>"Help with anything" instructions</td><td>Scope cannot be tested</td><td>State role, topics, format, off-topic behaviour</td></tr>
<tr><td>Including personal or customer confidential data</td><td>Unnecessary exposure</td><td>Use redacted or synthetic examples and approved sources</td></tr>
<tr><td>Expecting Copilot Studio features in T1</td><td>Wrong expectations in the lab</td><td>Mark them "Advanced: requires Copilot Studio"</td></tr>
</table>
""" + src(["share_manage"]),
            },
            {
                "slug": "case-studies",
                "title": "Inspiration from large organizations",
                "minutes": 8,
                "body": callout("<strong>Read this first.</strong> These are external adoption stories for inspiration. They are "
                                "<strong>not</strong> evidence that these companies used T1 Agent Builder, and you cannot reproduce advanced enterprise "
                                "solutions with this beginner tool. The product each one used is named. Facilitators: open each source and re-check "
                                "it before presenting; do not quote figures that you have not verified.", "note") + """
<table class="grid small">
<tr><th>Organization</th><th>Product / technology named in the source</th><th>Beginner lesson</th><th>What this does NOT mean</th></tr>
<tr><td>HEINEKEN</td><td>Microsoft Copilot Studio + Power Platform</td><td>Start with a focused use case</td><td>Not built with T1 Agent Builder</td></tr>
<tr><td>Kantar</td><td>Microsoft Copilot Studio; Microsoft 365 Copilot adoption</td><td>Train people before scaling</td><td>The specialised agents used Copilot Studio, not T1</td></tr>
<tr><td>Epiq Global</td><td>Microsoft Copilot Studio + Power Platform</td><td>Pick repetitive questions first</td><td>Not built with T1 Agent Builder</td></tr>
<tr><td>PeopleCert</td><td>Microsoft Copilot Studio + Azure OpenAI</td><td>Ground answers in trusted content</td><td>Uses developer-level Azure services</td></tr>
<tr><td>Games Global</td><td>Microsoft Copilot Studio + Power Platform</td><td>Measure value with simple checks</td><td>Not built with T1 Agent Builder</td></tr>
<tr><td>Komatsu Australia</td><td>Microsoft Power Automate / AI Builder</td><td>Automate one small process at a time</td><td>A workflow automation story, not an agent built in T1</td></tr>
<tr><td>Accenture</td><td>Microsoft 365 Copilot (large-scale rollout)</td><td>Adoption needs training and change support</td><td>A Copilot rollout story, not an Agent Builder example</td></tr>
<tr><td>Emirates NBD</td><td>Microsoft 365 Copilot pilot (company statement)</td><td>Pilot first, then expand</td><td>Not an Agent Builder example</td></tr>
<tr><td>Duolingo</td><td colspan="3"><em>Company requested; a directly relevant Microsoft Agent Builder example is not verified. Do not present a success story until a first-party source naming the actual platform is checked.</em></td></tr>
<tr><td>ANZ Bank</td><td colspan="3"><em>Company requested; a directly relevant Microsoft Agent Builder example is not verified. Source and name the actual platform before including any claim.</em></td></tr>
<tr><td>WEX</td><td colspan="3"><em>Company requested; a directly relevant Microsoft Agent Builder example is not verified. Check whether examples refer to a different vendor's "agent builder" (for example UiPath); never confuse vendor products.</em></td></tr>
</table>
""" + CASE_SOURCES,
            },
            {
                "slug": "next-steps",
                "title": "Templates and what to learn next",
                "minutes": 5,
                "body": """
<p>All three standard templates and both example configurations are on the <a href="/templates">Templates</a> page with copy buttons.
Print the <a href="/quickref">Quick reference card</a> to keep next to your screen.</p>
<h3>Make a second agent</h3>
<p>Pick another small, repeated task from your week. Fill in a new charter, copy Template B, and run the three tests.</p>
<h3>What to learn next</h3>
<p>T1 is the entry point. When you need workflows, approvals, connections to business systems, autonomous actions or publishing
outside Microsoft 365 Copilot, move on to your organization's <strong>Copilot Studio</strong> training. You can copy an agent you built
here to Copilot Studio instead of starting again. Ask your Copilot champion where to find the training.</p>
""" + src(["compare_studio"]),
            },
        ],
    },
]


for _m in MODULES:
    _m.setdefault("track", "core")

# Optional tracks. They are not needed for the T1 certificate.
MODULES += [
    {
        "slug": "leader",
        "track": "leader",
        "title": "Leader track: leading Copilot adoption",
        "summary": "What leading companies do, governing agents by tier and zone, and measuring value over 12 months.",
        "minutes": 25,
        "lessons": [
            {
                "slug": "what-leaders-do",
                "title": "What leading companies do",
                "minutes": 8,
                "body": """
<p>Public stories from Toyota, Siemens, Hitachi, Rabobank, Lloyds and others show that leaders do not win on licence count.
They share four habits that a 10,000-person company can match in about twelve months:</p>
<ol>
<li><strong>One front door.</strong> Siemens (SiemensGPT), Toyota (ToyotaGPT, O-Beya) and Barclays give employees one hub to reach models, find agents and share what they built. In our organization, that front door is this hub.</li>
<li><strong>Governance scaled to risk.</strong> Hitachi and Rabobank run a cross-functional AI centre or committee. Gartner warns that applying the same heavy governance to every agent is itself a cause of failure.</li>
<li><strong>Peer-led skilling at a fixed ratio.</strong> Lloyds trained more than 10,000 colleagues through 1,000 volunteer coaches (about 1 per 60 staff). Hitachi targets 50,000 certified GenAI Professionals.</li>
<li><strong>Prove, then expand on demand.</strong> Vodafone and Lloyds scaled only after a measured pilot. Each agent has one outcome metric, such as Rabobank's chat self-service rate.</li>
</ol>
""" + callout("Most figures are company- or vendor-reported and not independently audited. Usage numbers do not prove productivity. See <a href='/insights/benchmarks'>Benchmarks</a> for sources.", "note"),
            },
            {
                "slug": "tiers-zones",
                "title": "Govern agents by what they can do",
                "minutes": 9,
                "body": """
<p>Use light controls for agents that only read and advise, and stronger controls for agents that act.</p>
<table class="grid small">
<tr><th>Tier</th><th>What the agent may do</th><th>Who builds</th><th>Controls before release</th></tr>
<tr><td>1. Observe</td><td>Read data the user already has; answers only to them</td><td>Any trained associate (Zone 1)</td><td>T1 course, sharing off by default</td></tr>
<tr><td>2. Advise</td><td>Draft and recommend; a person acts</td><td>Certified builder with a coach (Zone 1)</td><td>Test set, approved sources, named owner, one KPI</td></tr>
<tr><td>3. Act with approval</td><td>Write data or send messages after explicit approval</td><td>CoE or IT with a business owner (Zone 2-3)</td><td>Security review, approval workflow, incident runbook</td></tr>
<tr><td>4. Act autonomously</td><td>Execute within guardrails</td><td>IT only (Zone 3)</td><td>Council sign-off, monitoring, rollback</td></tr>
</table>
<p>Microsoft's zoned governance guidance places <strong>Agent Builder in Zone 1 (citizen development)</strong>: personal and team agents over
content the maker can already access. Zone 2 (partnered development) and Zone 3 (professional development) use Copilot Studio and
other professional tools. T1 agents are Tier 1 or Tier 2.</p>
<p>In this hub, agents shared with a team or the organization go through a governance review by a coach. Tier 3 and 4 requests go to the CoE.</p>
""" + src(["compare_studio"]),
            },
            {
                "slug": "value-roadmap",
                "title": "Measure value and run a 12-month roadmap",
                "minutes": 8,
                "body": """
<ul>
<li><strong>One KPI per shared agent</strong>, with a baseline at registration and a result at the 90-day review. Retire agents that do not deliver.</li>
<li><strong>Hours saved</strong>: ask associates to log hours saved each week in the hub. Vodafone's trial reported about 3 hours per person per week; measure your own before using a figure in a business case.</li>
<li><strong>Monthly active use</strong>: SiemensGPT reports about 53% of registered users active each month, a realistic ceiling for voluntary tools.</li>
<li><strong>Licences on demand</strong>: give everyone Copilot Chat first, then allocate full licences in waves to teams that finish training and submit a use case.</li>
</ul>
<table class="grid small">
<tr><th>Months</th><th>Focus</th><th>Gate to the next phase</th></tr>
<tr><td>0-3</td><td>Council, CoE, guideline; 300 pilot users; first 50 coaches</td><td>2+ hours/week saved and 80% want to keep it</td></tr>
<tr><td>3-6</td><td>Copilot Chat for everyone; foundation course; first licence wave</td><td>55% monthly active, no high-severity data incidents</td></tr>
<tr><td>6-9</td><td>1,000 certified builders; ~170 coaches; monthly promptathons</td><td>Every shared agent has a KPI and a passing test set</td></tr>
<tr><td>9-12</td><td>Second licence wave; 90-day reviews retire low-value agents; board value report</td><td>Hours saved and KPIs reported quarterly</td></tr>
</table>
<p>Track progress against these targets on the <a href="/insights">Insights</a> page.</p>
""",
            },
        ],
    },
    {
        "slug": "coach",
        "track": "coach",
        "title": "Coach track: supporting colleagues and reviewing agents",
        "summary": "How Copilot coaches help colleagues, run promptathons and review agents against the governance checklist.",
        "minutes": 15,
        "lessons": [
            {
                "slug": "being-a-coach",
                "title": "Being a Copilot coach",
                "minutes": 7,
                "body": """
<p>Coaches are volunteer associates who help colleagues in their department. Lloyds used about one coach per 60 staff; for 10,000 associates that is roughly 170 coaches.</p>
<ul>
<li>Hold short office hours and list them in your profile so colleagues can find you in the <a href="/community">Community</a> directory.</li>
<li>Run a promptathon or show-and-tell: everyone brings one real task, tries it with Copilot, and shares what worked.</li>
<li>Add prompts that work to the shared prompt library, and rate others' prompts.</li>
<li>Answer "how do I" questions; pass policy, data and incident questions to the CoE through <a href="/help">Ask the CoE</a>.</li>
<li>Model the six key messages, especially "one agent, one purpose" and "always verify important outputs".</li>
</ul>
""",
            },
            {
                "slug": "reviewing-agents",
                "title": "Reviewing an agent",
                "minutes": 8,
                "body": """
<p>When an agent is submitted for team or organization sharing, a coach reviews it in the <a href="/hub/reviews">Review queue</a>.</p>
<ol class="steps">
<li>Read the purpose, tier, knowledge sources, data sensitivity and test results.</li>
<li>Check the registry for an approved agent that already does the same job. Prefer reuse.</li>
<li>Ask the owner for the chat link and run the three tests yourself on the Try it tab or in the agent.</li>
<li>Tick each item on the governance checklist. You can only approve when every item is true.</li>
<li>Choose <strong>Approve</strong>, <strong>Request changes</strong> (explain what to change) or <strong>Not approve</strong>.</li>
</ol>
<p>Tier 3 and 4 agents (acting on data or autonomously) are not reviewed by coaches. They go to the CoE and usually need Copilot Studio or IT.</p>
<p>You cannot review your own agent.</p>
""",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Hands-on lab steps (brief section 8)
# ---------------------------------------------------------------------------

LAB_STEPS = [
    (1, "Write your agent's single purpose in one sentence", "Purpose describes one job; an off-topic boundary is written."),
    (2, "Open Microsoft 365 Copilot and select Agents > New agent", "Correct entry point shown to the facilitator or evidenced with a redacted screenshot."),
    (3, "Describe your agent on the Describe tab (or use Skip to configure)", "Name, description and purpose appear on the Configure tab."),
    (4, "Edit instructions and boundaries", "Instructions cover style, uncertain facts and the off-topic redirect."),
    (5, "Add at least 3 starter prompts", "Prompts relate directly to the one purpose."),
    (6, "Test one clear prompt on the Try it tab", "A useful answer meets the agent's purpose."),
    (7, "Test one vague prompt", "The agent asks for clarification instead of inventing missing details."),
    (8, "Test one unrelated question", "The agent stays in scope, or you adjust the instructions and retest."),
    (9, "Check a fact-sensitive response", "You can show where a fact came from, or identify uncertainty."),
    (10, "Select Create, then find and reopen the agent", "Your agent appears in your agent list and opens again."),
    (11, "Open the Share dialog and review the options, without sharing sensitive information", "You can explain Can chat vs Can edit, and agent sharing vs separate chat sharing."),
    (12, "Complete the knowledge check", "You score 3/3 on the module 7 quiz or review your incorrect answers."),
]
LAB_REQUIRED_STEPS = 10  # steps 1-10 are required to pass


# ---------------------------------------------------------------------------
# Question bank
# Each question: code, module slug, category, difficulty, scenario flag,
# prompt, options, correct index (0-based), rationale, source key,
# in_slide_check flag.
# ---------------------------------------------------------------------------

def _q(code, module, category, difficulty, scenario, prompt, options, correct, rationale, source=None, in_slide=False):
    return {
        "code": code,
        "module": module,
        "category": category,
        "difficulty": difficulty,
        "scenario": scenario,
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "rationale": rationale,
        "source_url": SOURCES[source]["url"] if source else "",
        "in_slide_check": in_slide,
    }


QUESTIONS = [
    # --- The three in-slide knowledge-check questions (brief section 9) ---
    _q("T1-Q01", "basics", "Planning", "Easy", False,
       "Why should an associate create one agent for one purpose?",
       ["It makes the agent's role clear and easier to test.",
        "Microsoft limits all agents to one question.",
        "It automatically grants the agent access to any file."],
       0, "A single, narrow purpose keeps instructions clear and lets you test whether the agent does its job. There is no one-question limit, and purpose has nothing to do with file access.",
       "build", in_slide=True),
    _q("T1-Q02", "safety", "Sharing", "Medium", True,
       "You share your agent with a colleague. What does that normally mean?",
       ["The colleague automatically sees all of your personal agent chats.",
        "The colleague can use the shared agent according to access settings, but your personal conversations are not automatically shared.",
        "The colleague can access every SharePoint file you can access."],
       1, "Sharing an agent shares the helper, not your personal chat history. Sharing a conversation is a separate action, and knowledge sources still respect each user's own permissions. Tenant policies and special agent types can change details.",
       "share_agent", in_slide=True),
    _q("T1-Q03", "safety", "Memory", "Medium", False,
       "Does the agent permanently learn every question from every conversation?",
       ["Yes, all chats automatically become permanent shared knowledge.",
        "No, chat context and enabled Copilot memory/personalization differ from the agent's configured instructions and knowledge; not every detail is remembered.",
        "No, Copilot cannot ever reference previous conversation context."],
       1, "The agent is shaped mainly by its configuration and knowledge. Where enabled, Copilot memory may use selected useful details from earlier chats, but it does not remember everything, and chats do not become shared knowledge.",
       "memory", in_slide=True),

    # --- Module 1: welcome ---
    _q("T1-Q04", "welcome", "Concepts", "Easy", False,
       "Which plain-English description of an agent does this course use?",
       ["Copilot with a job description.", "A robot that works without instructions.",
        "A replacement for your manager.", "A database of all company files."],
       0, "An agent is Copilot set up for one job, following the instructions and knowledge you give it."),
    _q("T1-Q05", "welcome", "Scope", "Easy", False,
       "Which tool does the T1 course teach?",
       ["Power Automate workflow designer",
        "Agent Builder inside Microsoft 365 Copilot / Copilot Chat",
        "Azure OpenAI Studio",
        "The standalone Microsoft Copilot Studio portal"],
       1, "T1 covers Agent Builder in the Microsoft 365 Copilot experience. Copilot Studio is the next-level course.",
       "overview"),
    _q("T1-Q06", "welcome", "Scope", "Medium", True,
       "A colleague asks whether this course will teach them to connect an agent to the HR system using APIs. What is the best answer?",
       ["Yes, module 5 covers APIs.",
        "No. APIs and system integrations are out of scope for T1; that is Copilot Studio territory.",
        "Yes, if they use the Configure tab.",
        "No, agents can never connect to anything."],
       1, "Programming, APIs and integrations are out of scope for this beginner track and belong to the advanced Copilot Studio training.",
       "compare_studio"),

    # --- Module 2: basics ---
    _q("T1-Q07", "basics", "Concepts", "Easy", True,
       "You have a one-off question about a news topic. Where should you ask it?",
       ["In your Email Clarity Coach agent", "In normal Copilot Chat",
        "In your Expense Policy Helper agent", "In any agent; it does not matter"],
       1, "One-off, unrelated questions belong in normal Copilot Chat, not in a purpose-built agent."),
    _q("T1-Q08", "basics", "Planning", "Medium", True,
       "Which proposed agent best follows the one-purpose principle?",
       ["Helps with expense policies, language lessons and holiday planning",
        "Helps with anything I need",
        "Turns my meeting notes into a short action list",
        "Acts as my HR, IT and Finance assistant"],
       2, "Only the meeting-notes agent has one clear, testable job."),
    _q("T1-Q09", "basics", "Concepts", "Medium", False,
       "What is the difference between instructions and knowledge sources?",
       ["They are the same thing",
        "Instructions tell the agent how to help; knowledge sources tell it what information to use",
        "Knowledge sources set the tone; instructions add files",
        "Instructions are only for administrators"],
       1, "Instructions describe behaviour and format; knowledge sources provide permitted information.",
       "build"),
    _q("T1-Q10", "basics", "Scope", "Medium", True,
       "You want an agent that runs automatically every night and updates records in a business system. Which label applies in this course?",
       ["Covered in the T1 lab",
        "Possible by writing longer instructions",
        "Next-level capability, not covered by T1",
        "Not possible with any Microsoft tool"],
       2, "Autonomous actions and system updates need advanced tools such as Copilot Studio; they are out of scope for T1.",
       "compare_studio"),

    # --- Module 3: plan ---
    _q("T1-Q11", "plan", "Planning", "Easy", False,
       "Which sentence pattern helps you define an agent's purpose?",
       ["This agent can do everything for everyone.",
        "This agent helps me [one clear task] for [audience].",
        "This agent replaces Copilot Chat.",
        "This agent learns from all my files."],
       1, "Naming one task and one audience keeps the purpose narrow and testable."),
    _q("T1-Q12", "plan", "Planning", "Medium", True,
       "Your purpose sentence is: 'This agent helps me write emails and plan team holidays.' What should you do?",
       ["Keep it; more jobs means more value",
        "Split it into two agents, each with one purpose",
        "Add more knowledge sources",
        "Remove the word 'helps'"],
       1, "Joining two unrelated jobs with 'and' is a sign you need two agents."),
    _q("T1-Q13", "plan", "Knowledge", "Medium", True,
       "You want your Expense Policy Helper to answer from a policy. Which source is most appropriate?",
       ["A colleague's old personal notes about expenses",
        "A forum post about another company's policy",
        "The approved, current expense policy owned by Finance",
        "Your own claims history with bank details"],
       2, "Use approved, current sources owned by the right team, and avoid sensitive personal data.",
       "build"),
    _q("T1-Q14", "plan", "Planning", "Medium", False,
       "Why write a 'does not' list when planning?",
       ["It becomes the boundary rules in your instructions",
        "Microsoft requires exactly four items",
        "It hides the agent from other users",
        "It increases the agent's file access"],
       0, "Clear boundaries tell the agent what to refuse or redirect, which you can then test."),

    # --- Module 4: build ---
    _q("T1-Q15", "build", "UI build", "Easy", True,
       "Microsoft's guide says to select 'New agent', but your screen shows a slightly different label in the same place. What should you do?",
       ["Stop; the training is wrong so you cannot continue",
        "Use the label you actually see; Microsoft labels can vary",
        "Install Copilot Studio instead",
        "Ask IT to rename the button"],
       1, "The interface changes and varies by tenant. Follow the actual label you see.",
       "build_guide"),
    _q("T1-Q16", "build", "UI build", "Easy", False,
       "Where are agents you have access to usually listed in Microsoft 365 Copilot?",
       ["In the Agents area of the Copilot navigation", "Only in Outlook settings",
        "In the Windows Control Panel", "Nowhere; you must recreate them each time"],
       0, "Agents are found in the Agents area; exact placement can vary by version.",
       "build_guide"),
    _q("T1-Q17", "build", "UI build", "Medium", True,
       "The Describe tab generated a draft name, description and instructions. What next?",
       ["Save immediately; generated drafts are always correct",
        "Review and tighten each setting on the Configure tab, then test on the Try it tab",
        "Delete it and start again in Copilot Studio",
        "Share it with everyone to get feedback"],
       1, "The generated draft is a starting point. Check every setting in Configure and test before saving.",
       "build"),
    _q("T1-Q18", "build", "Escalation", "Medium", True,
       "You cannot find any option to create an agent. What is the right action?",
       ["Use a personal account instead of your work account",
        "Ask your Copilot champion or IT service desk; it may not be enabled for your licence",
        "Download an unofficial plugin",
        "Borrow a colleague's login"],
       1, "Availability depends on licence and organization settings. Escalate through proper channels; never work around controls."),

    # --- Module 5: configure ---
    _q("T1-Q19", "configure", "Configuration", "Easy", False,
       "Which agent name is best?",
       ["My Bot", "Helper 1", "Email Clarity Coach", "Assistant"],
       2, "A good name says what the agent does."),
    _q("T1-Q20", "configure", "Configuration", "Medium", True,
       "Your instructions say only 'Help with anything.' Why is that a problem?",
       ["It is too short for Microsoft to accept",
        "The scope cannot be tested and results become unpredictable",
        "It gives the agent access to all files",
        "It is not a problem"],
       1, "Instructions should state role, allowed topics, format, what to do when unsure, and the off-topic rule."),
    _q("T1-Q21", "configure", "Configuration", "Medium", False,
       "Which line belongs in good agent instructions?",
       ["Always sound confident, even if unsure.",
        "If information is missing, ask for clarification or say you cannot confirm it.",
        "Invent a source if none is available.",
        "Answer every question on any topic."],
       1, "Good instructions tell the agent to handle uncertainty honestly and never invent facts or citations."),
    _q("T1-Q22", "configure", "Configuration", "Medium", True,
       "Which set of starter prompts suits the Email Clarity Coach?",
       ["'Plan my holiday', 'Tell me a joke', 'Who won the match?'",
        "'Improve this email', 'Make this more formal', 'Suggest a subject line for this draft'",
        "'Show me the expense policy', 'What is the weather?', 'Write code'",
        "No prompts are needed"],
       1, "Starter prompts should all fit the agent's one purpose."),
    _q("T1-Q23", "configure", "Permissions", "Hard", True,
       "You add a SharePoint file to your agent's knowledge and share the agent. A colleague without access to that file asks a question. What happens?",
       ["They see the full file through the agent",
        "Sharing the agent grants them file access",
        "They cannot receive content from that file, because knowledge access is permission-based",
        "The file is copied into their OneDrive"],
       2, "Each user only receives content from sources they are allowed to access. Sharing an agent is not a workaround for file permissions.",
       "share_manage"),

    # --- Module 6: test ---
    _q("T1-Q24", "test", "Testing", "Easy", False,
       "Which three tests should you run on every agent?",
       ["Speed, colour and font",
        "On-topic, vague and off-topic prompts",
        "Login, logout and password reset",
        "Three identical prompts"],
       1, "The three tests check the job is done, unclear requests are clarified, and unrelated requests are redirected."),
    _q("T1-Q25", "test", "Testing", "Medium", True,
       "You type 'Make it better.' into the Email Clarity Coach. Which response is a pass?",
       ["It writes a random email about a sales meeting",
        "It asks you to paste the draft or give context",
        "It answers a sports question",
        "It refuses to talk to you ever again"],
       1, "With a vague prompt, the agent should ask for the missing information instead of inventing it."),
    _q("T1-Q26", "test", "Testing", "Medium", True,
       "You ask the Email Clarity Coach 'Who won a sports match?' and it answers the question in detail. What should you do?",
       ["Accept it; extra help is fine",
        "Add or strengthen the off-topic rule in the instructions, then retest all three tests",
        "Delete the agent",
        "Share it so others can test"],
       1, "Fix the instructions with one clear edit, then rerun all tests to confirm the change worked."),
    _q("T1-Q27", "test", "Verification", "Medium", True,
       "The Expense Policy Helper gives a confident spending limit but no source. What should you do?",
       ["Trust it because it sounds confident",
        "Ask which document or section it came from and check the source; treat it as unconfirmed until verified",
        "Share the answer with your team immediately",
        "Ask the same question until it agrees with you"],
       1, "Always verify important outputs. Confident answers can still be wrong."),
    _q("T1-Q28", "test", "Testing", "Medium", False,
       "Why change only one thing at a time when improving instructions?",
       ["Microsoft only allows one edit per day",
        "So you know which edit actually fixed the problem",
        "It makes the agent faster",
        "It hides earlier versions"],
       1, "A single change per loop makes cause and effect clear."),
    _q("T1-Q29", "test", "Ethics", "Hard", True,
       "An agent's answer about a legal requirement seems plausible. Who has the final word?",
       ["The agent", "Whoever asked the question",
        "The authorized team (for example Legal or Compliance), after checking the source",
        "The most senior person in the chat"],
       2, "Agents give guidance from allowed sources, not definitive legal, HR, policy or financial decisions."),

    # --- Module 7: safety ---
    _q("T1-Q30", "safety", "Sharing", "Medium", False,
       "How do you share a specific Copilot conversation or response with a colleague?",
       ["It happens automatically when you share the agent",
        "Through a separate, deliberate conversation/response sharing feature, where available",
        "By giving them your password",
        "It is impossible"],
       1, "Sharing a conversation is a separate action from sharing an agent.",
       "share_chat"),
    _q("T1-Q31", "safety", "Memory", "Hard", True,
       "A teammate says: 'Everything I type into Copilot becomes knowledge for every user of my agent.' How do you correct them?",
       ["They are right",
        "Chats do not become shared agent knowledge; the agent is shaped by its configuration and knowledge, and any Copilot memory is personal and controllable",
        "Only questions typed on Mondays are shared",
        "Copilot deletes every chat instantly"],
       1, "Personal chat history and memory are not shared through the agent. The agent's instructions and knowledge are what others use.",
       "memory"),
    _q("T1-Q32", "safety", "Memory", "Medium", False,
       "Where enabled, what can Copilot memory/personalization do?",
       ["Remember every word you have ever typed",
        "Use selected useful details from earlier chats, subject to user and admin controls",
        "Share your chats with your manager",
        "Retrain the agent for all users"],
       1, "Memory may use selected useful details; it does not remember everything and can be controlled.",
       "memory"),
    _q("T1-Q33", "safety", "Privacy", "Medium", True,
       "While practising, what should you paste into your agent?",
       ["A real customer contract", "Your colleague's bank details",
        "Made-up or redacted example text", "System passwords so it can help with IT"],
       2, "Use synthetic or redacted examples and follow your company's data policies."),
    _q("T1-Q34", "safety", "Privacy", "Hard", False,
       "Which statement about chat privacy is accurate?",
       ["Chats are totally private and nobody can ever access them",
        "Chat history is generally personal but subject to your organization's compliance and governance settings",
        "All chats are public to the company",
        "Admins can read chats only on weekends"],
       1, "Never promise absolute privacy. Chat history is personal but governed by tenant compliance settings.",
       "chat_history"),
    _q("T1-Q35", "safety", "Conversation hygiene", "Medium", True,
       "You are chatting with your Expense Policy Helper and want to ask for a recipe. What is the best practice?",
       ["Ask it anyway in the same chat",
        "Switch to normal Copilot Chat for the unrelated question",
        "Add recipes to the agent's knowledge",
        "Rename the agent"],
       1, "Use the right conversation for the right topic to keep the agent's context clean."),

    # --- Module 8: examples ---
    _q("T1-Q36", "examples", "Examples", "Easy", False,
       "Which example agent needs no external knowledge source?",
       ["Expense Policy Helper", "Email Clarity Coach", "Both", "Neither"],
       1, "The Email Clarity Coach works only on the text you paste in."),
    _q("T1-Q37", "examples", "Examples", "Medium", True,
       "You ask the Expense Policy Helper 'Can I claim an unlisted special expense?' and the policy does not cover it. What is the correct behaviour?",
       ["Approve it to be helpful",
        "Say it cannot confirm from the source and suggest checking with Finance",
        "Invent a reasonable limit",
        "Answer a different question"],
       1, "The agent must never guess limits, exceptions or approval authority."),
    _q("T1-Q38", "examples", "Examples", "Medium", True,
       "No approved expense policy is available for your training session. What should you use?",
       ["The real policy from another company",
        "A clearly labelled fictional sample policy created for training",
        "Your own guess at the policy",
        "Skip knowledge and tell learners it is the real policy"],
       1, "A visibly labelled fictional training document avoids presenting made-up content as company policy."),

    # --- Module 9: lab ---
    _q("T1-Q39", "lab-intro", "Lab", "Easy", False,
       "Which lab steps are required to pass the hands-on lab?",
       ["Only step 1", "Steps 1 to 10", "Only step 11 (sharing)", "None"],
       1, "Steps 1 to 10 are required; sharing is reviewed but not required if policy forbids it."),
    _q("T1-Q40", "lab-intro", "Lab", "Medium", True,
       "Your company policy does not allow you to share agents. Can you still pass the lab?",
       ["No, sharing is mandatory",
        "Yes; you review and explain the sharing options without actually sharing",
        "Only if you share it with yourself",
        "Only if you use a personal account"],
       1, "Actual sharing is not required when policy or licence forbids it."),

    # --- Module 10: wrap-up ---
    _q("T1-Q41", "wrap-up", "Case studies", "Medium", True,
       "A presenter says a large company 'built its solution with T1 Agent Builder' but the source names Copilot Studio and Power Platform. What is correct?",
       ["The presenter is right; they are the same",
        "State the actual product used; it is an inspiration story, not proof of a T1 build",
        "Remove the product name to avoid confusion",
        "Add an impressive ROI figure"],
       1, "Always name the actual product and avoid implying advanced solutions can be reproduced with the beginner tool."),
    _q("T1-Q42", "wrap-up", "Next steps", "Easy", False,
       "You need an agent that connects to business systems and publishes to several channels. Where should you go next?",
       ["Repeat T1", "Your organization's Copilot Studio training",
        "Write longer T1 instructions", "Ask the agent to upgrade itself"],
       1, "Those are Copilot Studio capabilities; T1 is the entry point."),
    _q("T1-Q43", "wrap-up", "Mistakes", "Medium", True,
       "A colleague says your shared agent 'cannot answer' questions about the policy file. What should you check first?",
       ["Whether they have permission to the policy source",
        "Whether their screen is big enough",
        "Whether the agent name is long enough",
        "Whether you typed in capital letters"],
       0, "Knowledge access is permission-based; missing file access is a common cause.",
       "share_manage"),
    _q("T1-Q44", "wrap-up", "Mistakes", "Medium", False,
       "Which word list should you avoid when describing AI to colleagues?",
       ["'Check the source', 'verify'", "'100% accurate', 'totally private', 'learns everything'",
        "'One purpose', 'test'", "'Approved source', 'permission'"],
       1, "Categorical claims like these are misleading."),
    # --- Added after the Microsoft Learn review (2026-10-23) ---
    _q("T1-Q45", "configure", "Configuration", "Medium", True,
       "You edited the instructions of an agent that colleagues already use. They still get the old behaviour. What did you most likely forget?",
       ["To delete and recreate the agent", "To select Update after editing",
        "To restart your computer", "To share your chat history"],
       1, "Edits save automatically, but other users only see them after you select Update. Updates can take a few minutes.",
       "share_manage"),
    _q("T1-Q46", "safety", "Sharing", "Medium", True,
       "You add a security group to your agent's share list. Which role can the group receive?",
       ["Can edit", "Can chat", "Administrator", "Any role"],
       1, "Groups can only be added as Can chat. Owner (Can edit) rights must be given to individual users.",
       "share_manage"),
    _q("T1-Q47", "safety", "Sharing", "Medium", True,
       "You share a Copilot chat link with a colleague and then keep chatting. What does the colleague see?",
       ["Every new message as you type it", "A snapshot of the chat at the moment you shared it",
        "Nothing until you share again", "Your whole chat history"],
       1, "A shared chat or response is a fixed snapshot. Later messages are not included, and you can stop sharing in Settings > Data controls > Shared links.",
       "share_chat"),
    _q("T1-Q48", "safety", "Memory", "Hard", True,
       "You delete a chat, but Copilot still seems to remember a preference you mentioned in it. Why?",
       ["Deleted chats are never deleted", "Deleting a chat does not delete saved memories created from it; delete them in Settings > Personalization",
        "The agent was retrained by the chat", "Your colleague shared it back to you"],
       1, "Saved memories are kept until you delete them in Settings > Personalization, even if the chat they came from is deleted.",
       "memory"),
    _q("T1-Q49", "build", "UI build", "Easy", False,
       "Where do you test your agent before creating it?",
       ["In Outlook", "On the Try it tab", "In the Microsoft 365 admin center", "You cannot test before creating"],
       1, "The Try it tab is enabled once the agent has a name, description and instructions.",
       "build"),
    _q("T1-Q50", "plan", "Knowledge", "Hard", True,
       "You add 'My emails' as knowledge and share the agent with your team. Can your teammates read your email through the agent?",
       ["Yes, sharing gives them your mailbox", "No, people you share the agent with do not get access to your email",
        "Only managers can", "Only on Fridays"],
       1, "Microsoft states that users you share the agent with do not get access to your email. The agent respects each user's own permissions.",
       "knowledge"),
    _q("T1-Q51", "configure", "Knowledge", "Hard", True,
       "You turned on 'Only use specified sources'. A user asks the agent to translate a sentence. What happens?",
       ["The agent refuses everything not in the sources", "Simple tasks like translation can still use general AI knowledge; the setting prioritizes your sources for search questions but does not fully block general knowledge",
        "The agent shuts down", "The agent searches all websites"],
       1, "The setting prioritizes your knowledge sources but does not completely block general knowledge. Keep the 'say you cannot confirm it' rule in your instructions.",
       "knowledge"),
    _q("T1-Q52", "configure", "Scope", "Medium", True,
       "A colleague wants to use your Agent Builder agent inside a Teams group chat. What should you tell them?",
       ["It works the same everywhere", "Agent Builder agents cannot be used in Teams group or 1:1 chats",
        "Only if they @mention you", "Only on mobile"],
       1, "Microsoft lists Teams group and 1:1 chats as unsupported for Agent Builder agents.",
       "overview"),
# --- Leader and coach tracks (optional; not used in the final assessment) ---
    _q("T1-Q53", "leader", "Adoption", "Medium", True,
       "Your company wants to compete with leaders such as Siemens and Toyota. Which habit do their stories share?",
       ["Buying the most licences first", "One front door where people reach models, agents and learning",
        "Letting every team build its own chatbot platform", "Avoiding any governance"],
       1, "SiemensGPT, ToyotaGPT and Barclays' Colleague AI Agent all give employees a single hub. It stops shadow chatbots and makes usage measurable."),
    _q("T1-Q54", "leader", "Governance", "Medium", True,
       "An agent drafts answers and a person decides what to send. Which tier is it?",
       ["Tier 1 - Observe", "Tier 2 - Advise", "Tier 3 - Act with approval", "Tier 4 - Act autonomously"],
       1, "Tier 2 agents draft and recommend; a human acts. Agent Builder agents are Tier 1 or 2."),
    _q("T1-Q55", "leader", "Value", "Medium", True,
       "Gartner expects over 40% of agentic AI projects to be cancelled by 2027. Which practice best protects your agents?",
       ["Report only the number of agents built", "Declare one KPI with a baseline and review it after 90 days",
        "Never retire an agent", "Share every agent org-wide"],
       1, "Tie each shared agent to one outcome KPI and review it after 90 days; retire agents without measurable value."),
    _q("T1-Q56", "coach", "Governance", "Medium", True,
       "As a coach, you review an agent and one checklist item is not met. What can you do?",
       ["Approve it anyway", "Request changes and explain what must change",
        "Approve and fix it yourself later", "Delete the agent"],
       1, "You can only approve when every governance check is true. Otherwise request changes with a clear explanation."),
    _q("T1-Q57", "coach", "Governance", "Easy", True,
       "A colleague submits an agent that sends emails automatically. Who should review it?",
       ["Any coach", "The CoE, because it is Tier 3 or 4",
        "Nobody", "The colleague's friend"],
       1, "Agents that act (Tier 3-4) go to the CoE and usually need Copilot Studio or IT. Coaches review Tier 1-2 agents."),
    _q("T1-Q58", "coach", "Community", "Easy", False,
       "About how many volunteer coaches would 10,000 associates need at Lloyds' ratio?",
       ["10", "About 170", "1,000", "5,000"],
       1, "Lloyds used about 1 coach per 60 staff, so roughly 170 for 10,000 associates."),
]

FINAL_QUESTION_COUNT = 15
DEFAULT_PASS_MARK = 80  # percent


# ---------------------------------------------------------------------------
# Supporting pages: glossary, quick reference card, facilitator guide
# ---------------------------------------------------------------------------

GLOSSARY = [
    ("Agent", "A version of Copilot set up for one job, with its own name, description, instructions and optional knowledge."),
    ("Agent Builder", "The no-code tool inside Microsoft 365 Copilot for building agents. This course calls it T1."),
    ("Copilot Chat", "The general Microsoft 365 Copilot chat. Use it for one-off or unrelated questions."),
    ("Copilot Studio", "Microsoft's advanced tool for makers and developers: workflows, connectors, autonomous agents, wider publishing."),
    ("Describe tab", "Where you create an agent by chatting with the builder in everyday language."),
    ("Configure tab", "Where you see and edit the agent's name, icon, model, description, instructions, knowledge, capabilities and starter prompts."),
    ("Try it tab", "Where you test the agent before and after creating it."),
    ("Instructions", "Text (up to 8,000 characters) that tells the agent its role, scope, format and rules."),
    ("Description", "A short summary (up to 1,000 characters) that users read and Copilot uses to decide when the agent is relevant."),
    ("Knowledge source", "Content the agent may use: websites, SharePoint or OneDrive files, uploaded files, connectors and more, depending on licence."),
    ("Starter prompts", "Example prompts shown to users so they know what the agent is for."),
    ("Only use specified sources", "A setting that makes the agent prefer your knowledge sources. It does not fully block general AI knowledge."),
    ("Can chat / Can edit", "Sharing roles. Can chat users only use the agent; Can edit users are co-owners who can edit, share and delete it."),
    ("Org-wide sharing", "A setting that lets everyone in the organization find and chat with the agent in the Agent Store, if your admin allows it."),
    ("Update", "The button that publishes your edits to people you shared the agent with."),
    ("Chat history", "Your personal list of past Copilot chats, subject to your organization's compliance settings."),
    ("Copilot memory", "A preview feature (Settings > Personalization) with custom instructions, saved memories and details from chat history."),
    ("Saved memory", "Something Copilot was asked to remember. It stays until you delete it, even if the chat it came from is deleted."),
    ("Shared link", "A snapshot link to a chat or response. Manage it in Settings > Data controls > Shared links."),
    ("Sensitivity label", "A label your organization applies to files to protect them. Agents respect these labels."),
    ("Hallucination", "A confident-sounding answer that is wrong or not supported by a source. Always verify important outputs."),
    ("Agent registry", "This app's list of agents built in the organization, with owner, purpose, data and sharing details."),
    ("Governance review", "This app's approval step before an agent is shared widely or uses confidential data."),
    ("Copilot champion", "A trained associate who helps colleagues and reviews agents for their department."),
]

QUICKREF = {
    "title": "T1 Quick Reference: One Agent, One Purpose",
    "steps": [
        ("Plan", ["Write one sentence: This agent helps me [task] for [audience].",
                  "List what it does and does not do.",
                  "Choose approved knowledge, or none."]),
        ("Build", ["Copilot > Agents > New agent.",
                   "Describe tab, Skip to configure, or Start with a template.",
                   "Check name (30), description (1,000) and instructions (8,000) on Configure."]),
        ("Test", ["Try it tab: one on-topic, one vague, one off-topic prompt.",
                  "Ask for the source and check it.",
                  "Make one edit, then test again."]),
        ("Use safely", ["New agents are private. Share with Can chat or Can edit only as allowed.",
                        "Sharing an agent does not share your chats. Sharing a chat is a separate snapshot link.",
                        "Each user only gets content they are allowed to open.",
                        "Memory: Settings > Personalization. Deleting a chat does not delete saved memories.",
                        "After editing a shared agent, select Update.",
                        "Register the agent in this app before sharing it widely."]),
    ],
}

FACILITATOR_AGENDA = [
    ("0:00", 10, "Welcome and outcomes", "Module 1"),
    ("0:10", 15, "Agent basics; one agent, one purpose", "Module 2"),
    ("0:25", 15, "Plan your agent; fill in the charter", "Module 3 + My agent charter"),
    ("0:40", 20, "Live demo: build in Microsoft 365 Copilot", "Module 4"),
    ("1:00", 15, "Configure well", "Module 5"),
    ("1:15", 10, "Break", ""),
    ("1:25", 15, "Test and improve", "Module 6"),
    ("1:40", 15, "Sharing, history, memory and safety", "Module 7"),
    ("1:55", 25, "Hands-on lab (Email Clarity Coach)", "Modules 8-9 + Lab page"),
    ("2:20", 10, "Mistakes, inspiration, quiz and next steps", "Module 10 + Final assessment"),
]

FACILITATOR_PREP = [
    "Check that every learner can see Agents > New agent in Microsoft 365 Copilot (desktop or web).",
    "Re-read the Microsoft sources on the References page and note any label changes.",
    "Capture fresh, redacted screenshots of your own tenant for module 4.",
    "Prepare a fictional sample expense policy file, clearly labelled as training material.",
    "Import the cohort into this app (Admin > Import associates) and share the address.",
    "Confirm your organization's rules for sharing agents and chats.",
    "Name the escalation contacts (Copilot champion, IT service desk, Finance, Legal).",
]


# ---------------------------------------------------------------------------
# Agent hub: registry, governance review and ideas
# ---------------------------------------------------------------------------

SHARING_SCOPES = [
    ("private", "Only me"),
    ("people", "Specific people (Can chat)"),
    ("team", "My team or a security group"),
    ("org", "Org-wide sharing"),
]

SENSITIVITY_LEVELS = [
    ("public", "Public or general information"),
    ("internal", "Internal (company-only, not sensitive)"),
    ("confidential", "Confidential or personal data"),
]

KNOWLEDGE_TYPES = [
    ("none", "None"),
    ("web", "Public websites"),
    ("sharepoint", "SharePoint / OneDrive"),
    ("upload", "Uploaded files"),
    ("email", "Outlook email / Teams chats and meetings"),
    ("connector", "Copilot connectors"),
]

# An agent needs a governance review before it is shared beyond a few people
# or if it uses confidential data.
REVIEW_REQUIRED_SCOPES = {"team", "org"}

GOVERNANCE_CHECKLIST = [
    ("one_purpose", "The agent has one clear purpose and the description says what it is for."),
    ("boundaries", "Instructions say what to do when unsure and redirect off-topic questions."),
    ("tests", "The owner ran on-topic, vague and off-topic tests and recorded the results."),
    ("sources", "Knowledge sources are approved, current and owned by the right team."),
    ("permissions", "File permissions are correct for the intended audience; sharing does not bypass them."),
    ("data", "No unnecessary personal, customer or confidential data is used or requested."),
    ("duplicates", "No approved agent in the registry already does the same job."),
    ("owner", "A named owner and a review date are set, and the owner has completed T1 training."),
]

AGENT_STATUSES = [
    ("registered", "Registered (personal use)"),
    ("in_review", "In review"),
    ("changes", "Changes requested"),
    ("approved", "Approved for sharing"),
    ("rejected", "Not approved"),
    ("retired", "Retired"),
]

IDEA_CATEGORIES = [
    ("writing", "Writing and communication"),
    ("knowledge", "Finding information / policies"),
    ("meetings", "Meetings and notes"),
    ("analysis", "Data and reporting"),
    ("onboarding", "Onboarding and learning"),
    ("customer", "Customer and sales support"),
    ("other", "Other"),
]

IDEA_STATUSES = [
    ("new", "New"),
    ("planned", "Planned"),
    ("built", "Built"),
    ("declined", "Not taken forward"),
]


# ---------------------------------------------------------------------------
# Benchmarks (filled in from the benchmark research)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Agent tiers, governance zones and builder levels
# Tiers follow Gartner's autonomy levels and zones follow Microsoft's zoned
# governance guidance, as summarized in the benchmark report.
# ---------------------------------------------------------------------------

AGENT_TIERS = [
    ("1", "Tier 1 - Observe: reads what the user can already see; answers only to them"),
    ("2", "Tier 2 - Advise: drafts and recommends; a person decides and acts"),
    ("3", "Tier 3 - Act with approval: writes data or sends messages after explicit approval"),
    ("4", "Tier 4 - Act autonomously: executes within guardrails"),
]
# Agent Builder (T1) agents are Tier 1-2. Tier 3-4 need Copilot Studio or
# IT-built solutions and can only be approved by an administrator (CoE).
COE_ONLY_TIERS = {"3", "4"}

ZONES = [
    ("Zone 1: Citizen development", "Anyone trained", "Agent Builder in Microsoft 365 Copilot, SharePoint agents",
     "Personal and team agents over content the maker can already access"),
    ("Zone 2: Partnered development", "Certified makers with coach oversight", "Copilot Studio",
     "Agents for other teams and departments, with IT approval to publish"),
    ("Zone 3: Professional development", "Professional developers and IT", "Copilot Studio, Microsoft Foundry Agent Service",
     "Mission-critical, enterprise-grade agents"),
]

BUILDER_LEVELS = [
    ("foundation", "Foundation", "Finish modules 1, 2 and 7 and pass their quizzes.",
     "Use Copilot Chat safely and know when an agent helps."),
    ("level1", "Builder level 1", "Earn the T1 certificate (all lessons, lab steps 1-10, final assessment).",
     "Build Tier 1-2 agents for yourself and share with specific people."),
    ("level2", "Builder level 2", "Level 1, plus one of your agents approved in a governance review.",
     "Share approved agents with your team or organization (Zone 1)."),
    ("level3", "Builder level 3", "Level 2, plus a completed 90-day value review with a KPI result.",
     "Mentor others and propose Zone 2 (Copilot Studio) projects to the CoE."),
]

SKILL_STATEMENTS = [
    ("chat", "I use Copilot Chat confidently for everyday tasks."),
    ("purpose", "I can describe a task clearly enough to give an agent one purpose."),
    ("build", "I have built an agent in Agent Builder."),
    ("test", "I test agents with on-topic, vague and off-topic prompts."),
    ("safety", "I can explain sharing, permissions, chat history and memory to a colleague."),
    ("value", "I can measure the time or quality an agent saves."),
    ("lead", "I help my team decide where AI should and should not be used."),
]
SKILL_SCALE = [("1", "Not yet"), ("2", "A little"), ("3", "Mostly"), ("4", "Confidently")]


# ---------------------------------------------------------------------------
# Policy and help (admins can replace the policy text in Settings)
# ---------------------------------------------------------------------------

DEFAULT_POLICY = """1. Use only Microsoft 365 Copilot and agents provided through this hub with your work account.
2. One agent, one purpose. Register every agent you share with others in the Agent hub.
3. Do not paste passwords, secrets, bank details, health data or customer records into Copilot or an agent unless an approved process allows it.
4. Use only approved, current knowledge sources, and never share an agent to get around file permissions.
5. Always check important answers against the source. You are responsible for what you send or decide.
6. Agents give guidance; legal, HR, financial and policy decisions stay with the authorized teams.
7. Agents shared with a team or the whole organization need a governance review, a named owner, one KPI and a review date.
8. Report suspected data exposure or harmful output to the CoE through "Ask the CoE" straight away.
(This is a starting template. Your administrator should replace it with your organization's approved guideline.)"""

QUESTION_TOPICS = [
    ("howto", "How do I...?"),
    ("policy", "Is this allowed?"),
    ("data", "Data or privacy concern"),
    ("licence", "Licence or access"),
    ("incident", "Report a problem or incident"),
]

EVENT_KINDS = [
    ("promptathon", "Promptathon"),
    ("office_hours", "Coach office hours"),
    ("showcase", "Show and tell"),
    ("training", "Live training session"),
]

PROMPT_CATEGORIES = IDEA_CATEGORIES


# ---------------------------------------------------------------------------
# Benchmarks (from the project's benchmark report, 2026-10-23; public sources,
# mostly company- or vendor-reported and not independently audited)
# ---------------------------------------------------------------------------

BENCHMARK_DATE = "2026-10-23"

BENCHMARKS = [
    {"company": "Toyota", "region": "Japan HQ and North America",
     "scale": "~800 powertrain engineers on O-Beya; 45,000+ TMNA staff on AgentAsk",
     "platform": "O-Beya: 9 expert agents on Azure OpenAI combined into one answer. ToyotaGPT: central platform with 50+ production agents.",
     "governance": "The platform gets one security and architecture review and agents inherit it. Cybersecurity involved from day one.",
     "skilling": "Not disclosed. Change management named as the main challenge.",
     "result": "70,000+ hours returned per year; 11.4-minute mean time to repair on IT issues (reported).",
     "copy": "A knowledge agent per critical function, grounded in your own documents, with expert feedback captured.",
     "sources": [1, 2, 3, 20]},
    {"company": "Siemens", "region": "Germany",
     "scale": "150,000 registered and 80,000 monthly users on SiemensGPT",
     "platform": "SiemensGPT: multi-model internal platform with tools to build and share agents.",
     "governance": "Policy-as-code authorization, central identity, three admin roles, full audit logs.",
     "skilling": "My Learning World: 216,000 active learners; AI tutor and skills-gap engine used by 65,000.",
     "result": "About 53% of registered users active each month.",
     "copy": "A single hub with role-based access, and learning paths driven by each person's skill gaps.",
     "sources": [4, 5, 6]},
    {"company": "Hitachi", "region": "Japan",
     "scale": "Microsoft 365 Copilot and GitHub Copilot across a 270,000-person group",
     "platform": "Generative AI Assistant Tool on Azure OpenAI (2023), then Microsoft 365 Copilot and GitHub Copilot group-wide.",
     "governance": "Generative AI Center CoE with IT, security, legal, QA and IP experts. Internal-use guidelines published before launch (April 2023).",
     "skilling": "Target of 50,000+ certified GenAI Professionals, plus prompt-engineer training.",
     "result": "Guidelines and help desk in place from day one; AI ethics principles applied to 500+ projects.",
     "copy": "Publish the rules and the help channel on day one, and make certification the path to wider builder rights.",
     "sources": [7, 8]},
    {"company": "Rabobank", "region": "Netherlands",
     "scale": "Microsoft 365 Copilot and GitHub Copilot for employees; 3 customer agents",
     "platform": "Copilot Studio voice and chat agents; Agentic AI Hub for software delivery.",
     "governance": "Central AI committee with the COO; impact assessment and named owners before broad rollout; models in the bank's own Azure subscription.",
     "skilling": "You&AI programme for leaders and employees.",
     "result": "62% of chats resolved without a human (reported); built in about 3 months.",
     "copy": "An executive AI committee, a test suite for every shared agent, and one outcome KPI per agent.",
     "sources": [9, 10]},
    {"company": "Lloyds Banking Group", "region": "UK",
     "scale": "30,000 Copilot licences for ~61,000 staff",
     "platform": "Microsoft 365 Copilot; GitHub Copilot for ~5,000 engineers.",
     "governance": "Started with 300 early-access licences; departments bid for more.",
     "skilling": "10,000+ trained by 1,000 volunteer coaches; weekly promptathons.",
     "result": "93% daily usage (reported).",
     "copy": "Peer coaching at about 1 coach per 60 staff, and licences that follow demand.",
     "sources": [11]},
    {"company": "Vodafone", "region": "UK and multi-country",
     "scale": "Up to 68,000 employees after a trial",
     "platform": "Microsoft 365 Copilot across service, network, sales and marketing.",
     "governance": "Existing responsible-AI framework; trial run with Microsoft and KPMG.",
     "skilling": "Not disclosed.",
     "result": "About 3 hours saved per person per week in the trial (reported).",
     "copy": "Measure a pilot before scaling, and track time saved per person.",
     "sources": [12, 19]},
    {"company": "Barclays", "region": "UK",
     "scale": "100,000 employees",
     "platform": "Colleague AI Agent inside the existing colleague portal.",
     "governance": "Not disclosed.", "skilling": "Not disclosed.",
     "result": "No measured outcome published yet.",
     "copy": "Put AI where colleagues already go: one front door.",
     "sources": [13]},
    {"company": "Volkswagen Group", "region": "Germany",
     "scale": "330,000+ employees, phased",
     "platform": "Copilot Chat first, then Copilot with Work IQ and agents.",
     "governance": "Not disclosed.", "skilling": "Not disclosed.",
     "result": "300,000+ monthly Copilot Chat users; 26,000+ active agents in one month (usage, not productivity).",
     "copy": "Give everyone Copilot Chat first, then expand in phases.",
     "sources": [14]},
    {"company": "Accenture", "region": "Global",
     "scale": "~743,000 employees",
     "platform": "Microsoft 365 Copilot, multi-model.",
     "governance": "Reportedly ties some senior promotions to AI usage (media report).",
     "skilling": "Not disclosed.",
     "result": "97% of 200,000 surveyed said routine tasks got faster (self-reported survey).",
     "copy": "Leadership signals matter, but self-reported surveys are not proof of productivity.",
     "sources": [15]},
]

BENCHMARK_HABITS = [
    ("A single front door", "Employees reach every model, agent and learning path from one place. It stops shadow chatbots and makes usage measurable."),
    ("Tiered governance", "Light controls for personal, read-only agents and heavy controls for agents that act. Gartner warns that uniform governance causes agent failure."),
    ("A cross-functional CoE with an executive owner", "Technology, security, legal, risk and HR sit together, and a senior executive owns the decisions."),
    ("Measured pilot, demand-led expansion", "Licences follow demonstrated value, as at Lloyds (300 early seats to 30,000)."),
    ("Peer coaching at a fixed ratio", "About one volunteer coach per 60 employees (Lloyds); Hitachi targets about one certified professional per five employees."),
    ("Outcome metrics per agent", "Credible numbers are tied to a process: self-service rate, time to repair, hours returned. Gartner expects over 40% of agentic AI projects to be cancelled by 2027 for unclear value."),
]

# Targets scaled per associate; the hub compares them with live data.
BENCHMARK_TARGETS = [
    ("coaches", "Volunteer AI coaches", "1 per 60 associates", "Lloyds: 1,000 coaches for ~61,000 staff"),
    ("builders", "Certified agent builders", "10% to 18% of associates", "Hitachi targets ~18% of its group"),
    ("monthly_active", "Monthly active users of the hub", "55% or more", "SiemensGPT: 80,000 of 150,000 registered users monthly"),
    ("hours", "Hours saved per active user per week", "3 hours", "Vodafone trial average; measure your own"),
    ("kpi", "Shared agents with a declared KPI", "100%", "Rabobank and Toyota track one outcome per agent"),
    ("pilot", "Pilot seats before scaling", "300 for 90 days", "Lloyds started with 300 early-access licences"),
]

BENCHMARK_ROADMAP = [
    ("Months 0-3", "Foundation and pilot",
     ["Council, CoE and guideline live", "300 pilot users across 5 functions", "Recruit the first 50 coaches", "Measure baseline hours and quality"],
     "Gate: at least 2 h/week saved and 80% want to keep it."),
    ("Months 3-6", "Copilot Chat for everyone",
     ["All associates complete the foundation course", "First licence wave of 2,000 by demand", "Zone 1 building opens", "5 expert knowledge agents in build"],
     "Gate: 55% monthly active and no high-severity data incidents."),
    ("Months 6-9", "Builders and agents",
     ["1,000 certified builders", "Shared agents published through the registry", "Coach network at full strength (~170)", "Monthly promptathons per business unit"],
     "Gate: every shared agent has a KPI and a passing test set."),
    ("Months 9-12", "Scale and prune",
     ["Second licence wave based on usage", "First Tier 3 approval-based agents (with IT)", "90-day reviews retire low-value agents", "Publish a value report to the board"],
     "Gate: hours saved and agent KPIs reported quarterly."),
]

BENCHMARK_SOURCES = {
    1: ("Microsoft Source Asia: Toyota is deploying AI agents to harness the collective wisdom of engineers (Nov 2024)", "https://news.microsoft.com/source/asia/features/toyota-is-deploying-ai-agents-to-harness-the-collective-wisdom-of-engineers-and-innovate-faster/"),
    2: ("ZenML LLMOps Database: Building ToyotaGPT", "https://www.zenml.io/llmops-database/building-toyotagpt-a-centralized-ai-agent-platform-for-enterprise-scale-manufacturing"),
    3: ("CIO.com: Toyota transforms IT service desk with gen AI (Dec 2023)", "https://www.cio.com/article/1251333/toyota-transforms-it-service-desk-with-gen-ai.html"),
    4: ("AWS case study: Scaling AI authorization with Siemens (SiemensGPT)", "https://aws.amazon.com/solutions/case-studies/siemens-gpt-case-study/"),
    5: ("Infosys and Siemens AG to accelerate digital learning with generative AI (Jan 2025)", "https://www.infosys.com/newsroom/press-releases/2025/accelerate-digital-learning-generative-ai.html"),
    6: ("Microsoft Source EMEA: How AI is helping Siemens and thyssenkrupp bridge skilling gaps", "https://news.microsoft.com/source/emea/features/how-ai-is-helping-siemens-and-thyssenkrupp-bridge-skilling-gaps-in-manufacturing/"),
    7: ("Microsoft News: Hitachi and Microsoft enter milestone agreement (Jun 2024)", "https://news.microsoft.com/2024/06/03/hitachi-and-microsoft-enter-milestone-agreement-to-accelerate-business-and-social-innovation-with-generative-ai/"),
    8: ("Hitachi: Establishment of the Generative AI Center (May 2023)", "https://www.hitachi.com/en/press/articles/2023/05/0515/"),
    9: ("Rabobank: Rabobank and AI", "https://www.rabobank.com/about-us/rabobank-and-ai"),
    10: ("Microsoft Learn: Rabobank embraces conversational banking with Copilot Studio (2025)", "https://learn.microsoft.com/en-us/power-platform/guidance/case-studies/rabobank-conversational-banking"),
    11: ("Microsoft UK Stories: Lloyds Banking Group using AI at scale (Oct 2025)", "https://ukstories.microsoft.com/features/lloyds-banking-group-using-ai-at-scale-to-transform-operations-and-employee-experience/"),
    12: ("Microsoft Source EMEA: Vodafone to roll out Microsoft 365 Copilot to 68,000 employees (Sep 2024)", "https://news.microsoft.com/source/emea/features/vodafone-to-roll-out-microsoft-365-copilot-to-68000-employees-to-boost-productivity-innovation-and-quality/"),
    13: ("TechRadar: Barclays signs major Microsoft Copilot deal (Jun 2025)", "https://www.techradar.com/pro/microsoft-and-barclays-bank-sign-major-copilot-license-deal"),
    14: ("Let's Data Science: Microsoft equips 330,000 Volkswagen Group employees with Copilot (Oct 2026)", "https://letsdatascience.com/news/microsoft-equips-330000-volkswagen-group-employees-with-copi-7d9d97f9"),
    15: ("Reuters via Yahoo Finance: Accenture to roll out Copilot to 743,000 employees (Apr 2026)", "https://finance.yahoo.com/sectors/technology/articles/accenture-roll-copilot-743-000-180346038.html"),
    16: ("Gartner: Over 40% of agentic AI projects will be canceled by end of 2027 (Jun 2025)", "https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027"),
    17: ("Gartner: Applying uniform governance across AI agents will lead to failure (May 2026)", "https://www.gartner.com/en/newsroom/press-releases/2026-05-26-gartner-says-applying-uniform-governance-across-ai-agents-will-lead-to-enterprise-ai-agent-failure"),
    18: ("Microsoft Learn: Implement a zoned governance strategy for Copilot Studio", "https://learn.microsoft.com/en-za/microsoft-Copilot-studio/guidance/sec-gov-phase2"),
    19: ("Microsoft customer story: Vodafone time savings with Microsoft 365 Copilot", "https://www.microsoft.com/en/customers/story/19346-vodafone-microsoft-365-copilot"),
    20: ("ABI Research: Toyota's O-Beya best practices for GenAI knowledge management", "https://www.abiresearch.com/market-research/insight/7786905-toyotas-o-beya-provides-best-practices-for"),
}
