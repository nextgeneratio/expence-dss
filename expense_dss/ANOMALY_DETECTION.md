# Anomaly Detection System

## Overview

The Expense DSS includes a sophisticated anomaly detection system that identifies spending issues and provides actionable recommendations. The system detects 5 types of spending anomalies with configurable thresholds.

## Features

### 1. **Overspending Detection** 💰
- **What it detects**: Categories exceeding their monthly budget by a threshold percentage
- **Default threshold**: 1.1 (10% over budget)
- **Configurable**: Yes (1.0 - 2.0)
- **Action**: Recommends reducing category spending by the overage percentage

### 2. **Spending Spike Detection** ⚡
- **What it detects**: Sudden increases in spending month-over-month
- **Default threshold**: 0.3 (30% increase)
- **Configurable**: Yes (0.0 - 1.0)
- **Action**: Flags unusual spending patterns for investigation

### 3. **Budget Risk Detection** ⚠️
- **What it detects**: Categories approaching or exceeding their budget
- **Default threshold**: 0.75 (75% of budget)
- **Configurable**: Yes (0.5 - 1.0)
- **Action**: Provides early warning to prevent overspending

### 4. **Fixed Cost Danger Detection** 🔒
- **What it detects**: When fixed costs consume too much of total spending
- **Default threshold**: 0.5 (50% of spending)
- **Configurable**: Yes (0.2 - 0.8)
- **Action**: Recommends cost restructuring to improve spending flexibility

### 5. **Rising Trend Detection** 📈
- **What it detects**: Spending increasing over a 3-month period
- **Default threshold**: 0.15 (15% increase over 3 months)
- **Configurable**: Yes (0.0 - 0.5)
- **Action**: Early warning for preventive action

## How to Use

### Accessing Anomaly Detection

1. Open the Expense DSS application
2. Select **"Anomaly Detection"** from the sidebar navigation
3. View all detected anomalies organized by type in 6 tabs:
   - **All Recommendations**: Complete action plan prioritized by impact
   - **Overspending**: Categories exceeding budget
   - **Spikes**: Sudden spending increases
   - **Budget Risk**: Categories at risk of overspending
   - **Fixed Costs**: Analysis of fixed vs variable expenses
   - **Trends**: Rising spending patterns

### Configuring Thresholds

1. Go to **Settings** → **⚠️ Anomaly Detection** tab
2. Adjust sliders for each detection type:
   - Higher threshold = fewer alerts (less sensitive)
   - Lower threshold = more alerts (more sensitive)
3. Click **"💾 Save Anomaly Settings"** to save changes
4. Use **"🔄 Reset to Defaults"** to restore original thresholds

## Understanding Alerts

### Severity Levels

- 🔴 **CRITICAL**: Immediate action required
- 🟠 **HIGH**: Address within a week
- 🟡 **MEDIUM**: Monitor and plan action
- 🟢 **LOW**: Informational, no immediate action needed

### Recommendation Priorities

Recommendations are prioritized by:
1. **Impact**: How much the action will improve finances
2. **Effort**: How easy/difficult the action is to implement
3. **Urgency**: How soon action needs to be taken

## Recommendation Types

Each anomaly includes specific recommendations:

1. **Reduce Category Spending**: Cut specific categories to meet budget
2. **Investigate Anomaly**: Research unusual spending patterns
3. **Restructure Expenses**: Reorganize fixed/variable costs
4. **Early Warning**: Prepare for trend reversal

## Threshold Adjustment Guide

### Finding the Right Balance

- **Too many alerts?** Increase thresholds to reduce sensitivity
- **Missing important issues?** Decrease thresholds to increase sensitivity
- **First-time users?** Start with defaults, adjust based on your needs

### Recommended Adjustments

| Situation | Recommendation |
|-----------|-----------------|
| High variable income | Increase overspending threshold (1.2-1.5) |
| Fixed budget | Decrease all thresholds for early warnings |
| Business expenses | Increase spike threshold (0.5-0.7) |
| Optimizing spending | Decrease all thresholds |

## Integration with Other Features

### Works with:
- **Summary**: View detected anomalies at a glance
- **Historical Analysis**: Correlate anomalies with historical patterns
- **Insights & Recommendations**: Get comprehensive recommendations
- **Settings**: Fully customizable thresholds

## Technical Details

### Detection Algorithms

- **Overspending**: Budget vs actual comparison
- **Spikes**: Month-over-month percentage change
- **Budget Risk**: Spending as percentage of budget
- **Fixed Costs**: Fixed/Total expense ratio
- **Rising Trends**: 3-month trend analysis using linear regression

### Data Processing

- Anomalies calculated from last 90 days of expense data
- Updates in real-time as new expenses are added
- Uses session-state thresholds with config fallback
- Handles edge cases (no data, zero values, etc.)

## Tips & Best Practices

1. **Review regularly**: Check anomalies weekly for early intervention
2. **Adjust thresholds**: Customize based on your spending patterns
3. **Link to actions**: Use recommendations as concrete action steps
4. **Track changes**: Monitor improvement after implementing recommendations
5. **Cross-reference**: Compare anomalies with historical trends

## FAQ

**Q: Why am I getting so many alerts?**
A: Your thresholds are too sensitive. Go to Settings > Anomaly Detection and increase the threshold values.

**Q: Can I ignore medium/low priority alerts?**
A: Yes, focus on critical and high-priority recommendations first.

**Q: How are fixed costs determined?**
A: Expenses marked as "fixed" type in the expense entry contribute to fixed cost calculations.

**Q: Will anomalies update automatically?**
A: Yes, the system recalculates anomalies each time you add an expense or refresh the page.

**Q: Can I export recommendations?**
A: Currently, recommendations display in-app. You can take screenshots or export settings as JSON.

## Example Scenarios

### Scenario 1: High Overspending
**Alert**: Food category 40% over budget
**Action**: Review food expenses, identify discretionary items, plan reduction strategy

### Scenario 2: Spending Spike
**Alert**: Transport spending up 60% month-over-month
**Action**: Investigate cause (car repair? more commuting?), assess if temporary or permanent trend

### Scenario 3: Rising Trend
**Alert**: Utilities increasing 20% over 3 months
**Action**: Check for efficiency improvements, identify usage growth factors

### Scenario 4: Fixed Cost Danger
**Alert**: Fixed costs 65% of total spending
**Action**: Consider restructuring, negotiate lower fixed costs, increase variable expense flexibility

## Performance Notes

- Anomaly detection runs on app load and when settings change
- Minimal performance impact even with large expense databases
- Real-time updates with new expenses
- Efficient SQL queries for historical data aggregation

---

**Last Updated**: January 2026
**Version**: 1.0
