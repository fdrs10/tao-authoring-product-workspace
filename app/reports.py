"""Governed report contracts + generators (FINAL STRUCTURAL STEP).

Model:  Application Product Truth → Report Contract → Generated Report.

- Five predefined contracts (D1–D5) with fixed target delivery dates and
  predefined section structures.
- Generators consume canonical application data ONLY (PostgreSQL) — a
  generated report is a representation, never a source of truth, and
  generating one never mutates Product Truth.
- Missing data renders explicitly as "Awaiting Product data" /
  "Product decision required" (§10) — no AI-filled assumptions.
- M1–M6 in D4 come from the governed canonical milestone dataset (§D4).
- Section states: AVAILABLE / INCOMPLETE / PRODUCT DECISION REQUIRED /
  NOT APPLICABLE.
"""

import datetime
import html as _html

# ---- report contracts -------------------------------------------------------
TARGET_DATES = {
    "D1": "30 October 2026",
    "D2": "30 October 2026",
    "D3": "13 November 2026",
    "D4": "13 November 2026",
    "D5": "20 November 2026",
}

REPORT_NAMES = {
    "D1": "Authoring Product Definition — Ideation & Target Scope",
    "D2": "TAO Studio Creator V2 — Product Backlog",
    "D3": "TAO Studio Creator V2 — Product Roadmap",
    "D4": "TAO 3.x → TAO Studio Authoring — Common Migration Path",
    "D5": "Customer Migration Plan",
}

CONSUMES = {
    "D1": "Sources + Ideation + Cross-analysis + Target Scope",
    "D2": "Canonical Capabilities + Features + Markets + Product Review + Traceability + Admission",
    "D3": "Product Backlog + Roadmap Timing + Features + Markets + M1–M6",
    "D4": "Roadmap + M1–M6 + derived Migration availability/dependencies",
    "D5": "Customer + Required Capabilities + Features + Roadmap + M1–M6 + blockers + readiness",
}

SECTIONS = {
    "D1": ["Executive Summary", "Product Vision and Authoring Objective", "Sources and Evidence",
           "TAO Studio V1 Carry-forward", "TAO 3.x Direct Migration", "New Needs & Gaps",
           "Discontinued", "Cross-analysis", "Target Authoring V2 Scope",
           "Market and MEXCBT / Uchida Relevance", "Open Product Decisions"],
    "D2": ["Executive Summary", "Product Backlog Overview", "Canonical Capabilities",
           "Strategic Categories", "Market Coverage", "Feature Composition",
           "Product Review Status", "Source / Evidence Traceability",
           "MoSCoW and Roadmap Admission", "Open Decisions and Gaps"],
    "D3": ["Executive Summary", "Roadmap Principles", "Roadmap Timeline",
           "Full / 0–6m / 7–24m / Tail Horizons", "Capabilities by Strategic Category",
           "Priorities and Sequencing", "Feature Composition View", "Market Views",
           "Dependencies", "M1–M6 Alignment", "Risks and Open Product Decisions"],
    "D4": ["Executive Summary", "Migration Objective", "Current → Target Authoring Model",
           "Common Migration Principles", "M1 — Target Authoring agreed",
           "M2 — Migration foundation proven", "M3 — First production cutovers",
           "M4 — No new 3.x Authoring deployments", "M5 — 3.x read-only / final exceptions",
           "M6 — TAO 3.x Authoring EOL", "Capabilities and Value Available by Milestone",
           "Roadmap Dependencies", "Migration Conditions", "Common Blockers and Exceptions",
           "Customer Transition Approach"],
    "D5": ["Executive Summary", "Customer Context", "Current Authoring Situation",
           "Current TAO Environment", "Required Functionality",
           "Required Canonical Capabilities", "Relevant Features",
           "Product Roadmap Availability", "Proposed Migration Milestone / Interval",
           "Proposed Migration Window", "Customer-specific Dependencies", "Blockers",
           "Assumptions", "Exceptions", "Customer Feedback / Evidence",
           "Migration Readiness", "Product Decisions Required", "Validation Status",
           "Next Actions"],
}

PILOT_INTENDED_CUSTOMERS = ["DEPP", "INVALSI", "NSA", "NCCER"]

MONTHS = ["Oct 2026", "Nov 2026", "Dec 2026", "Jan 2027", "Feb 2027", "Mar 2027",
          "Apr 2027", "May 2027", "Jun 2027", "Jul 2027", "Aug 2027", "Sep 2027",
          "Oct 2027", "Nov 2027", "Dec 2027", "Jan 2028", "Feb 2028", "Mar 2028",
          "Apr 2028", "May 2028", "Jun 2028", "Jul 2028", "Aug 2028", "Sep 2028",
          "Oct 2028", "Nov 2028", "Dec 2028"]


