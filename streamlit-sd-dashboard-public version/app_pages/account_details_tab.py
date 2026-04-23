import streamlit as st
from data import render_nav_bar
import json as _json
import re
import hashlib
import math

QUARTERS = ["FQ1 FY27", "FQ2 FY27", "FQ3 FY27", "FQ4 FY27"]
REGIONS  = ["EntAcqEast", "EntAcqCentral", "EntAcqWest", "CommAcqEast", "CommAcqWest", "MajorsAcq", "LATAM"]

MIGRATION_TERMS  = ["redshift","databricks","teradata","oracle","bigquery","synapse","netezza","greenplum","hive","impala","presto","spark","microsoft fabric","fabric","azure data factory","sql server","db2"]
MIGRATION_INTENT = ["migrat","consolidat","take out","takeout","moving off","replac","legacy","transition from","moderniz","lift and shift","data takeout","move off"]

LEGACY_ONPREM_DW = [
    ("teradata","Teradata"),("netezza","Netezza"),("greenplum","Greenplum"),
    ("exadata","Oracle Exadata"),("oracle","Oracle"),("sql server","SQL Server"),
    ("db2","IBM DB2"),("ibm db2","IBM DB2"),("sap hana","SAP HANA"),("sap","SAP"),
    ("sybase","Sybase"),("vertica","Vertica"),("cloudera","Cloudera"),
    ("hadoop","Hadoop"),("impala","Impala"),("on-prem","On-Prem"),
    ("on premise","On-Prem"),("on-premises","On-Prem"),("self-hosted","Self-Hosted"),
]
CLOUD_DW = [
    ("microsoft fabric","Microsoft Fabric"),("fabric","Microsoft Fabric"),
    ("synapse","Azure Synapse"),("redshift","Redshift"),
    ("bigquery","BigQuery"),("databricks","Databricks"),
]

_NOT_ES_SIGNALS = [
    "snowsight","dashboard only","data model build","schema design",
    "data cleansing","data quality","copy into","simple ingestion",
    "advisory","account review","optimization review","quickstart",
    "enablement","training","ci/cd setup","tool integration",
    "api support","sharepoint connector",
]
_SD_ONLY_SIGNALS = [
    "lift and shift","lift & shift","lift-and-shift",
    "replatform","re-platform","off-prem","legacy replacement",
    "decommission","sunset",
]
_BESPOKE_SIGNALS = [
    "custom","bespoke","specific","tailored","unique","proprietary",
    "business rule","business logic","customer requirement","nuance",
    "personali","compliance","regulatory","fraud","risk",
    "pricing","revenue","churn","forecast","predict",
    "recommend","automat","real-time","agent","cortex",
]
_BEYOND_CORE_SIGNALS = [
    "custom","bespoke","business logic","proprietary","algorithm",
    "specific workflow","unique","tailored","purpose-built",
    "customer-specific","nuanced","complex transform",
]
_MIG_SIGNALS = [
    "lift and shift","lift & shift","lift-and-shift",
    "migration","migrate","replatform","re-platform",
    "move to snowflake","move from","exadata","teradata",
    "oracle migration","netezza","hadoop","greenplum",
    "warehouse migration","cloud migration","data migration",
    "sunset","decommission","off-prem","legacy replacement",
]
_DE_SIMPLE_SIGNALS = [
    "sharepoint connector","simple openflow","copy into","standard ingestion",
]
_APP_KW = {"streamlit","native app","spcs","container","react","nativeapp","managed app"}
_AI_KW  = {"cortex","agent","intelligence","llm","genai","machine learn","artificial intel","generative","document ai","search"}
_DE_KW  = {"dynamic table","iceberg","snowpark","pipeline","openflow","data sharing","clean room","ingestion","etl","elt"}

OUTCOME_COLORS = {
    "Data Migration & Modernization": "#a78bfa",
    "Analytics & BI Acceleration":    "#38bdf8",
    "AI & ML Capabilities":           "#c084fc",
    "Data Engineering & Pipelines":   "#22d3ee",
    "Application Development":        "#fb923c",
    "Governance & Security":          "#f59e0b",
    "Data Collaboration":             "#4ade80",
    "Cost & Platform Consolidation":  "#f97316",
}

STAGE_SHORT = {
    "Discovery": "Discovery",
    "SDR Qualified: SQL": "SQL",
    "Sales Qualified Opportunity": "SQO",
    "Scope / Use Case": "Scope",
    "Technical / Business Impact Validation": "Tech Valid",
}

def safe_int(v, default=0):
    try: return int(v or default)
    except: return default

def safe_float(v, default=0.0):
    try: return float(v or default)
    except: return default

def fmt_acv(v):
    v = safe_float(v)
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

def esc(s):
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def dashoff(sc):
    return round(138.2 * (1 - sc / 100), 1)

def get_cloud(agr):
    if not agr: return ""
    a = agr.lower()
    if "aws" in a: return "AWS"
    if "azure" in a: return "Azure"
    if "gcp" in a: return "GCP"
    return ""

def parse_wl(raw):
    if not raw: return []
    parts = set()
    for seg in raw.split(" | "):
        for w in seg.split(";"):
            w = w.strip()
            if w: parts.add(w)
    return list(parts)

def parse_comp(raw):
    if not raw: return []
    parts = set()
    for seg in raw.split(" | "):
        for c in seg.split(";"):
            c = c.strip()
            if c: parts.add(c)
    return list(parts)

def wl_badges(wls):
    h = ""
    seen = set()
    for w in wls[:7]:
        if w.lower() in seen: continue
        seen.add(w.lower())
        cls = "badge-ai" if ("ai" in w.lower() or "ml" in w.lower()) else ("badge-migration" if any(mt in w.lower() for mt in MIGRATION_TERMS) else "badge-uc")
        h += f'<span class="badge {cls}">{esc(w)}</span>'
    return h

def detect_dw(row):
    combined = (
        (row.get("se_comments")              or "") + " " +
        (row.get("ae_notes")                 or "") + " " +
        (row.get("meddpicc_pain")            or "") + " " +
        (row.get("meddpicc_metrics")         or "") + " " +
        (row.get("uc_descriptions")          or "") + " " +
        (row.get("meddpicc_primary_competitor") or "")
    ).lower()
    for kw, label in LEGACY_ONPREM_DW:
        if kw in combined: return label, True
    for kw, label in CLOUD_DW:
        if kw in combined: return label, False
    return None, False

def scolor(sc, ps_e, partner):
    if ps_e:      col = "#10b981"
    elif partner: col = "#a78bfa"
    elif sc >= 85: col = "#ef4444"
    elif sc >= 75: col = "#f97316"
    elif sc >= 65: col = "#eab308"
    else:          col = "#6366f1"
    return col, "#1a1a2e", "#3a3a7e"

def _classify_domain(full_text, wl_raw):
    wl = wl_raw.lower()
    ft = full_text.lower()
    app_sigs = sum(1 for s in _APP_KW if s in ft)
    ai_sigs  = sum(1 for s in _AI_KW  if s in ft)
    de_sigs  = sum(1 for s in _DE_KW  if s in ft)
    has_app_wl = "applications" in wl or "collaboration" in wl
    has_ai_wl  = bool(re.search(r"(?:^|;|\|)\s*ai\s*(?:;|\||$)", wl))
    has_de_wl  = "data engineering" in wl or "analytics" in wl
    if has_app_wl or app_sigs >= 2: return "Apps"
    if has_ai_wl or ai_sigs >= 1:   return "AI/ML"
    if has_de_wl or de_sigs >= 1:   return "DE"
    return "General"

