# Backtest Framework Guide

## Overview

The Backtest Framework is a flexible, reusable system for testing strategies, signals, and metrics against historical crash game data. It provides comprehensive tools for validating predictive models and trading strategies with verified results.

## Features

- **Flexible Test Scope**: Configure backtests with specific parameters and data ranges
- **Test Phase Management**: 8 structured phases for thorough testing
- **Signal Detection**: Built-in detection for 10 different signal types
- **Metric Calculation**: 11 built-in performance metrics
- **Parallel Execution**: Run multiple tests concurrently
- **Comprehensive Reporting**: Detailed results with recommendations
- **Honest Accuracy**: All predictions are recorded before rounds land

## Quick Start

### Simple Backtest

```python
from momento.backtest import run_backtest, BacktestConfig

# Create configuration
config = BacktestConfig(
    name="Quick Test",
    source="aviator",
    rounds_limit=1000,
)

# Run backtest
result = run_backtest(config)

# Access results
print(f"Status: {result.status}")
print(f"Signals detected: {len(result.signal_results)}")
print(f"Metrics calculated: {len(result.metric_results)}")
```

### With Custom Configuration

```python
from momento.backtest import run_backtest, BacktestConfig, TestPhase

config = BacktestConfig(
    name="Custom Test",
    source="aviator",
    rounds_limit=1000,
    test_phases=[TestPhase.PREPARE, TestPhase.SIGNAL_DETECTION, TestPhase.METRIC_CALCULATION]
)

result = run_backtest(config)
```

## Test Phases

The framework executes 8 phases in sequence:

1. **PREPARE** - Setup and data validation
2. **BASELINE** - Establish baseline metrics
3. **SIGNAL_DETECTION** - Test signal detection
4. **METRIC_CALCULATION** - Calculate performance metrics
5. **OPTIMIZATION** - Optimize strategy parameters
6. **VALIDATION** - Validate results
7. **COMPARISON** - Compare with benchmarks
8. **REPORTING** - Generate reports

## Built-in Signals

1. **Pressure** - Detects high pressure conditions
2. **Moonshot** - Identifies moonshot opportunities
3. **Collapse** - Warns of potential collapses
4. **Resistance Break** - Detects resistance level breaks
5. **Support Bounce** - Identifies support level bounces
6. **Trend Reversal** - Detects trend direction changes
7. **Gap Swing** - Identifies large price gaps
8. **Ladder** - Detects ladder patterns (ascending/descending)
9. **Compression** - Identifies compression patterns
10. **Expansion** - Identifies expansion patterns

## Built-in Metrics

1. **Accuracy** - Prediction accuracy
2. **Precision** - True positives / predicted positives
3. **Recall** - True positives / actual positives
4. **F1 Score** - Harmonic mean of precision and recall
5. **Sharpe Ratio** - Risk-adjusted return
6. **Profit Factor** - Gross profit / gross loss
7. **Max Drawdown** - Maximum drawdown
8. **Win Rate** - Percentage of winning trades
9. **Risk/Reward** - Average risk/reward ratio
10. **Expected Value** - Expected value per trade
11. **Brier Score** - Probability prediction accuracy

## API Endpoints

### Run Backtest
```
POST /api/v1/backtest
```

### Simple Backtest
```
GET /api/v1/backtest/simple?source=aviator&limit=1000
```

### Test Signal Detection
```
GET /api/v1/backtest/signals?source=aviator&limit=1000
```

### Test Metric Calculation
```
GET /api/v1/backtest/metrics?source=aviator&limit=1000
```

## Best Practices

### 1. Data Quality
- Always validate data before backtesting
- Check for missing values and outliers
- Ensure timestamps are in the correct format
- Verify multiplier ranges are reasonable

### 2. Test Configuration
- Start with small datasets (100-1000 rounds)
- Gradually increase data size as you validate results
- Use appropriate time ranges for your strategy
- Set random seeds for reproducibility

### 3. Signal Detection
- Test signals individually before combining
- Validate signal detection logic manually
- Check for false positives and false negatives
- Adjust confidence thresholds as needed

### 4. Metric Calculation
- Understand what each metric measures
- Compare metrics across different time periods
- Look for consistent patterns
- Don't over-optimize for a single metric

### 5. Performance
- Cache expensive calculations
- Use efficient data structures
- Limit parallel execution based on system resources
- Monitor memory usage

## Examples

### Example 1: Testing Pressure Signals

```python
from momento.backtest import run_backtest, BacktestConfig, TestPhase

config = BacktestConfig(
    name="Pressure Signal Test",
    source="aviator",
    rounds_limit=500,
    test_phases=[TestPhase.PREPARE, TestPhase.SIGNAL_DETECTION],
)

result = run_backtest(config)
pressure_signals = [s for s in result.signal_results if s.signal_type == "pressure"]
print(f"Pressure signals detected: {len(pressure_signals)}")
```

### Example 2: Comparing Strategies

```python
from momento.backtest import run_backtest, BacktestConfig

config1 = BacktestConfig(
    name="Pressure Strategy",
    source="aviator",
    rounds_limit=1000,
    parameters={"strategy": "pressure"},
)

config2 = BacktestConfig(
    name="Trend Strategy",
    source="aviator",
    rounds_limit=1000,
    parameters={"strategy": "trend"},
)

result1 = run_backtest(config1)
result2 = run_backtest(config2)

print("Pressure Strategy Metrics:")
for metric in result1.metric_results:
    print(f"  {metric.name}: {metric.value}")
```

## Integration

### With Pressure Plugin

```python
from momento.backtest import run_backtest, BacktestConfig
from momento.features.pressure import calculate_pressure

config = BacktestConfig(
    name="Pressure Backtest",
    source="aviator",
    rounds_limit=1000,
)

result = run_backtest(config)
pressure_result = calculate_pressure([{"multiplier": r["multiplier"]} for r in data], source=config.source)
result.summary["pressure"] = pressure_result.to_dict()
```

### With Equal Baseline

```python
from momento.backtest import run_backtest, BacktestConfig
from momento.features.equal_baseline import convert_multipliers

config = BacktestConfig(
    name="Equal Baseline Backtest",
    source="aviator",
    rounds_limit=1000,
)

result = run_backtest(config)
multipliers = [r["multiplier"] for r in data]
points = convert_multipliers(multipliers)
result.summary["equal_baseline"] = {"points": points, "reference": 50.0}
```

## Troubleshooting

### No data available
- Check that the source has data
- Verify the date range is correct
- Ensure the database is properly configured

### Slow performance
- Reduce the number of rounds
- Limit the number of signals and metrics
- Check for inefficient algorithms

### No signals detected
- Verify the signal detection logic
- Check that the data has the expected patterns
- Adjust confidence thresholds

### Metric values seem incorrect
- Review the metric calculation logic
- Check for data quality issues
- Validate against manual calculations

## Conclusion

The Backtest Framework provides a powerful, flexible system for testing and validating strategies against historical crash game data. With its modular architecture, extensive built-in features, and comprehensive reporting, it enables thorough testing and optimization of predictive models and trading strategies.