# ---- small html helpers -------------------------------------------------------
def esc(v) -> str:
    return _html.escape(str(v)) if v is not None else ""


def h(tag: str, inner: str, attrs: str = "") -> str:
    a = f" {attrs}" if attrs else ""
    return f"<{tag}{a}>{inner}</{tag}>"


def table(headers, rows) -> str:
    if not rows:
        return ""
    head = "".join(h("th", esc(x)) for x in headers)
    body = "".join(h("tr", "".join(h("td", c) for c in r)) for r in rows)
    return f'<table class="rt"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def notice(kind: str, msg: str) -> str:
    return f'<p class="rn rn-{kind}">{esc(msg)}</p>'


AWAITING = "Awaiting Product data"
DECISION = "Product decision required"


# ---- data loaders (canonical only) ---------------------------------------------
class Data:
    def __init__(self, cur):
        self.cur = cur

    def q(self, sql, params=()):
        self.cur.execute(sql, params)
        cols = [d.name for d in self.cur.description]
        return [dict(zip(cols, r)) for r in self.cur.fetchall()]

    def capabilities(self):
        caps = self.q("""SELECT cap_id, working_name, description, strategic_category,
            moscow, visibility, scope, origin, owner, decision, v2_mapping,
            ideation_sheet, roadmap_admission, analysis_budget_hours,
            execution_budget_hours, notes, review_status, version,
            extraction_origin, product_review_status, product_rationale,
            EXISTS (SELECT 1 FROM source_capabilities sc
                    WHERE sc.canonical_cap_id = capabilities.cap_id) AS traceable,
            COALESCE((SELECT json_agg(m.name ORDER BY m.name)
                      FROM capability_markets cm JOIN markets m
                      ON m.market_id = cm.market_id
                      WHERE cm.cap_id = capabilities.cap_id), '[]'::json) AS markets
            FROM capabilities ORDER BY cap_id""")
        for c in caps:
            c["traceability_status"] = (
                "OK" if c["traceable"] or (
                    c["extraction_origin"] == "PRODUCT_CREATED" and c["product_rationale"])
                else "TRACEABILITY_REVIEW_REQUIRED")
        return caps

    def markets(self):
        return self.q("SELECT market_id, name, color FROM markets ORDER BY market_id")

    def sources(self):
        return self.q("""SELECT s.source_id, s.title, s.source_type, s.owner, s.status,
            s.document_uri, s.input_form, s.upstream_reference,
            (SELECT count(*) FROM source_capabilities sc WHERE sc.source_id = s.source_id)
              AS extracted_capability_count
            FROM sources s ORDER BY s.source_id""")

    def milestones(self):
        return self.q("""SELECT milestone_id, name, milestone_date, position_month,
            description FROM milestones
            ORDER BY position_month NULLS LAST, milestone_id""")

    def features(self):
        return self.q("""SELECT f.feat_id, f.name, f.description, f.owner, f.status,
            f.version,
            (SELECT count(*) FROM feature_capabilities fc WHERE fc.feat_id = f.feat_id)
              AS capability_count
            FROM features f ORDER BY f.feat_id""")

    def timing(self):
        return self.q("""SELECT cap_id, start_month, duration_months, version
            FROM roadmap_timing ORDER BY cap_id""")

    def caps_by_id(self):
        return {c["cap_id"]: c for c in self.capabilities()}


def month_range_label(start, dur):
    if start is None:
        return "—"
    a, b = start, min(26, start + (dur or 1) - 1)
    return f"{MONTHS[a]} → {MONTHS[b]}"


def state_of(has_data: bool, decision_required: bool = False):
    if decision_required:
        return "PRODUCT DECISION REQUIRED"
    return "AVAILABLE" if has_data else "INCOMPLETE"


# ---- section generators ---------------------------------------------------------
# each returns (state, html)

def _exec_summary(rows, extra=""):
    if not rows:
        return "INCOMPLETE", notice("missing", AWAITING)
    return "AVAILABLE", f"<p>{esc(extra)}</p>"