def score(row, max_acv):
    wl     = parse_wl(row.get("workloads_raw", ""))
    comp   = parse_comp(row.get("competitors_raw", ""))
    mc     = (row.get("meddpicc_primary_competitor") or "").lower()
    se_n   = (row.get("se_comments")              or "").lower()
    ae_n   = (row.get("ae_notes")                 or "").lower()
    pain   = (row.get("meddpicc_pain")            or "").lower()
    metr   = (row.get("meddpicc_metrics")         or "").lower()
    uc_d   = (row.get("uc_descriptions")          or "").lower()
    uc_ns  = (row.get("uc_next_steps")            or "").lower()
    notes  = se_n + " " + ae_n + " " + pain + " " + metr + " " + uc_d + " " + uc_ns
    uc_n   = safe_int(row.get("uc_count"), 1)
    acv    = safe_float(row.get("opportunity_acv"), 0)
    partner = ((row.get("spn_partner") or "").strip()
               or (row.get("si_partner_names") or "").strip()
               or (row.get("spn_obj_partner_names") or "").strip()
               or (safe_int(row.get("has_deal_reg"), 0) and "deal_reg")
               or (safe_int(row.get("has_funding_request"), 0) and "funding_req"))
    wl_l   = [w.lower() for w in wl]
    comp_l = [c.lower() for c in comp]
    all_text = " ".join(comp_l) + " " + mc + " " + notes

    d1 = 0
    if any(mt in all_text for mt in MIGRATION_TERMS): d1 += 15
    if any(mt in " ".join(wl_l) for mt in MIGRATION_TERMS): d1 += 8
    if any(mi in notes for mi in MIGRATION_INTENT): d1 += 6
    d1 += min(7, len(set(wl_l)) * 2)
    d1 = min(35, d1)

    has_ai    = any("ai" in w or "ml" in w for w in wl_l) or any(k in notes for k in ["cortex","llm","machine learn","artificial intel","generative"])
    has_de    = any("data engineer" in w or "platform" in w for w in wl_l) or any(k in notes for k in ["data engineer","data pipeline","data platform"])
    has_ana   = any("analytic" in w or "collab" in w for w in wl_l) or any(k in notes for k in ["analytic","business intel"," bi ","reporting","dashboard"])
    has_share = any("shar" in w or "marketplace" in w for w in wl_l) or any(k in notes for k in ["data shar","datashare","marketplace","data product","data listing"])
    has_app   = any(k in notes for k in ["native app","managed app","snowflake intelligence","nativeapp"])
    has_dcr   = any("clean room" in w or "cleanroom" in w for w in wl_l) or any(k in notes for k in ["clean room","cleanroom","data clean room"])
    d2 = min(35, min(10, uc_n * 3) + (5 if has_ai else 0) + (5 if has_de else 0) + (5 if has_ana else 0) + (5 if has_share else 0) + (5 if has_app else 0) + (5 if has_dcr else 0) + (5 if any(k in notes + " " + " ".join(wl_l) for k in _BESPOKE_SIGNALS) else 0))

    d3 = 0
    d4 = min(15, round((acv / max_acv) * 15)) if max_acv > 0 else 7

    d5 = 0
    if not partner: d5 += 4
    if se_n and len(se_n) > 30: d5 += 4
    elif ae_n and len(ae_n) > 30: d5 += 2
    if mc: d5 += 3
    _, is_legacy = detect_dw(row)
    if is_legacy: d5 += 4
    d5 = min(15, d5)

    return min(d1 + d2 + d3 + d4 + d5, 99), d1, d2, d3, d4, d5

def _note_snippet(row, keywords, max_chars=110):
    sources = [
        row.get("meddpicc_pain")   or "",
        row.get("uc_descriptions") or "",
        row.get("se_comments")     or "",
        row.get("ae_notes")        or "",
    ]
    kw_lower = [k.lower() for k in keywords]
    for src in sources:
        for sent in re.split(r"[.!?\n|;]+", src):
            s = sent.strip()
            if len(s) > 20 and any(k in s.lower() for k in kw_lower):
                return s[:max_chars] + ("\u2026" if len(s) > max_chars else "")
    for src in sources:
        s = src.strip()
        if len(s) > 20:
            return s[:max_chars] + ("\u2026" if len(s) > max_chars else "")
    return ""

def detect_outcomes_rule_based(row, dw_name, is_legacy):
    se    = (row.get("se_comments")              or "").lower()
    ae    = (row.get("ae_notes")                 or "").lower()
    pain  = (row.get("meddpicc_pain")            or "").lower()
    metr  = (row.get("meddpicc_metrics")         or "").lower()
    uc_d  = (row.get("uc_descriptions")          or "").lower()
    uc_ns = (row.get("uc_next_steps")            or "").lower()
    wl    = (row.get("workloads_raw")            or "").lower()
    mc    = (row.get("meddpicc_primary_competitor") or "").lower()
    comp  = (row.get("competitors_raw")          or "").lower()
    all_t = se + " " + ae + " " + pain + " " + metr + " " + uc_d + " " + uc_ns + " " + wl + " " + mc + " " + comp

    has_mig    = is_legacy or any(mt in all_t for mt in MIGRATION_TERMS) or any(mi in all_t for mi in MIGRATION_INTENT)
    has_ai     = any(k in all_t for k in ["cortex","llm","machine learn","artificial intel","generative","ai model","ml model","forecasting","sentiment","classification","snowflake intelligence"])
    has_ml_mig = any(k in all_t for k in ["sagemaker","mlflow","databricks ml","ml pipeline","ml platform","sklearn","pytorch","tensorflow","xgboost"])
    has_de     = any(k in all_t for k in ["data engineer","data pipeline","etl","ingestion","transform","dbt","stored proc","architecture","medallion","data lake","openflow","bronze"])
    has_app    = any(k in all_t for k in ["native app","managed app","nativeapp","chatbot","user portal","employee portal","customer portal","web app","streamlit","application layer","front end","frontend"])
    has_sec    = any(k in all_t for k in ["security","compliance","governance","hipaa","soc2","pci","masking","encryption","access control","rbac","regulatory","audit","gdpr"])
    has_share  = any(k in all_t for k in ["data shar","datashare","marketplace","data product","data listing","clean room","data collaboration"])
    has_bi     = any(k in all_t for k in ["analytic","business intel"," bi ","reporting","dashboard","self-service","visualization"])
    has_cost   = any(k in all_t for k in ["cost","vendor","consolidat","savings","reduce spend","tco","infrastructure","maintenance","sprawl","rationali"])

    dw_label = dw_name or "current data warehouse"
    outcomes = []

    def _ev(keywords, fallback):
        s = _note_snippet(row, keywords)
        return s if s else fallback

    if has_mig:
        ev = _ev(["migrat","replac","moderniz","legacy","consolidat",dw_label],
                 f"Moving off {dw_label} to modernize the data platform." if dw_name
                 else "Migration intent detected — consolidating workloads onto a modern cloud data platform.")
        outcomes.append(("Data Migration & Modernization","#a78bfa",ev))

    if has_ml_mig:
        ev = _ev(["sagemaker","mlflow","databricks","ml pipeline","ml platform","sklearn","pytorch","tensorflow"],
                 "ML platform consolidation — move models from external tools to run where the data lives.")
        outcomes.append(("AI & ML Capabilities","#c084fc",ev))
    elif has_ai:
        ev = _ev(["llm","cortex","ai","ml","model","chatbot","generative","intelligence","forecast","sentiment"],
                 "AI/ML workloads identified — Cortex-powered models or LLM workflows without data egress.")
        outcomes.append(("AI & ML Capabilities","#c084fc",ev))

    if has_de:
        ev = _ev(["pipeline","etl","ingestion","transform","dbt","medallion","data lake","engineer"],
                 "Data engineering modernization — replace complex ETL/pipeline infrastructure with scalable governed data flows.")
        outcomes.append(("Data Engineering & Pipelines","#22d3ee",ev))

    if has_app:
        ev = _ev(["native app","chatbot","portal","streamlit","web app","application","frontend"],
                 "Build customer- or employee-facing applications powered directly by Snowflake data.")
        outcomes.append(("Application Development","#fb923c",ev))

    if has_share:
        ev = _ev(["shar","marketplace","data product","clean room","collaboration"],
                 "Data sharing and monetization — distribute data products to partners or customers.")
        outcomes.append(("Data Collaboration","#4ade80",ev))

    if has_sec and not has_mig:
        ev = _ev(["security","compliance","governance","masking","hipaa","gdpr","audit","rbac"],
                 "Compliance and governance requirements — data masking, access control, and regulatory audit readiness.")
        outcomes.append(("Governance & Security","#f59e0b",ev))

    if has_bi:
        ev = _ev(["analytic","bi ","reporting","dashboard","self-service","visualization"],
                 "Analytics acceleration — faster self-service BI and reporting across business teams.")
        outcomes.append(("Analytics & BI Acceleration","#38bdf8",ev))

    if has_cost and len(outcomes) < 2:
        ev = _ev(["cost","consolidat","savings","tco","vendor","sprawl","reduce spend"],
                 "Platform consolidation — reduce infrastructure cost and vendor sprawl by centralizing on Snowflake.")
        outcomes.append(("Cost & Platform Consolidation","#f97316",ev))

    if not outcomes:
        outcomes.append(("Analytics & BI Acceleration","#38bdf8",
            "No specific signals yet — recommend a Customer Journey Workshop to uncover and prioritize outcomes."))
    if len(outcomes) < 2:
        ev = _ev(["cost","consolidat","savings","vendor"],
                 "Consolidation opportunity — centralize workloads on Snowflake to reduce complexity and cost.")
        outcomes.append(("Cost & Platform Consolidation","#f97316",ev))

    return outcomes[:4], (has_app or has_ai or has_de or any(k in all_t for k in _BESPOKE_SIGNALS))

