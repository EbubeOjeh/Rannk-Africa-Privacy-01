# Corrections in privacy-assessment-v1

- Preserved Logo.jsx, globals.css and all original public branding assets byte-for-byte.
- Retained the React page shells, navigation structure, profile builder and existing styles.
- Added independent private-by-default public/recruiter consent with audience-specific extras.
- Added saved previews, explicit unsaved feedback, withdrawal and student-visible sharing history.
- Added school-scoped roster/release operations; eligibility never supplies student consent.
- Replaced legacy discovery reads with shared policy checks registered before legacy routers.
- Filtered lists, direct profiles, recruiter searches/bookmarks, archives and homepage highlights.
- Limited discovery to core information and selected biography/photo/portfolio; no email/CV/transcript.
- Recomputed displayed positions after eligible filters and before pagination.
- Added named-recipient review with independent optional application fields and required confirmation.
- Stored immutable original application snapshots; wrong recipients and revoked recruiters are denied.
- Allowed opportunity browsing and confirmed applications while discovery and extras remain off.
- Removed browser-persisted login tokens; saved consent persists independently in SQLite.
- Protected upload reads and retained application photo access; disabled public Supabase uploads.
- Seeded 12 fictional students, 3 schools, 2 approved recruiters, 1 pending recruiter and 6 opportunities.
- Added API acceptance tests, build logs and a startup/lifecycle-restart smoke check.
- Added Docker/Render deployment files, Windows startup helpers and a clean ZIP script.
- Revised proposal and report to distinguish tested implementation from unrun team/hosting evaluation.

## Intentional scope changes
Discovery profiles omit legacy detailed score breakdowns, contact channels, project evidence,
achievements and CV links because the proposal permits only core information and three extras.
The owner profile builder retains its detailed private editing screens.
Direct contact relay is disabled in the fictional demonstration.
Application recipients use the new Applications navigation item; broad administrator applicant reads
are denied instead of returning live student data.
The new limited school roster is at /school; legacy administrative management remains separate.
Historical discovery rechecks present disclosure for archived membership rather than replaying
stale serialized optional fields. No immutable historical score claim is made.
No production-security, legal-compliance, fairness, hosted-availability or general-usability claim is made.

## Verification limits
The source passed the included API suite and frontend build in Linux/Python 3.12.14/Node 24.22.1.
The Docker target is Python 3.11/Node 22 and has not been built in this environment.
Cloud-browser access to local preview was refused; team visual and keyboard checks remain open.
No live host has been provisioned and there is no verified public link yet.
