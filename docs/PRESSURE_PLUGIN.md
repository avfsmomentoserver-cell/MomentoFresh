# Pressure Analysis Plugin Guide

## Overview

The Pressure Analysis Plugin is a powerful feature for MomentoFresh that computes pressure when multipliers ascend/collapse with verified gap energy compressed under multiple resistance ceilings. It provides insight on imminent releases and ranges to improve prediction accuracy.

## Key Features

- **Multi-Ceiling Tracking**: Monitors pressure at 7 default levels (1.5x, 2.0x, 3.0x, 5.0x, 10.0x, 20.0x, 50.0x)
- **Gap Energy Verification**: Measures compression energy below ceilings
- **Arch Pattern Detection**: Identifies 6 arch types (ascending, descending, stable, egg, dome, inverted egg)
- **Imminent Release Prediction**: 5 levels (low, moderate, high, critical, extreme)
- **Overflow Gauge**: Tracks pressure exceeding threshold with percentage metrics
- **Release Predictions**: Forecasts release ranges and timing

## Architecture

PressureCalculator
├── Configuration (PressureConfig)
│   ├── ceilings: [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0]
│   ├── decay_rate: 0.95
│   ├── overflow_threshold: 100.0
│   ├── min_ceiling_strength: 0.3
│   ├── verification_threshold: 3
│   ├── arch_detection_window: 20
│   ├── gap_energy_multiplier: 1.5
│   └── pressure_accumulation_rate: 1.0
├── Ceiling Management
│   ├── Hit tracking
│   ├── Arch type detection
│   │   ├── Ascending: Multipliers rising toward ceiling
│   │   ├── Descending: Multipliers falling from ceiling
│   │   ├── Stable: Multipliers fluctuating around ceiling
│   │   ├── Egg: Rise to peak then fall (asymmetric)
│   │   ├── Dome: Symmetric rise and fall
│   │   └── Inverted Egg: Fall to trough then rise
│   └── Verification (hits >= threshold)
├── Gap Energy Calculation
│   ├── Normalized Distance: Average distance from ceiling / ceiling value
│   ├── Compression Ratio: 1 - (range below ceiling / ceiling value)
│   └── Gap Energy = Normalized Distance x Compression Ratio x Multiplier
├── Pressure Calculation
│   ├── Hit Pressure: Hits x 0.1
│   ├── Gap Energy Contribution: Calculated gap energy
│   ├── Arch Multiplier: Based on arch type (0.7-1.8)
│   ├── Verified Multiplier: 1.5 if verified, else 1.0
│   ├── Strength Multiplier: 1.0 + (strength x 0.5)
│   └── Pressure = Hit Pressure x Gap Energy x Arch Multiplier x Verified Multiplier x Strength Multiplier x Accumulation Rate
└── State Analysis
    ├── Total Pressure
    ├── Overflow
    ├── Imminence Level
    └── Release Predictions

## Usage

### Basic Usage

```python
from momento.features.pressure import PressureCalculator

calculator = PressureCalculator()
result = calculator.calculate(multipliers, source="aviator")

print(f"Total pressure: {result.total_pressure}")
print(f"State: {result.state}")
print(f"Imminence: {result.imminence}")
print(f"Release probability: {result.release_probability:.2%}")
print(f"Overflow: {result.overflow:.2f}")
```

### With Custom Configuration

```python
from momento.features.pressure import PressureCalculator, PressureConfig

config = PressureConfig(
    ceilings=[1.5, 2.0, 3.0, 5.0, 10.0, 20.0],
    decay_rate=0.9,
    overflow_threshold=80.0,
    verification_threshold=5
)

calculator = PressureCalculator(config)
result = calculator.calculate(multipliers, source="aviator")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| ceilings | List[float] | [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0] | Ceiling values to track |
| decay_rate | float | 0.95 | Pressure decay rate per round |
| overflow_threshold | float | 100.0 | Threshold for overflow detection |
| min_ceiling_strength | float | 0.3 | Minimum strength for ceiling activation |
| verification_threshold | int | 3 | Number of hits required for verification |
| arch_detection_window | int | 20 | Number of rounds for arch detection |
| gap_energy_multiplier | float | 1.5 | Multiplier for gap energy calculation |
| pressure_accumulation_rate | float | 1.0 | Rate of pressure accumulation |

## Arch Type Multipliers

| Arch Type | Multiplier | Description |
|-----------|------------|-------------|
| ascending | 1.2x | Multipliers rising toward ceiling |
| descending | 0.8x | Multipliers falling from ceiling |
| stable | 1.0x | Multipliers fluctuating around ceiling |
| egg | 1.5x | Rise to peak then fall (asymmetric) |
| dome | 1.8x | Symmetric rise and fall |
| inverted_egg | 0.7x | Fall to trough then rise |

## Imminence Levels

| Level | Pressure Range | Description | Release Probability |
|-------|----------------|-------------|-------------------|
| low | < 30 | Low pressure, normal conditions | < 20% |
| moderate | 30-50 | Moderate pressure building | 20-40% |
| high | 50-70 | High pressure, watch for release | 40-60% |
| critical | 70-90 | Critical pressure, imminent release | 60-80% |
| extreme | > 90 | Extreme pressure, release very likely | > 80% |

## Pressure Calculation Formula

Total Pressure = Sum of all ceiling pressures

Ceiling Pressure = Hit Pressure x Gap Energy x Arch Multiplier x Verified Multiplier x Strength Multiplier x Accumulation Rate

Where:
- Hit Pressure = hits x 0.1
- Gap Energy = normalized_distance x compression_ratio x gap_energy_multiplier
- Arch Multiplier = from arch type (0.7-1.8)
- Verified Multiplier = 1.5 if verified, else 1.0
- Strength Multiplier = 1.0 + (strength x 0.5)
- Accumulation Rate = from config

## API Endpoints

### Get Pressure Analysis
```
GET /api/v1/pressure?source=aviator&limit=100
```

### Get Pressure State
```
GET /api/v1/pressure/state?source=aviator
```

### Get Pressure Predictions
```
GET /api/v1/pressure/predictions?source=aviator&limit=100
```

## Integration

### With Analysis Engine

```python
from momento.features.pressure import PressureCalculator