def d1_sections(data: Data, caps):
    sources = data.sources()
    markets = data.markets()
    out = {}

    def sheet_caps(sheet):
        return [c for c in caps if c["ideation_sheet"] == sheet]

    def cap_table(cs):
        return table(["CAP", "Capability", "Strategic Category", "MoSCoW", "Markets", "Admission"],
                     [[c["cap_id"], esc(c["working_name"]), esc(c["strategic_category"]),
                       esc(c["moscow"] or "UNSET"), esc(", ".join(c["markets"] or [])),
                       esc(c["roadmap_admission"] or "UNSET")] for c in cs])

    out["Executive Summary"] = _exec_summary(caps,
        f"{len(caps)} canonical capabilities across {len(set(c['strategic_category'] for c in caps))} strategic categories; "
        f"{len(sources)} registered sources; {sum(s['extracted_capability_count'] for s in sources)} extracted source capabilities.")

    out["Product Vision and Authoring Objective"] = (
        "AVAILABLE", "<p>TAO Studio becomes the common authoring environment; TAO 3.x Authoring is progressively retired. "
        "One Authoring function roadmap for all current and potential new customers.</p>"
        + '<p class="rn">Authoritative reference: V2 Position (assets/V2_POSITION_REFERENCE.png — see Ideation 01).</p>')

    src_rows = [[s["source_id"], esc(s["title"]), esc(s["source_type"] or "—"),
                 esc(s["owner"] or "—"), s["extracted_capability_count"],
                 "connected" if s["document_uri"] else "unavailable"] for s in sources]
    src_state = "AVAILABLE" if sources and all(s["document_uri"] for s in sources) else "INCOMPLETE"
    out["Sources and Evidence"] = (
        src_state,
        table(["Source ID", "Document", "Type", "Owner", "Extracted", "Artifact"], src_rows)
        + (notice("missing", "Some source artifacts are not yet materialised — see docs/SOURCE_DOCUMENT_COVERAGE_REPORT.md.")
           if src_state != "AVAILABLE" else ""))

    for title, sheet in [("TAO Studio V1 Carry-forward", "V1 Carry-forward"),
                         ("TAO 3.x Direct Migration", "3.x Direct Migration to V2"),
                         ("New Needs & Gaps", "New Needs & Gaps / Developments"),
                         ("Discontinued", "Discontinued")]:
        cs = sheet_caps(sheet)
        out[title] = (("AVAILABLE", cap_table(cs)) if cs
                      else ("INCOMPLETE", notice("missing", AWAITING)))

    traced = [c for c in caps if c["traceability_status"] == "OK"]
    out["Cross-analysis"] = ("AVAILABLE" if traced else "INCOMPLETE",
        f"<p>Cross-source reconciliation covers {len(traced)} of {len(caps)} canonical capabilities "
        f"(source-traceable). {len(caps) - len(traced)} await reconstruction.</p>")

    admitted = [c for c in caps if c["roadmap_admission"]]
    dec = not admitted
    out["Target Authoring V2 Scope"] = (
        ("PRODUCT DECISION REQUIRED" if dec else "AVAILABLE"),
        (f"<p>{len(admitted)} capabilities carry a Roadmap Admission decision "
         f"({', '.join(sorted(set(c['roadmap_admission'] for c in admitted)))}).</p>" + cap_table(admitted[:40]))
        if admitted else notice("decision", DECISION + " — no capability carries a Roadmap Admission decision yet (Target Scope membership is undecided)."))

    mex = [c for c in caps if any("MEXCBT" in (m or "") for m in (c["markets"] or []))]
    out["Market and MEXCBT / Uchida Relevance"] = (
        "AVAILABLE",
        table(["Market", "Capabilities"], [[esc(m["name"]),
              sum(1 for c in caps if m["name"] in (c["markets"] or []))] for m in markets]))

    review_null = [c for c in caps if not c["product_review_status"]]
    untraced = [c for c in caps if c["traceability_status"] != "OK"]
    out["Open Product Decisions"] = (
        "AVAILABLE" if (review_null or untraced) else "AVAILABLE",
        f"<p>{len(review_null)} capabilities await Product Review; {len(untraced)} carry "
        f"TRACEABILITY_REVIEW_REQUIRED; Roadmap Admission decisions pending on "
        f"{sum(1 for c in caps if not c['roadmap_admission'])} capabilities.</p>"
        + notice("decision", "Product decisions required (listed counts) — not auto-resolved."))
    return out


