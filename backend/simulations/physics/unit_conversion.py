# Conversion factors
KM_PER_M = 0.001
M_PER_KM = 1000.0  # Corrected to float
FT_PER_M = 3.28084
M_PER_FT = 0.3048
MI_PER_M = 0.000621371
M_PER_MI = 1609.34
S_PER_H = 3600.0 # Corrected to float
MIN_PER_S = 1.0 / 60.0
S_PER_MIN = 60.0 # Corrected to float

# Allowed unit strings (for reference, actual validation is in models)
# VELOCITY_UNITS = ["m/s", "km/h", "ft/s", "mph"]
# LENGTH_UNITS_INPUT = ["m", "ft"]
# LENGTH_UNITS_OUTPUT = ["m", "km", "ft", "mi"]
# TIME_UNITS_OUTPUT = ["s", "min"]

def convert_velocity_to_base(value: float, unit: str) -> float:
    """Converts velocity from a given unit to m/s (base unit)."""
    if unit == "m/s":
        return value
    elif unit == "km/h":
        return value * M_PER_KM / S_PER_H
    elif unit == "ft/s":
        return value * M_PER_FT
    elif unit == "mph":
        return value * M_PER_MI / S_PER_H
    else:
        raise ValueError(f"Unknown velocity unit for conversion to base: {unit}")

def convert_length_to_base(value: float, unit: str) -> float:
    """Converts length from a given unit to meters (base unit)."""
    if unit == "m":
        return value
    elif unit == "ft":
        return value * M_PER_FT
    else:
        raise ValueError(f"Unknown length unit for conversion to base: {unit}")

def convert_velocity_from_base(value_mps: float, target_unit: str) -> float:
    """Converts velocity from m/s (base unit) to a target unit."""
    if target_unit == "m/s":
        return value_mps
    elif target_unit == "km/h":
        return value_mps * KM_PER_M * S_PER_H
    elif target_unit == "ft/s":
        return value_mps / M_PER_FT # Equivalent to value_mps * FT_PER_M
    elif target_unit == "mph":
        return value_mps * MI_PER_M * S_PER_H
    else:
        raise ValueError(f"Unknown target velocity unit for conversion from base: {target_unit}")

def convert_length_from_base(value_m: float, target_unit: str) -> float:
    """Converts length from meters (base unit) to a target unit."""
    if target_unit == "m":
        return value_m
    elif target_unit == "km":
        return value_m * KM_PER_M
    elif target_unit == "ft":
        return value_m * FT_PER_M
    elif target_unit == "mi":
        return value_m * MI_PER_M
    else:
        raise ValueError(f"Unknown target length unit for conversion from base: {target_unit}")

def convert_time_from_base(value_s: float, target_unit: str) -> float:
    """Converts time from seconds (base unit) to a target unit."""
    if target_unit == "s":
        return value_s
    elif target_unit == "min":
        return value_s * MIN_PER_S
    else:
        raise ValueError(f"Unknown target time unit for conversion from base: {target_unit}")
