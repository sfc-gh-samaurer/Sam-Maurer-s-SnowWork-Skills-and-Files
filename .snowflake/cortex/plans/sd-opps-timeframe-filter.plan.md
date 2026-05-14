# Plan: SD Opportunities Timeframe Filter

## Overview
Add independent **Fiscal Quarter quick-select + Custom Date Range** filters to both the **Pipeline** and **Historical** sections of the SD Opportunities tab, filtering on `CLOSE_DATE`.

## File to Modify
`streamlit-sd-dashboard-public-version/app_pages/sd_opportunities_tab.py`

## Design

### Filter UI (same pattern for both sections)
A new row above the existing filter columns containing:
1. **Fiscal Quarter selectbox** — options: `All`, `FQ1 FY26`, `FQ2 FY26`, ..., `FQ4 FY27` (rolling ~8 quarters centered around current). Default = current FQ.
2. **Date range picker** — two `st.date_input` fields (start/end) that appear only when "Custom Range" is selected from the FQ dropdown.

Layout: 3 columns — `[FQ Selectbox | Start Date | End Date]`  
When FQ is selected (not "All" or "Custom Range"), the date pickers are hidden/disabled.

### Filtering Logic
- **FQ selected**: Filter where `CLOSE_DATE` falls within that quarter's boundaries (using Snowflake fiscal calendar: Q1=Feb-Apr, Q2=May-Jul, Q3=Aug-Oct, Q4=Nov-Jan).
- **Custom Range**: Filter `CLOSE_DATE` between start and end dates.
- **All**: No date filtering applied.

### Fiscal Quarter Helper
```python
def _fiscal_quarters():
    """Return list of FQ labels + date boundaries for ~8 quarters around today."""
    # FY starts Feb 1. Generate quarters from ~2 quarters ago to ~6 ahead.
    # Returns: [("FQ1 FY26", date(2025,2,1), date(2025,4,30)), ...]
```

### Pipeline Section Changes
- Pipeline already has `FISCAL_QUARTER` column from SQL, but we'll filter on `CLOSE_DATE` directly for consistency with custom ranges.
- New filter row inserted at line 26 (before existing `fc1-fc5` columns).
- Filtering applied to `filtered_p` before the existing multiselect filters.

### Historical Section Changes  
- History has `CLOSE_DATE` but no `FISCAL_QUARTER` — filter directly on `CLOSE_DATE`.
- New filter row inserted at line 90 (before existing `hc1-hc5` columns).
- Default to "All" for historical (users typically want full history, then narrow down).

### KPI Impact
KPI strips already compute from `filtered_p` / `filtered_h`, so they'll automatically reflect the timeframe filter.

## Steps

1. **Add `_fiscal_quarters()` helper** at the top of `sd_opportunities_tab.py` — generates quarter options with date boundaries.
2. **Add timeframe filter row to Pipeline section** — FQ selectbox + conditional date range, apply to `filtered_p`.
3. **Add timeframe filter row to Historical section** — same pattern, apply to `filtered_h`. Default to "All".
4. **Verify KPI metrics** recalculate correctly with filtered data.
5. **Test locally** — run the app and verify both filters work.
