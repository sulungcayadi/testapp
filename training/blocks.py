"""Shared building blocks for lesson HTML, used by every language file.

SOURCES lists the official Microsoft pages the course is based on. Each was
re-read on VERIFIED_DATE; ``updated`` is the "last updated" date shown on the
page at that time.
"""

from html import escape

VERIFIED_DATE = "2026-10-23"

SOURCES = {
    "overview": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder",
        "title": "Agent Builder in Microsoft 365 Copilot (Microsoft Learn)",
        "updated": "2026-09-30",
    },
    "build": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents",
        "title": "Build agents with Agent Builder (Microsoft Learn)",
        "updated": "2026-09-30",
    },
    "knowledge": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge",
        "title": "Add knowledge sources in Agent Builder (Microsoft Learn)",
        "updated": "2026-09-30",
    },
    "share_manage": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-share-manage-agents",
        "title": "Share and manage agents built in Agent Builder (Microsoft Learn)",
        "updated": "2026-09-30",
    },
    "compare_studio": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/copilot-studio-experience",
        "title": "Choose between Agent Builder and Copilot Studio (Microsoft Learn)",
        "updated": "",
    },
    "memory": {
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory",
        "title": "Copilot personalization and memory (Microsoft Learn)",
        "updated": "2026-09-02",
    },
    "build_guide": {
        "url": "https://support.microsoft.com/en-us/microsoft-365-copilot/build-your-own-agent-with-microsoft-365-copilot",
        "title": "Build your own agent with Microsoft 365 Copilot (Microsoft Support)",
        "updated": "2026-10-01",
    },
    "share_agent": {
        "url": "https://support.microsoft.com/en-us/microsoft-365-copilot/how-to-share-your-agent",
        "title": "How to share your agent (Microsoft Support)",
        "updated": "2026-08-13",
    },
    "chat_history": {
        "url": "https://support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-chat-history-works",
        "title": "How Microsoft 365 Copilot chat history works (Microsoft Support)",
        "updated": "2026-10-06",
    },
    "share_chat": {
        "url": "https://support.microsoft.com/en-us/microsoft-365-copilot/share-conversations-responses-in-microsoft-copilot",
        "title": "Share conversations and responses in Microsoft Copilot (Microsoft Support)",
        "updated": "2026-09-08",
    },
}


def src(keys, label="Sources (Microsoft Learn / Support)"):
    """A list of official sources shown at the end of a lesson."""
    items = "".join(
        '<li><a href="{url}" target="_blank" rel="noopener">{title}</a></li>'.format(
            url=SOURCES[k]["url"], title=escape(SOURCES[k]["title"])
        )
        for k in keys
    )
    return '<div class="sources"><strong>{}</strong><ul>{}</ul></div>'.format(escape(label), items)


def copy(text):
    """A copyable text block. The button label is set by app.js in the page language."""
    return '<div class="copybox"><button type="button" class="copy-btn">Copy</button><pre>{}</pre></div>'.format(
        escape(text)
    )


def callout(html, kind=""):
    return '<div class="callout {}">{}</div>'.format(kind, html)
