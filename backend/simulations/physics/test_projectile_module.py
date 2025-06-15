import pytest
import math

from backend.simulations.physics.projectile_module import ProjectileModule
from backend.simulations.physics.models_projectile import ProjectileLaunchParams, TrajectoryPoint, OutputUnitSelection
from backend.simulations.physics import unit_conversion as uc

# Instantiate the module once for all tests
module = ProjectileModule()

# Default output units (SI) for many tests
SI_OUTPUT_UNITS = OutputUnitSelection(
    velocity_unit="m/s",
    time_unit="s",
    range_unit="m",
    height_unit="m"
)

# Test 1: Lançamento a 45 graus (alcance máximo em solo plano)
def test_launch_45_degrees():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=45, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)

    # Theoretical calculations for g=9.81, v0=10, angle=45, h0=0:
    # Max Height (H) = (v0^2 * sin^2(angle)) / (2 * g) = (100 * 0.5) / (2 * 9.81) = 2.5484 m
    # Total Time (T) = (2 * v0 * sin(angle)) / g = (2 * 10 * math.sqrt(2)/2) / 9.81 = 1.4416 s
    # Max Range (R)  = (v0^2 * sin(2*angle)) / g = (100 * 1) / 9.81 = 10.1936 m

    assert math.isclose(result.max_range, 10.1936, rel_tol=1e-3)
    assert math.isclose(result.max_height, 2.5484, rel_tol=1e-3)
    assert math.isclose(result.total_time, 1.4416, rel_tol=1e-3)

    assert result.initial_velocity_x_unit == "m/s"
    assert result.initial_velocity_y_unit == "m/s"
    assert result.total_time_unit == "s"
    assert result.max_range_unit == "m"
    assert result.max_height_unit == "m"

    assert result.trajectory is not None
    assert len(result.trajectory) > 0
    assert math.isclose(result.trajectory[0].x, 0.0, abs_tol=1e-3)
    assert math.isclose(result.trajectory[0].y, 0.0, abs_tol=1e-3)
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert math.isclose(result.trajectory[-1].x, result.max_range, rel_tol=1e-2)
    assert result.parameters_used == params

# Test 2: Lançamento com ângulo alto (ex: 80 graus)
def test_launch_high_angle():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=80, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)

    assert math.isclose(result.max_range, 3.486, rel_tol=1e-3)
    assert math.isclose(result.max_height, 4.943, rel_tol=1e-3)
    assert math.isclose(result.total_time, 2.0077, rel_tol=1e-3)
    assert result.max_range_unit == "m"
    assert result.trajectory is not None and len(result.trajectory) > 0
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params

# Test 3: Lançamento horizontal de uma altura
def test_launch_horizontal_from_height():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=0, initial_height=10, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)

    assert math.isclose(result.max_range, 14.278, rel_tol=1e-3)
    assert math.isclose(result.max_height, 10.0, rel_tol=1e-3) # Max height is initial height
    assert math.isclose(result.total_time, 1.4278, rel_tol=1e-3)
    assert result.max_range_unit == "m"
    assert result.max_height_unit == "m" # Relative to y=0, so it's initial height
    assert result.trajectory is not None and len(result.trajectory) > 0
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params

# Test 4: Validação de entrada (Pydantic validation for core model) - units handled by their validators
def test_input_validation():
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=-10, launch_angle=45, initial_height=0)
    # ... (other validation tests remain the same as they test core model constraints, not units)

# Test 5: Trajetória com pontos específicos (exemplo simples com g=10)
def test_trajectory_specific_point():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=30, initial_height=0, gravity=10,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)

    assert math.isclose(result.max_height, 1.25, rel_tol=1e-3)
    assert math.isclose(result.total_time, 1.0, rel_tol=1e-3)
    assert math.isclose(result.max_range, 8.660, rel_tol=1e-3)
    assert result.max_range_unit == "m"

    found_peak_time_point = False
    for point in result.trajectory:
        if math.isclose(point.time, 0.5, abs_tol=0.025): # time_step is 0.05
            assert math.isclose(point.x, 4.330, rel_tol=1e-2)
            assert math.isclose(point.y, 1.25, rel_tol=1e-2)
            found_peak_time_point = True
            break
    assert found_peak_time_point
    assert result.parameters_used == params

