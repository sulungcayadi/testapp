# Copilot Agent Hub and T1 Training

A local web app that teaches associates to build **one Microsoft 365 Copilot agent with one purpose**, and then becomes the organization's single front door for Copilot agents: an agent registry with governance reviews, an ideas board, licence requests, a coach network, a prompt library, adoption insights and benchmarks against leading companies.

It runs on any PC with Python. There is nothing to install and no internet connection is needed; all data is kept in one SQLite file. The whole app is available in **English, Japanese, Simplified Chinese, Thai, Indonesian and Vietnamese**.

**Guides in other languages:** [日本語](docs/README.ja.md) · [简体中文](docs/README.zh-CN.md) · [ไทย](docs/README.th.md) · [Bahasa Indonesia](docs/README.id.md) · [Tiếng Việt](docs/README.vi.md)

## Quick start

1. Install **Python 3.8 or newer** from <https://www.python.org/downloads/>. On Windows, tick *Add Python to PATH* during setup.
2. Download or clone this folder.
3. Start the app:
   - **Windows:** double-click `start_windows.bat`
   - **macOS / Linux:** run `./start_mac_linux.sh`
   - **Or from any terminal:** `python app.py`
4. Your browser opens at <http://127.0.0.1:8000>. On first launch, create the administrator account.
5. Learners select **Create your account** on the sign-in page and register with their associate ID.
6. Anyone can change the language from the **Language** menu at the top of every page, including the sign-in page. The choice is remembered.

To stop the app, press `Ctrl+C` in the terminal window (or close it).

## Languages

Every screen, lesson, quiz question, explanation, lab step, template, glossary entry, benchmark table, notification and the certificate is translated. Two things are deliberately left in English:

- **Microsoft interface labels** such as *New agent*, *Configure*, *Try it*, *Can chat* and *Settings > Personalization*. Learners see these labels in Microsoft 365 Copilot, so the course uses them exactly.
- **Titles of Microsoft Learn source pages**, so facilitators can find the original page.

On the Templates page, each translated template also offers the **English original**, because some organizations require agent instructions to be written in English. Text that administrators type in (organization questions, a custom acceptable-use policy) is shown as written.

Translations live in `training/locales/<code>.py` as simple `English: translation` dictionaries. After editing course content, run `python app.py i18n-extract --check` to see which new or changed segments still need a translation in each language, and `python app.py i18n-extract --missing ja` to list them for a translator. Until a segment is translated, the English text is shown.

## What's included

### Learn (every associate)
| Feature | What it does |
|---|---|
| **Core T1 course: 10 modules, 29 lessons** | Welcome, agent basics, planning, building in Microsoft 365 Copilot, configuring, testing, sharing/memory/safety, two guided examples, lab briefing, mistakes and real-world inspiration. About 150 minutes; a 60-minute essentials route is described in lesson 1.3. |
| **Leader track and coach track** | Optional modules on what leading companies do, tiered governance, measuring value and a 12-month roadmap (leaders), and on supporting colleagues and reviewing agents (coaches). |
| **Skills check and learning paths** | A 2-minute self-assessment recommends modules. Builder levels 1 to 3 unlock wider sharing in the hub, as in Hitachi's certification-led approach. |
| **Module quizzes and final assessment** | Instant scoring with an explanation for every answer. The final assessment draws 15 questions from a 58-question bank, always including the 3 key knowledge-check questions. Pass mark 80% by default. |
| **Hands-on lab tracker** | The 12 lab steps with their "Done when" checks, ticked while working in Microsoft 365 Copilot. |
| **My agent charter** | Template A as a form. It drafts copy-ready agent instructions and can register the agent in the hub. |
| **Toolkit** | Templates with Copy buttons, a printable quick reference card, glossary, Microsoft references, facilitator guide, and the policy and help page. |
| **Certificate** | Unlocks after all lessons, lab steps 1 to 10 and the final assessment. Printable or saved as PDF, in the learner's language. |

