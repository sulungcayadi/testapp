# Copilot Agent Builder Training (T1)

A local training app that teaches associates to build **one Microsoft 365 Copilot agent with one purpose**, test it and use it safely. It runs on any PC with Python. There is nothing to install and no internet connection is needed; all data is kept in one SQLite file.

The course content follows the project brief *Copilot_Agent_Builder_Training_Brief.md*: the six key messages, both guided examples (Email Clarity Coach and Expense Policy Helper), the 12-step hands-on lab, the three standard templates, the three knowledge-check questions, and the 11 organization case studies with honest product labels.

## Quick start

1. Install **Python 3.8 or newer** from <https://www.python.org/downloads/>. On Windows, tick *Add Python to PATH* during setup.
2. Download or clone this folder.
3. Start the app:
   - **Windows:** double-click `start_windows.bat`
   - **macOS / Linux:** run `./start_mac_linux.sh`
   - **Or from any terminal:** `python app.py`
4. Your browser opens at <http://127.0.0.1:8000>. On first launch, create the administrator account.
5. Learners select **Create your learner account** on the sign-in page and register with their associate ID.

To stop the app, press `Ctrl+C` in the terminal window (or close it).

## What's included

### For learners
| Feature | What it does |
|---|---|
| **10 course modules, 28 lessons** | Welcome, agent basics, planning, building in Microsoft 365 Copilot, configuring, testing, sharing/memory/safety, two guided examples, lab briefing, mistakes and case studies. About 150 minutes in total; a 60-minute essentials route is described in lesson 1.3. |
| **Module quizzes** | A short quiz after each module with instant scoring and an explanation for every answer. Answer options are shuffled, and learners can retry. |
| **Final assessment** | 15 questions drawn at random from the 44-question bank, always including the 3 key knowledge-check questions. Pass mark is 80% by default. |
| **Hands-on lab tracker** | The 12 lab steps with their "Done when" checks. Learners tick each step and can add an optional note while they work in Microsoft 365 Copilot. |
| **My agent charter** | A form for Template A. It saves the charter, drafts copy-ready agent instructions from it, and downloads both as a `.txt` file. |
| **Templates page** | The 3 standard templates and both example configurations, each with a **Copy** button. |
| **Progress dashboard** | Overall progress bar, a suggested next step, and the status of every module. |
| **Certificate** | Unlocks once all lessons, lab steps 1 to 10 and the final assessment are done. It is printable and can be saved as a PDF. |
| **Feedback** | A 1 to 5 rating and a comment. |

### For administrators
| Feature | What it does |
|---|---|
| **Overview dashboard** | Associates loaded, certified, in progress and not started; activity in the last 7 days; average final score; average feedback; certification rate by department; and a module funnel showing where learners drop off. |
| **Learners** | Search and filter by department or status, 50 per page. Open a learner to see their quiz attempts, lab steps and charter, edit their details or reset their password. |
| **Import associates** | Upload or paste a CSV (`associate_id, name, email, department, location`). This is built for a 10,000-associate roll-out: re-importing updates details and keeps progress. |
| **CSV export** | A full progress report for everyone or for one department, ready for Excel. |
| **Question bank** | Each question's correct-answer rate, hardest first. Admins can disable questions or add organization-specific ones. |
| **Settings** | Organization name (shown in the header and on certificates) and the pass mark. |

## Rolling out to 10,000 associates

- **Pre-load associates:** export a list from HR into the CSV template (Admin → Import associates → *Download a CSV template*), or run `python app.py import-users associates.csv`. Associates then register with their ID and choose a password. The department you imported is kept.
- **One shared copy:** to let everyone use the same database, run the app on a machine people can reach on your intranet: `python app.py --host 0.0.0.0 --port 8000`. Learners then open `http://<that-machine>:8000`. The app uses plain HTTP, so only expose it on a trusted internal network, or put it behind your organization's HTTPS reverse proxy. Check with IT before you do this.
- **Single PC / classroom:** the default setup (`127.0.0.1`) only accepts connections from the same computer. This suits facilitator demos, kiosks or individual use.
- **Performance:** the tests load 10,000 associates and build the dashboard, filtered lists and the CSV export in well under 10 seconds. SQLite runs in WAL mode so several learners can save at once.
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
python app.py demo-data 500            Add 500 fictional DEMO learners to try out the reports
python app.py --db other.db ...        Use a different database file (or set TRAINING_DB)
```

Use `demo-data` only on a test database. Demo learners have IDs starting with `DEMO`.

## Updating the course content

All learner-facing text (lessons, lab steps, templates and questions) is in `training/content.py`. To change it:

1. Edit `training/content.py`.
2. Run `python app.py reseed`. Matching is by lesson slug and question code, so learner progress and quiz history are kept.
3. Restart the app.

**Before you deliver the course**, a facilitator should:
- Open each Microsoft source link listed in the lessons and confirm the steps and labels still match your tenant. Microsoft changes the Copilot UI often.
- Add your organization's own verified screenshots for module 4. The app does not include Microsoft screenshots, so that no image is shown as current UI without being verified.
- Re-check each case-study source before presenting it. The app names the product used and flags the three evidence gaps (Duolingo, ANZ, WEX), but it quotes no outcome figures.
- Replace placeholder escalation routes ("Copilot champion or IT service desk") with your real contacts, if you want to.

## Project layout

```text
app.py                 Entry point and command line
start_windows.bat      Double-click launcher for Windows
start_mac_linux.sh     Launcher for macOS / Linux
training/
  content.py           Course content: modules, lessons, lab, templates, question bank
  db.py                SQLite schema and content seeding
  services.py          Accounts, progress, quizzes, lab, charters, reports
  web.py               Web server, pages and routing (Python standard library only)
  static/              CSS, JavaScript and the CSV template
tests/test_app.py      End-to-end and unit tests
data/training.db       Created on first run (not committed)
```

## Running the tests

```text
python -m unittest discover -s tests -v
```

The tests start the real server on a random port. They cover first-time setup, registration, the full learner journey to the certificate, CSRF protection, the final-assessment tamper check, CSV import and claiming an account, admin reports, the question bank, settings, and a 10,000-associate load.

## Security notes

- Passwords are stored as salted PBKDF2-SHA256 hashes. Sessions use random tokens in HttpOnly, SameSite cookies and expire after 12 hours.
- Every form submitted by a signed-in user is protected against CSRF, and all user input is HTML-escaped.
- The question set for the final assessment is signed, so learners cannot swap in easier questions.
- Tell learners not to enter confidential data in notes, charters or feedback. The app reminds them on each page.

## Scope and limitations

- The app teaches Microsoft 365 Copilot Agent Builder. It does not connect to Microsoft 365 and does not check that a learner really built an agent. The lab is self-reported, and facilitators can review the learner's notes and charter in the admin pages.
- The content is in English only. The brief's Thai, Japanese and Simplified Chinese versions, PowerPoint decks, DOCX guides, PDFs and cartoon assets are separate deliverables and are not part of this app.
- There is no single sign-on (Microsoft Entra ID). Accounts are local to the app.
