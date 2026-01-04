# Action Plan: DSS Alignment Improvements

## Overview

Based on the requirements review, here are recommended changes to strengthen alignment with the original DSS specification. Changes are categorized by priority and complexity.

---

## Priority 1: HIGH (Recommended - Implement First)

### **P1.1: Standardize Recommendation Output Format**

**Objective**: Make all recommendations follow the 4-part format from original spec

**What to Change**:
- Current format: Varies between services (different field names, structure)
- Target format: Standardized 4-part structure everywhere

**Files to Modify**:
1. `data/models.py` - Add DSSRecommendation dataclass
2. `services/decision_service.py` - Update all functions to use new format
3. `services/anomaly_service.py` - Update all functions to use new format
4. `ui/views.py` - Update display logic

**Implementation Steps**:

**Step 1**: Add to `data/models.py`:
```python
from dataclasses import dataclass

@dataclass
class DSSRecommendation:
    """Standard DSS recommendation output format."""
    what_happened: str           # Problem detected
    why_it_matters: str          # Financial consequence  
    what_to_do: str              # Specific action
    financial_impact: str        # Quantified: "Save $X" or "Reduce Y%"
    priority: str                # critical/high/medium/low
    category: str                # Affected category
    rule_name: str               # Rule that triggered (e.g., "OVERSPENDING")
    explanation: str             # Why this rule matters (educational)
```

**Step 2**: Update `services/anomaly_service.py`:
```python
# Example conversion for detect_overspending()
from data.models import DSSRecommendation

def detect_overspending() -> List[DSSRecommendation]:
    """Detect overspending with standardized output."""
    recommendations = []
    # ... existing logic ...
    
    rec = DSSRecommendation(
        what_happened=f"Food category overspent by ${overage:.2f}",
        why_it_matters=f"Exceeds monthly budget of $500 by {percentage:.1f}%",
        what_to_do=f"Reduce Food spending by {percentage:.1f}% (~${overage:.2f})",
        financial_impact=f"Save ${overage:.2f} this month, ${overage*12:.2f}/year if sustained",
        priority="critical",
        category="Food",
        rule_name="OVERSPENDING_DETECTION",
        explanation="Spending within budget is critical for financial health",
    )
    recommendations.append(rec)
    return recommendations
```

**Benefits**:
- ✅ Consistent format everywhere
- ✅ Matches original spec exactly
- ✅ Easier for UI to render
- ✅ Better for testing

**Effort**: Medium (2-3 hours)
**Impact**: High (Improves spec compliance significantly)

---

### **P1.2: Fix Fixed Cost Rule to Use Income-Based Threshold**

**Objective**: Make fixed cost rule align with original spec (60% of income, not 50% of spending)

**Current Implementation** (Wrong):
```python
# In anomaly_service.py
fixed_costs_total > 0.5 * (fixed_costs_total + variable_costs_total)
# This is: Fixed > 50% of total spending
```

**Target Implementation** (Correct):
```python
# Should be: Fixed > 60% of monthly income
fixed_costs_total > 0.6 * monthly_income
```

**Files to Modify**:
1. `services/anomaly_service.py` - Update `detect_fixed_cost_danger()`
2. `config.py` - Ensure MONTHLY_INCOME is accessible
3. `services/history_service.py` - May need to add get_monthly_income()

**Implementation Steps**:

**Step 1**: Update `config.py`:
```python
# Add/verify this exists:
MONTHLY_INCOME = 4000  # User configurable
FIXED_COST_INCOME_THRESHOLD = 0.6  # 60% of income
```

**Step 2**: Update `services/anomaly_service.py`:
```python
def detect_fixed_cost_danger() -> List[Dict]:
    """
    Detect if fixed costs are > 60% of monthly income.
    
    Original spec: "Fixed expenses > 60% of income"
    This indicates insufficient income flexibility.
    """
    monthly_income = (
        st.session_state.get("monthly_income", config.MONTHLY_INCOME)
        if HAS_STREAMLIT else config.MONTHLY_INCOME
    )
    
    if monthly_income <= 0:
        return []  # Can't evaluate without income
    
    # Get current month fixed costs
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")
    
    expenses = get_expenses_by_date_range(month_start, month_end)
    fixed_total = sum(exp.amount for exp in expenses if exp.type == "fixed")
    
    threshold = config.FIXED_COST_INCOME_THRESHOLD  # 0.6 = 60%
    
    if fixed_total > threshold * monthly_income:
        # Alert
        ratio = (fixed_total / monthly_income) * 100
        ...
```