def d2_sections(data: Data, caps):
    features = data.features()
    markets = data.markets()
    out = {}
    out["Executive Summary"] = _exec_summary(caps,
        f"{len(caps)} canonical capabilities; {len(features)} Features; {len(markets)} governed markets.")
    out["Product Backlog Overview"] = ("AVAILABLE" if caps else "INCOMPLETE",
        "<p>The Product Backlog is the governed set of Product capabilities resulting from Ideation and "
        "Product analysis. It answers what the Authoring product should contain — when is decided by Roadmap Admission.</p>")
    rows = [[c["cap_id"], esc(c["working_name"]), esc(c["strategic_category"]),
             esc(c["visibility"] or "—"), esc(c["moscow"] or "UNSET"),
             esc(c["roadmap_admission"] or "UNSET"),
             esc(c["product_review_status"] or "not reviewed"),
             esc(c["traceability_status"])] for c in caps]
    out["Canonical Capabilities"] = (("AVAILABLE", table(
        ["CAP", "Capability", "Category", "Visibility", "MoSCoW", "Admission", "Product Review", "Traceability"],
        rows)) if caps else ("INCOMPLETE", notice("missing", AWAITING)))
    out["Strategic Categories"] = ("AVAILABLE", table(["Strategic Category", "Capabilities"],
        [[esc(cat), sum(1 for c in caps if c["strategic_category"] == cat)]
         for cat in sorted(set(c["strategic_category"] for c in caps))]))
    out["Market Coverage"] = ("AVAILABLE", table(["Market", "Capabilities"],
        [[esc(m["name"]), sum(1 for c in caps if m["name"] in (c["markets"] or []))] for m in markets]))
    out["Feature Composition"] = (("AVAILABLE", table(
        ["Feature", "Name", "Owner", "Status", "Capabilities"],
        [[f["feat_id"], esc(f["name"]), esc(f["owner"] or "—"), esc(f["status"] or "—"),
          f["capability_count"]] for f in features]))
        if features else ("INCOMPLETE", notice("missing", AWAITING + " — Features are Product-created compositions; none are auto-generated.")))
    unreviewed = [c for c in caps if not c["product_review_status"]]
    out["Product Review Status"] = (
        "AVAILABLE",
        f"<p>{len(unreviewed)} of {len(caps)} capabilities are not yet Product-reviewed "
        f"(extraction provenance is recorded separately and never overwritten).</p>")
    untraced = [c for c in caps if c["traceability_status"] != "OK"]
    out["Source / Evidence Traceability"] = (
        ("INCOMPLETE", f"<p>{len(untraced)} capabilities carry TRACEABILITY_REVIEW_REQUIRED: "
         f"{esc(', '.join(c['cap_id'] for c in untraced))}.</p>") if untraced
        else ("AVAILABLE", "<p>All capabilities are source-traceable.</p>"))
    out["MoSCoW and Roadmap Admission"] = ("AVAILABLE", table(
        ["MoSCoW", "Admission", "Capabilities"],
        [[esc(c["moscow"] or "UNSET"), esc(c["roadmap_admission"] or "UNSET"), 1]
         for c in caps]))
    out["Open Decisions and Gaps"] = ("AVAILABLE",
        f"<p>Roadmap Admission undecided on {sum(1 for c in caps if not c['roadmap_admission'])} capabilities; "
        f"{len(unreviewed)} awaiting Product Review; {len(untraced)} with traceability gaps.</p>"
        + notice("decision", DECISION))
    return out


