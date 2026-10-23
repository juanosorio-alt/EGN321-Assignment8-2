# Inventory Reorder Decision Assistant
**Juan Pablo Osorio — EGN 321 Assignment 8.2**

This local application implements the inventory proposal from Assignment 4.2. It calculates replenishment recommendations from the original six-item workbook, validates inputs and preserves review history. The temperature application from Modules 5–7 was a separate course exercise; its Flask/SQLite/logging/supervisor patterns informed this capstone, but temperature readings do not represent inventory measurements.

The software, technical verification and presentation preparation are complete for a classroom demonstration. The classmate handoff, its observations, two subsequent improvements and the live instructor defense remain to be performed. See `docs/HANDOFF.md`. No partner success is claimed.

## 1. Project Overview
The fictional store manager needs to decide which items require replenishment and in what quantities. The purchasing assistant reviews recommendations before preparing orders. This tool replaces the manual review process in `original/INVENTORY_REORDER_SANITIZED_JUAN_OSORIO.xlsx`. It does not place purchases or connect to a stock system. No operational owner has approved the classroom policy.

## 2. System Requirements
Python 3.10+, Flask 3.1.3, a browser and a writable project folder. SQLite is included with Python. macOS was tested; Linux uses the same documented commands but was not tested in this run. Windows is not verified. Internet is needed to install dependencies; operation is local. Port 5082 must be free. Keep `app.py`, `logic.py`, `supervisor.py`, `templates/index.html` and `data/sample_inventory.json` together. Keep the original workbook for verification. Excel is not needed to run the application.