def get_es_info(a):
    notes  = " ".join(filter(None,[
        a.get("se_comments"),a.get("ae_notes"),a.get("meddpicc_pain"),
        a.get("meddpicc_metrics"),a.get("uc_descriptions"),a.get("uc_next_steps"),
    ])).lower()
    wl_raw = (a.get("workloads_raw") or "").lower()
    mc_raw = (a.get("meddpicc_primary_competitor") or "").lower()
    full_text = notes + " " + wl_raw + " " + mc_raw

    domain = _classify_domain(full_text, wl_raw)
    bespoke_hits = sum(1 for s in _BESPOKE_SIGNALS if s in full_text)
    not_es_hits  = [s for s in _NOT_ES_SIGNALS if s in full_text]
    sd_only_hits = [s for s in _SD_ONLY_SIGNALS if s in full_text]
    de_simple    = [s for s in _DE_SIMPLE_SIGNALS if s in full_text]
    beyond_hits  = sum(1 for s in _BEYOND_CORE_SIGNALS if s in full_text)

    chips = []
    if domain == "Apps":
        chips.append("Apps")
    elif domain == "AI/ML":
        chips.append("AI / ML")
    elif domain == "DE":
        if not de_simple and not (sd_only_hits and beyond_hits == 0):
            chips.append("DE")

    if bespoke_hits >= 1 and not not_es_hits and not chips:
        chips.append("Bespoke")
    elif bespoke_hits >= 1 and not not_es_hits:
        chips.append("Bespoke")

    if not chips:
        return False, "No qualifying ES signals"
    return True, ", ".join(chips)

def parse_outcomes_llm(raw):
    if not raw: return None
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if not match: return None
    try:
        items = _json.loads(match.group())
        if not isinstance(items, list): return None
        result = []
        for item in items[:4]:
            bucket   = (item.get("bucket") or "").strip()
            evidence = (item.get("evidence") or "").strip()
            if bucket and evidence and evidence.lower() not in ("none","n/a","not applicable","not mentioned","unknown","null"):
                result.append((bucket, OUTCOME_COLORS.get(bucket,"#64748b"), evidence))
        return result if len(result) >= 2 else None
    except Exception:
        return None

@st.cache_data(ttl=43200, show_spinner=False)
def _batch_load_llm(cache_keys: tuple) -> dict:
    if not cache_keys: return {}
    keys_sql = ", ".join(f"'{k}'" for k in cache_keys)
    try:
        conn = st.connection("snowflake")
        df = conn.query(
            f"SELECT cache_key, result FROM TEMP.PPACHENCE.PS_LLM_CACHE WHERE cache_key IN ({keys_sql})",
            ttl=0)
        return {row["CACHE_KEY"]: row["RESULT"] for _, row in df.iterrows()}
    except Exception:
        return {}

def _compute_one(rank, a, llm_results=None):
    opp_id  = a.get("opportunity_id") or f"rank_{rank}"
    dw_name, is_legacy = detect_dw(a)
    _ck = hashlib.md5(f"v2|{a.get('account_name','')}|{a.get('se_comments','')}|{a.get('ae_notes','')}|{a.get('meddpicc_pain','')}|{a.get('workloads_raw','')}".encode()).hexdigest()
    raw = (llm_results or {}).get(_ck)
    parsed = parse_outcomes_llm(raw)
    if parsed:
        all_t = " ".join(filter(None,[
            a.get("se_comments"),a.get("ae_notes"),
            a.get("meddpicc_pain"),a.get("meddpicc_metrics"),a.get("workloads_raw"),
        ])).lower()
        has_app = any(k in all_t for k in ["native app","managed app","nativeapp"])
        has_ai  = any(k in all_t for k in ["cortex","llm","machine learn","artificial intel","generative"])
        has_de_dom = any(k in all_t for k in ["data engineer","etl","ingestion","transform","dbt","openflow","snowpark","pipeline","iceberg","dynamic table"])
        has_es  = has_app or has_ai or has_de_dom or any(k in all_t for k in _BESPOKE_SIGNALS)
        return opp_id, (parsed, has_es)
    else:
        return opp_id, detect_outcomes_rule_based(a, dw_name, is_legacy)

def _dedup_rows(rows):
    seen = {}
    for r in rows:
        k = (r.get("fq_label",""), r.get("region",""), r.get("account_name",""))
        if k not in seen or safe_float(r.get("opportunity_acv"),0) > safe_float(seen[k].get("opportunity_acv"),0):
            seen[k] = r
    return list(seen.values())