def d3_sections(data: Data, caps, timing):
    features = data.features()
    markets = data.markets()
    milestones = data.milestones()
    tmap = {t["cap_id"]: t for t in timing}
    out = {}
    timed = [c for c in caps if c["cap_id"] in tmap]
    out["Executive Summary"] = _exec_summary(timed,
        f"{len(timed)} of {len(caps)} canonical capabilities carry Roadmap timing; hierarchy: Strategic Category → Capability.")
    out["Roadmap Principles"] = ("AVAILABLE",
        "<p>Hierarchy: Strategic Category → Capability. Markets are filters and metadata — never a hierarchy level; "
        "each canonical capability appears exactly once when Market = All. Features are a composition view with derived coverage. "
        "Roadmap timing is canonical at Capability level.</p>")
    tl_rows = [[esc(c["cap_id"]), esc(c["working_name"]), esc(c["strategic_category"]),
                month_range_label(tmap[c["cap_id"]]["start_month"], tmap[c["cap_id"]]["duration_months"]),
                f"v{tmap[c['cap_id']]['version']}"] for c in timed]
    out["Roadmap Timeline"] = (("AVAILABLE", table(
        ["CAP", "Capability", "Category", "Window", "Timing version"], tl_rows))
        if timed else ("INCOMPLETE", notice("missing", AWAITING)))
    out["Full / 0–6m / 7–24m / Tail Horizons"] = (
        "AVAILABLE" if timed else "INCOMPLETE",
        table(["Horizon", "Capabilities"],
              [["Full", sum(1 for c in timed)],
               ["0–6m", sum(1 for c in timed if c["cap_id"] in tmap and tmap[c["cap_id"]]["start_month"] < 6)],
               ["7–24m", sum(1 for c in timed if 6 <= tmap.get(c["cap_id"], {}).get("start_month", -1) < 24)],
               ["Tail", sum(1 for c in timed if tmap.get(c["cap_id"], {}).get("start_month", -1) >= 24)]]))
    out["Capabilities by Strategic Category"] = ("AVAILABLE", table(
        ["Strategic Category", "Timed capabilities"],
        [[esc(cat), sum(1 for c in timed if c["strategic_category"] == cat)]
         for cat in sorted(set(c["strategic_category"] for c in timed))]))
    prios = sorted(set(c["moscow"] for c in caps if c["moscow"]))
    out["Priorities and Sequencing"] = ("AVAILABLE", table(["MoSCoW", "Capabilities"],
        [[esc(p), sum(1 for c in caps if c["moscow"] == p)] for p in prios])
        + "<p>Sequencing derives from Roadmap timing order (canonical, capability level).</p>")
    out["Feature Composition View"] = (("AVAILABLE", table(
        ["Feature", "Derived coverage window"],
        [[f"{f['feat_id']} {esc(f['name'])}",
          month_range_label(min((tmap[c["cap_id"]]["start_month"] for c in f["capabilities"] for t in [None]), default=None), None)]
         for f in features]))
        if features else ("INCOMPLETE", notice("missing", AWAITING + " — Feature composition is a Product decision; nothing is auto-generated.")))
    out["Market Views"] = ("AVAILABLE", table(["Market", "Applicable timed capabilities"],
        [[esc(m["name"]), sum(1 for c in timed if m["name"] in (c["markets"] or []))] for m in markets]))
    deps = [c for c in caps if c["cap_id"] not in tmap]
    out["Dependencies"] = (("INCOMPLETE", f"<p>{len(deps)} canonical capabilities are untimed "
        f"({esc(', '.join(c['cap_id'] for c in deps[:20]))}{'…' if len(deps) > 20 else ''}).</p>") if deps
        else ("AVAILABLE", "<p>All canonical capabilities carry Roadmap timing.</p>"))
    out["M1–M6 Alignment"] = (
        ("AVAILABLE", table(["Milestone", "Date", "Position (month)", "Description"],
            [[esc(m["milestone_id"]), esc(m["milestone_date"]), m["position_month"],
              esc(m["description"] or "—")] for m in milestones]))
        if milestones else ("INCOMPLETE", notice("missing", AWAITING + " — governed milestone baseline M1–M6 has not been imported.")))
    unadmitted = [c for c in caps if not c["roadmap_admission"]]
    out["Risks and Open Product Decisions"] = ("AVAILABLE",
        f"<p>{len(unadmitted)} capabilities without a Roadmap Admission decision; "
        f"{len(deps)} without timing; {len(milestones)} governed milestones in place.</p>"
        + notice("decision", DECISION))
    return out


