import math
from typing import List, Optional, Type, Any, Dict

from fastapi import HTTPException # For input validation if kept in module
from pydantic import BaseModel # BaseModel is used by Type[BaseModel]

from ..base_simulation import SimulationModule, BaseSimulationParams # BaseSimulationParams not strictly needed here but good for context
from .models_projectile import ProjectileLaunchParams, TrajectoryPoint, ProjectileLaunchResult

class ProjectileModule(SimulationModule):

    def get_name(self) -> str:
        return "projectile-launch"

    def get_display_name(self) -> str:
        return "Lançamento Oblíquo"

    def get_category(self) -> str:
        return "Física"

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

        g = params.gravity
        v0 = params.initial_velocity
        angle_rad = math.radians(params.launch_angle)
        y0 = params.initial_height

        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)

        max_h_from_y0 = (v0y**2) / (2 * g) if v0y > 0 else 0
        max_h = y0 + max_h_from_y0

        # discriminant = b^2 - 4ac where a = -g/2, b = v0y, c = y0 (for y(t) = y0 + v0y*t - 0.5*g*t^2 = 0)
        # Or, for 0.5*g*t^2 - v0y*t - y0 = 0, a = 0.5g, b = -v0y, c = -y0
        discriminant_calc = (v0y**2) + (2 * g * y0) # Simplified from (-v0y)^2 - 4*(0.5g)*(-y0) = v0y^2 + 2*g*y0

        if discriminant_calc < 0: # Should not happen if y0 >= 0 and g > 0
            total_t = 0
        else:
            # t = (v0y + sqrt(v0y^2 + 2gy0)) / g  (time to reach y=0 from y0, taking positive root for future time)
            # This formula is for when the object hits the ground (y=0).
            # If v0y is negative (launched downwards) or zero, it hits ground.
            # If v0y is positive (launched upwards), it goes up, then comes down.
            if y0 == 0 and v0y == 0: # Starts on ground, no vertical velocity (e.g. angle=0, y0=0)
                 total_t = 0
            elif y0 == 0: # Starts on ground with some vertical velocity (angle > 0, y0=0)
                 total_t = (2 * v0y) / g
            else: # Starts at y0 > 0
                 total_t = (v0y + math.sqrt(discriminant_calc)) / g

        if total_t < 0: # Should not occur with proper physics unless initial conditions are unusual
            total_t = 0

        max_r = v0x * total_t

        trajectory_points: List[TrajectoryPoint] = []
        time_step = 0.05
        current_time = 0.0

        if total_t > 1e-6: # Only generate trajectory if there's flight time
            while current_time <= total_t + 1e-9: # Add small epsilon to ensure last point is included
                x = v0x * current_time
                y = y0 + v0y * current_time - 0.5 * g * current_time**2

                if y < 0: y = 0 # Object cannot go below ground

                trajectory_points.append(TrajectoryPoint(time=round(current_time,3), x=round(x,3), y=round(y,3)))

                if y == 0 and current_time > 1e-6 and current_time < total_t - 1e-9 : # Stop if hits ground before total_t (e.g. due to rounding in time_step)
                    # This check might be redundant if total_t is calculated accurately as time to hit ground.
                    pass # Loop continues till total_t

                if current_time > total_t: # Ensure we don't overshoot total_t significantly
                    break
                current_time += time_step
                # Ensure the loop terminates, especially if total_t is very small or time_step is tiny
                if len(trajectory_points) > 2000: # Safety break for very long simulations
                    break

            # Ensure final point at total_t and y=0 is included if not already captured
            if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4 :
                x_final = v0x * total_t
                trajectory_points.append(TrajectoryPoint(time=round(total_t,3), x=round(x_final,3), y=0.0))
            elif trajectory_points[-1].y != 0.0 and abs(trajectory_points[-1].time - total_t) < 1e-4:
                 trajectory_points[-1].y = 0.0 # Correct y for the last point if it's at total_t

        else: # No flight time (e.g. on the ground with no upward velocity)
            trajectory_points.append(TrajectoryPoint(time=0.0, x=0.0, y=y0))
            if y0 == 0 and v0 == 0:
                max_h = 0.0


        return ProjectileLaunchResult(
            initial_velocity_x=round(v0x, 3),
            initial_velocity_y=round(v0y, 3),
            total_time=round(total_t, 3),
            max_range=round(max_r, 3),
            max_height=round(max_h, 3),
            trajectory=trajectory_points,
            parameters_used=params # Assign the input params directly
        )