**Step 3**: Update `ui/settings.py`:
```python
# Add monthly income configuration to Settings
# In the Currency & Display tab or new Financial tab

monthly_income = st.number_input(
    "Monthly Income",
    min_value=0.0,
    value=st.session_state.get("monthly_income", config.MONTHLY_INCOME),
    step=100.0,
    help="Your average monthly income (used for budget calculations)",
)
st.session_state.monthly_income = monthly_income
```

**Benefits**:
- ✅ Matches original DSS spec exactly
- ✅ More meaningful metric (relates to flexibility)
- ✅ Aligns with budget risk calculation (should also use income)

**Effort**: Medium (1-2 hours)
**Impact**: High (Core rule correction)

---

### **P1.3: Add Rule Evaluation Details for Transparency**

**Objective**: Show HOW each rule triggered, not just THAT it triggered

**What to Add**:
```python
"rule_evaluation": {
    "formula": "spent > budget × threshold",
    "values": {"spent": 650, "budget": 500, "threshold": 1.1},
    "trigger_value": 550,
    "actual_value": 650,
    "triggered": "650 > 550 (TRUE)",
}
```

**Files to Modify**:
1. `services/anomaly_service.py` - Add to all detection functions
2. `services/decision_service.py` - Add to all rule functions
3. `ui/views.py` or `ui/anomaly_view.py` - Display rule details

**Implementation Steps**:

**Step 1**: Update `services/anomaly_service.py` functions:
```python
def detect_overspending() -> List[Dict]:
    """..."""
    alert = {
        "type": "overspending",
        "category": category,
        # Existing fields...
        "what_happened": f"Food spending exceeded budget",
        "why_it_matters": f"${overage:.2f} unplanned expense",
        "what_to_do": f"Reduce Food by {percentage:.1f}%",
        "financial_impact": f"Save ${overage:.2f}",
        # NEW: Add rule evaluation
        "rule_evaluation": {
            "rule_name": "OVERSPENDING_DETECTION",
            "formula": "spent > budget × threshold",
            "threshold_percentage": 10,  # 10% over
            "values": {
                "category": category,
                "budget": budget,
                "spent": total,
                "threshold_multiplier": 1.1,
                "trigger_value": budget * 1.1,
                "actual_value": total,
                "exceeded_by": overage,
            },
            "check": f"{total:.2f} > {budget * 1.1:.2f} = TRUE",
        }
    }
```

**Step 2**: Add display in UI (`ui/anomaly_view.py`):
```python
# In anomaly alert display
with st.expander("🔍 See how this rule was triggered"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Rule Formula**")
        st.code(alert["rule_evaluation"]["formula"])
    
    with col2:
        st.write("**Values**")
        for key, val in alert["rule_evaluation"]["values"].items():
            st.write(f"- {key}: {val}")
    
    st.write(f"**Result**: {alert['rule_evaluation']['check']}")
```

**Benefits**:
- ✅ Full transparency ("white box" DSS)
- ✅ Users understand exactly why alert triggered
- ✅ Auditable decision logic
- ✅ Educational for users

**Effort**: Medium (1-2 hours)
**Impact**: High (Explainability improvement)

---

## Priority 2: MEDIUM (Recommended - Implement Second)

### **P2.1: Enforce Top Insights Limit (2-3)**

**Objective**: Implement "Only show top 2-3 insights" from original spec

**Files to Modify**:
1. `services/decision_service.py` or new `services/dss_service.py`
2. `ui/views.py` (Insights page)

**Implementation Steps**:

```python
# In services/decision_service.py or anomaly_service.py
MAX_INSIGHTS_TO_SHOW = 3

def get_dss_insights(limit: int = MAX_INSIGHTS_TO_SHOW) -> List[Dict]:
    """Get top DSS insights, limited to reduce information overload."""
    # Get all recommendations from all rules
    all_recommendations = []
    all_recommendations.extend(get_overspending_recommendations())
    all_recommendations.extend(get_spike_recommendations())
    # ... etc
    
    # Sort by priority, then impact
    all_recommendations.sort(
        key=lambda r: (
            priority_order.get(r["priority"], 999),
            -float(r["financial_impact_amount"])
        )
    )
    
    # Return only top N
    top_insights = all_recommendations[:limit]
    total_insights = len(all_recommendations)
    
    return {
        "insights": top_insights,
        "total_available": total_insights,
        "showing": len(top_insights),
    }

def get_all_dss_insights() -> List[Dict]:
    """Get ALL recommendations (for detailed view)."""
    # Return unfiltered list
```

