import pytest
import math
# from fastapi import HTTPException # Not testing direct HTTPException from module if Pydantic handles validation.
# from pydantic import ValidationError # Using ValueError for Pydantic v2 default validation errors.

from backend.simulations.physics.projectile_module import ProjectileModule
from backend.simulations.physics.models_projectile import ProjectileLaunchParams, TrajectoryPoint

# Instantiate the module once for all tests
module = ProjectileModule()

# Test 1: Lançamento a 45 graus (alcance máximo em solo plano)
def test_launch_45_degrees():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=9.81)
    result = module.run_simulation(params)

    # Theoretical calculations for g=9.81, v0=10, angle=45, h0=0:
    # Max Height (H) = (v0^2 * sin^2(angle)) / (2 * g) = (100 * 0.5) / (2 * 9.81) = 2.5484 m
    # Total Time (T) = (2 * v0 * sin(angle)) / g = (2 * 10 * sqrt(2)/2) / 9.81 = 1.4416 s
    # Max Range (R)  = (v0^2 * sin(2*angle)) / g = (100 * 1) / 9.81 = 10.1936 m

    assert math.isclose(result.max_range, 10.1936, rel_tol=1e-3), f"Max range expected ~10.1936, got {result.max_range}"
    assert math.isclose(result.max_height, 2.5484, rel_tol=1e-3), f"Max height expected ~2.5484, got {result.max_height}"
    assert math.isclose(result.total_time, 1.4416, rel_tol=1e-3), f"Total time expected ~1.4416, got {result.total_time}"

    assert result.trajectory is not None, "Trajectory should not be None"
    assert len(result.trajectory) > 0, "Trajectory should not be empty"

    assert math.isclose(result.trajectory[0].x, 0.0, abs_tol=1e-3), "Initial x should be 0"
    assert math.isclose(result.trajectory[0].y, 0.0, abs_tol=1e-3), "Initial y should be 0"

    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2), f"Final y should be close to 0, got {result.trajectory[-1].y}"
    assert math.isclose(result.trajectory[-1].x, result.max_range, rel_tol=1e-2), f"Final x should be close to max_range, got {result.trajectory[-1].x}"

    assert result.parameters_used == params, "parameters_used should match input params"


# Test 2: Lançamento com ângulo alto (ex: 80 graus)
def test_launch_high_angle():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=80, initial_height=0, gravity=9.81)
    result = module.run_simulation(params)

    # H = (100 * sin^2(80)) / (2 * 9.81) approx 4.943 m
    # T = (2 * 10 * sin(80)) / 9.81 approx 2.0077 s
    # R = (100 * sin(160)) / 9.81 approx 3.486 m

    assert math.isclose(result.max_range, 3.486, rel_tol=1e-3)
    assert math.isclose(result.max_height, 4.943, rel_tol=1e-3)
    assert math.isclose(result.total_time, 2.0077, rel_tol=1e-3)

    assert result.trajectory is not None and len(result.trajectory) > 0
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params

# Test 3: Lançamento horizontal de uma altura
def test_launch_horizontal_from_height():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=0, initial_height=10, gravity=9.81)
    result = module.run_simulation(params)

    # Max height = initial_height = 10m.
    # Time to fall: t = sqrt(2*y0/g) = sqrt(2*10/9.81) approx 1.4278 s
    # Max range = v0x * t = 10 * 1.4278 = 14.278 m

    assert math.isclose(result.max_range, 14.278, rel_tol=1e-3)
    assert math.isclose(result.max_height, 10.0, rel_tol=1e-3)
    assert math.isclose(result.total_time, 1.4278, rel_tol=1e-3)

    assert result.trajectory is not None and len(result.trajectory) > 0
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params

# Test 4: Validação de entrada (Pydantic validation)
def test_input_validation():
    with pytest.raises(ValueError, match="Input should be greater than 0"): # Pydantic v2 gt error
        ProjectileLaunchParams(initial_velocity=-10, launch_angle=45, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than 0"): # Matches default message for gt
        ProjectileLaunchParams(initial_velocity=0, launch_angle=45, initial_height=0)

    with pytest.raises(ValueError, match="Input should be less than 90"): # lt=90
        ProjectileLaunchParams(initial_velocity=10, launch_angle=90, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than or equal to 0"): # ge=0
        ProjectileLaunchParams(initial_velocity=10, launch_angle=-5, initial_height=0)

    with pytest.raises(ValueError, match="Input should be greater than or equal to 0"): # ge=0
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=-10)

    with pytest.raises(ValueError, match="Input should be greater than 0"): # gt=0
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=0)
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=-9.81)

# Test 5: Trajetória com pontos específicos (exemplo simples com g=10)
def test_trajectory_specific_point():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=30, initial_height=0, gravity=10)
    result = module.run_simulation(params)

    # v0x = 10 * cos(30) = 8.660254 m/s; v0y = 10 * sin(30) = 5 m/s
    # Time to max height (t_peak) = v0y / g = 5 / 10 = 0.5s
    # At t=0.5s: x = 4.330127 m; y = 1.25 m (max height)
    # Total time = 1.0s; Max range = 8.660254 m

    assert math.isclose(result.max_height, 1.25, rel_tol=1e-3)
    assert math.isclose(result.total_time, 1.0, rel_tol=1e-3)
    assert math.isclose(result.max_range, 8.660, rel_tol=1e-3)

    found_peak_time_point = False
    for point in result.trajectory:
        if math.isclose(point.time, 0.5, abs_tol=0.025): # time_step is 0.05, so abs_tol should be half of that
            assert math.isclose(point.x, 4.330, rel_tol=1e-2), f"X at t=0.5s: Expected ~4.33, got {point.x}"
            assert math.isclose(point.y, 1.25, rel_tol=1e-2),  f"Y at t=0.5s: Expected ~1.25, got {point.y}"
            found_peak_time_point = True
            break
    assert found_peak_time_point, "Trajectory point at peak time t=0.5s not found or values incorrect."
    assert result.parameters_used == params

