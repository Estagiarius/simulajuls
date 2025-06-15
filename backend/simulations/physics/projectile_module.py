import math
from typing import List, Optional, Type # Removed Any, Dict as they are not explicitly used after changes
# BaseModel is not directly used, Type is sufficient for parameter_schema
from backend.simulations.base_simulation import SimulationModule # BaseSimulationParams not strictly needed here
from .models_projectile import ProjectileLaunchParams, TrajectoryPoint, ProjectileLaunchResult, OutputUnitSelection
from .unit_conversion import (
    convert_velocity_to_base,
    convert_length_to_base,
    convert_velocity_from_base,
    convert_length_from_base,
    convert_time_from_base
)

class ProjectileModule(SimulationModule):

    def get_name(self) -> str:
        return "projectile-launch"

    def get_display_name(self) -> str:
        return "Lançamento Oblíquo"

    def get_category(self) -> str:
        return "Physics"

    def get_description(self) -> str:
        return "Analise a trajetória de um projétil em lançamento oblíquo."

    def get_parameter_schema(self) -> Type[ProjectileLaunchParams]:
        return ProjectileLaunchParams

    def get_result_schema(self) -> Type[ProjectileLaunchResult]:
        return ProjectileLaunchResult

    def run_simulation(self, params: ProjectileLaunchParams) -> ProjectileLaunchResult:
        # Logic moved from perform_projectile_launch_simulation in main.py

        # Validação de Parâmetros de Entrada (using Pydantic Field constraints now, but explicit checks can be kept for complex cross-field validation or very specific error messages)
        # The Pydantic Field constraints in models_projectile.py (e.g., gt=0) already handle these.
        # If an invalid value is passed that Pydantic catches, FastAPI will return a 422 error before this code is even reached.
        # However, if these checks were more complex (e.g. relationships between fields), they could remain.
        # For this refactoring, we assume Pydantic's validation is sufficient for these simple cases.
        # If specific HTTPExceptions are desired for these, they can be re-added, but it's often cleaner to let Pydantic handle it.

        # Example of keeping explicit validation if needed (though redundant if Pydantic models are well-defined):
        # if params.initial_velocity <= 0: raise HTTPException(status_code=400, detail="Velocidade inicial deve ser positiva.")
        # if not (0 <= params.launch_angle < 90): raise HTTPException(status_code=400, detail="Ângulo de lançamento deve estar entre 0 e 90 graus (0 <= angle < 90).")
        # if params.initial_height < 0: raise HTTPException(status_code=400, detail="Altura inicial não pode ser negativa.")
        # if params.gravity <= 0: raise HTTPException(status_code=400, detail="Gravidade deve ser positiva.")
        # Note: The original check was `0 < params.launch_angle < 90`. The model uses `ge=0, lt=90`.
        # For a true oblique launch, angle > 0 is typical. If angle = 0, it's a horizontal launch.
        # The problem description mentions "Lançamento Oblíquo", so `gt=0` might be more appropriate for launch_angle if strictly oblique.
        # The model has `ge=0` allowing horizontal launch. We'll stick to model validation.

        # Input conversion to SI units
        # Gravity is assumed to be in m/s^2 as per model description.
        g_si = params.gravity if params.gravity is not None else 9.81 # Default if not provided

        v0_si = convert_velocity_to_base(params.initial_velocity, params.initial_velocity_unit or "m/s")
        y0_si = convert_length_to_base(params.initial_height if params.initial_height is not None else 0.0, params.initial_height_unit or "m")

        angle_rad = math.radians(params.launch_angle)

        v0x_si = v0_si * math.cos(angle_rad)
        v0y_si = v0_si * math.sin(angle_rad)

        # Calculations in SI units
        max_h_from_y0_si = (v0y_si**2) / (2 * g_si) if v0y_si > 0 else 0
        max_h_si = y0_si + max_h_from_y0_si

        discriminant_calc_si = (v0y_si**2) + (2 * g_si * y0_si)

        if discriminant_calc_si < -1e-9: # Added tolerance for floating point issues
            total_t_si = 0.0
        else:
            if discriminant_calc_si < 0: discriminant_calc_si = 0 # Clamp if very slightly negative due to precision

            if y0_si == 0 and abs(v0y_si) < 1e-9: # Starts on ground, no vertical velocity
                 total_t_si = 0.0
            elif y0_si == 0: # Starts on ground with some vertical velocity
                 total_t_si = (2 * v0y_si) / g_si
            else: # Starts at y0_si > 0
                 total_t_si = (v0y_si + math.sqrt(discriminant_calc_si)) / g_si

        if total_t_si < 0: total_t_si = 0.0 # Ensure non-negative time

        max_r_si = v0x_si * total_t_si

        trajectory_points_si: List[TrajectoryPoint] = []
        time_step_si = 0.05 # Default time_step for SI calculations
        current_time_si = 0.0

        min_desired_points = 20
        max_points_limit = 2000

        if total_t_si > 1e-5: # Effectively non-zero flight time
            if (total_t_si / time_step_si) < min_desired_points:
                time_step_si = total_t_si / min_desired_points

            if (total_t_si / time_step_si) > max_points_limit:
                time_step_si = total_t_si / max_points_limit
        # The case for total_t_si <= 1e-6 (effectively zero flight time) is handled later by appending one point.
        # No special 'elif' needed here for adaptive time step, as it's guarded by total_t_si > 1e-5.

        if total_t_si > 1e-6: # Generate trajectory if there's significant flight time
            while current_time_si <= total_t_si + 1e-9: # Add epsilon for last point
                x_si = v0x_si * current_time_si
                y_si = y0_si + v0y_si * current_time_si - 0.5 * g_si * current_time_si**2

                if y_si < 0: y_si = 0.0 # Object cannot go below ground

                # Store SI points temporarily
                trajectory_points_si.append(TrajectoryPoint(time=current_time_si, x=x_si, y=y_si))

                if y_si == 0.0 and current_time_si > 1e-6 and abs(current_time_si - total_t_si) > 1e-9 :
                    # If it hits ground before calculated total_t_si (e.g. due to time step choice)
                    # and it's not already the last point, break early.
                    # This ensures trajectory stops when it hits ground.
                    total_t_si = current_time_si # Adjust total_t_si to actual impact time
                    break

                if current_time_si > total_t_si and abs(current_time_si - total_t_si) > 1e-9 :
                    break

                current_time_si += time_step_si
                if time_step_si < 1e-9 : # Avoid infinite loop if time_step becomes zero
                    if len(trajectory_points_si) >= min_desired_points: break
                    else: break # Pathological case

                if len(trajectory_points_si) > max_points_limit + 10: # Safety break
                    break

            # Ensure final point at total_t_si (and y_si=0 if applicable) is captured
            if not trajectory_points_si or abs(trajectory_points_si[-1].time - total_t_si) > 1e-4 :
                x_final_si = v0x_si * total_t_si
                y_final_si = y0_si + v0y_si * total_t_si - 0.5 * g_si * total_t_si**2
                if y_final_si < 0 : y_final_si = 0.0
                trajectory_points_si.append(TrajectoryPoint(time=total_t_si, x=x_final_si, y=y_final_si))
            elif trajectory_points_si: # If list is not empty
                 # Correct y for the last point if it should be at ground
                 last_point = trajectory_points_si[-1]
                 if abs(last_point.time - total_t_si) < 1e-4 and last_point.y != 0.0 and y0_si + v0y_si * total_t_si - 0.5 * g_si * total_t_si**2 < 1e-3 :
                     trajectory_points_si[-1].y = 0.0


        else: # No significant flight time or zero flight time
            # Append a single point representing the initial state (in SI units for now)
            trajectory_points_si.append(TrajectoryPoint(time=0.0, x=0.0, y=y0_si))
            if y0_si == 0.0 and abs(v0_si) < 1e-9 : # if started on ground with no velocity
                max_h_si = 0.0 # Max height is initial height

        # Output Conversion
        output_units = params.output_units if params.output_units is not None else OutputUnitSelection()

        final_v0x = convert_velocity_from_base(v0x_si, output_units.velocity_unit or "m/s")
        final_v0y = convert_velocity_from_base(v0y_si, output_units.velocity_unit or "m/s")
        final_total_t = convert_time_from_base(total_t_si, output_units.time_unit or "s")
        final_max_r = convert_length_from_base(max_r_si, output_units.range_unit or "m")
        final_max_h = convert_length_from_base(max_h_si, output_units.height_unit or "m")

        final_trajectory_points: List[TrajectoryPoint] = []
        for point_si in trajectory_points_si:
            # Time is always in seconds for trajectory points as per model spec
            time_val = round(point_si.time, 3)
            x_val = round(convert_length_from_base(point_si.x, output_units.range_unit or "m"), 3)
            y_val = round(convert_length_from_base(point_si.y, output_units.height_unit or "m"), 3)
            final_trajectory_points.append(TrajectoryPoint(time=time_val, x=x_val, y=y_val))

        # Ensure at least one point in final trajectory if total_t_si was ~0
        if not final_trajectory_points:
             x_val = round(convert_length_from_base(0.0, output_units.range_unit or "m"),3)
             y_val = round(convert_length_from_base(y0_si, output_units.height_unit or "m"),3)
             final_trajectory_points.append(TrajectoryPoint(time=0.0, x=x_val, y=y_val))


        return ProjectileLaunchResult(
            initial_velocity_x=round(final_v0x, 3),
            initial_velocity_y=round(final_v0y, 3),
            total_time=round(final_total_t, 3),
            max_range=round(final_max_r, 3),
            max_height=round(final_max_h, 3),
            trajectory=final_trajectory_points,

            initial_velocity_x_unit=output_units.velocity_unit or "m/s",
            initial_velocity_y_unit=output_units.velocity_unit or "m/s",
            total_time_unit=output_units.time_unit or "s",
            max_range_unit=output_units.range_unit or "m",
            max_height_unit=output_units.height_unit or "m",

            parameters_used=params
        )