def d4_sections(data: Data, caps, timing, milestones):
    tmap = {t["cap_id"]: t for t in timing}
    committed = [c for c in caps if c["roadmap_admission"] == "COMMITTED"]
    customers = data.q("SELECT customer_id, name, validation_status, earliest_milestone_interval FROM customers ORDER BY customer_id")
    out = {}
    out["Executive Summary"] = _exec_summary(milestones,
        f"{len(milestones)} governed milestones; {len(committed)} COMMITTED capabilities feeding the derivation.")
    out["Migration Objective"] = ("AVAILABLE",
        "<p>Move customers from TAO 3.x Authoring to TAO Studio Authoring through one shared transition framework: "
        "dependency on 3.x decreases; capability and value increase.</p>")
    out["Current → Target Authoring Model"] = ("AVAILABLE",
        "<p>Current: TAO 3.x Authoring. Target: TAO Studio Authoring (common authoring environment). "
        "Transition states are expressed through the milestone baseline — TS1/TS2/TS3 are not canonical.</p>")
    out["Common Migration Principles"] = ("AVAILABLE",
        "<p>One Product Roadmap delivers capabilities; capabilities enable migration milestones; milestones make customer "
        "transitions possible. Migration owns no capability timing.</p>")
    for sec, mid in [("M1 — Target Authoring agreed", "M1"), ("M2 — Migration foundation proven", "M2"),
                     ("M3 — First production cutovers", "M3"), ("M4 — No new 3.x Authoring deployments", "M4"),
                     ("M5 — 3.x read-only / final exceptions", "M5"), ("M6 — TAO 3.x Authoring EOL", "M6")]:
        m = next((x for x in milestones if x["milestone_id"] == mid), None)
        out[sec] = (("AVAILABLE", f"<p><b>{esc(m['milestone_id'])} · {esc(m['name'])}</b> — "
                    f"{esc(m['milestone_date'])} (month {m['position_month']}). {esc(m['description'] or '')}</p>")
                    if m else ("INCOMPLETE", notice("missing", AWAITING + " — milestone not present in the governed dataset.")))
    by_ms = []
    for m in milestones:
        if m["position_month"] is None:
            continue
        av = [c for c in committed if c["cap_id"] in tmap and tmap[c["cap_id"]]["start_month"] is not None
              and tmap[c["cap_id"]]["start_month"] + (tmap[c["cap_id"]]["duration_months"] or 0) <= m["position_month"]]
        by_ms.append([esc(m["milestone_id"]), esc(m["name"]), len(av)])
    out["Capabilities and Value Available by Milestone"] = (
        ("AVAILABLE", table(["By milestone", "Name", "COMMITTED capabilities available"], by_ms))
        if by_ms else ("INCOMPLETE", notice("missing", AWAITING + " — no milestones in the governed dataset.")))
    untimed = [c for c in committed if c["cap_id"] not in tmap]
    out["Roadmap Dependencies"] = (
        ("INCOMPLETE", f"<p>{len(untimed)} COMMITTED capabilities without Roadmap timing.</p>") if untimed
        else ("AVAILABLE", "<p>All COMMITTED capabilities carry Roadmap timing.</p>"))
    out["Migration Conditions"] = ("AVAILABLE",
        "<p>Required capabilities available ≠ customer ready: workflow, governance, data, metadata, integrations, "
        "training, contracts, procedures, adoption and organisational readiness remain customer-side conditions.</p>")
    out["Common Blockers and Exceptions"] = (
        "AVAILABLE" if customers else "INCOMPLETE",
        (table(["Customer", "Blockers", "Exceptions"],
               [[esc(c["customer_id"]), esc(c.get("blockers") or "—"), esc(c.get("exceptions") or "—")]
                for c in customers]) if customers
         else notice("missing", AWAITING + " — no governed customer records (D3).")))
    out["Customer Transition Approach"] = ("AVAILABLE",
        f"<p>{len(customers)} governed customer record(s). Each customer receives a Customer Migration Plan applying this "
        f"common path (see D5). No customers are invented.</p>")
    return out