def _load_all_data():
    try:
        conn = st.connection("snowflake")
        df = conn.query("""
WITH opps AS (
  SELECT
    CASE o.theater
      WHEN 'AMSAcquisition' THEN 'Acquisitions'
      WHEN 'AMSExpansion'   THEN 'Expansions'
      ELSE o.theater
    END AS theater,
    CASE
      WHEN o.theater = 'AMSExpansion' AND o.region = 'Commercial' THEN 'CommercialExp'
      ELSE o.region
    END AS region,
    'F' || o.fiscal_quarter || ' FY' || RIGHT(o.fiscal_year::VARCHAR, 2) AS fq_label,
    o.district, o.account_name, o.close_date::DATE AS close_date,
    COALESCE(o.forecast_acv, 0)  AS opportunity_acv,
    o.stage_name, o.opportunity_id,
    COALESCE(o.ps_forecast, 0)   AS ps_forecast_raw,
    o.agreement_type,
    COALESCE(o.opportunity_owner_name, '') AS ae_name,
    COALESCE(o.spn_partner, '')            AS spn_partner,
    COALESCE(o.meddpicc_primary_competitor, '') AS meddpicc_primary_competitor,
    COALESCE(o.meddpicc_identify_pain, '')      AS opp_meddpicc_pain,
    COALESCE(o.meddpicc_metrics, '')            AS opp_meddpicc_metrics,
    COALESCE(o.meddpicc_decision_criteria, '')  AS opp_meddpicc_dc,
    COALESCE(o.meddpicc_champion, '')           AS opp_meddpicc_champion,
    COALESCE(o.meddpicc_primary_value_driver, '') AS opp_value_driver,
    COALESCE(o.se_comments, '')            AS se_comments,
    COALESCE(o.next_steps, '')             AS ae_notes,
    COALESCE(o.country, '')                AS country
  FROM SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW o
  WHERE o.theater IN ('AMSAcquisition', 'AMSExpansion', 'USMajors')
    AND o.stage_name IN (
      'Discovery', 'SDR Qualified: SQL', 'Sales Qualified Opportunity',
      'Scope / Use Case', 'Technical / Business Impact Validation'
    )
    AND COALESCE(o.forecast_acv, 0) > 49000
    AND o.close_date BETWEEN CURRENT_DATE AND DATEADD(day, 90, CURRENT_DATE)
    AND o.ds >= DATEADD(day, -7, CURRENT_DATE)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY o.opportunity_id ORDER BY o.ds DESC) = 1
),
se_data AS (
  SELECT opportunity_id, MAX(use_case_lead_se_name) AS se_name
  FROM SALES.RAVEN.SDA_SE_HERO_ACTIVITIES_VIEW
  GROUP BY opportunity_id
),
spn_records AS (
  SELECT
    opportunity_id,
    MAX(has_funding_req)                                         AS has_funding_request,
    LISTAGG(CASE WHEN is_si_partner = 1 THEN partner_name END, ', ')
      WITHIN GROUP (ORDER BY partner_name)                       AS spn_obj_partner_names
  FROM (
    SELECT DISTINCT
      p.PARTNER_INFLUENCE_OPPORTUNITY_ID_C AS opportunity_id,
      CASE WHEN p.RECORD_TYPE_NAME_C = 'Funding Request' THEN 1 ELSE 0 END AS has_funding_req,
      COALESCE(a.ACCOUNT_NAME, '')         AS partner_name,
      CASE WHEN pv.PARTNER_NAME IS NOT NULL THEN 1 ELSE 0 END              AS is_si_partner
    FROM SALES.PARTNER_BASIC.PARTNER p
    LEFT JOIN SALES.PARTNER_BASIC.ACCOUNT a ON p.PARTNER_C = a.ACCOUNT_ID
    LEFT JOIN (
      SELECT DISTINCT OPPORTUNITY_ID, PARTNER_NAME
      FROM SALES.RAVEN.SDA_OPPORTUNITY_W_PARTNER_SPLIT_VIEW
      WHERE (PARTNER_SUBTYPE LIKE '%Global SI%' OR PARTNER_SUBTYPE LIKE '%Regional SI%')
    ) pv ON pv.OPPORTUNITY_ID = p.PARTNER_INFLUENCE_OPPORTUNITY_ID_C
         AND pv.PARTNER_NAME  = COALESCE(a.ACCOUNT_NAME, '')
    WHERE p.IS_DELETED = FALSE
      AND p.PARTNER_INFLUENCE_OPPORTUNITY_ID_C IN (SELECT opportunity_id FROM opps)
      AND (
        (p.RECORD_TYPE_NAME_C = 'Funding Request'    AND p.STATUS_C IN ('Approved','Claim Submitted','Under Review','Pending'))
        OR (p.RECORD_TYPE_NAME_C = 'Partner Engagement' AND p.STATUS_C IN ('Engaged','Pending'))
        OR (p.RECORD_TYPE_NAME_C = 'Channel Partner')
      )
  ) _spn
  GROUP BY opportunity_id
),
uc_data AS (
  SELECT
    opportunity_id, COUNT(*) AS uc_count,
    LISTAGG(workloads,   ', ') WITHIN GROUP (ORDER BY workloads)   AS workloads_raw,
    LISTAGG(competitors, ', ') WITHIN GROUP (ORDER BY competitors) AS competitors_raw,
    MAX(CASE WHEN is_ps_engaged THEN 1 ELSE 0 END)                AS is_ps_engaged,
    MAX(COALESCE(use_case_comments, ''))                          AS se_notes,
    LISTAGG(COALESCE(use_case_description, ''), ' | ')
      WITHIN GROUP (ORDER BY created_date)                        AS uc_descriptions,
    MAX(COALESCE(meddpicc_identify_pain, ''))                     AS uc_meddpicc_pain,
    MAX(COALESCE(meddpicc_metrics,       ''))                     AS uc_meddpicc_metrics,
    LISTAGG(COALESCE(next_steps, ''), ' | ')
      WITHIN GROUP (ORDER BY created_date)                        AS uc_next_steps
  FROM SALES.RAVEN.SDA_USE_CASE_VIEW
  GROUP BY opportunity_id
),
si_partners AS (
  SELECT
    opportunity_id,
    LISTAGG(partner_name, ', ') WITHIN GROUP (ORDER BY partner_name) AS si_partner_names
  FROM SALES.RAVEN.SDA_OPPORTUNITY_W_PARTNER_SPLIT_VIEW
  WHERE (partner_subtype LIKE '%Global SI%' OR partner_subtype LIKE '%Regional SI%')
    AND opportunity_id IN (SELECT opportunity_id FROM opps)
  GROUP BY opportunity_id
),
deal_regs AS (
  SELECT
    opportunity_id,
    MAX(1)                                                           AS has_deal_reg,
    LISTAGG(partner_name, ', ') WITHIN GROUP (ORDER BY partner_name) AS dr_partner_names
  FROM SALES.RAVEN.SDA_DEAL_REGISTRATION_VIEW
  WHERE opportunity_id IN (SELECT opportunity_id FROM opps)
    AND LOWER(deal_reg_status) NOT LIKE '%reject%'
  GROUP BY opportunity_id
),
ps_overrides AS (
  SELECT opportunity_id, MAX(ps_acv_override_usd) AS ps_acv_override
  FROM SALES.RAVEN.SDA_OPPORTUNITY_PS_VIEW
  WHERE opportunity_id IN (SELECT opportunity_id FROM opps)
  GROUP BY opportunity_id
)
SELECT
  o.theater, o.fq_label, o.region, o.district, o.account_name,
  TO_CHAR(o.close_date)                                                    AS close_date,
  o.opportunity_acv, o.stage_name, o.opportunity_id,
  COALESCE(NULLIF(po.ps_acv_override, 0), o.ps_forecast_raw, 0)           AS ps_acv,
  o.ae_name,
  COALESCE(s.se_name,        '')  AS se_name,
  COALESCE(u.workloads_raw,  '')  AS workloads_raw,
  COALESCE(u.competitors_raw,'')  AS competitors_raw,
  COALESCE(u.uc_count,       0)   AS uc_count,
  COALESCE(u.is_ps_engaged,  0)   AS is_ps_engaged,
  COALESCE(o.agreement_type, '')  AS agreement_type,
  o.spn_partner, o.meddpicc_primary_competitor,
  COALESCE(u.uc_meddpicc_pain,    o.opp_meddpicc_pain,    '') AS meddpicc_pain,
  COALESCE(u.uc_meddpicc_metrics, o.opp_meddpicc_metrics, '') AS meddpicc_metrics,
  o.opp_meddpicc_dc        AS meddpicc_dc,
  o.opp_meddpicc_champion  AS meddpicc_champion,
  o.opp_value_driver       AS meddpicc_value_driver,
  COALESCE(u.uc_descriptions, '') AS uc_descriptions,
  COALESCE(u.uc_next_steps,   '') AS uc_next_steps,
  COALESCE(u.se_notes, o.se_comments, '') AS se_comments,
  o.ae_notes, o.country,
  COALESCE(sp.si_partner_names,       '')  AS si_partner_names,
  COALESCE(dr.has_deal_reg,           0)   AS has_deal_reg,
  COALESCE(dr.dr_partner_names,       '')  AS dr_partner_names,
  COALESCE(sr.has_funding_request,    0)   AS has_funding_request,
  COALESCE(sr.spn_obj_partner_names,  '')  AS spn_obj_partner_names
FROM opps o
LEFT JOIN se_data    s  ON o.opportunity_id = s.opportunity_id
LEFT JOIN uc_data    u  ON o.opportunity_id = u.opportunity_id
LEFT JOIN si_partners sp ON o.opportunity_id = sp.opportunity_id
LEFT JOIN deal_regs  dr  ON o.opportunity_id = dr.opportunity_id
LEFT JOIN spn_records sr ON o.opportunity_id = sr.opportunity_id
LEFT JOIN ps_overrides po ON o.opportunity_id = po.opportunity_id
""", ttl=0)
        return _dedup_rows(df.rename(columns=str.upper).to_dict("records"))
    except Exception as e:
        st.error(str(e))
        st.stop()
        return []