# Test for edge case angle near 0
def test_very_low_angle_launch():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=0.001, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert result.max_height > 0 and result.max_height < 0.01
    assert result.total_time > 0 and result.total_time < 0.01
    assert result.max_range > 0 and result.max_range < 0.1
    assert result.max_range_unit == "m"
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test for edge case angle near 90
def test_very_high_angle_launch():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=89.999, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert math.isclose(result.max_height, 5.0969, rel_tol=1e-3)
    assert math.isclose(result.total_time, 2.0387, rel_tol=1e-3)
    assert result.max_range < 0.01
    assert result.max_range_unit == "m"
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test to ensure parameters_used is correctly populated
def test_parameters_used_population():
    params = ProjectileLaunchParams(
        initial_velocity=25, launch_angle=35, initial_height=5, gravity=9.8,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert result.parameters_used == params

# Test with different gravity (e.g., Moon's gravity)
def test_different_gravity_moon():
    moon_gravity = 1.62
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=45, initial_height=0, gravity=moon_gravity,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert math.isclose(result.max_range, 61.728, rel_tol=1e-3)
    assert math.isclose(result.max_height, 15.432, rel_tol=1e-3)
    assert math.isclose(result.total_time, 8.729, rel_tol=1e-3)
    assert result.max_range_unit == "m"
    assert result.parameters_used.gravity == moon_gravity
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test for a case where the projectile doesn't move much
def test_low_velocity_on_ground():
    params = ProjectileLaunchParams(
        initial_velocity=0.01, launch_angle=45, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert result.max_range < 1e-3
    assert result.max_height < 1e-4
    assert result.total_time < 1e-2
    assert result.max_range_unit == "m"
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test for launch from a significant height with an upward angle
def test_launch_from_height_upward_angle():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=30, initial_height=20, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    assert math.isclose(result.max_height, 21.274, rel_tol=1e-3)
    assert math.isclose(result.total_time, 2.5922, rel_tol=1e-3)
    assert math.isclose(result.max_range, 22.449, rel_tol=1e-3)
    assert result.max_range_unit == "m"
    assert result.max_height_unit == "m"
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params

# --- New Tests for Unit Conversion ---
def test_input_conversion_velocity_kmh():
    params = ProjectileLaunchParams(
        initial_velocity=36, initial_velocity_unit="km/h", # 36 km/h = 10 m/s
        launch_angle=45, initial_height=0, gravity=10.0, # Using g=10 for simpler math
        initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    # Expected results for v0=10m/s, angle=45, g=10, h0=0:
    # Max Range = v0^2 / g = 100 / 10 = 10 m
    # Max Height = (v0^2 * sin^2(45)) / (2g) = (100 * 0.5) / 20 = 2.5 m
    # Total Time = (2 * v0 * sin(45)) / g = (2 * 10 * sqrt(2)/2) / 10 = sqrt(2) approx 1.414 s
    assert math.isclose(result.max_range, 10.0, rel_tol=1e-3)
    assert math.isclose(result.max_height, 2.5, rel_tol=1e-3)
    assert math.isclose(result.total_time, 1.4142, rel_tol=1e-3)
    assert result.max_range_unit == "m"
    assert result.initial_velocity_x_unit == "m/s" # Output is SI

def test_input_conversion_height_ft():
    params = ProjectileLaunchParams(
        initial_velocity=5, initial_velocity_unit="m/s",
        launch_angle=0, # Horizontal launch
        initial_height=10, initial_height_unit="ft", # 10 ft = 3.048 m
        gravity=10.0, output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    # Expected for y0 = 3.048m, v0x=5m/s, v0y=0, g=10:
    # Time to fall: t = sqrt(2*y0/g) = sqrt(2*3.048/10) = sqrt(0.6096) approx 0.7807 s
    # Max range = v0x * t = 5 * 0.7807 = 3.9035 m
    # Max height = initial height = 3.048 m
    assert math.isclose(result.max_range, 3.9035, rel_tol=1e-3)
    assert math.isclose(result.max_height, 3.048, rel_tol=1e-3)
    assert math.isclose(result.total_time, 0.7807, rel_tol=1e-3)
    assert result.max_height_unit == "m"
    assert result.max_range_unit == "m"

def test_output_conversion_various_units():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=45, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m",
        output_units=OutputUnitSelection(
            velocity_unit="km/h", time_unit="min", range_unit="km", height_unit="ft"
        )
    )
    result = module.run_simulation(params)

    # SI results first (from test_launch_45_degrees):
    max_r_si = 10.1936  # m
    max_h_si = 2.5484   # m
    total_t_si = 1.4416 # s
    v0x_si = 10 * math.cos(math.radians(45)) # approx 7.071 m/s
    v0y_si = 10 * math.sin(math.radians(45)) # approx 7.071 m/s

    expected_max_r_km = max_r_si * uc.KM_PER_M
    expected_max_h_ft = max_h_si * uc.FT_PER_M
    expected_total_t_min = total_t_si * uc.MIN_PER_S
    expected_v0x_kmh = v0x_si * uc.M_PER_KM / uc.S_PER_H # This is wrong, should be v0x_si / (uc.M_PER_KM / uc.S_PER_H) or v0x_si * (uc.S_PER_H / uc.M_PER_KM) or 3.6
    expected_v0x_kmh_corrected = v0x_si * 3.6 # m/s to km/h
    expected_v0y_kmh_corrected = v0y_si * 3.6 # m/s to km/h


    assert math.isclose(result.max_range, expected_max_r_km, rel_tol=1e-3)
    assert result.max_range_unit == "km"
    assert math.isclose(result.max_height, expected_max_h_ft, rel_tol=1e-3)
    assert result.max_height_unit == "ft"
    assert math.isclose(result.total_time, expected_total_t_min, rel_tol=1e-3)
    assert result.total_time_unit == "min"
    assert math.isclose(result.initial_velocity_x, expected_v0x_kmh_corrected, rel_tol=1e-3)
    assert result.initial_velocity_x_unit == "km/h"
    assert math.isclose(result.initial_velocity_y, expected_v0y_kmh_corrected, rel_tol=1e-3)
    assert result.initial_velocity_y_unit == "km/h"

    # Check a few trajectory points
    # Last point: x should be in km, y in ft, time in s
    # For trajectory, x is in range_unit, y is in height_unit. Time is always 's'.
    if result.trajectory:
        last_point = result.trajectory[-1]
        # last_point.x is already converted to km by the module
        assert math.isclose(last_point.x, expected_max_r_km, rel_tol=1e-2)
        # last_point.y should be close to 0 ft
        assert math.isclose(last_point.y, 0.0, abs_tol=0.1) # 0m converted to ft is 0ft. abs_tol for ft.
        # last_point.time is in seconds
        assert math.isclose(last_point.time, total_t_si, rel_tol=1e-3)

# --- New Tests for Adaptive Trajectory Generation ---
MIN_DESIRED_POINTS = 20
MAX_POINTS_LIMIT = 2000

def test_trajectory_adaptive_low_energy():
    params = ProjectileLaunchParams(
        initial_velocity=0.1, launch_angle=45, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    # total_t for v0=0.1, angle=45, g=9.81 is (2*0.1*sin(45))/9.81 = 0.0144s
    # Default time_step = 0.05. 0.0144 / 0.05 < MIN_DESIRED_POINTS (20)
    # New time_step = 0.0144 / 20 = 0.00072s
    # Num intervals = total_t / new_time_step = 20. Num points = 21.
    assert len(result.trajectory) == MIN_DESIRED_POINTS + 1

def test_trajectory_adaptive_high_energy_capped():
    params = ProjectileLaunchParams(
        initial_velocity=700, launch_angle=30, initial_height=0, gravity=9.81, # Results in ~2474 points with 0.05 step
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    # v0y = 700 * sin(30) = 350. total_t = 2 * 350 / 9.81 = 71.355 s
    # Default num_intervals = 71.355 / 0.05 = 1427. This is < MAX_POINTS_LIMIT.
    # Let's try velocity that WILL exceed it.
    # If total_t / 0.05 > 2000 => total_t > 100s.
    # 2 * v0y / g > 100 => v0y > 100 * g / 2 = 50 * 9.81 = 490.5
    # v0 * sin(angle) > 490.5. Let angle=30, sin(30)=0.5. v0 * 0.5 > 490.5 => v0 > 981 m/s
    params_high = ProjectileLaunchParams(
        initial_velocity=1000, launch_angle=30, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    # total_t = (2 * 1000 * 0.5) / 9.81 = 1000 / 9.81 = 101.936 s
    # Default steps = 101.936 / 0.05 = 2038.72 -> this should trigger capping.
    # New time_step = 101.936 / 2000 = 0.050968
    result = module.run_simulation(params_high)
    assert len(result.trajectory) == MAX_POINTS_LIMIT + 1

def test_trajectory_adaptive_standard_case():
    params = ProjectileLaunchParams(
        initial_velocity=10, launch_angle=45, initial_height=0, gravity=9.81,
        initial_velocity_unit="m/s", initial_height_unit="m", output_units=SI_OUTPUT_UNITS
    )
    result = module.run_simulation(params)
    # total_t approx 1.4416s. Default time_step 0.05s.
    # num_intervals = 1.4416 / 0.05 = 28.832.
    # This is > MIN_DESIRED_POINTS (20) and < MAX_POINTS_LIMIT (2000)
    # So, time_step should remain 0.05.
    # Expected points = floor(num_intervals) + 1 (for t=0) + 1 (for final point if not perfectly aligned)
    # Or, more robustly, check it's NOT 21 and NOT 2001.
    # The loop runs while current_time <= total_t + 1e-9.
    # Number of points = floor(total_t / time_step) + 1. Potentially +1 if last point added separately.
    # The logic is: `while current_time <= total_t_si + 1e-9`.
    # Point for current_time=0. Then current_time becomes 0.05, 0.10, ...
    # Number of steps = ceil(total_t / time_step). Points = Number of steps + 1 if t=0 is counted.
    # Or simpler: total_t / time_step = 1.4416 / 0.05 = 28.832.
    # loop runs for time = 0, 0.05, ..., 1.40. (29 points)
    # Then final point at 1.4416s is added if not already close. (Potentially 30th point)
    # The current implementation adds the final point if the last point's time is not close to total_t.
    # If last point is at 1.40, and total_t is 1.4416, it will add one more. So 29+1 = 30.
    # If last point is at 1.40, current_time becomes 1.45. Loop terminates.
    # trajectory_points_si.append(TrajectoryPoint(time=current_time_si, x=x_si, y=y_si))
    # So it will be 1.40. Then check `abs(trajectory_points_si[-1].time - total_t_si) > 1e-4`
    # `abs(1.40 - 1.4416) > 1e-4` is true. So one more point is added.
    # Expected points = floor(1.4416/0.05) + 1 (initial) + 1 (final adjustment) = 28 + 1 + 1 = 30.
    # Let's verify:
    # t=0 (1)
    # t=0.05 (2)
    # ...
    # t=1.40 (0.05 * 28) -> 28+1 = 29th point
    # current_time becomes 1.45. Loop condition: 1.45 <= 1.4416 + 1e-9 is false.
    # Last point in loop is at t=1.40.
    # Then, `if not trajectory_points_si or abs(trajectory_points_si[-1].time - total_t_si) > 1e-4`
    # `abs(1.40 - 1.4416) > 1e-4` is true. So, point at `total_t_si` is added.
    # So, number of points will be `floor(total_t_si / time_step_si) + 1 + 1`
    # `floor(1.4416 / 0.05)` = 28. So `28 + 1 + 1 = 30`.

    # However, the adaptive logic for time_step_si is:
    # if (total_t_si / time_step_si) < min_desired_points: ...
    # 1.4416 / 0.05 = 28.832. This is > 20. So time_step_si remains 0.05.
    # if (total_t_si / time_step_si) > max_points_limit: ... (28.832 is not > 2000)

    assert len(result.trajectory) > MIN_DESIRED_POINTS + 1 # Greater than 21
    assert len(result.trajectory) < MAX_POINTS_LIMIT + 1 # Less than 2001
    # For this specific case, total_t_si = 1.4416s, time_step_si = 0.05s
    # num_generated_in_loop = 0
    # temp_current_time = 0.0
    # while temp_current_time <= total_t_si + 1e-9:
    #    num_generated_in_loop+=1
    #    temp_current_time += 0.05
    #    if num_generated_in_loop > 2000+10: break # safety
    # num_generated_in_loop is 29 (for t=0 to t=1.40)
    # Then one more point is added by the final adjustment logic. So 30.
    assert len(result.trajectory) == 30

# Re-add the input validation tests that might have been accidentally removed by diff markers
def test_input_validation_original(): # Renamed to avoid conflict if parts were kept
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=-10, launch_angle=45, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=0, launch_angle=45, initial_height=0)

    with pytest.raises(ValueError, match="Input should be less than 90"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=90, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=-5, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=-10)

    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=0)
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=-9.81)
