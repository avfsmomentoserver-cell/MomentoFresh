# Equal Baseline Feature Guide

## Overview

The **Equal Baseline** feature is a core component of MomentoFresh that transforms crash game multipliers into a symmetric, forex-style scale. This enables professional technical analysis with equal trendlines upside and downside, making pattern recognition and forecasting more accurate and intuitive.

## Problem Statement

Traditional crash game charts suffer from **asymmetric scaling**:
- **1.0x** is the absolute floor (minimum value)
- Multipliers can ascend to **50x, 100x, or higher**
- This creates a **compressed downside** and **expanded upside**, making it difficult to:
  - Compare upside and downside movements equally
  - Apply standard technical analysis techniques
  - Detect symmetric patterns (head & shoulders, triangles, etc.)
  - Use traditional indicators (MACD, RSI, Bollinger Bands)

## Solution: Symmetric Conversion

The Equal Baseline feature **remaps multipliers** to a symmetric scale where:
- **1.00x** maps to **-50 points** (reference value)
- **50.0x** maps to **+50 points** (same reference value)
- All intermediate values are **linearly interpolated**
- The scale is **continuous** and **unbounded**

This creates **equal visual weight** for upside and downside movements, enabling proper technical analysis.

---

## Conversion Formula

### For Multipliers Less Than or Equal to 1.0x (Crash/Downside)

points = -reference x (2 - multiplier)

**Examples with reference=50:**
- 1.0x to -50 x (2 - 1.0) = -50 points
- 0.5x to -50 x (2 - 0.5) = -75 points
- 0.0x to -50 x (2 - 0.0) = -100 points

### For Multipliers Greater Than 1.0x (Upside)

points = (multiplier - 1) x (2 x reference) - reference

**Examples with reference=50:**
- 1.0x to (1.0 - 1) x 100 - 50 = -50 points
- 1.5x to (1.5 - 1) x 100 - 50 = 0 points (neutral)
- 2.0x to (2.0 - 1) x 100 - 50 = +50 points
- 2.5x to (2.5 - 1) x 100 - 50 = +75 points
- 50.0x to (50.0 - 1) x 100 - 50 = +50 points
- 100.0x to (100.0 - 1) x 100 - 50 = +100 points

### Key Properties

1. Symmetric around neutral: 1.5x always maps to 0 points
2. Linear scaling: Equal distance in multipliers = equal distance in points (above 1.5x)
3. Reference configurable: Default is 50.0, but can be customized
4. Continuous: No gaps or jumps in the conversion

---

## Band Classification

Multipliers are automatically classified into 11 bands based on their point values:

With reference=50:
- ultra-crash: less than or equal to -100 points (less than or equal to 0.0x multiplier)
- crash: less than or equal to -75 points (less than or equal to 0.5x multiplier)
- deep-low: less than or equal to -50 points (less than or equal to 1.0x multiplier)
- low: less than or equal to -25 points (less than or equal to 1.25x multiplier)
- neutral: less than or equal to 0 points (less than or equal to 1.5x multiplier)
- mid: less than or equal to 25 points (less than or equal to 1.75x multiplier)
- high: less than or equal to 50 points (less than or equal to 2.0x multiplier)
- ignition: less than or equal to 75 points (less than or equal to 2.5x multiplier)
- moonshot: less than or equal to 100 points (less than or equal to 50.0x multiplier)
- stratospheric: greater than 100 points (greater than 50.0x multiplier)

---

## Architecture and Integration

The Equal Baseline feature integrates with the analysis engine and can be used for:
- Pattern recognition
- Technical indicator application
- Support/Resistance analysis
- Cross-game comparison
- Machine learning

For more details, see the implementation in backend/momento/features/equal_baseline/