# Test for edge case angle near 0 (e.g. 0.001 degrees)
def test_very_low_angle_launch():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=0.001, initial_height=0, gravity=9.81)
    result = module.run_simulation(params)

    assert result.max_height > 0 and result.max_height < 0.01 # Should be very small
    assert result.total_time > 0 and result.total_time < 0.01 # Should be very small
    assert result.max_range > 0 and result.max_range < 0.1   # sin(2*angle) will be small
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test for edge case angle near 90 (e.g. 89.999 degrees, valid as per lt=90)
def test_very_high_angle_launch():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=89.999, initial_height=0, gravity=9.81)
    result = module.run_simulation(params)

    # Expect max_height to be close to v0^2 / (2g) = 100 / 19.62 = 5.0969m
    # Expect total_time to be close to 2*v0/g = 20 / 9.81 = 2.0387s
    # Expect max_range to be very small
    assert math.isclose(result.max_height, 5.0969, rel_tol=1e-3)
    assert math.isclose(result.total_time, 2.0387, rel_tol=1e-3)
    assert result.max_range < 0.01 # Range should be very small as cos(angle) is tiny
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test to ensure parameters_used is correctly populated
def test_parameters_used_population():
    params = ProjectileLaunchParams(initial_velocity=25, launch_angle=35, initial_height=5, gravity=9.8) # Using 9.8 for variety
    result = module.run_simulation(params)
    assert result.parameters_used.initial_velocity == params.initial_velocity
    assert result.parameters_used.launch_angle == params.launch_angle
    assert result.parameters_used.initial_height == params.initial_height
    assert result.parameters_used.gravity == params.gravity
    # Or simply:
    assert result.parameters_used == params

# Test with different gravity (e.g., Moon's gravity)
def test_different_gravity_moon():
    moon_gravity = 1.62
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=45, initial_height=0, gravity=moon_gravity)
    result = module.run_simulation(params)

    # Max Range (R)  = (v0^2 * sin(2*angle)) / g = (100 * 1) / 1.62 = 61.728 m
    # Max Height (H) = (v0^2 * sin^2(angle)) / (2 * g) = (100 * 0.5) / (2 * 1.62) = 15.432 m
    # Total Time (T) = (2 * v0 * sin(angle)) / g = (2 * 10 * sqrt(2)/2) / 1.62 = 8.729 s (approx)

    assert math.isclose(result.max_range, 61.728, rel_tol=1e-3)
    assert math.isclose(result.max_height, 15.432, rel_tol=1e-3)
    assert math.isclose(result.total_time, 8.729, rel_tol=1e-3)
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used.gravity == moon_gravity

# Test for a case where the projectile doesn't move much due to very low velocity but valid angle/height
def test_low_velocity_on_ground():
    params = ProjectileLaunchParams(initial_velocity=0.01, launch_angle=45, initial_height=0, gravity=9.81)
    result = module.run_simulation(params)

    assert result.max_range < 1e-3
    assert result.max_height < 1e-4
    assert result.total_time < 1e-2
    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)

# Test for launch from a significant height with a slightly upward angle
def test_launch_from_height_upward_angle():
    params = ProjectileLaunchParams(initial_velocity=10, launch_angle=30, initial_height=20, gravity=9.81)
    result = module.run_simulation(params)

    # v0y = 10 * sin(30) = 5 m/s
    # Time to reach peak from y0: t_to_peak_from_y0 = v0y / g = 5 / 9.81 = 0.5096s
    # Height gained from y0 to peak: h_gain = v0y^2 / (2g) = 25 / (2 * 9.81) = 1.274 m
    # Absolute max height = y0 + h_gain = 20 + 1.274 = 21.274 m
    assert math.isclose(result.max_height, 21.274, rel_tol=1e-3)

    # Time from peak (at y_max) to ground (y=0): t_fall = sqrt(2 * y_max / g) = sqrt(2 * 21.274 / 9.81) = sqrt(4.337) = 2.0825s
    # Total time = t_to_peak_from_y0 + t_fall = 0.5096 + 2.0825 = 2.5921s
    # This can also be found by solving y(t) = y0 + v0y*t - 0.5*g*t^2 = 0 for t.
    # -4.905*t^2 + 5*t + 20 = 0. Using quadratic formula: t = (-5 +- sqrt(25 - 4*(-4.905)*20)) / (2*-4.905)
    # t = (-5 +- sqrt(25 + 392.4)) / -9.81 = (-5 +- sqrt(417.4)) / -9.81 = (-5 +- 20.43) / -9.81
    # Positive t = (-5 + 20.43) / 9.81 = 15.43 / 9.81 = 1.5728s (This is time from y0 if it could go through ground until v is same magnitude downwards) - no, this is wrong.
    # Positive t for y=0:  t = (v0y + sqrt(v0y^2 + 2*g*y0)) / g = (5 + sqrt(25 + 2*9.81*20)) / 9.81
    # t = (5 + sqrt(25 + 392.4)) / 9.81 = (5 + sqrt(417.4)) / 9.81 = (5 + 20.4303) / 9.81 = 25.4303 / 9.81 = 2.5922s

    assert math.isclose(result.total_time, 2.5922, rel_tol=1e-3)

    # Max range = v0x * total_time = (10 * cos(30)) * 2.5922 = 8.66025 * 2.5922 = 22.449 m
    assert math.isclose(result.max_range, 22.449, rel_tol=1e-3)

    assert math.isclose(result.trajectory[-1].y, 0.0, abs_tol=1e-2)
    assert result.parameters_used == params