### Agent hub (the integrated ecosystem)
| Feature | What it does |
|---|---|
| **Agent registry** | Every agent shared beyond its owner is registered with a purpose, owner, tier, knowledge sources, data sensitivity, sharing scope, one KPI with a baseline, test results and a review date. Before building, associates search the approved catalogue for an agent they can reuse. |
| **Governance reviews** | Agents shared with a team or the organization, or using confidential data, go to a coach's review queue with an 8-point checklist. Tier 3 and 4 agents (acting on data or autonomously) go to the CoE. Owners must hold the T1 certificate before submitting. |
| **90-day value reviews** | Approved agents get a review date. Owners record the KPI result; agents without measurable value are retired. Overdue reviews appear in a retirement queue. |
| **Ideas board** | Associates post tasks Copilot could help with, vote and comment. Agents built from an idea are linked back to it. |
| **Licence requests** | Teams request Microsoft 365 Copilot seats with a use case and expected hours saved. The CoE approves them in waves, highest expected value first, as Lloyds did. |
| **Community** | Coach directory with office hours, events (promptathons, show and tell, live training), and a rated prompt library. |
| **Ask the CoE** | Questions about policy, data, licences and incidents, with the acceptable-use guideline and data rules beside them. |
| **Hours saved** | Each associate logs hours saved per week on the hub home page. |
| **Notifications** | An inbox for review decisions, licence decisions, comments on ideas and answers from the CoE. |
| **Insights** | One dashboard across training, agents, ideas, licences and hours saved, with a 6-month trend, breakdowns by tier, status and department, and an adoption index. |
| **Benchmarks** | What Toyota, Siemens, Hitachi, Rabobank, Lloyds, Vodafone, Barclays, Volkswagen and Accenture did; six shared habits; Microsoft's governance zones; a 12-month roadmap; and live progress against targets scaled to your number of associates. Every figure is labelled as company- or vendor-reported, with its source. |

### Administration (the CoE)
| Feature | What it does |
|---|---|
| **Overview dashboard** | Associates loaded, certified, in progress and not started; activity; average final score and feedback; certification rate by department; and a module funnel. |
| **Learners** | Search and filter, 50 per page. Open a learner to see quiz attempts, lab steps, charter and agents, edit details, reset the password, or make them a coach. |
| **Import associates** | Upload or paste a CSV (`associate_id, name, email, department, location`). Re-importing updates details and keeps progress. |
| **CSV exports** | The full progress report, and the whole question bank with answers in any or all languages. |
| **Question bank** | Each question's correct-answer rate, hardest first. Disable questions or add organization-specific ones. |
| **Settings** | Organization name, pass mark, and your own acceptable-use guideline (otherwise a translated starter guideline is shown). |

## Rolling out to 10,000 associates

- **Pre-load associates:** export a list from HR into the CSV template (Admin → Import associates → *Download a CSV template*), or run `python app.py import-users associates.csv`. Associates then register with their ID and choose a password.
- **Appoint coaches:** open a learner in Admin → Learners and select *Make this person a coach*. Aim for about 1 coach per 60 associates (about 170 for 10,000).
- **One shared copy:** to let everyone use the same database, run the app on a machine people can reach on your intranet: `python app.py --host 0.0.0.0 --port 8000`. The app uses plain HTTP, so only expose it on a trusted internal network, or put it behind your organization's HTTPS reverse proxy. Check with IT first.
- **Single PC / classroom:** the default setup (`127.0.0.1`) only accepts connections from the same computer.
- **Performance:** the tests load 10,000 associates and build the dashboard, filtered lists and the CSV export in well under 10 seconds. SQLite runs in WAL mode so several people can save at once.
- **Backups:** all data is in `data/training.db`. Copy that file while the app is stopped, or use a SQLite backup tool.

## Command reference

```text
python app.py                          Start the app (opens your browser)
python app.py --port 8080 --no-browser Use another port, and don't open a browser
python app.py --host 0.0.0.0           Listen on your network (see the roll-out notes above)
python app.py create-admin             Add an administrator, or promote an existing account
python app.py import-users FILE.csv    Import or update associates from CSV
python app.py export FILE.csv          Write the progress report to CSV
python app.py reseed                   Reload course content after editing training/content.py
python app.py demo-data 500            Add 500 fictional DEMO learners to try out the training reports
python app.py i18n-extract --check     Report missing translations for every language
python app.py i18n-extract --missing th  List the English segments not yet translated into Thai
python app.py --db other.db ...        Use a different database file (or set TRAINING_DB)
```