def _has_linked_partner(a):
    if (a.get("spn_partner") or "").strip():            return True
    if (a.get("si_partner_names") or "").strip():       return True
    if safe_int(a.get("has_deal_reg"), 0):              return True
    if (a.get("spn_obj_partner_names") or "").strip():  return True
    if safe_int(a.get("has_funding_request"), 0):       return True
    return False

CARD_CSS = """
<style>
.acct-card{background:var(--score-bg,#0e1629);border:1.5px solid var(--score-border,#1e293b);border-radius:14px;margin-bottom:18px;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
.card-header{display:flex;align-items:flex-start;gap:16px;padding:16px 20px 12px;border-bottom:1px solid #1e293b;background:var(--score-bg,#0e1629)}
.rank-badge{flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#1e2a4a;border:2px solid #6366f1;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#a5b4fc;margin-top:2px}
.card-title-block{flex:1;min-width:0}
.card-acct-name{font-size:16px;font-weight:700;color:#f1f5f9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:6px}
.sf-acct-link{color:#f1f5f9 !important;text-decoration:none}
.sf-acct-link:hover{text-decoration:underline}
.card-meta-row{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.badge{display:inline-flex;align-items:center;padding:2px 8px;border-radius:100px;font-size:10px;font-weight:700;letter-spacing:.4px}
.badge-stage{background:#1e293b;color:#cbd5e1}
.badge-district{background:#1e293b;color:#94a3b8}
.badge-cloud{background:#1e293b;color:#38bdf8}
.badge-ai{background:#2d1a4a;color:#c084fc}
.badge-migration{background:#2d1111;color:#fca5a5}
.badge-uc{background:#1e3a5f;color:#93c5fd;border:1px solid #2d5a8e}
.badge-engaged{background:#064e3b;color:#6ee7b7}
.badge-partner-led{background:#1e1540;color:#a78bfa}
.badge-gap{background:#2d1111;color:#fca5a5}
.badge-es{background:#431407;color:#f97316;border:1px solid #7c2d12}
.badge-partner{background:#1e1540;color:#a78bfa}
.badge-nopartner{background:#14532d;color:#4ade80;border:1px solid #16a34a}
.badge-dr{background:#451a03;color:#fb923c;border:1px solid #7c2d12}
.card-acv{font-size:14px;font-weight:700;color:#f1f5f9}
.card-ae{font-size:13px;font-weight:500;color:#94a3b8;margin-left:4px}
.score-block{flex-shrink:0;display:flex;flex-direction:column;align-items:center;width:64px}
.score-ring{position:relative;width:56px;height:56px}
.score-bg-ring{fill:none;stroke:#1e293b;stroke-width:5;transform:rotate(-90deg);transform-origin:28px 28px}
.score-fg-ring{fill:none;stroke:var(--score-color,#6366f1);stroke-width:5;stroke-linecap:round;transform:rotate(-90deg);transform-origin:28px 28px;transition:stroke-dashoffset .4s}
.score-num{font-size:16px;font-weight:800;color:var(--score-color,#6366f1);line-height:1}
.score-max{font-size:9px;color:#94a3b8}
.card-body{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-bottom:1px solid #1e293b}
.card-col{padding:14px 16px;border-right:1px solid #1e293b}
.card-col:last-child{border-right:none}
.card-col h4{margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8}
.signal-list{display:flex;flex-direction:column;gap:5px}
.signal-item{display:flex;gap:6px;font-size:11px;color:#cbd5e1;line-height:1.4}
.signal-item.highlight{color:#f1f5f9}
.signal-dot{width:5px;height:5px;border-radius:50%;background:#94a3b8;flex-shrink:0;margin-top:4px}
.uc-grid{display:flex;flex-wrap:wrap;gap:4px}
.callout{background:#080d1a;border:1px solid #1e293b;border-radius:6px;padding:7px 10px;font-size:11px;color:#cbd5e1;line-height:1.4;margin-top:6px}
.dim-bars{display:flex;flex-direction:column;gap:5px}
.dim-row{display:flex;align-items:center;gap:6px}
.dim-lbl{font-size:10px;color:#94a3b8;width:120px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dim-bar{flex:1;height:4px;background:#1e293b;border-radius:2px;overflow:hidden}
.dim-fill{height:100%;border-radius:2px}
.dim-d1{background:#7c3aed}.dim-d2{background:#0891b2}.dim-d4{background:#d97706}.dim-d5{background:#059669}
.dim-val{font-size:10px;color:#cbd5e1;width:16px;text-align:right;flex-shrink:0}
.ramp-block{background:#080d1a;border:1px solid #1e293b;border-radius:8px;padding:10px 12px}
.ramp-label{font-size:10px;color:#94a3b8;font-weight:700;letter-spacing:.6px;text-transform:uppercase;margin-bottom:6px}
.ramp-bar{height:5px;background:#1e293b;border-radius:3px;overflow:hidden;margin-bottom:5px}
.ramp-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px}
.ramp-zero{font-size:11px;color:#f97316;font-weight:700}
.ramp-pct{font-size:11px;color:#cbd5e1}
.people-row{display:flex;flex-direction:column;gap:3px}
.person-item{font-size:11px;color:#cbd5e1}
.person-item strong{color:#f1f5f9}
.sf-link{display:inline-flex;align-items:center;gap:4px;font-size:11px;color:#38bdf8;text-decoration:none;padding:3px 8px;border:1px solid #1e4060;border-radius:5px;margin-top:4px}
.sf-link:hover{background:#0c2233}
.rec-section{padding:14px 16px 16px}
.rec-header{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.rec-title{font-size:10px;font-weight:700;letter-spacing:1.2px;color:#94a3b8;text-transform:uppercase}
.es-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:6px;font-size:10px;font-weight:800;letter-spacing:.5px;background:linear-gradient(135deg,#f97316,#eab308);color:#1a0800;box-shadow:0 0 12px rgba(249,115,22,.5)}
.rec-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.rec-item{background:#080d1a;border:1px solid #1e293b;border-radius:8px;padding:10px 12px;border-top-width:2px;border-top-style:solid}
.rec-cat{display:block;font-size:9px;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:5px}
.rec-text{font-size:11px;color:#cbd5e1;line-height:1.55}
</style>
"""

