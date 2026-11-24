# Install the photo privacy update

This update keeps your existing local database, accounts, synthetic grades, schools, consent settings and questionnaire. It does not upload or score transcripts. It also retains the requested removal of the top classroom banner and the words “& Music” from the Technology label.

## Apply to your current project
1. Stop both running servers with Ctrl+C in their command windows.
2. Extract RankAfrica-Photo-Privacy-Update.zip into a separate temporary folder.
3. Open that extracted folder. Copy its backend and frontend folders, together with the included guides, into your existing RankAfrica-Final project folder containing START_LOCAL.cmd. Choose Replace for the included matching files. Do NOT delete the old project folder. The update does not include a database, .env or uploads.
4. In VS Code at the existing project root run `cmd /c START_LOCAL.cmd` again.
5. Wait for both servers and refresh the browser. Log in again if needed.

## Student steps
1. Open My Profile > Your details and use Change photo to upload a JPG, PNG, WebP or GIF. The existing upload size limit applies (25 MB by default).
2. You can see your photo privately in your profile builder. Uploading does not enable either discovery audience.
3. Edit your biography under Your details, and portfolio link under the profile contact section. Save profile changes. Use an http:// or https:// portfolio link.
4. Open Privacy. Enable public discovery and independently choose Share photo, Share biography and/or Share portfolio link. Click Save. Only checked optional fields are sent with the public ranking/profile.
5. Open /rankings in a private browser window. The picture appears beside the student's ranking only when public discovery and public photo sharing are saved and the profile remains eligible. Selected biography and portfolio appear with the ranking and profile. Email and transcript are excluded.
6. Switch photo sharing OFF and save: refresh the public window and confirm the image is gone; new requests to its direct URL are denied too. Switch public discovery OFF and save to remove the whole public entry.
7. Recruiter discovery has its own separate audience/photo/biography/portfolio choices. Enabling public sharing does not enable recruiter sharing.

Withdrawal cannot recall photos already downloaded or retained authorized application snapshots. Applications continue to require their separate confirmation, as before. A recipient needs current approval to read an authorized snapshot.

## Checks
The automated suite checks private upload/owner access, public photo consent and withdrawal, independent recruiter access, exclusions of email/transcript, continued academic restrictions and the existing privacy behavior. The frontend production build is also checked. Actual Windows, phone and hosted deployment checks remain yours to complete using LOCAL_TEST_CHECKLIST.md. No live Railway site was changed.

After local testing, apply these same changed source files to your new repository/deployment. Railway needs its persistent volume for both database and uploads. Do not push your local database, uploads or .env to GitHub.
