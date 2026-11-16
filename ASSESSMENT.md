# Assessment submission notes

1. **Source** — Submit the source archive, which contains the Python server, browser UI, and test script.
2. **Run instructions** — Install Python 3.10+, run `python app.py` from the extracted folder, then open http://127.0.0.1:8000. See README.md.
3. **Short AI disclosure** — OpenAI Codex generated the initial implementation, tests, and documentation from the assignment checklist and a request to build the app from scratch. The app itself uses no AI service.
4. **Optional demo** — For a short recording, show a booking, attempt a conflicting booking, reschedule the original visit, then cancel it and show it under the Cancelled filter. Use fictional patient names.
5. **AI tools used** — OpenAI Codex.
6. **Development use** — Codex chose a dependency-free Python/SQLite design, implemented the booking workflows, and checked the request handlers.
7. **Prompts** — The direct build prompt was “build the app from scatch for me”. The full assessment checklist was also supplied as context. Two more prompts to actually run before submitting, if you want to meet the requested prompt count: “Review the appointment app for double-booking and validation edge cases.” and “Walk me through an end-to-end browser test for booking, editing and cancelling an appointment.” Report these only after using them. Add what each produced and what you verified.
8. **Unsuitable AI output** — Codex initially wrote a test that used a loopback HTTP connection. The environment blocked that connection, so the initial test could not verify the app there.
9. **Identification and correction** — The run failed with Windows socket permission error 10013. Codex changed the test to pass HTTP requests directly to the request handler and use a temporary SQLite database. The revised test passed.
10. **Testing** — Request checks passed for serving the page, loading the schedule, rejecting empty names and past dates, simultaneous booking conflicts, rescheduling, cancellation, freeing a cancelled slot, preserving database records, and missing appointment IDs. Browser interaction was not verified in this environment. Run the README walkthrough before claiming browser testing.
11. **Limitations** — Local demo, fixed providers and slots, and no login, reminders, audit log, or timezone handling. Use fictional data.
12. **Two more hours** — Prioritize showing only available times for the selected provider and date. Keep the database constraint as the final conflict check and add tests that confirm a cancelled slot becomes selectable again.