def render_card(rank, a, outcomes, has_es, max_acv):
    sc, d1, d2, d3, d4, d5 = score(a, max_acv)
    ps_e       = safe_int(a.get("is_ps_engaged"), 0)
    ps_t       = safe_float(a.get("ps_acv"), 0)
    partner    = (a.get("spn_partner") or "").strip()
    si_partner = (a.get("si_partner_names") or "").strip()
    has_dr     = safe_int(a.get("has_deal_reg"), 0)
    dr_partner = (a.get("dr_partner_names") or "").strip()
    spn_obj_p  = (a.get("spn_obj_partner_names") or "").strip()
    partner_display = partner or si_partner or dr_partner or spn_obj_p
    col, bg, bdr = scolor(sc, ps_e, partner_display)
    acv_f   = fmt_acv(a.get("opportunity_acv"))
    cloud   = get_cloud(a.get("agreement_type",""))
    ae      = esc(a.get("ae_name") or "")
    se      = esc(a.get("se_name") or "")
    dist    = esc(a.get("district") or "")
    stage   = a.get("stage_name") or ""
    stage_s = STAGE_SHORT.get(stage, stage[:10])
    cdate   = str(a.get("close_date") or "")[:10]
    mc      = esc(a.get("meddpicc_primary_competitor") or "")
    notes_raw    = a.get("se_comments") or ""
    ae_notes_raw = a.get("ae_notes") or ""
    pain_raw     = a.get("meddpicc_pain") or ""
    metrics_raw  = a.get("meddpicc_metrics") or ""
    wls     = parse_wl(a.get("workloads_raw",""))
    comps   = list({c for c in (parse_comp(a.get("competitors_raw","")) + ([mc] if mc else [])) if c})[:3]
    dw_name, is_legacy = detect_dw(a)
    ramp_pct = min(100, round(ps_t / max(safe_float(a.get("opportunity_acv"),1),1) * 100))

    def _latest_note(raw, max_chars=220):
        if not raw: return ""
        first = raw.strip().split("\n")[0].strip()
        return esc(first[:max_chars] + ("\u2026" if len(first) > max_chars else ""))

    def _note_block(label, text, border_color):
        if not (text or "").strip(): return ""
        return (f'<div style="margin-bottom:8px">'
                f'<div style="font-size:9px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:#94a3b8;margin-bottom:3px">{label}</div>'
                f'<div style="font-size:11px;color:#e2e8f0;line-height:1.5;background:#0d1829;border-left:2px solid {border_color};padding:5px 9px;border-radius:0 4px 4px 0">{_latest_note(text)}</div>'
                f'</div>')

    pain_h    = _note_block("Identified Pain",  pain_raw,     "#ef4444")
    metrics_h = _note_block("Success Metrics",  metrics_raw,  "#f59e0b")
    ae_note_h = _note_block("AE Next Steps",    ae_notes_raw, "#3b82f6")
    se_note_h = _note_block("SE / UC Comments", notes_raw,    "#6366f1")

    other_sigs = []
    if mc:
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot"></span><span>Competitor: <strong>{mc}</strong></span></div>')
    if dw_name:
        dw_label = f'Legacy DW: <strong>{esc(dw_name)}</strong>' if is_legacy else f'Current DW: <strong>{esc(dw_name)}</strong>'
        other_sigs.append(f'<div class="{"signal-item highlight" if is_legacy else "signal-item"}"><span class="signal-dot"></span><span>{dw_label}</span></div>')
    if partner:
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot"></span><span>Partner (SF): <strong>{esc(partner)}</strong></span></div>')
    spn_obj = (a.get("spn_obj_partner_names") or "").strip()
    if si_partner and si_partner != partner:
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot" style="background:#a78bfa"></span><span>SI Partner: <strong>{esc(si_partner[:60])}</strong></span></div>')
    if spn_obj and spn_obj not in (partner + si_partner):
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot" style="background:#a78bfa"></span><span>Partner: <strong>{esc(spn_obj[:60])}</strong></span></div>')
    if has_dr:
        dr_label = f"Deal Reg: {esc(dr_partner[:50])}" if dr_partner else "Deal Registration on file"
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot" style="background:#f59e0b"></span><span>{dr_label}</span></div>')
    if len(wls) >= 3:
        other_sigs.append(f'<div class="signal-item"><span class="signal-dot"></span><span>{len(wls)} workloads identified</span></div>')
    other_sigs_h = "\n".join(other_sigs)

    wl_h = wl_badges(wls)
    if comps:
        wl_h += "".join(f'<span class="badge badge-migration">{esc(c)}</span>' for c in comps)

    close_lbl = f"{cdate} · {cloud} · {dist}" if cloud else f"{cdate} · {dist}"
    sigs_h = ae_note_h + se_note_h + (f'<div class="signal-list" style="margin-top:2px">{other_sigs_h}</div>' if other_sigs_h else "")

    callout = ""
    if wls: callout += f"Workloads: {esc(', '.join(wls[:5]))}."
    if comps: callout += f" Competing vs: {esc(', '.join(comps[:3]))}."
    if not callout: callout = "No workload or competitor data available."

    ps_badge  = ('<span class="badge badge-engaged">ENGAGED</span>' if ps_e
                 else (f'<span class="badge badge-partner-led">Partner Led</span>' if partner_display else ''))
    stage_b   = f'<span class="badge badge-stage">{esc(stage_s)}</span>'
    cloud_b   = f'<span class="badge badge-cloud">{cloud}</span>' if cloud else ""
    has_fr    = safe_int(a.get("has_funding_request"),0)
    part_b    = (f'<span class="badge badge-partner">{esc(partner_display[:30])}</span>'
                 if partner_display
                 else ('<span class="badge badge-dr">Deal Reg</span>' if has_dr
                       else '<span class="badge badge-nopartner">No Partner</span>'))
    _es_flag, _es_sigs = get_es_info(a)

    d1p = round(d1/35*100); d2p = round(d2/35*100)
    d4p = round(d4/15*100); d5p = round(d5/15*100)

    opp_id  = a.get("opportunity_id") or ""
    sf_url  = f"https://snowforce.lightning.force.com/lightning/r/Opportunity/{opp_id}/view"
    sf_link = f'<a class="sf-link" href="{sf_url}" target="_blank">&#x2197; Open in Salesforce</a>' if opp_id else ""

    outcome_items = ""
    for bucket, color, evidence in outcomes:
        outcome_items += (
            f'<div style="border-left:3px solid {color};padding:7px 10px;margin-bottom:7px;'
            f'background:#0d1220;border-radius:0 6px 6px 0">'
            f'<div style="color:{color};font-size:9px;font-weight:800;letter-spacing:.6px;'
            f'text-transform:uppercase;margin-bottom:3px">{esc(bucket)}</div>'
            f'<div style="font-size:11px;color:#cbd5e1;line-height:1.4">{esc(evidence)}</div>'
            f'</div>'
        )

    es_footer = ""
    if _es_flag:
        sig_colors = {"AI / ML":"#c084fc","Apps":"#fb923c","DE":"#22d3ee","Bespoke":"#fbbf24","Migration":"#fca5a5","General":"#94a3b8"}
        sig_chips = ""
        if _es_sigs:
            sig_chips = "".join(
                f'<span style="display:inline-block;padding:3px 10px;border-radius:100px;'
                f'font-size:10px;font-weight:700;letter-spacing:.4px;'
                f'background:{sig_colors.get(s,"#22d3ee")}25;'
                f'color:{sig_colors.get(s,"#22d3ee")};border:1px solid {sig_colors.get(s,"#22d3ee")}60;'
                f'margin-right:6px">{esc(s)}</span>'
                for s in _es_sigs.split(", ") if s
            )
        es_footer = (
            '<div style="padding:12px 20px;'
            'background:linear-gradient(90deg,#1a0a00,#1c1000,#0a1a0a);'
            'border-top:2px solid #f97316;'
            'display:flex;flex-wrap:wrap;gap:6px;align-items:center">'
            '<span style="font-size:14px;font-weight:900;color:#f97316;letter-spacing:.5px;'
            'text-transform:uppercase;margin-right:10px;'
            'text-shadow:0 0 12px rgba(249,115,22,.7)">&#x26A1; ENGINEERING SOLUTIONS CANDIDATE</span>'
            f'{sig_chips}</div>'
        )

    return f"""
<div class="acct-card" style="--score-color:{col};--score-bg:{bg};--score-border:{bdr}">
  <div class="card-header">
    <div class="rank-badge">#{rank}</div>
    <div class="card-title-block">
      <div class="card-acct-name">{'<a class="sf-acct-link" href="'+sf_url+'" target="_blank">'+esc(a.get('account_name',''))+'</a>' if opp_id else esc(a.get('account_name',''))}</div>
      <div class="card-meta-row">
        <span class="card-acv">{acv_f} ACV</span>
        {f'<span class="card-ae">· AE: {ae}</span>' if ae else ''}
        {stage_b}
        <span class="badge badge-district">{dist}</span>
        {cloud_b}{part_b}{ps_badge}
      </div>
    </div>
    <div class="score-block" style="--score-color:{col}">
      <div class="score-ring">
        <svg width="56" height="56" viewBox="0 0 56 56">
          <circle class="score-bg-ring" cx="28" cy="28" r="22" stroke-dasharray="138.2"/>
          <circle class="score-fg-ring" cx="28" cy="28" r="22" stroke-dasharray="138.2" stroke-dashoffset="{dashoff(sc)}"/>
        </svg>
      </div>
      <div style="text-align:center;margin-top:-42px">
        <div class="score-num">{sc}</div>
        <div class="score-max">/100</div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <div class="card-col">
      <h4>&#x1F3AF; Business Outcomes</h4>
      <div style="margin-top:6px">{outcome_items}</div>
    </div>
    <div class="card-col">
      <h4>Workloads &amp; Migration</h4>
      <div class="uc-grid" style="margin-bottom:10px">{wl_h}</div>
      <div class="callout">{esc(callout)}</div>
      <h4 style="margin-top:12px">Dimension Scoring</h4>
      <div class="dim-bars" style="margin-top:6px">
        <div class="dim-row"><span class="dim-lbl">Migration Complexity</span><div class="dim-bar"><div class="dim-fill dim-d1" style="width:{d1p}%"></div></div><span class="dim-val">{d1}</span></div>
        <div class="dim-row"><span class="dim-lbl">Use Case Breadth</span><div class="dim-bar"><div class="dim-fill dim-d2" style="width:{d2p}%"></div></div><span class="dim-val">{d2}</span></div>
        <div class="dim-row"><span class="dim-lbl">ACV Magnitude</span><div class="dim-bar"><div class="dim-fill dim-d4" style="width:{d4p}%"></div></div><span class="dim-val">{d4}</span></div>
        <div class="dim-row"><span class="dim-lbl">Field Signals</span><div class="dim-bar"><div class="dim-fill dim-d5" style="width:{d5p}%"></div></div><span class="dim-val">{d5}</span></div>
      </div>
    </div>
    <div class="card-col">
      <h4>DEAL NOTES</h4>
      <div style="margin-top:6px">{sigs_h}</div>
    </div>
  </div>
  {es_footer}
</div>
"""