**UI Update** (`ui/views.py`):
```python
def show_insights():
    """Display DSS insights - top 3 only."""
    insights_data = get_dss_insights(limit=3)
    
    st.subheader("💡 Top Insights & Recommendations")
    
    # Show top 3
    for idx, insight in enumerate(insights_data["insights"], 1):
        display_insight(insight)
    
    # Show "View All" if more available
    if insights_data["total_available"] > insights_data["showing"]:
        with st.expander(f"📋 View all {insights_data['total_available']} insights"):
            all_insights = get_all_dss_insights()
            for insight in all_insights[insights_data["showing"]:]:
                display_insight(insight)
```

**Benefits**:
- ✅ Matches original spec ("show top 2-3")
- ✅ Reduces information overload
- ✅ Focuses on critical issues
- ✅ Still allows access to all insights

**Effort**: Low (1 hour)
**Impact**: Medium (User experience improvement)

---

### **P2.2: Add Confidence Score to Rules**

**Objective**: Show confidence in each rule trigger (always 1.0 for rules, but good for future)

**Implementation**:
```python
def detect_overspending() -> List[Dict]:
    """..."""
    alert = {
        # ... existing fields ...
        "confidence": 1.0,  # Always 1.0 for rule-based (not ML)
        "confidence_reason": "Deterministic rule: budget × threshold comparison",
    }
```

**Benefits**:
- ✅ Prepares for future ML integration
- ✅ Makes rule-based nature explicit
- ✅ Shows this isn't probabilistic

**Effort**: Low (<1 hour)
**Impact**: Low-Medium

---

## Priority 3: LOW (Optional - Nice to Have)

### **P3.1: Create Unified DSS Engine** (Refactoring)

**Objective**: Consolidate DecisionService and AnomalyService into single DSSService

**Current**:
- `decision_service.py` - DSS rules, returns 3-5 recommendations
- `anomaly_service.py` - Anomaly detection, returns 5+ alerts

**Proposed**: Single unified service
- `services/dss_service.py` - All DSS logic in one place

**Note**: This is a refactoring, not a requirement change. Current architecture works fine. Only do if planning significant expansion.

**Effort**: High (3-4 hours of refactoring)
**Impact**: Medium (Code organization)

---

## Implementation Timeline

### **Recommended Order**:

```
Week 1:
  ✅ P1.1: Standardize recommendation format (3-4 hours)
  ✅ P1.2: Fix fixed cost rule (1-2 hours)
  ✅ P2.1: Enforce top insights limit (1 hour)

Week 2:
  ✅ P1.3: Add rule evaluation details (1-2 hours)
  ✅ P2.2: Add confidence scores (1 hour)

Optional (Week 3):
  ✅ P3.1: Unified DSS engine (if time permits)
```

**Total Effort**: 6-8 hours for all Priority 1-2 items
**Total Effort**: 9-12 hours including Priority 3

---

## Summary Table

| Priority | Item | Spec Alignment | User Impact | Effort | Recommendation |
|----------|------|---|---|---|---|
| P1.1 | Standardize format | ⬆️⬆️ High | Medium | Medium | **DO THIS** |
| P1.2 | Fix fixed cost rule | ⬆️⬆️ High | High | Medium | **DO THIS** |
| P1.3 | Add rule details | ⬆️⬆️ High | Medium | Medium | **DO THIS** |
| P2.1 | Top insights limit | ⬆️ Medium | High | Low | **DO THIS** |
| P2.2 | Confidence score | ⬆️ Medium | Low | Low | Consider |
| P3.1 | Unified engine | Same | None | High | Skip |

---

## Testing Plan

For each change:

1. **Unit Tests**: Verify rule logic unchanged
2. **Integration Tests**: Verify output format
3. **UI Tests**: Verify display works with new format
4. **User Tests**: Verify recommendations still make sense

**Test Files to Update**:
- `test_anomaly.py` - Update assertion for new format
- `test_settings.py` - Add monthly income test
- `test_model.py` - Add DSSRecommendation tests

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|-----------|
| Format standardization | Breaking UI | Update UI at same time |
| Fixed cost rule change | Different alerts | Document threshold change |
| Rule details | Performance | Test with 1000+ expenses |
| Top insights | User confusion | Add "View All" option |

---

## Conclusion

**Current Status**: ✅ Excellent alignment with original spec

**Recommended Actions**:
1. **HIGH PRIORITY**: Implement P1.1, P1.2, P1.3 (improves spec compliance)
2. **MEDIUM PRIORITY**: Implement P2.1, P2.2 (improves UX)
3. **OPTIONAL**: Skip P3.1 (not necessary)

**Timeline**: All Priority 1-2 items can be done in ~6-8 hours

**Result**: System will have **perfect alignment** with original DSS specification

---

**Generated**: January 3, 2026
**Status**: Ready for implementation planning