Use `demo-data` only on a test database. Demo learners have IDs starting with `DEMO`.

## Updating the course content

All learner-facing English text (lessons, lab steps, templates, questions, benchmarks, glossary) is in `training/content.py` and `training/blocks.py`. To change it:

1. Edit the English text.
2. Run `python app.py reseed`. Matching is by lesson slug and question code, so learner progress and quiz history are kept.
3. Run `python app.py i18n-extract --check` and add translations for the changed segments to `training/locales/`.
4. Restart the app.

**Before you deliver the course**, a facilitator should:
- Open each Microsoft Learn source on the References page and confirm the steps and labels still match your tenant. Microsoft changes the Copilot UI often.
- Add your organization's own verified screenshots for module 4. The app includes no Microsoft screenshots, so that no image is shown as current UI without being verified.
- Re-check each case study and benchmark source before presenting it. The app names the product each company used and labels reported figures, but facilitators should verify them.
- Replace the starter acceptable-use guideline (Admin → Settings) with your approved one.

## Project layout

```text
app.py                 Entry point and command line
start_windows.bat      Double-click launcher for Windows
start_mac_linux.sh     Launcher for macOS / Linux
training/
  content.py           Course and hub content: modules, lab, templates, questions, benchmarks
  blocks.py            Reusable HTML blocks and Microsoft Learn sources
  db.py                SQLite schema and content seeding
  services.py          Accounts, progress, quizzes, lab, charters, reports
  hub.py               Agent registry, reviews, ideas, licences, community, insights
  core.py              Request handling, HTML layout, CSRF, sessions
  pages_learn.py       Learner pages
  pages_hub.py         Agent hub, community, help and insights pages
  pages_admin.py       Administration pages
  web.py               Routing and the web server (Python standard library only)
  i18n.py              Language selection and translation lookup
  i18n_tools.py        Finds every translatable segment (for translators and tests)
  locales/             ja, zh_CN, th, id, vi translations
  static/              CSS, JavaScript and the CSV template
docs/                  This guide in Japanese, Chinese, Thai, Indonesian and Vietnamese
tests/                 End-to-end and unit tests
data/training.db       Created on first run (not committed)
```

## Running the tests

```text
python -m unittest discover -s tests -v
```

The tests start the real server on a random port. They cover first-time setup, registration, the full learner journey to the certificate, CSRF protection, the final-assessment tamper check, CSV import, admin reports, the question bank, settings, a 10,000-associate load, the full agent lifecycle (register, submit, review, approve, value review, retire), CoE-only tiers, ideas, licences, events, prompts and coaches. A crawl test opens every page, module, lesson and quiz in all six languages and fails if any text is left untranslated, and a check confirms every translation keeps the same placeholders as the English.

## Security notes

- Passwords are stored as salted PBKDF2-SHA256 hashes. Sessions use random tokens in HttpOnly, SameSite cookies and expire after 12 hours.
- Every form submitted by a signed-in user is protected against CSRF, and all user input is HTML-escaped.
- The question set for the final assessment is signed, so learners cannot swap in easier questions.
- Associates cannot review their own agents, and only the CoE can approve Tier 3 and 4 agents.
- Tell associates not to enter confidential data in notes, charters, ideas or prompts. The app reminds them where it matters.

## Scope and limitations

- The app teaches Microsoft 365 Copilot Agent Builder and governs agents built with it. It does not connect to Microsoft 365: it cannot see agents in your tenant or check that a learner really built one. The lab and the registry are self-reported, and coaches verify agents through the chat link during review.
- Benchmark figures come from public company, vendor and media sources dated in the app. They are not independently audited, and targets are planning assumptions derived from them.
- There is no single sign-on (Microsoft Entra ID). Accounts are local to the app.
- Translations were prepared for this project and should be reviewed by a native-speaking facilitator in each country before roll-out, as you would with any training material.
