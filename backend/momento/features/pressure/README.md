# Pressure Analysis Plugin

## Overview

The Pressure Analysis Plugin computes pressure when multipliers ascend/collapse with verified gap energy compressed under multiple resistance ceilings. It provides insight on imminent releases and ranges.

## Features

- Multi-ceiling tracking (7 default levels: 1.5x, 2.0x, 3.0x, 5.0x, 10.0x, 20.0x, 50.0x)
- Gap energy verification
- Arch/egg pattern detection (6 types: ascending, descending, stable, egg, dome, inverted egg)
- Imminence prediction (5 levels: low, moderate, high, critical, extreme)
- Overflow gauge with percentage metrics
- Release predictions (range and timing)

## Usage

### Basic Usage

```python
from momento.features.pressure import PressureCalculator

calculator = PressureCalculator()
result = calculator.calculate(multipliers, source="aviator")

print(f"Total pressure: {result.total_pressure}")
print(f"State: {result.state}")
print(f"Imminence: {result.imminence}")
print(f"Release probability: {result.release_probability:.2f}")
```

### With Custom Configuration

```python
from momento.features.pressure import PressureCalculator, PressureConfig

config = PressureConfig(
    ceilings=[1.5, 2.0, 3.0, 5.0, 10.0],
    decay_rate=0.9,
    overflow_threshold=80.0
)

calculator = PressureCalculator(config)
result = calculator.calculate(multipliers, source="aviator")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| ceilings | List[float] | [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0] | Ceiling values to track |
| decay_rate | float | 0.95 | Pressure decay rate |
| overflow_threshold | float | 100.0 | Threshold for overflow |
| min_ceiling_strength | float | 0.3 | Minimum strength for ceiling |
| verification_threshold | int | 3 | Hits required for verification |
| arch_detection_window | int | 20 | Window size for arch detection |
| gap_energy_multiplier | float | 1.5 | Multiplier for gap energy |
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

| Level | Pressure Range | Description |
|-------|----------------|-------------|
| low | < 30 | Low pressure, normal conditions |
| moderate | 30-50 | Moderate pressure building |
| high | 50-70 | High pressure, watch for release |
| critical | 70-90 | Critical pressure, imminent release |
| extreme | > 90 | Extreme pressure, release very likely |

## Pressure Calculation Formula

```
Pressure = Hit Pressure 	imes Gap Energy 	imes Arch Multiplier 	imes Verified Multiplier 	imes Strength Multiplier 	imes Accumulation Rate

Where:
- Hit Pressure = hits 	imes 0.1
- Gap Energy = normalized_distance 	imes compression_ratio 	imes gap_energy_multiplier
- Arch Multiplier = based on arch type (0.7-1.8)
- Verified Multiplier = 1.5 if verified, else 1.0
- Strength Multiplier = 1.0 + (strength 	imes 0.5)
- Accumulation Rate = from config
```

## Integration

### With Analysis Engine

```python
from momento.features.pressure import calculate_pressure

pressure_result = calculate_pressure(multipliers, source="aviator")
analysis_payload["pressure"] = pressure_result.to_dict()
```

### With Backtest Framework

```python
from momento.backtest import run_backtest, BacktestConfig
from momento.features.pressure import PressureCalculator

config = BacktestConfig(name="Pressure Test", source="aviator", rounds_limit=1000)
result = run_backtest(config)

# Pressure is automatically integrated
```

## Testing

```python
from momento.features.pressure import PressureCalculator

calculator = PressureCalculator()

# Test with ascending multipliers
multipliers = list(range(1, 100, 2))
result = calculator.calculate(multipliers, source="test")

assert result.total_pressure > 0
assert result.state != "neutral"
```

## Best Practices

1. **Ceiling Selection**: Choose ceilings that match your typical multiplier ranges
2. **Verification Threshold**: Set based on your data frequency
3. **Decay Rate**: Adjust based on how quickly pressure should dissipate
4. **Overflow Threshold**: Set based on your risk tolerance
5. **Arch Detection**: Larger windows provide more stable detection but less responsiveness

## Troubleshooting

### No pressure detected
- Check that multipliers are reaching ceiling values
- Verify that ceilings are configured correctly
- Increase the verification threshold if needed

### Pressure too high/low
- Adjust the arch multipliers
- Modify the gap energy multiplier
- Change the decay rate

### Incorrect arch type detection
- Increase the arch detection window
- Check that multipliers have enough variation
- Verify the data quality