def d5_sections(data: Data, caps, timing, milestones, customer):
    tmap = {t["cap_id"]: t for t in timing}
    required = data.q("""SELECT c.cap_id, c.working_name, c.moscow, c.roadmap_admission,
        r.start_month, r.duration_months
        FROM customer_capabilities cc JOIN capabilities c ON c.cap_id = cc.cap_id
        LEFT JOIN roadmap_timing r ON r.cap_id = c.cap_id
        WHERE cc.customer_id=%s ORDER BY c.cap_id""", (customer["customer_id"],))
    interval = (customer.get("earliest_milestone_interval") or "")
    start_mid = interval.split("->")[0].strip() if "->" in interval else None
    start_pos = next((m["position_month"] for m in milestones if m["milestone_id"] == start_mid), None)
    for rc in required:
        end = (rc["start_month"] + (rc["duration_months"] or 0)
               if rc["start_month"] is not None else None)
        rc["available"] = end is not None and start_pos is not None and end <= start_pos
        rc["dependency"] = (
            "available by the proposed interval start"
            if rc["available"]
            else ("untimed — dependent on Roadmap planning" if end is None
                  else f"Roadmap timing completes month {end}, after the proposed interval start (month {start_pos})"))
    blocked = [r for r in required if not r["available"]]
    validated = (customer.get("validation_status") or "") in ("Customer validated", "Migration committed")
    if not interval:
        readiness, reason = "PRODUCT DECISION REQUIRED", "no proposed milestone interval yet"
    elif blocked:
        readiness, reason = "BLOCKED BY ROADMAP CAPABILITY", f"{len(blocked)} required capabilities not available by the proposed interval start"
    elif not validated:
        readiness, reason = "CUSTOMER VALIDATION REQUIRED", "all required capabilities available; validation not committed"
    else:
        readiness, reason = "READY FOR PROPOSED INTERVAL", "all required capabilities available and validated"
    out = {}
    kv = lambda pairs: "".join(f"<p><b>{esc(k)}:</b> {esc(v) if v else '<i>Awaiting Product data</i>'}</p>" for k, v in pairs)
    has = lambda v: bool(v)
    out["Executive Summary"] = ("AVAILABLE",
        f"<p>Customer Migration Plan for {esc(customer['name'])} ({esc(customer['customer_id'])}). "
        f"Readiness: {esc(readiness)} — {esc(reason)}.</p>")
    out["Customer Context"] = ("AVAILABLE" if has(customer.get("relevant_markets")) else "INCOMPLETE",
        kv([("Customer ID", customer["customer_id"]), ("Name", customer["name"]),
            ("Relevant markets / use case", customer.get("relevant_markets"))]))
    out["Current Authoring Situation"] = ("AVAILABLE" if has(customer.get("current_use")) else "INCOMPLETE",
        kv([("Current Authoring use", customer.get("current_use")),
            ("Minimum functionality required today", customer.get("min_functionality_today"))]))
    out["Current TAO Environment"] = ("AVAILABLE" if has(customer.get("current_environment")) else "INCOMPLETE",
        kv([("Current TAO version / environment", customer.get("current_environment"))]))
    out["Required Functionality"] = (
        "AVAILABLE" if has(customer.get("min_functionality_studio")) or has(customer.get("desired_outcome"))
        else "INCOMPLETE",
        kv([("Minimum functionality required in TAO Studio", customer.get("min_functionality_studio")),
            ("Desired outcome", customer.get("desired_outcome")),
            ("Value opportunity", customer.get("value_opportunity"))]))
    out["Required Canonical Capabilities"] = (
        ("AVAILABLE", table(["CAP", "Capability", "Admission", "Roadmap timing",
                             "Available by interval start", "Dependency"],
            [[esc(r["cap_id"]), esc(r["working_name"]), esc(r["roadmap_admission"] or "UNSET"),
              month_range_label(r["start_month"], r["duration_months"]),
              "yes" if r["available"] else "no",
              esc(r["dependency"])] for r in required]))
        if required else ("INCOMPLETE", notice("missing", AWAITING + " — no required capabilities linked.")))
    feats = data.q("""SELECT DISTINCT f.feat_id, f.name FROM feature_capabilities fc
        JOIN features f ON f.feat_id = fc.feat_id
        WHERE fc.cap_id IN (SELECT cap_id FROM customer_capabilities WHERE customer_id=%s)
        ORDER BY f.feat_id""", (customer["customer_id"],))
    out["Relevant Features"] = (("AVAILABLE", table(["Feature", "Name"],
        [[esc(f["feat_id"]), esc(f["name"])] for f in feats])) if feats
        else ("NOT APPLICABLE", "<p>No Features composed around this customer's required capabilities.</p>"))
    out["Product Roadmap Availability"] = (
        "AVAILABLE" if required else "INCOMPLETE",
        f"<p>{len(required) - len(blocked)} of {len(required)} required capabilities are available by the "
        f"proposed interval start ({esc(start_mid or '—')}). Roadmap timing is the only timing truth consumed.</p>")
    out["Proposed Migration Milestone / Interval"] = (
        "AVAILABLE" if interval else ("PRODUCT DECISION REQUIRED", notice("decision", DECISION + " — no interval proposed yet.")),
        kv([("Earliest viable milestone interval", interval or None),
            ("Interval start milestone", start_mid or None)]))
    out["Proposed Migration Window"] = ("AVAILABLE" if has(customer.get("proposed_migration_window"))
        else "INCOMPLETE", kv([("Proposed migration window", customer.get("proposed_migration_window"))]))
    out["Customer-specific Dependencies"] = ("AVAILABLE" if has(customer.get("customer_dependencies"))
        else "INCOMPLETE", kv([("Customer-specific dependencies", customer.get("customer_dependencies"))]))
    out["Blockers"] = ("AVAILABLE" if has(customer.get("blockers")) else "INCOMPLETE",
        kv([("Blockers", customer.get("blockers"))]))
    out["Assumptions"] = ("AVAILABLE" if has(customer.get("assumptions")) else "INCOMPLETE",
        kv([("Assumptions", customer.get("assumptions"))]))
    out["Exceptions"] = ("AVAILABLE" if has(customer.get("exceptions")) else "INCOMPLETE",
        kv([("Exceptions", customer.get("exceptions"))]))
    out["Customer Feedback / Evidence"] = ("AVAILABLE" if has(customer.get("customer_feedback"))
        else "INCOMPLETE", kv([("Customer feedback / evidence", customer.get("customer_feedback"))]))
    out["Migration Readiness"] = ("AVAILABLE",
        f"<p><b>{esc(readiness)}</b> — {esc(reason)}. Blocked capabilities: "
        f"{esc(', '.join(r['cap_id'] for r in blocked)) or 'none'}.</p>")
    out["Product Decisions Required"] = (
        "AVAILABLE" if blocked or not interval else "NOT APPLICABLE",
        (f"<p>Product decisions required: {'propose a migration interval; ' if not interval else ''}"
         f"resolve {len(blocked)} capability timing gap(s) or re-propose the interval.</p>")
        if (blocked or not interval) else "<p>No open Product decisions for this customer.</p>")
    out["Validation Status"] = ("AVAILABLE",
        kv([("Validation status", customer.get("validation_status") or "Not assessed"),
            ("Product notes", customer.get("notes"))]))
    next_actions = []
    if blocked:
        next_actions.append("Resolve blocked capabilities (Roadmap planning) or re-propose the interval.")
    if not interval:
        next_actions.append("Product proposes the earliest viable milestone interval.")
    if validated is False and readiness == "CUSTOMER VALIDATION REQUIRED":
        next_actions.append("Customer validates the proposed plan; Product records validation status.")
    out["Next Actions"] = ("AVAILABLE", "<ul>" + "".join(f"<li>{esc(a)}</li>" for a in next_actions) + "</ul>"
                           or "<p>None.</p>")
    return out


