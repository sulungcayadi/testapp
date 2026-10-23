"""Course content for the T1 "Simple Copilot Agent Builder" track.

All learner-facing text lives here so it can be reviewed, updated or translated
in one place. Run ``python app.py reseed`` after editing to push changes into
the database (learner progress is kept).

Content follows the project brief (Copilot_Agent_Builder_Training_Brief.md).
Microsoft UI labels and feature availability vary by tenant and licence, so the
lessons tell learners to check the labels they actually see.
"""

EDITION_DATE = "2026-10-23"

SOURCES = {
    "overview": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder",
    "build": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents",
    "share_manage": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-share-manage-agents",
    "build_guide": "https://support.microsoft.com/en-us/microsoft-365-copilot/build-your-own-agent-with-microsoft-365-copilot",
    "share_agent": "https://support.microsoft.com/en-us/microsoft-365-copilot/how-to-share-your-agent",
    "compare_studio": "https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/copilot-studio-experience",
    "chat_history": "https://support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-chat-history-works",
    "memory": "https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory",
    "share_chat": "https://support.microsoft.com/en-us/microsoft-365-copilot/share-conversations-responses-in-microsoft-copilot",
}


def _src(*keys):
    items = "".join(
        '<li><a href="{0}" target="_blank" rel="noopener">{0}</a></li>'.format(SOURCES[k])
        for k in keys
    )
    return '<div class="sources"><strong>Sources to check</strong><ul>{}</ul></div>'.format(items)