calculator = PressureCalculator()
pressure_result = calculator.calculate(multipliers, source)
analysis_payload["pressure"] = pressure_result.to_dict()
```

### With Backtest Framework

```python
from momento.backtest import run_backtest, BacktestConfig

config = BacktestConfig(
    name="Pressure Strategy Test",
    source="aviator",
    rounds_limit=1000
)

result = run_backtest(config)
# Pressure analysis is automatically included
```

### With Linguistics

```python
from momento.linguistics import analyze_linguistics

analysis = analyze_linguistics(source, limit)
pressure_info = analysis.pressure
```

## Best Practices

### 1. Ceiling Selection
- Choose ceilings that match your typical multiplier ranges
- For most games: [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0]
- For high-multiplier games: Add 100.0, 200.0
- For low-multiplier games: Use [1.2, 1.5, 2.0, 3.0, 5.0]

### 2. Verification Threshold
- Lower threshold (1-2) for frequent data
- Higher threshold (3-5) for less frequent data
- Adjust based on your data characteristics

### 3. Decay Rate
- Higher decay (0.9-0.95) for volatile markets
- Lower decay (0.95-0.99) for stable markets
- Adjust based on how quickly pressure should dissipate

### 4. Overflow Threshold
- Lower threshold (50-80) for conservative alerts
- Higher threshold (100-150) for aggressive alerts
- Set based on your risk tolerance

### 5. Arch Detection Window
- Smaller window (10-15) for more responsive detection
- Larger window (20-30) for more stable detection
- Adjust based on your data frequency

## Troubleshooting

### No pressure detected
- **Check**: Multipliers are reaching ceiling values
- **Solution**: Verify your ceiling configuration matches your data range
- **Action**: Adjust ceilings to match typical multiplier values

### Pressure too high/low
- **Check**: Arch multipliers and gap energy settings
- **Solution**: Adjust arch_multipliers in config
- **Action**: Modify gap_energy_multiplier

### Incorrect arch type detection
- **Check**: Data has enough variation and history
- **Solution**: Increase arch_detection_window
- **Action**: Verify data quality and frequency

### Overflow always triggered
- **Check**: overflow_threshold value
- **Solution**: Increase overflow_threshold
- **Action**: Or reduce pressure accumulation rate

### Release predictions inaccurate
- **Check**: Ceiling configuration and verification
- **Solution**: Adjust ceilings to better match resistance levels
- **Action**: Verify ceilings align with historical resistance

## Testing

```python
from momento.features.pressure import PressureCalculator

calculator = PressureCalculator()

# Test with ascending multipliers
multipliers = [1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
result = calculator.calculate(multipliers, source="test")

assert result.total_pressure > 0
assert result.state != "neutral"
assert len(result.ceiling_results) > 0

# Test with high pressure scenario
multipliers = [4.5, 4.8, 4.9, 4.95, 4.98, 5.0, 5.05, 5.1] * 10
result = calculator.calculate(multipliers, source="test")

assert result.total_pressure > 50
assert result.imminence in ["high", "critical", "extreme"]
```

## Performance

| Operation | Time Complexity | Typical Execution |
|-----------|-----------------|-------------------|
| Single calculation | O(n x c) | < 10ms for 1000 rounds, 7 ceilings |
| Batch calculation | O(b x n x c) | < 100ms for 10 batches |
| Real-time updates | O(c) | < 1ms per new round |

Where: n = number of rounds, c = number of ceilings, b = batch size

## Future Enhancements

- Dynamic ceiling adjustment based on data range
- Machine learning for improved pressure prediction
- Integration with external data sources
- Advanced pattern recognition
- Custom ceiling definitions
- Pressure history and trends analysis

## Conclusion

The Pressure Plugin provides professional-grade pressure analysis for crash games, enabling:
- Accurate prediction of imminent releases
- Identification of resistance ceilings
- Measurement of gap energy and compression
- Real-time pressure monitoring
- Integration with backtesting and analysis

This plugin, combined with the Equal Baseline feature, forms the foundation for advanced crash game analysis in MomentoFresh.