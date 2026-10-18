#!/usr/bin/env python3
"""Governed ingestion of the FINAL Source-analysis package (CONTROLLED OPERATION).

Usage:
  DATABASE_URL=… .venv/bin/python scripts/import/ingest_source_analysis.py <extracted-package-dir>

Deterministic + idempotent:
- Sources: 9 governed Sources upserted (metadata refresh; document_uri preserved).
- Artifacts: copied faithfully into data/source-documents/<SRC-ID>/ (when absent/different).
- Evidence: 426 signals inserted ON CONFLICT (evidence_id) DO NOTHING.
- Candidates: 34 reconciled candidates inserted ON CONFLICT (candidate_id) DO NOTHING;
  imported into `capabilities` as population='SOURCE_ANALYSIS_CANDIDATE' (cap_id='CAND-<family>');
  previous 135 caps marked population='HISTORICAL_BASELINE_V1'.
- Focus: Cross-market Focus Set (15) + per-market sets → is_focus / focus_markets.
- Manifest: data/import-manifests/<package-id>.json (counts, skips, conflicts, warnings).
Re-running the same package must not duplicate records.
"""

import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import psycopg

REPO = Path(__file__).resolve().parents[2]

MARKET_COLS = [
    ("Market: Traditional / K-12", "market_k12"),
    ("Market: Professional / Credentialing", "market_prof"),
    ("Market: Higher Education", "market_hed"),
    ("Market: Governed Formative", "market_formative"),
    ("Market: Assessment-led Learning", "market_ale"),
    ("Strategic Initiative: MEXCBT / Uchida", "mexcbt_relevance"),
]