TENANT_NOTE = (
    '<div class="callout note"><strong>Your screen may look different.</strong> '
    "Microsoft updates the Copilot interface often, and features depend on your licence "
    "and your organization's settings. If a button is called <em>Create agent</em> "
    "instead of <em>New agent</em>, or sits in a different place, follow the label you "
    "actually see.</div>"
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

TEMPLATE_CHARTER = """AGENT NAME: [short and specific]
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
    {
        "slug": "charter",
        "title": "Template A: One-Purpose Agent Charter",
        "use": "Fill this in before you open the builder. It forces you to name one job.",
        "body": TEMPLATE_CHARTER,
    },
    {
        "slug": "instructions",
        "title": "Template B: Copy-ready Agent Instructions",
        "use": "Paste into the Instructions box and replace every [bracket].",
        "body": TEMPLATE_INSTRUCTIONS,
    },
    {
        "slug": "test-card",
        "title": "Template C: 3-Test Agent Quality Card",
        "use": "Run all three tests every time you change the instructions.",
        "body": TEMPLATE_TEST_CARD,
    },
    {
        "slug": "email-coach",
        "title": "Example A: Email Clarity Coach instructions",
        "use": "Name: Email Clarity Coach. Description: Helps me improve the clarity, tone and structure of work emails.",
        "body": EMAIL_COACH_INSTRUCTIONS,
    },
    {
        "slug": "expense-helper",
        "title": "Example B: Expense Policy Helper instructions",
        "use": "Name: Expense Policy Helper. Description: Helps me find answers in my organization's approved expense policy.",
        "body": EXPENSE_HELPER_INSTRUCTIONS,
    },
]


def _copy_block(text):
    from html import escape

    return '<div class="copybox"><button type="button" class="copy-btn">Copy</button><pre>{}</pre></div>'.format(
        escape(text)
    )


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
<div class="callout analogy"><strong>Plain-English idea:</strong> An agent is Copilot with a job description.</div>
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
<p>This course covers <strong>Agent Builder inside Microsoft 365 Copilot / Copilot Chat</strong> (we call it
<strong>T1</strong>). It does <em>not</em> cover the separate, more powerful Microsoft Copilot Studio portal.</p>
""" + _src("overview", "build_guide"),
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
<li>Create an agent by describing it in natural language, or with the Configure / template experience.</li>
<li>Add a clear name, description, instructions, starter prompts and permitted knowledge sources.</li>
<li>Test a good prompt, a vague prompt and an unrelated prompt, then improve the instructions.</li>
<li>Find your agent again and explain the difference between <strong>sharing an agent</strong> and
<strong>sharing chat content</strong>.</li>
<li>Tell apart chat history, Copilot memory/personalization and the agent's own instructions and knowledge.</li>
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
<tr><td>Plan</td><td>Fill in your own Agent Charter in the <em>My agent charter</em> page.</td></tr>
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
<p>The full course takes about 150 minutes including the lab. A 60-minute essentials route is: modules 2, 3, 4, 6 and 7, then the lab steps 1 to 8.</p>
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
<div class="callout analogy"><strong>Plain-English idea:</strong> Instructions tell it <em>how</em> to help;
knowledge sources tell it <em>what information</em> to use.</div>
<h3>No code needed</h3>
<p>In Agent Builder you describe what you want in everyday language, then review and adjust the settings.
You do not write code, call APIs or design workflows. Those are out of scope for T1.</p>
""" + _src("overview"),
            },
            {
                "slug": "one-purpose",
                "title": "One agent, one purpose",
                "minutes": 5,
                "body": """
<div class="callout analogy"><strong>Plain-English idea:</strong> One agent, one job, like having a separate
folder for each subject.</div>
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
noisy and can add unhelpful context.</p>
<p class="tag">Course best practice, consistent with Microsoft guidance to give agents a defined purpose and scoped instructions.</p>
""" + _src("build"),
            },
            {
                "slug": "t1-vs-studio",
                "title": "T1 Agent Builder versus Copilot Studio",
                "minutes": 5,
                "body": """
<table class="grid">
<tr><th></th><th>T1: Agent Builder in Microsoft 365 Copilot</th><th>Microsoft Copilot Studio</th></tr>
<tr><td>Who</td><td>Any associate, no code</td><td>Makers, developers, IT teams</td></tr>
<tr><td>Typical use</td><td>Personal, narrow task helpers; approved reference documents</td><td>Advanced agents, workflows, integrations, multiple channels</td></tr>
<tr><td>In this course?</td><td>Yes</td><td>No, it is the next level</td></tr>
</table>
<p>If a feature needs Copilot Studio (for example, connecting to business systems, autonomous actions or
publishing to many channels), we label it <strong>"Next-level capability, not covered by T1."</strong></p>
<p>Product options and licences vary by organization. Check what is enabled for you.</p>
""" + _src("compare_studio"),
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
<div class="callout"><strong>This agent helps me</strong> [one clear task] <strong>for</strong> [audience].</div>
<p>Examples:</p>
<ul>
<li>This agent helps me <em>rewrite my work email drafts in clear, polite English</em> for <em>my colleagues and customers</em>.</li>
<li>This agent helps me <em>find answers in our approved expense policy</em> for <em>my own expense claims</em>.</li>
</ul>
<p>If your sentence needs the word "and" to join two unrelated jobs, you probably need two agents.</p>
""",
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
answer only from an approved source (the Expense Policy Helper uses the official policy).</p>
<ul>
<li>Use <strong>approved, current</strong> documents or sites owned by the right team.</li>
<li>Do not add files with personal, customer or confidential data unless your company policy allows it.</li>
<li>Remember: <strong>knowledge access is permission-based.</strong> A colleague using your agent can only get
answers from sources they are allowed to open themselves.</li>
</ul>
<p>Write your plan down in <a href="/charter">My agent charter</a> before you build.</p>
""" + _src("build", "share_manage"),
            },
        ],
    },
    {
        "slug": "build",
        "title": "4. Build in Microsoft 365 Copilot",
        "summary": "Find Agent Builder, describe your agent in plain language, then review it in Configure.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "find-builder",
                "title": "Open Copilot and find Agent Builder",
                "minutes": 5,
                "body": TENANT_NOTE + """
<ol class="steps">
<li>Sign in to Microsoft 365 Copilot with your work account.</li>
<li>Look for the <strong>Agents</strong> area in the Copilot navigation. Agents you have access to are listed there.</li>
<li>Select the entry for making a new agent. Depending on your version it may be labelled
<strong>New agent</strong> or <strong>Create agent</strong>.</li>
</ol>
<p>If you cannot see an option to create an agent, it may not be enabled for your licence or organization.
Ask your Copilot champion or IT service desk. Do not try to work around it.</p>
<p class="facilitator">Facilitator: show your organization's own verified screenshots of these screens here, with the verification date.</p>
""" + _src("build_guide", "build"),
            },
            {
                "slug": "describe",
                "title": "Describe your agent in plain language",
                "minutes": 8,
                "body": """
<p>The builder usually opens with a place to <strong>describe</strong> what you want. Type your purpose in everyday
language. The builder may ask follow-up questions and fill in a draft name, description and instructions for you.</p>
<p>Example description to type:</p>
""" + _copy_block(
                    "Create an agent called Email Clarity Coach. Its only job is to help me rewrite my own work "
                    "email drafts in simple, polite English without changing the meaning. It should not invent facts "
                    "and should redirect unrelated questions to normal Copilot Chat."
                ) + """
<p>Read what the builder proposes. It is a draft, not a finished agent. You will check and tighten it in the next lesson.</p>
<p>Some versions also offer <strong>templates</strong> to start from. A template is fine as long as you still narrow it to one purpose.</p>
""" + _src("build_guide"),
            },
            {
                "slug": "configure-tab",
                "title": "Review everything in Configure",
                "minutes": 7,
                "body": """
<p>Switch to the <strong>Configure</strong> view (the label may vary). This is where you can see and edit each
setting directly:</p>
<table class="grid">
<tr><th>Setting</th><th>What to check</th></tr>
<tr><td>Name</td><td>Short and specific, e.g. "Email Clarity Coach".</td></tr>
<tr><td>Description</td><td>One sentence a colleague would understand.</td></tr>
<tr><td>Instructions</td><td>Role, allowed topics, answer format, what to do when unsure, off-topic rule.</td></tr>
<tr><td>Knowledge</td><td>Only approved sources you are allowed to use, or none.</td></tr>
<tr><td>Starter prompts</td><td>Three examples that match the one purpose.</td></tr>
</table>
<p>Use the <strong>preview / test</strong> panel next to Configure to try the agent before you create or save it.
Module 6 shows how to test properly.</p>
""" + _src("build"),
            },
        ],
    },
    {
        "slug": "configure",
        "title": "5. Configure well",
        "summary": "Name, description, scoped instructions, starter prompts, knowledge permissions, answer shape and saving.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "name-description",
                "title": "Name and description",
                "minutes": 4,
                "body": """
<p>A good name says what the agent does. A good description says who it helps and how.</p>
<div class="two-col">
<div class="good"><h4>Clear</h4><ul><li><strong>Email Clarity Coach</strong>: Helps me improve the clarity, tone and structure of work emails.</li></ul></div>
<div class="bad"><h4>Unclear</h4><ul><li><strong>My Bot</strong>: Helps with stuff.</li></ul></div>
</div>
""",
            },
            {
                "slug": "instructions",
                "title": "Write scoped instructions",
                "minutes": 8,
                "body": """
<p>Good instructions cover five things:</p>
<ol>
<li><strong>Role and one purpose</strong>: "You are my Email Clarity Coach. Your only job is..."</li>
<li><strong>Style</strong>: simple, polite English; short or formal versions.</li>
<li><strong>When unsure</strong>: ask one short question or say you cannot confirm it.</li>
<li><strong>Never</strong>: invent dates, names, approvals, policy or citations.</li>
<li><strong>Off-topic rule</strong>: politely suggest normal Copilot Chat.</li>
</ol>
<p>Plus an <strong>answer format</strong>, for example <em>Improved email / What I changed / What to double-check</em>.</p>
<p>Start from Template B and replace each bracket:</p>
""" + _copy_block(TEMPLATE_INSTRUCTIONS) + _src("build"),
            },
            {
                "slug": "prompts-knowledge-save",
                "title": "Starter prompts, knowledge, citations and saving",
                "minutes": 8,
                "body": """
<h3>Starter prompts</h3>
<p>Add at least three. They show users what the agent is for. Each one should fit the one purpose.</p>
<h3>Knowledge sources</h3>
<ul>
<li>Add only approved files or sites you are permitted to use.</li>
<li>Sharing an agent is <strong>not</strong> a way around file permissions. Each user only gets content they can already access.</li>
<li>When answers are grounded in a source, ask the agent to name the source or section, and check it.</li>
</ul>
<h3>Create / save</h3>
<p>When the tests pass, select the button that creates or saves the agent (the label varies). Then find it again
in your agents list and open it to confirm it works.</p>
""" + _src("build", "share_manage"),
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
<table class="grid">
<tr><th>Test</th><th>Example (Email Clarity Coach)</th><th>Pass when the agent...</th></tr>
<tr><td>1. On topic</td><td>Please improve this email: Hi team, we need the latest status by Friday. Thanks.</td><td>Returns a clearer email, keeps the facts, explains changes.</td></tr>
<tr><td>2. Vague</td><td>Make it better.</td><td>Asks for the draft or context instead of inventing one.</td></tr>
<tr><td>3. Off topic</td><td>Who won a sports match?</td><td>Says this is outside its purpose and suggests normal Copilot Chat.</td></tr>
</table>
<p>Record the results on Template C:</p>
""" + _copy_block(TEMPLATE_TEST_CARD),
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
<p>Changing one thing at a time tells you which edit actually helped.</p>
""",
            },
        ],
    },
    {
        "slug": "safety",
        "title": "7. Sharing, chat history, memory and safety",
        "summary": "Agent sharing versus conversation sharing, permissions, chat history, optional memory, and data hygiene.",
        "minutes": 20,
        "lessons": [
            {
                "slug": "sharing",
                "title": "Sharing an agent versus sharing a chat",
                "minutes": 7,
                "body": """
<div class="callout analogy"><strong>Plain-English idea:</strong> A shared agent is a shared helper, not a shared personal diary.</div>
<ul>
<li><strong>Sharing an agent</strong> lets others use the agent (its name, instructions and knowledge settings), according to the access settings available in your organization.</li>
<li>Sharing the agent <strong>does not by itself share your personal conversations</strong> with it.</li>
<li><strong>Sharing a conversation or response</strong> is a separate, deliberate action using Copilot's sharing features.</li>
<li>Tenant policies, permission settings and special agent types can change the rules. Never promise absolute privacy.</li>
</ul>
<p>Follow your organization's rules before sharing any agent. In the lab you only <em>review</em> the share options; you do not need to share.</p>
""" + _src("share_agent", "share_manage", "share_chat"),
            },
            {
                "slug": "permissions",
                "title": "Knowledge is permission-based",
                "minutes": 4,
                "body": """
<p>If your agent uses a SharePoint site or file, a colleague using the agent can only receive content from that
source if <strong>they</strong> are allowed to access it. Sharing the agent does not grant file access.</p>
<p>If a colleague says "the agent cannot answer", check whether they have permission to the source.</p>
""" + _src("share_manage"),
            },
            {
                "slug": "memory",
                "title": "Chat history, memory and what the agent 'learns'",
                "minutes": 6,
                "body": """
<div class="callout analogy"><strong>Plain-English idea:</strong> The agent is not a magic memory box that remembers every chat forever.</div>
<table class="grid">
<tr><th>Thing</th><th>What it is</th></tr>
<tr><td>Agent configuration</td><td>The instructions, starter prompts and knowledge you set. This is what mainly shapes the agent.</td></tr>
<tr><td>Conversation context</td><td>What has been said in the current chat. It helps the current conversation.</td></tr>
<tr><td>Chat history</td><td>Your personal list of past chats, subject to your organization's compliance and retention settings.</td></tr>
<tr><td>Copilot memory / personalization</td><td>Where enabled, Copilot <em>may</em> use selected useful details from earlier chats. It does not remember everything, and admins and users can control it.</td></tr>
</table>
<p>So: <strong>an agent is not permanently retrained by every question</strong>, and your chats do not become shared knowledge for everyone.</p>
<p>Some preview or shared-memory agent types have different rules. They are out of scope for T1.</p>
""" + _src("chat_history", "memory"),
            },
            {
                "slug": "data-hygiene",
                "title": "Data hygiene",
                "minutes": 3,
                "body": """
<ul>
<li>Do not paste passwords, secrets, bank details or customer records into an agent.</li>
<li>Use redacted or made-up examples when practising.</li>
<li>Follow your company's sensitivity labels and data policies.</li>
<li>Keep unrelated questions out of a purpose-built agent's chat.</li>
</ul>
""",
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
<p><strong>Name:</strong> Email Clarity Coach<br><strong>Description:</strong> Helps me improve the clarity, tone and structure of work emails.<br><strong>Knowledge:</strong> none needed.</p>
<h3>Instructions</h3>
""" + _copy_block(EMAIL_COACH_INSTRUCTIONS) + """
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
<strong>Knowledge:</strong> the approved expense policy file or site only. If none is available for training, use a clearly labelled
<em>fictional sample policy created for training</em>, and never present it as the real company policy.</p>
<h3>Instructions</h3>
""" + _copy_block(EXPENSE_HELPER_INSTRUCTIONS) + """
<h3>Tests</h3>
<ul>
<li><strong>Good:</strong> "Where does the policy explain meal reimbursements? Please cite the section."</li>
<li><strong>Unsupported:</strong> "Can I claim an unlisted special expense?" Expected: explains it cannot confirm and suggests Finance; does not invent approval.</li>
<li><strong>Off topic:</strong> "Can you plan my holiday?" Expected: redirects to normal Copilot Chat.</li>
</ul>
<p><strong>Proof of success:</strong> stays in the policy domain, cites sources, separates known from unknown, and invents no policy facts.
Results vary with the knowledge, licence and features available to each user.</p>
""",
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
<li>A work account with access to Microsoft 365 Copilot and the ability to create agents.</li>
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
<tr><td>Asking random questions in the agent chat</td><td>The thread gets noisy; personalization may pick up details where enabled</td><td>Use normal Copilot Chat or a new, relevant thread</td></tr>
<tr><td>Thinking every chat permanently retrains the agent</td><td>Factually misleading</td><td>Separate conversation context, configuration and optional memory</td></tr>
<tr><td>Expecting a shared agent to include your past chats</td><td>Confuses access with history</td><td>Share only the agent; conversation sharing is separate</td></tr>
<tr><td>Using a source a colleague cannot access</td><td>The agent may not answer for them</td><td>Check file and agent permissions</td></tr>
<tr><td>Accepting a confident answer without checking</td><td>Wrong answers can sound convincing</td><td>Ask for the source and verify it</td></tr>
<tr><td>"Help with anything" instructions</td><td>Scope cannot be tested</td><td>State role, topics, format, off-topic behaviour</td></tr>
<tr><td>Including personal or customer confidential data</td><td>Unnecessary exposure</td><td>Use redacted or synthetic examples and approved sources</td></tr>
<tr><td>Expecting Copilot Studio features in T1</td><td>Wrong expectations in the lab</td><td>Mark them "Advanced: requires Copilot Studio"</td></tr>
</table>
""",
            },
            {
                "slug": "case-studies",
                "title": "Inspiration from large organizations",
                "minutes": 8,
                "body": """
<div class="callout note"><strong>Read this first.</strong> These are external adoption stories for inspiration. They are
<strong>not</strong> evidence that these companies used T1 Agent Builder, and you cannot reproduce advanced enterprise
solutions with this beginner tool. The product each one used is named. Facilitators: open each source and re-check
it before presenting; do not quote figures that you have not verified.</div>
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
<h4>Source leads (verify before use)</h4>
<ul class="small">
<li><a href="https://www.microsoft.com/en/customers/story/25909-heineken-microsoft-copilot-studio" target="_blank" rel="noopener">HEINEKEN customer story</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/25674-kantar-microsoft-copilot-studio" target="_blank" rel="noopener">Kantar (Copilot Studio)</a> and <a href="https://www.microsoft.com/en/customers/story/24603-kantar-microsoft-365-copilot" target="_blank" rel="noopener">Kantar (Microsoft 365 Copilot)</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/23132-epiq-global-microsoft-power-platform" target="_blank" rel="noopener">Epiq Global customer story</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/24130-peoplecert-hellas-ae-azure-openai" target="_blank" rel="noopener">PeopleCert customer story</a></li>
<li><a href="https://www.microsoft.com/en/customers/story/23332-games-global-microsoft-copilot-studio" target="_blank" rel="noopener">Games Global customer story</a></li>
<li><a href="https://www.microsoft.com/en-us/power-platform/blog/power-apps/power-platform-stories/" target="_blank" rel="noopener">Power Platform stories (Komatsu Australia)</a></li>
<li><a href="https://news.microsoft.com/source/features/digital-transformation/accenture-is-rolling-out-copilot-to-a-workforce-the-size-of-denver/" target="_blank" rel="noopener">Accenture feature story</a></li>
<li><a href="https://www.emiratesnbd.com/en/media-center/emirates-nbd-to-transform-business-operations-and-enhance-productivity-with-generative-ai" target="_blank" rel="noopener">Emirates NBD media release</a></li>
</ul>
""",
            },
            {
                "slug": "next-steps",
                "title": "Templates and what to learn next",
                "minutes": 5,
                "body": """
<p>All three standard templates and both example configurations are on the <a href="/templates">Templates</a> page with copy buttons.</p>
<h3>Make a second agent</h3>
<p>Pick another small, repeated task from your week. Fill in a new charter, copy Template B, and run the three tests.</p>
<h3>What to learn next</h3>
<p>T1 is the entry point. When you need workflows, connections to business systems, autonomous actions or publishing
to several channels, move on to your organization's <strong>Copilot Studio</strong> training. Ask your Copilot champion where to find it.</p>
""" + _src("compare_studio"),
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Hands-on lab steps (brief section 8)
# ---------------------------------------------------------------------------

LAB_STEPS = [
    (1, "Write your agent's single purpose in one sentence", "Purpose describes one job; an off-topic boundary is written."),
    (2, "Open Microsoft 365 Copilot and locate the agent builder", "Correct entry point shown to the facilitator or evidenced with a redacted screenshot."),
    (3, "Describe your agent in the builder", "Name, description and purpose appear in the configuration."),
    (4, "Edit instructions and boundaries", "Instructions cover style, uncertain facts and the off-topic redirect."),
    (5, "Add at least 3 starter prompts", "Prompts relate directly to the one purpose."),
    (6, "Test one clear prompt", "A useful answer meets the agent's purpose."),
    (7, "Test one vague prompt", "The agent asks for clarification instead of inventing missing details."),
    (8, "Test one unrelated question", "The agent stays in scope, or you adjust the instructions and retest."),
    (9, "Check a fact-sensitive response", "You can show where a fact came from, or identify uncertainty."),
    (10, "Save/create and reopen the agent", "Your agent appears in your list and opens again."),
    (11, "Review sharing, without sharing sensitive information", "You can explain agent sharing versus separate chat sharing."),
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
        "source_url": SOURCES.get(source, "") if source else "",
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
       "In your version of Copilot the button says 'Create agent', but the training said 'New agent'. What should you do?",
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
       "The builder generated a draft name, description and instructions from your description. What next?",
       ["Save immediately; generated drafts are always correct",
        "Review and tighten each setting in Configure, then test",
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
]

FINAL_QUESTION_COUNT = 15
DEFAULT_PASS_MARK = 80  # percent