## 3. Installation
Download/extract the project, then open a terminal in the folder containing this README:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest -v
python supervisor.py
```

Open **http://127.0.0.1:5082**. Leave the terminal running. Startup messages go to `runtime/application_console.log`; a quiet terminal is normal. Ctrl+C stops the supervisor and child. The application binds only to this computer. No boot service is installed.

## 4. Quick Start
After installation:

```bash
source .venv/bin/activate
python supervisor.py
```

Open the local URL, click **Load workbook sample**, then **Calculate and save review**. P-110 should show demand 24, reorder point 30 and order quantity 36. Download the CSV if needed. These actions save a review, not a purchasing order.

## 5. Normal Operation
Load the supplied six items or choose Add item and enter every field. SKU identifies an item independently of its row position. Remove only removes an unsaved input row; it does not delete earlier history. Editing a saved review and calculating again creates a new dated review, leaving the earlier record intact.

Review inputs, click Calculate and save review, then inspect each recommendation and its calculation columns. The stock bars visualize stock on hand; the printed label also states the reorder point. Select a saved history entry to inspect its original inputs/results. Refresh logs and health to see status and events. History, status and logs refresh on these actions or a page reload; they are not a continuous live sensor feed.

## 6. Inputs and Units
| Field | Meaning | Supported input |
|---|---|---|
| SKU | Unique item identifier within a review | 1–32 letters/digits, hyphen or underscore; normalized uppercase |
| Item | Description | Nonempty text, up to 120 characters |
| On hand | Stock count | Whole items, 0–1,000,000 |
| Weekly use | Average consumption | Finite items/week, 0–1,000,000 |
| Lead time | Delivery interval | Finite weeks, 0–1,000,000 |
| Safety stock | Additional allowance | Whole items, 0–1,000,000 |
| Unit / lead unit | API declarations | Exactly `each` and `weeks` |

The interface fixes units to each and weeks. It does not convert packs, days or currencies. The JSON API accepts 1–100 item objects and up to 256 KB per request. Sample JSON is included; Excel/CSV upload is not implemented. Export format is CSV, with spreadsheet-formula escaping for user-entered text.

## 7. What the Tool Refuses
Missing values, nonnumeric or nonfinite values, negative values, fractional stock counts, unsupported units, duplicate SKUs and unsupported ranges cause a clear refusal. The whole review is rejected and no partial review is saved. During storage failure no review can be saved, and the interface reports failure instead of claiming success. A failed network response leaves the outcome uncertain; check history before retrying.

## 8. Expected Output and Policy
Policy `classroom-v1`:

```text
demand = weekly_use × lead_time
reorder_point = demand + safety_stock
reorder = on_hand <= reorder_point
exact_order_qty = 2 × reorder_point - on_hand, when reorder is YES
order_qty = ceiling(exact_order_qty), otherwise 0
```

The input safety stock applies to every SKU, intentionally replacing the row-7 fixed allowance. The multiplier 2 comes from the workbook and is retained as an explicit classroom assumption, not a proven optimum. Negative stock/backorders are unsupported. Ceiling rounding supplies whole items for fractional demand. All original integer cases match; rounding is a documented extension. Zero stock with zero reorder point returns YES but zero quantity under the original comparison rule.

A successful response includes a review ID, UTC timestamp, all inputs, demand, reorder point, decision, exact quantity, whole order quantity and policy version. SQLite preserves each complete review. The CSV contains the same results.

## 9. System Health and Alerts
HEALTHY means the database write probe succeeds. FAILED means the storage probe fails or a controlled outage is active. RECOVERING identifies startup before the first successful probe in event transitions. Process downtime makes the web page unavailable, rather than falsely showing a new health response. An already-open page can display old content until refreshed.

The inventory YES decision is a replenishment recommendation, not a temperature alert. There is no sensor sampling interval or stale-sensor alarm in this final application. Inventory records are dated snapshots; their business freshness requires human review.

## 10. Logs
`runtime/events.jsonl` records startup, review saved/exported, refusal, storage errors and health changes. `runtime/supervisor.jsonl` records child starts, exits and restart attempts. `runtime/application_console.log` records HTTP activity and tracebacks. The dashboard displays up to 100 recent application events. A separate file log remains available during the simulated storage outage; real disk failure could prevent both logging and database writes.

```bash
tail -n 30 runtime/events.jsonl
tail -n 30 runtime/supervisor.jsonl
tail -n 30 runtime/application_console.log
```

Compare the earliest storage warning with failed requests and the subsequent FAILED-to-HEALTHY event. Preserve evidence before changing files.

## 11. Troubleshooting
| Symptom | Check | Action |
|---|---|---|
| Flask import error | Active virtual environment | Activate .venv and install requirements |
| Browser cannot connect | Correct port; console and supervisor logs | Start supervisor; resolve a duplicate port/process |
| Input refused | Error message and labeled units | Correct the indicated field and recalculate |
| FAILED storage | Logs; runtime permissions; outage marker | Follow recovery below; do not delete history |
| No sample loads | data/sample_inventory.json | Restore this bundled file from the package |
| Supervisor stops retrying | RESTART_LIMIT_REACHED | Correct cause and restart manually |

## 12. Recovery Procedures
For the controlled outage, keep the app running and open another terminal in the project folder:

```bash
source .venv/bin/activate
python -c "from pathlib import Path; Path('runtime/storage.unavailable').touch()"
```

Click Refresh logs and health. Expect FAILED and a storage message. Attempt a calculation: it must refuse to save. This is an application-level simulation, not disk corruption. Remove only the marker:

```bash
python -c "from pathlib import Path; Path('runtime/storage.unavailable').unlink(missing_ok=True)"
```

Refresh status, confirm HEALTHY, inspect prior history and save another review. Never delete the database to force recovery. A separate automated test also holds an actual SQLite write lock and verifies recovery after rollback.

For process exits, the supervisor restarts the child after roughly one second. It stops after five rapid failures. No protection against a hung child, lost supervisor or power failure is claimed. For a real storage error, stop the supervisor, preserve runtime files and diagnose permissions/corruption/disk capacity before restart.

## 13. Assumptions
Source data is fictional and instructor-authorized. Consumption and lead time are deterministic averages. No uncertainty model, pack size, minimum order or budget constraint is included. Units must match their labels. The ordering multiplier and universal safety-stock input are classroom policy choices; the original exception's business intent is unknown. Decimal arithmetic supports the calculation, while displayed JSON numbers use ordinary floating representation. One local operator and one supervisor per runtime are assumed.

Advanced settings: `INVENTORY_PORT` defaults to 5082, `INVENTORY_RUNTIME` defaults to the project runtime folder, and `INVENTORY_TEST_CONTROLS=1` enables a supervisor-controlled child-kill marker for reproducible testing only. Use absolute runtime paths. Invalid port settings are not automatically corrected. Keep test controls disabled for ordinary use.

## 14. Known Limitations
No physical inventory verification, real-time stock feed, physical temperature integration, supplier interface, authentication or production hosting. No automatic log retention, pagination, purchase execution, database repair or boot startup. Local Flask development server is suitable for the classroom demonstration only. Very large quantities pass the technical bounds but need business review. There is no guarantee of stockout prevention or cost optimization. Partner usability remains untested until the handoff session.

## 15. Testing and Reproduction
```bash
python -m unittest -v
```

Tests cover all six cached workbook cases, the safety-stock discrepancy, invalid input, SKU order independence, boundaries, rounding, atomic saves, exports and recovery. They use temporary databases. `evidence/unit_tests.txt` records the executed run; `docs/VERIFICATION.md` explains provenance and expected results.

For the real HTTP/restart verification, start a separate test runtime (terminal 1):

```bash
INVENTORY_TEST_CONTROLS=1 INVENTORY_RUNTIME="$PWD/runtime-test" python supervisor.py
```

Then run from terminal 2 with the environment activated:

```bash
python verify_live.py --runtime "$PWD/runtime-test" --output evidence-new
```

The output directory must not exist. Keep port 5082 free of other applications. The test requests a kill of the supervisor's own child through an opt-in marker, then checks the new PID and preserved history. It never targets another process. Stop the supervisor with Ctrl+C afterward. The submitted live evidence is already included and is not overwritten.

## Submission and preparation map
- `original/`: unchanged workbook, proposal and audit provenance.
- `data/`: source inputs and cached baseline outputs.
- `logic.py`: reusable validation/calculation policy.
- `app.py`, `templates/`, `supervisor.py`: interface, SQLite and recovery.
- `test_inventory.py`, `verify_live.py`: automated and live verification.
- `evidence/`: executed results, HTTP output, logs, database and screenshots.
- `docs/VERIFICATION.md`, `docs/DEMO_AND_DEFENSE.md`, `docs/HANDOFF.md`: explanation and rehearsal.
- `AI_LOG.md`: AI tasks, accepted work, changes and verification.

The repository URL is supplied separately when published. The partner handoff results and at least two post-handoff improvements remain outstanding; do not submit this as a completed handoff.