SOURCE_COLS = [
    "evidence_id", "source_id", "signal_name", "full_description", "evidence_type",
    "extraction_type", "source_confidence", "source_category", "strategic_category",
    "authoring_scope", "market_k12", "market_prof", "market_hed", "market_formative",
    "market_ale", "mexcbt_relevance", "market_mapping_basis", "evidence_reference",
    "current_canonical_cap_id", "current_treatment", "feature_composition_status",
    "feature_ids", "notes", "owner_proposer", "provenance", "product_review_status",
    "import_batch",
]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: ingest_source_analysis.py <extracted-package-dir>", file=sys.stderr)
        return 2
    pkg = Path(sys.argv[1]).resolve()
    if not pkg.is_dir():
        print(f"package dir not found: {pkg}", file=sys.stderr)
        return 2

    url = os.environ.get("DATABASE_URL") or ""
    if url.startswith("postgresql+psycopg"):
        url = "postgresql://" + url.split("://", 1)[1]
    if not url:
        print("DATABASE_URL required", file=sys.stderr)
        return 2

    package_id = "TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED"
    zip_path = Path.home() / "Desktop" / f"{package_id}.zip"
    zip_md5 = hashlib.md5(zip_path.read_bytes()).hexdigest() if zip_path.is_file() else None

    sc = json.load(open(pkg / "data" / "source_capabilities.json"))
    cc = json.load(open(pkg / "data" / "capability_candidates.json"))
    focus = json.load(open(pkg / "data" / "focus_sets.json"))
    meta = json.load(open(pkg / "data" / "SOURCE_SET_METADATA_v1_2.json"))

    warnings, conflicts = [], []
    manifest = {
        "package_id": package_id,
        "package_zip_md5": zip_md5,
        "analysis_html": "TAO_AUTHORING_ANALYSIS_v1_4_VERIFIED.html",
        "importer_version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    with psycopg.connect(url, autocommit=True) as conn, conn.cursor() as cur:
        # ---- 1. Sources: 9 governed sources (metadata refresh; document_uri preserved)
        for m in meta:
            cur.execute(
                """INSERT INTO sources (source_id, title, source_type, owner, status,
                       input_form, evidence_class, authority, extraction_rule)
                   VALUES (%s,%s,%s,%s,'REGISTERED',%s,%s,%s,%s)
                   ON CONFLICT (source_id) DO UPDATE
                     SET title=EXCLUDED.title, source_type=EXCLUDED.source_type,
                         owner=EXCLUDED.owner, input_form=EXCLUDED.input_form,
                         evidence_class=EXCLUDED.evidence_class,
                         authority=EXCLUDED.authority,
                         extraction_rule=EXCLUDED.extraction_rule""",
                (m["source_id"], m["title"], m["source_type"], m.get("owner_proposer"),
                 m.get("input_form"), m.get("evidence_class"), m.get("authority"),
                 m.get("extraction_rule")))
        manifest["sources_imported"] = len(meta)

        # ---- 2. Artifacts: faithful copies into the document store
        artifacts_connected = 0
        src_dir = pkg / "sources"
        for m in meta:
            sid = m["source_id"]
            artifact = m.get("artifact")
            if not artifact:
                continue
            src_file = src_dir / artifact
            if not src_file.is_file():
                warnings.append(f"artifact listed but missing: {artifact}")
                continue
            dest_dir = REPO / "data" / "source-documents" / sid
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / artifact
            if not dest.exists() or dest.read_bytes() != src_file.read_bytes():
                shutil.copyfile(src_file, dest)
            cur.execute("SELECT document_uri FROM sources WHERE source_id=%s", (sid,))
            uri = cur.fetchone()[0]
            if uri != f"local://{sid}/{artifact}":
                cur.execute("UPDATE sources SET document_uri=%s WHERE source_id=%s",
                            (f"local://{sid}/{artifact}", sid))
                artifacts_connected += 1
        manifest["artifacts_connected"] = artifacts_connected

        # ---- 3. Evidence: 426 signals (idempotent)
        inserted_ev = 0
        for r in sc:
            vals = {col: r.get(orig) for orig, col in MARKET_COLS}
            cur.execute(
                f"""INSERT INTO source_evidence ({", ".join(SOURCE_COLS)})
                    VALUES ({", ".join(["%s"] * len(SOURCE_COLS))})
                    ON CONFLICT (evidence_id) DO NOTHING""",
                (r.get("Source Capability ID"), r.get("Source ID"),
                 r.get("Capability / Signal Name"), r.get("Full Description"),
                 r.get("Evidence Type"), r.get("Extraction Type"),
                 r.get("Source Confidence"), r.get("Source Category"),
                 r.get("Strategic Category"), r.get("Authoring Scope"),
                 vals["market_k12"], vals["market_prof"], vals["market_hed"],
                 vals["market_formative"], vals["market_ale"], vals["mexcbt_relevance"],
                 r.get("Market / Initiative Mapping Basis"), r.get("Evidence / Reference"),
                 r.get("Current Canonical CAP-ID") or None,
                 r.get("Current Reconciliation / Treatment"),
                 r.get("Feature Composition Status"), r.get("Feature ID(s)"),
                 r.get("Notes"), r.get("Owner / Proposer"),
                 r.get("Origin / Extraction Provenance"), r.get("Product Review Status"),
                 package_id))
            inserted_ev += cur.rowcount
        cur.execute("SELECT count(*) FROM source_evidence")
        evidence_total = cur.fetchone()[0]
        manifest["evidence_imported_this_run"] = inserted_ev
        manifest["evidence_total"] = evidence_total

        # ---- 4. Historical baseline: previous 135 marked, never deleted
        cur.execute("""UPDATE capabilities SET population='HISTORICAL_BASELINE_V1'
                       WHERE population IS NULL""")
        historical = cur.rowcount

        # ---- 5. Candidates: 34 → capability_candidates + capabilities (active)
        cross_focus = {f["family_id"] for f in focus.get("Cross-market Focus Set", [])}
        focus_markets_by_family = {}
        for market, entries in focus.items():
            if market == "Cross-market Focus Set":
                continue
            for e in entries:
                focus_markets_by_family.setdefault(e["family_id"], []).append(market)

        inserted_cand, inserted_caps = 0, 0
        for c in cc:
            fam = c["Family ID"]
            cap_id = f"CAND-{fam}"
            focus_markets = ", ".join(sorted(focus_markets_by_family.get(fam, [])))
            cur.execute(
                """INSERT INTO capability_candidates (candidate_id, name, cap_id, markets, signals,
                     independent_sources, source_ids, evidence_strength,
                     cross_market_leverage, strategy_alignment, mexcbt_signals,
                     package_status, is_focus, focus_markets)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (candidate_id) DO NOTHING""",
                (fam, c["Capability Candidate"], cap_id, c["Markets"], c["Signals"],
                 c["Independent Sources"], c["Source IDs"], c["Evidence Strength"],
                 c["Cross-market Leverage"], c["Strategy Alignment"],
                 c["MEXCBT Direct Signals"], c["Status"],
                 fam in cross_focus, focus_markets or None))
            inserted_cand += cur.rowcount
            # active capability row (population = SOURCE_ANALYSIS_CANDIDATE)
            cur.execute(
                """INSERT INTO capabilities (cap_id, working_name, description,
                     strategic_category, roadmap_admission, notes,
                     extraction_origin, population, review_status)
                   VALUES (%s,%s,%s,'Awaiting Product data',NULL,NULL,'AI_ABSTRACTED',
                           'SOURCE_ANALYSIS_CANDIDATE',
                           'CANDIDATE · PRODUCT CONFIRMATION REQUIRED')
                   ON CONFLICT (cap_id) DO NOTHING""",
                (cap_id, c["Capability Candidate"],
                 f"Consolidated capability candidate ({c['Signals']} source evidence signals from {c['Independent Sources']} independent sources). Full description awaiting Product definition."))
            inserted_caps += cur.rowcount
            # markets as metadata relationships (names → ids)
            for name in [x.strip() for x in (c["Markets"] or "").split(",") if x.strip()]:
                cur.execute("SELECT market_id FROM markets WHERE name=%s", (name,))
                row = cur.fetchone()
                if not row:
                    warnings.append(f"unknown market name in candidate {fam}: {name}")
                    continue
                cur.execute("""INSERT INTO capability_markets (cap_id, market_id)
                               VALUES (%s,%s) ON CONFLICT DO NOTHING""", (cap_id, row[0]))
        cur.execute("SELECT count(*) FROM capabilities WHERE population='SOURCE_ANALYSIS_CANDIDATE'")
        active_total = cur.fetchone()[0]
        manifest.update({
            "candidates_imported_this_run": inserted_cand,
            "candidates_total": inserted_cand and len(cc),
            "active_candidate_rows": active_total,
            "capability_rows_imported_this_run": inserted_caps,
            "historical_baseline_marked": historical,
            "focus_cross_market_count": len(cross_focus),
            "warnings": warnings,
            "conflicts": conflicts,
        })
        manifest_path = REPO / "data" / "import-manifests" / f"{package_id}.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=1))
        print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