# ---- document assembly ------------------------------------------------------------
CSS = """
body{font-family:Georgia,'Times New Roman',serif;color:#1d2b3a;max-width:900px;margin:24px auto;padding:0 24px;line-height:1.45}
h1{font-size:26px;border-bottom:3px solid #17324d;padding-bottom:8px}h2{font-size:17px;margin-top:28px;border-bottom:1px solid #cbd7e2;padding-bottom:3px}
.meta{color:#5a6b7d;font-size:13px}.rn{border-left:4px solid #e6ae2d;background:#fff8e8;padding:6px 10px;font-size:13px}
.rn-missing{border-color:#c85f5f;background:#f8ecec}.rn-decision{border-color:#e6ae2d;background:#fff8e8}
table.rt{border-collapse:collapse;width:100%;font-size:12.5px;margin:8px 0}
.rt th{background:#17324d;color:#fff;text-align:left;padding:5px 8px}.rt td{border:1px solid #cbd7e2;padding:4px 8px}
.sec-state{float:right;font-size:11px;color:#5a6b7d;text-transform:uppercase;letter-spacing:.5px}
@media print{body{margin:0;max-width:none}.noprint{display:none}h2{page-break-after:avoid}table.rt{page-break-inside:auto}}
.print-btn{position:fixed;top:10px;right:10px;padding:8px 14px;font-size:14px}
"""


def render_document(report_id: str, sections_html: list[tuple[str, str, str]],
                    version: int, generated_at: str, actor: str, params: dict) -> str:
    name = REPORT_NAMES.get(report_id, "Customer Migration Pilot Set")
    toc = ""
    if len(sections_html) > 4:
        toc = h("h2", "Table of contents") + "<ul>" + "".join(
            f'<li>{esc(title)} <span class="sec-state">{esc(state)}</span></li>'
            for title, state, _ in sections_html) + "</ul>"
    body = "".join(
        h("h2", f'{esc(title)} <span class="sec-state">{esc(state)}</span>') + content
        for title, state, content in sections_html)
    params_html = ""
    if params:
        params_html = "<p class='meta'>Parameters: " + esc(", ".join(f"{k}={v}" for k, v in sorted(params.items()))) + "</p>"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>{esc(report_id)} — {esc(name)}</title><style>{CSS}</style></head><body>
<button class="print-btn noprint" onclick="window.print()">Print / Save as PDF</button>
<h1>{esc(report_id)} — {esc(name)}</h1>
<p class="meta">Report ID: {esc(report_id)} · Generated: {esc(generated_at)} by {esc(actor)} · Version: v{version} ·
Target delivery: {esc(TARGET_DATES.get(report_id, "20 November 2026"))} · Status: snapshot of Product Truth at generation time</p>
{params_html}
{toc}
{body}
<p class="meta">Generated from the TAO Authoring Product Workspace — the application remains the Product Truth; this document is a snapshot representation.</p>
</body></html>"""