# ── CSS ─────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.detail-header {
    background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin: 24px 0 14px 0;
    display: flex;
    align-items: center;
    box-shadow: 0 6px 24px rgba(41,181,232,0.30);
}
.detail-header-title { font-size: 4.4rem; font-weight: 800; color: white !important; margin: 0; letter-spacing: -0.02em; line-height: 1.15; }
.detail-header-sub { font-size: 0.92rem; color: rgba(255,255,255,0.78); margin: 5px 0 0; }
.debug-header {
    background: linear-gradient(135deg, #374151 0%, #6B7280 100%);
    border-radius: 16px;
    padding: 16px 32px;
    margin: 24px 0 14px 0;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 12px rgba(107,114,128,0.20);
}
.debug-header-title { font-size: 2.2rem; font-weight: 700; color: #e5e7eb !important; margin: 0; letter-spacing: -0.01em; line-height: 1.2; }
.debug-header-sub { font-size: 0.85rem; color: rgba(229,231,235,0.65); margin: 4px 0 0; }
</style>
""", unsafe_allow_html=True)

st.markdown(CARD_CSS, unsafe_allow_html=True)

# ── Page nav ────────────────────────────────────────────────────────────────────

render_nav_bar([
    ("Account Drill-Down", "nav-acct-drill"),
    ("Prioritized Account List", "nav-acct-list"),
])

# ── Load data ────────────────────────────────────────────────────────────────────

if "_ad_all" not in st.session_state:
    for _k in [_k for _k in st.session_state if _k.startswith("ad_recs_")]:
        del st.session_state[_k]
    st.session_state.pop("_ad_fstate", None)
    with st.spinner("Loading account data…"):
        st.session_state["_ad_all"] = _load_all_data()

_data = st.session_state["_ad_all"]

# ── ACCOUNT DRILL-DOWN ──────────────────────────────────────────────────────────

st.markdown("""
<div id="nav-acct-drill" class="detail-header">
  <div>
    <p class="detail-header-title">Account Drill-Down</p>
    <p class="detail-header-sub">Theater, region, and district controlled by the sidebar — filter further by AE and sort preference</p>
  </div>
</div>
""", unsafe_allow_html=True)

_sel_theater_f  = st.session_state.get("sf_theater", [])
_sel_region_f   = st.session_state.get("sf_region", [])
_sel_district_f = st.session_state.get("sf_district", [])

_fc1, _fc2 = st.columns([2, 2])
_ae_pool = [
    a for a in _data
    if (not _sel_theater_f  or a.get("theater") in _sel_theater_f)
    and (not _sel_region_f   or a.get("region")  in _sel_region_f)
    and (not _sel_district_f or a.get("district") in _sel_district_f)
]
_ae_names = sorted({a.get("ae_name","") or "" for a in _ae_pool if a.get("ae_name")})
with _fc1:
    _sel_ae = st.selectbox("Account Executive", ["All AEs"] + _ae_names, index=0, key="ad_sel_ae")
with _fc2:
    _sort_mode = st.radio("Sort By", ["Default Score","Product ACV"], horizontal=True, key="ad_sort_mode")

_filtered = [
    a for a in _data
    if (not _sel_theater_f  or a.get("theater") in _sel_theater_f)
    and (not _sel_region_f   or a.get("region")  in _sel_region_f)
    and (not _sel_district_f or a.get("district") in _sel_district_f)
    and (not _has_linked_partner(a))
    and (_sel_ae == "All AEs" or a.get("ae_name") == _sel_ae)
]
_max_acv = max((safe_float(a.get("opportunity_acv"),0) for a in _filtered), default=1.0) or 1.0
_scored  = sorted([(score(a,_max_acv)[0],a) for a in _filtered], key=lambda x: -x[0])
if _sort_mode == "Product ACV":
    _top15 = sorted([a for a in _filtered if safe_float(a.get("ps_acv"),0) == 0],
                    key=lambda a: -safe_float(a.get("opportunity_acv"),0))[:15]
else:
    _top15 = [a for _,a in _scored if safe_float(a.get("ps_acv"),0) == 0][:15]

if not _filtered:
    st.info("No accounts found for this selection.", icon=":material/inbox:")
else:
    st.caption(f"Showing top {len(_top15)} of **{len(_filtered)}** accounts · sorted by {'Product ACV' if _sort_mode == 'Product ACV' else 'SD Targeting Score'}")

    _ad_fstate = (tuple(_sel_theater_f), tuple(_sel_region_f), tuple(_sel_district_f), _sel_ae, _sort_mode)
    if _ad_fstate != st.session_state.get("_ad_fstate"):
        for _k in [_k for _k in st.session_state if _k.startswith("ad_recs_")]:
            del st.session_state[_k]
        st.session_state["_ad_fstate"] = _ad_fstate

    _needs = [
        (rank, a) for rank, a in enumerate(_top15, 1)
        if f"ad_recs_{a.get('opportunity_id') or f'rank_{rank}'}" not in st.session_state
    ]
    if _needs:
        _ck_list = tuple(
            hashlib.md5(f"v2|{a.get('account_name','')}|{a.get('se_comments','')}|{a.get('ae_notes','')}|{a.get('meddpicc_pain','')}|{a.get('workloads_raw','')}".encode()).hexdigest()
            for _, a in _needs
        )
        _batch = _batch_load_llm(_ck_list)
        with st.spinner(f"Analyzing {len(_needs)} account{'s' if len(_needs) != 1 else ''}…"):
            for _rank, _a in _needs:
                _oid, _res = _compute_one(_rank, _a, llm_results=_batch)
                st.session_state[f"ad_recs_{_oid}"] = _res

    _cards_html = []
    for _rank, _a in enumerate(_top15, 1):
        _opp_id  = _a.get("opportunity_id") or f"rank_{_rank}"
        _rec_key = f"ad_recs_{_opp_id}"
        if _rec_key not in st.session_state:
            _dw_name, _is_legacy = detect_dw(_a)
            st.session_state[_rec_key] = detect_outcomes_rule_based(_a, _dw_name, _is_legacy)
        _outcomes, _has_es = st.session_state[_rec_key]
        _cards_html.append(render_card(_rank, _a, _outcomes, _has_es, _max_acv))
    st.markdown("".join(_cards_html), unsafe_allow_html=True)

# ── PRIORITIZED ACCOUNT LIST ────────────────────────────────────────────────────

st.markdown("""
<div id="nav-acct-list" class="detail-header">
  <div>
    <p class="detail-header-title">Prioritized Account List</p>
    <p class="detail-header-sub">Top accounts ranked by SD Targeting Score</p>
  </div>
</div>
""", unsafe_allow_html=True)

_count_sel = st.radio("Count", ["Top 10","Top 25","Top 50"], index=0, horizontal=True, key="ad_list_count")
_count_n = int(_count_sel.split()[1])

import pandas as _pd
_list_max = max((safe_float(x.get("opportunity_acv"),0) for x in _data), default=1.0) or 1.0
_all_scored = []
for _a in _data:
    if (not _sel_theater_f  or _a.get("theater") in _sel_theater_f) \
    and (not _sel_region_f   or _a.get("region")  in _sel_region_f) \
    and (not _sel_district_f or _a.get("district") in _sel_district_f) \
    and not _has_linked_partner(_a) and safe_float(_a.get("ps_acv"),0) == 0:
        _sc = score(_a, _list_max)[0]
        _all_scored.append((_sc, _a))
_all_scored.sort(key=lambda x: -x[0])
_top_n = _all_scored[:_count_n]

_rows = []
for _rank, (_sc, _a) in enumerate(_top_n, 1):
    _opp_id = _a.get("opportunity_id") or ""
    _sf_url = f"https://snowforce.lightning.force.com/lightning/r/Opportunity/{_opp_id}/view" if _opp_id else ""
    _rows.append({
        "Rank":     _rank,
        "Account":  _a.get("account_name",""),
        "AE":       _a.get("ae_name",""),
        "Region":   _a.get("region",""),
        "District": _a.get("district",""),
        "Theater":  _a.get("theater",""),
        "Score":    _sc,
        "ACV":      fmt_acv(_a.get("opportunity_acv")),
        "Stage":    STAGE_SHORT.get(_a.get("stage_name",""), (_a.get("stage_name","") or "")[:12]),
        "SFDC":     _sf_url,
    })
_df = _pd.DataFrame(_rows)

with st.expander(f"Top {_count_n} accounts by SD Targeting Score", expanded=True):
    if _df.empty:
        st.info("No accounts found.")
    else:
        _tbl_rows = ""
        for _, _r in _df.iterrows():
            _link = f'<a href="{_r["SFDC"]}" target="_blank" style="color:#38bdf8;text-decoration:none">{esc(_r["Account"])} &#x2197;</a>' if _r["SFDC"] else esc(_r["Account"])
            _tbl_rows += (
                f'<tr>'
                f'<td style="padding:8px 12px;color:#94a3b8;font-weight:700;white-space:nowrap">{_r["Rank"]}</td>'
                f'<td style="padding:8px 12px;min-width:180px">{_link}</td>'
                f'<td style="padding:8px 12px;color:#94a3b8;white-space:nowrap">{esc(_r["AE"])}</td>'
                f'<td style="padding:8px 12px;color:#94a3b8;white-space:nowrap">{esc(_r["Region"])}</td>'
                f'<td style="padding:8px 12px;color:#94a3b8;white-space:nowrap">{esc(_r["District"])}</td>'
                f'<td style="padding:8px 12px;color:#94a3b8;white-space:nowrap">{esc(_r["Theater"])}</td>'
                f'<td style="padding:8px 12px;font-weight:800;color:#f1f5f9;white-space:nowrap">{_r["Score"]}</td>'
                f'<td style="padding:8px 12px;font-weight:700;color:#f1f5f9;white-space:nowrap">{_r["ACV"]}</td>'
                f'<td style="padding:8px 12px;color:#94a3b8;white-space:nowrap">{esc(_r["Stage"])}</td>'
                f'</tr>'
            )
        st.markdown(f"""
<div style="overflow-x:auto;border-radius:10px;border:1px solid #1e293b">
<table style="width:100%;border-collapse:collapse;background:#0e1629;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:12px">
<thead>
<tr style="background:#13213a;border-bottom:1px solid #1e293b">
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">#</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8">Account</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">AE</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">Region</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">District</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">Theater</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">Score</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">ACV</th>
  <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;white-space:nowrap">Stage</th>
</tr>
</thead>
<tbody style="color:#cbd5e1">{_tbl_rows}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── DEBUG ONLY (always rendered, no nav button) ─────────────────────────────────

st.markdown("""
<div class="debug-header">
  <div>
    <p class="debug-header-title">DEBUG ONLY</p>
    <p class="debug-header-sub">Batch process metadata — for engineering reference</p>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("Data Source Details", expanded=False):
    st.markdown(f"""
**Data source:** `SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW` (and related views) — queried directly, no intermediate table.

**Cache:** Session-state (`st.session_state["_ad_all"]`). Data is loaded once per browser session; refresh the page to force a reload.

**Query scope:** Theaters `Acquisitions` (AMSAcquisition), `Expansions` (AMSExpansion), and `USMajors` — opportunities with `close_date` within the next 90 days and ACV > $49K.

**Scoring is computed client-side** (not stored) on each page load using the `score()` function
across 4 dimensions: Migration Complexity (35 pts), Use Case Breadth (35 pts),
ACV Magnitude (15 pts), Field Signals (15 pts).

**LLM outcomes** (Business Outcomes section on each card) are cached in `TEMP.PPACHENCE.PS_LLM_CACHE`
keyed by an MD5 hash of the account name + SE/AE notes. If a cached result exists, it is used;
otherwise rule-based detection (`detect_outcomes_rule_based`) is applied as a fallback.

**Total accounts loaded:** `{len(_data):,}`
""")
