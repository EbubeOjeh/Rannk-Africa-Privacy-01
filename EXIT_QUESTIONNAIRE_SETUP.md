# Optional logout questionnaire and direct email

This update adds a second, short questionnaire when a student deliberately clicks an application Log out or Sign out button. It contains three True/False multiple-choice questions, four likelihood ratings (1 Very unlikely through 5 Very likely), an optional general privacy review, name and student ID fields. Answers may be skipped. Name, student ID and separate agreement are required only when choosing to submit. A student can always log out without submitting or stay signed in.

The exit review is identified, not anonymous. It does not change the student's account name, ranking, transcript, public discovery or recruiter consent. The name and student ID are stored only with the exit review and available to the super administrator. The original seven-question task questionnaire remains available separately.

Once a student has submitted an exit review, future app logout clicks do not prompt again. Skipping leaves them eligible for the prompt next time. This feature cannot reliably intercept closing a browser tab, browser crashes, expired sessions or closing the computer; those events do not submit anything automatically.

## Run the complete package
This is included in the full all-in-one system. No earlier project or update ZIP is required. Extract the complete ZIP to a new folder and follow START_HERE.md. Double-click START_LOCAL.cmd, wait for both servers, then open http://localhost:5173.

Email configuration is OPTIONAL. To inspect responses without email, sign in as super administrator, open Class review, and download identified exit reviews to see every question and answer alongside the submitted name and student ID. The admin page shows identity and general comment directly. Existing sent-email status labels do not mean you must configure email.

The short exit form appears when a signed-in student deliberately clicks Sign out or Log out. Once submitted it is not shown again for that account. The student may also log out without submitting. The original task questionnaire remains separate.

A fresh extraction starts with zero students. Normal startup creates the additional exit-review table without clearing existing accounts if you use an existing compatible database. Never delete a database to enable this feature.

## Configure email delivery
A receiving email address alone cannot send messages. Configure a functioning SMTP sender account/relay that your hosting service can reach. Use that provider's actual host, port, sender address and app password or SMTP credentials. Do not share the SMTP password in chat or commit it to GitHub.

Add these settings to backend/.env for local use. The values below are placeholders; replace them:
```
EXIT_FEEDBACK_RECIPIENT=your-receiving-address@example.com
SMTP_HOST=your-provider-smtp-host
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USER=your-provider-smtp-username
SMTP_PASSWORD=your-provider-app-password-or-smtp-secret
SMTP_FROM=your-provider-approved-sender@example.com
```
With SMTP_USE_SSL=false the code requires STARTTLS before authentication. For an implicit-TLS sender, use the provider's appropriate port and SMTP_USE_SSL=true. TLS failures do not fall back to sending credentials in plaintext. If SMTP_USER is blank, no username/password authentication is attempted; follow your relay's requirements.

Restart the backend after local .env changes. For Railway, put the same variables in the SERVICE variable settings, not in frontend variables or GitHub. Confirm that the host/account permits reaching the configured SMTP service; this cannot be determined by a local test. Keep the existing persistent volume for database and photos.

Before actual participant use set STUDY_CONTACT and STUDY_RETENTION_NOTICE to your agreed study details. The popup shows the recipient and explains that name, student ID and review will be emailed. Submission requires its own consent. The participant can skip without affecting logout or privacy controls.

## Delivery and privacy
The backend saves a response before attempting email. Email is sent as plain text to the configured recipient and includes participant ID, submitted name/student ID, the seven answers, general review and agreement text. Public rankings and recruiter discovery never include these review fields.

Status meanings:
- sent: the SMTP server accepted the message; inbox receipt is not guaranteed. Check spam and provider delivery logs.
- not_configured: sender host or receiving address is missing; the response is saved but no email was sent.
- failed: the response is saved but the SMTP attempt failed; fix credentials/connectivity and retry from Class review.
- pending: the response was saved before delivery completed; the administrator can retry if an earlier process stopped.

The same account cannot create duplicate reviews by double-clicking/resubmitting. Administrator retry does not resend responses already marked sent. A rare interruption after server acceptance but before saving the status can leave pending status; check the inbox before retrying to avoid duplicate delivery.

Authorized administrator student cleanup also removes these linked reviews from the application database. Already received email, prior exports, screenshots and backups are separate copies and are not automatically erased. Follow the agreed retention process for those copies too. This feature has not sent any real participant response while this package was prepared.

## Test checklist
- Student logout opens the popup from the student header/mobile menu and public-site navbar.
- Staff logout remains immediate.
- Close/Stay signed in keeps the session; Escape closes the popup.
- Log out without submitting creates no response and ends the session.
- Required name/ID/consent are validated, and answer options/rating labels are clear on a phone.
- Submit saves the record, shows an honest email status, and permits finishing logout.
- A second account sees none of the first account's draft fields.
- Submitted students are not prompted on subsequent logout.
- Public/recruiter profile output still excludes email, transcripts and all identified review data.
- Admin can export reviews and retry unsent email; actual inbox receipt must be verified with configured email.

Automated backend and build results are in submission/. Live SMTP delivery, Windows interactions and phone usability require your own observed tests. The unchanged original questionnaire is a separate instrument: report which one each participant completed and do not mix their different questions into one score.

The optional open-text box is labelled General comment. Its prompt asks how easy the privacy choices were to understand/use, whether starting hidden met expectations, and what should improve. You can use administrator review/export without configuring email.
