"""
Módulo de simulação para Lançamento Oblíquo de Projétil.

Este módulo implementa a lógica para simular o movimento de um projétil
lançado obliquamente (ou horizontalmente) sob a ação da gravidade,
desconsiderando a resistência do ar. Ele calcula componentes da velocidade inicial,
tempo total de voo, alcance máximo, altura máxima atingida e a trajetória completa
do projétil.
"""
import math
from typing import List, Optional, Type, Any, Dict

from fastapi import HTTPException # Para validação de entrada, se mantida no módulo
from pydantic import BaseModel # Usado por Type[BaseModel]

from backend.simulations.base_simulation import SimulationModule, BaseSimulationParams # BaseSimulationParams não é estritamente necessário aqui, mas bom para contexto
from .models_projectile import ProjectileLaunchParams, TrajectoryPoint, ProjectileLaunchResult

class ProjectileModule(SimulationModule):
    # Implementa a interface SimulationModule para a simulação de Lançamento de Projétil.

    def get_name(self) -> str:
        # Retorna o nome identificador da simulação.
        return "projectile-launch"

    def get_display_name(self) -> str:
        # Retorna o nome de exibição da simulação.
        return "Lançamento Oblíquo"

    def get_category(self) -> str:
        # Retorna a categoria da simulação.
        return "Física"

    def get_description(self) -> str:
        # Retorna uma breve descrição da simulação.
        return "Analise a trajetória de um projétil em lançamento oblíquo."

    def get_parameter_schema(self) -> Type[ProjectileLaunchParams]:
        # Retorna o tipo do modelo Pydantic para os parâmetros de entrada.
        return ProjectileLaunchParams

    def get_result_schema(self) -> Type[ProjectileLaunchResult]:
        # Retorna o tipo do modelo Pydantic para os resultados da simulação.
        return ProjectileLaunchResult

    def run_simulation(self, params: ProjectileLaunchParams) -> ProjectileLaunchResult:
        # Executa a lógica da simulação de lançamento de projétil.
        # Os parâmetros de entrada (params) já foram validados pelo Pydantic
        # conforme definido em ProjectileLaunchParams (ex: gt=0 para velocidade, ge=0 para altura).

        # Extração de parâmetros para facilitar o uso nas fórmulas.
        g = params.gravity # Aceleração da gravidade (m/s²)
        v0 = params.initial_velocity # Velocidade inicial (m/s)
        angle_rad = math.radians(params.launch_angle) # Ângulo de lançamento em radianos
        y0 = params.initial_height # Altura inicial (m)

        # Cálculo das componentes da velocidade inicial.
        v0x = v0 * math.cos(angle_rad) # Componente horizontal da velocidade inicial (Vx)
        v0y = v0 * math.sin(angle_rad) # Componente vertical da velocidade inicial (Vy)

        # Cálculo da altura máxima (H_max).
        # H_max = y0 + (v0y^2) / (2g)
        # A altura máxima é calculada a partir da altura inicial y0 mais a altura adicional
        # que o projétil ganha devido à sua velocidade vertical inicial v0y.
        # Se v0y for 0 ou negativo (lançamento para baixo), a altura adicional é 0.
        max_h_from_y0 = (v0y**2) / (2 * g) if v0y > 0 else 0
        max_h = y0 + max_h_from_y0

        # Cálculo do tempo total de voo (T_total).
        # Usamos a equação do movimento vertical: y(t) = y0 + v0y*t - 0.5*g*t^2
        # Para encontrar o tempo quando y(t) = 0 (atinge o solo), resolvemos a equação quadrática:
        # 0.5*g*t^2 - v0y*t - y0 = 0
        # O discriminante é delta = (-v0y)^2 - 4*(0.5g)*(-y0) = v0y^2 + 2*g*y0
        discriminant_calc = (v0y**2) + (2 * g * y0)

        if discriminant_calc < 0:
            # Isso não deve ocorrer em cenários físicos típicos com y0 >= 0 e g > 0.
            # Indicaria que o projétil nunca atinge y=0 se lançado de y0 > 0 e v0y <=0 (já no solo ou abaixo).
            # No entanto, com y0 >=0, o discriminante será sempre >=0.
            total_t = 0.0
        else:
            # A solução positiva da equação quadrática para t é:
            # t = (v0y + sqrt(discriminante)) / g
            # Esta fórmula calcula o tempo para atingir o solo (y=0).
            if y0 == 0 and abs(v0y) < 1e-9: # Caso especial: lançamento horizontal do solo (ângulo 0, y0=0)
                 total_t = 0.0 # Tempo de voo é zero, pois já está no solo sem velocidade vertical.
            elif y0 == 0: # Lançamento do solo (y0=0) com ângulo > 0.
                 total_t = (2 * v0y) / g # Fórmula simplificada para y0=0: T = 2*v0y/g
            else: # Lançamento de uma altura y0 > 0.
                 total_t = (v0y + math.sqrt(discriminant_calc)) / g

        if total_t < 0: # Tempo não pode ser negativo.
            total_t = 0.0

        # Cálculo do alcance máximo (R_max).
        # R_max = v0x * T_total
        # O alcance é a distância horizontal percorrida durante o tempo total de voo.
        max_r = v0x * total_t

        # Geração dos pontos da trajetória.
        trajectory_points: List[TrajectoryPoint] = []
        time_step = 0.05 # Intervalo de tempo para calcular os pontos da trajetória.
        current_time = 0.0

        if total_t > 1e-6: # Só gera trajetória se houver tempo de voo significativo.
            # Itera em passos de tempo até o tempo total de voo.
            while current_time <= total_t + 1e-9: # Adiciona um pequeno epsilon para garantir inclusão do último ponto.
                # Equações do movimento:
                # x(t) = v0x * t
                # y(t) = y0 + v0y * t - 0.5 * g * t^2
                x = v0x * current_time
                y = y0 + v0y * current_time - 0.5 * g * current_time**2

                if y < 0: y = 0.0 # Garante que o projétil não vá abaixo do solo (y=0).

                trajectory_points.append(TrajectoryPoint(time=round(current_time,3), x=round(x,3), y=round(y,3)))

                # Condição para parar se atingir o solo antes do tempo total calculado
                # (pode ocorrer devido a arredondamentos no time_step).
                # No entanto, o loop principal até total_t + epsilon deve ser suficiente.
                # if y == 0 and current_time > 1e-6 and current_time < total_t - 1e-9 :
                #     pass

                if current_time > total_t: # Garante que não ultrapasse significativamente total_t.
                    break
                current_time += time_step
                # Interrupção de segurança para simulações muito longas (mais de 2000 pontos).
                if len(trajectory_points) > 2000:
                    break

            # Garante que o último ponto da trajetória seja exatamente em (total_t, y=0),
            # caso não tenha sido capturado precisamente pelo loop.
            if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4 :
                x_final = v0x * total_t
                # Adiciona o ponto final se não estiver lá ou se o último ponto não for o tempo total.
                trajectory_points.append(TrajectoryPoint(time=round(total_t,3), x=round(x_final,3), y=0.0))
            elif trajectory_points[-1].y != 0.0 and abs(trajectory_points[-1].time - total_t) < 1e-4:
                 # Corrige a altura do último ponto se ele estiver no tempo total mas y não for exatamente 0.
                 trajectory_points[-1].y = 0.0

        else: # Caso não haja tempo de voo (ex: projétil no solo sem velocidade para cima).
            trajectory_points.append(TrajectoryPoint(time=0.0, x=0.0, y=round(y0,3)))
            # Se começa no solo sem velocidade, a altura máxima também é zero.
            if y0 == 0 and abs(v0) < 1e-9: # Verifica se v0 é praticamente zero.
                max_h = 0.0


        # Retorna o objeto de resultado da simulação com todos os valores calculados e arredondados.
        return ProjectileLaunchResult(
            initial_velocity_x=round(v0x, 3),
            initial_velocity_y=round(v0y, 3),
            total_time=round(total_t, 3),
            max_range=round(max_r, 3),
            max_height=round(max_h, 3),
            trajectory=trajectory_points,
            parameters_used=params # Atribui os parâmetros de entrada diretamente.
        )
