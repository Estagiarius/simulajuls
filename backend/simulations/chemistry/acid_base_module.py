import math
from typing import Type, Optional, Tuple # Removed Dict, Any as they are not directly used in this new version

from fastapi import HTTPException

from backend.simulations.base_simulation import SimulationModule
from backend.simulations.chemistry.models_acid_base import AcidBaseSimulationParams, AcidBaseSimulationResult

KW = 1e-14

def solve_quadratic(a: float, b: float, c: float) -> Optional[float]:
    # Solves ax^2 + bx + c = 0 for x, returning the positive root.
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None

    sqrt_discriminant = math.sqrt(discriminant)
    # For x^2 + Kx - KC = 0 (where a=1, b=K, c=-KC), K > 0, C_initial > 0.
    # The positive root is given by (-K + sqrt(K^2 + 4KC)) / 2.
    # More generally, for ax^2+bx+c=0, if a solution for concentration [H+] or [OH-] is sought,
    # it must be positive.
    x1 = (-b + sqrt_discriminant) / (2*a)
    x2 = (-b - sqrt_discriminant) / (2*a)

    if x1 > 1e-15: # Using a small epsilon to check for effectively positive
        return x1
    elif x2 > 1e-15: # This case might be relevant if 'a' could be negative, but not for typical Ka/Kb forms.
        return x2
    return None


class AcidBaseModule(SimulationModule):
    def get_name(self) -> str:
        return "acid-base"

    def get_display_name(self) -> str:
        return "Reação Ácido-Base (Fortes e Fracos)"

    def get_category(self) -> str:
        return "Chemistry"

    def get_description(self) -> str:
        return "Simula reações ácido-base, incluindo ácidos/bases fortes e fracos (monopróticos puros), calculando o pH e cor do indicador."

    def get_parameter_schema(self) -> Type[AcidBaseSimulationParams]:
        return AcidBaseSimulationParams

    def get_result_schema(self) -> Type[AcidBaseSimulationResult]:
        return AcidBaseSimulationResult

    def run_simulation(self, params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
        if not isinstance(params, AcidBaseSimulationParams):
            raise TypeError("Parâmetros fornecidos não são do tipo AcidBaseSimulationParams.")

        if params.acid_concentration < 0 or params.acid_volume < 0 or \
           params.base_concentration < 0 or params.base_volume < 0:
            raise HTTPException(status_code=400, detail="Concentrações e volumes não podem ser negativos.")
        if params.acid_ka is not None and params.acid_ka <= 0:
            raise HTTPException(status_code=400, detail="Ka do ácido deve ser positivo.")
        if params.base_kb is not None and params.base_kb <= 0:
            raise HTTPException(status_code=400, detail="Kb da base deve ser positivo.")

        acid_volume_l = params.acid_volume / 1000
        base_volume_l = params.base_volume / 1000

        final_ph: Optional[float] = -1.0 # Default to error/undefined
        final_poh: Optional[float] = None
        excess_reactant_val: Optional[str] = None
        status_val: str = "Indeterminado"
        message_val: Optional[str] = None

        is_weak_acid_calc = False
        is_weak_base_calc = False
        ka_val_used = None
        kb_val_used = None

        # Stoichiometry factors (only apply if NOT weak acid/base)
        mols_h_plus_factor = 1.0
        if not params.acid_ka: # Not a weak acid
            normalized_acid_name = params.acid_name.lower().strip() if params.acid_name else ""
            if "h2so4" in normalized_acid_name or "h₂so₄" in normalized_acid_name:
                mols_h_plus_factor = 2.0

        mols_oh_minus_factor = 1.0
        if not params.base_kb: # Not a weak base
            normalized_base_name = params.base_name.lower().strip() if params.base_name else ""
            if "ca(oh)2" in normalized_base_name or "ca(oh)₂" in normalized_base_name:
                mols_oh_minus_factor = 2.0

        # Calculate initial mols based on potential stoichiometry for strong species
        mols_h_initial = params.acid_concentration * acid_volume_l * mols_h_plus_factor
        mols_oh_initial = params.base_concentration * base_volume_l * mols_oh_minus_factor

        # Effective total volume for mixtures, or individual volumes for pure substances later
        total_volume_l = acid_volume_l + base_volume_l


        # Scenario 0: No reactants or zero concentration reactants (effectively pure water)
        is_acid_present_active = acid_volume_l > 0 and params.acid_concentration > 0
        is_base_present_active = base_volume_l > 0 and params.base_concentration > 0

        if not is_acid_present_active and not is_base_present_active:
            final_ph = 7.0
            status_val = "Neutra (água pura)"
            message_val = "Nenhum reagente ativo adicionado."
            mols_h_initial = 0
            mols_oh_initial = 0

        # Scenario 1: Only Acid present (and active)
        elif is_acid_present_active and not is_base_present_active:
            C_acid = params.acid_concentration # This is the initial concentration of the acid solution
            if params.acid_ka:
                is_weak_acid_calc = True
                ka_val_used = params.acid_ka
                # For weak acid HA: Ka = [H+][A-]/[HA] = x^2 / (C_acid - x) => x^2 + Ka*x - Ka*C_acid = 0
                x = solve_quadratic(1, ka_val_used, -ka_val_used * C_acid)
                if x is not None and x > 1e-15:
                    final_ph = -math.log10(x)
                else:
                    message_val = "Não foi possível calcular [H+] para ácido fraco (raiz inválida ou não positiva)."
                    final_ph = -1.0
                status_val = "Ácida"
            else: # Strong acid
                # For strong acid, [H+] is C_acid * factor (e.g., H2SO4)
                conc_h_strong = C_acid * mols_h_plus_factor
                if conc_h_strong > 1e-15:
                    final_ph = -math.log10(conc_h_strong)
                else:
                    final_ph = 7.0 # Effectively water if concentration is zero/negligible
                    message_val = "Concentração de ácido forte muito baixa, pH tratado como neutro."
                status_val = "Ácida"

        # Scenario 2: Only Base present (and active)
        elif is_base_present_active and not is_acid_present_active:
            C_base = params.base_concentration # This is the initial concentration of the base solution
            if params.base_kb:
                is_weak_base_calc = True
                kb_val_used = params.base_kb
                # For weak base B: Kb = [BH+][OH-]/[B] = x^2 / (C_base - x) => x^2 + Kb*x - Kb*C_base = 0
                x = solve_quadratic(1, kb_val_used, -kb_val_used * C_base)
                if x is not None and x > 1e-15:
                    final_poh = -math.log10(x)
                    final_ph = 14.0 - final_poh
                else:
                    message_val = "Não foi possível calcular [OH-] para base fraca (raiz inválida ou não positiva)."
                    final_ph = -1.0
                status_val = "Básica"
            else: # Strong base
                conc_oh_strong = C_base * mols_oh_minus_factor
                if conc_oh_strong > 1e-15:
                    final_poh = -math.log10(conc_oh_strong)
                    final_ph = 14.0 - final_poh
                else:
                    final_ph = 7.0 # Effectively water
                    message_val = "Concentração de base forte muito baixa, pH tratado como neutro."
                status_val = "Básica"

        # Scenario 3: Mixture of Acid and Base (both active)
        elif is_acid_present_active and is_base_present_active:
            if total_volume_l <= 1e-9: # Avoid division by zero if sum of volumes is tiny
                 final_ph = -1.0; message_val="Erro: Volume total da mistura é zero ou desprezível."; status_val="Erro"
            # Case 3.1: Strong Acid + Strong Base (no Ka, no Kb)
            elif not params.acid_ka and not params.base_kb:
                # Mols already adjusted by factors if applicable
                if abs(mols_h_initial - mols_oh_initial) < 1e-9: # Neutralization (using absolute comparison for mols)
                    final_ph = 7.0
                    status_val = "Neutra"
                    excess_reactant_val = "Nenhum"
                    message_val = "Neutralização completa entre ácido forte e base forte."
                elif mols_h_initial > mols_oh_initial:
                    mols_h_excess = mols_h_initial - mols_oh_initial
                    conc_h_final = mols_h_excess / total_volume_l
                    if conc_h_final > 1e-15:
                        final_ph = -math.log10(conc_h_final)
                    else: # Excess H+ is negligible
                        final_ph = 7.0
                        message_val = "Excesso de H+ desprezível após reação forte-forte."
                    status_val = "Ácida"
                    excess_reactant_val = "H+"
                else: # mols_oh_initial > mols_h_initial
                    mols_oh_excess = mols_oh_initial - mols_h_initial
                    conc_oh_final = mols_oh_excess / total_volume_l
                    if conc_oh_final > 1e-15:
                        final_poh = -math.log10(conc_oh_final)
                        final_ph = 14.0 - final_poh
                    else: # Excess OH- is negligible
                        final_ph = 7.0
                        message_val = "Excesso de OH- desprezível após reação forte-forte."
                    status_val = "Básica"
                    excess_reactant_val = "OH-"
            # Cases involving weak acids/bases in mixtures
            elif params.acid_ka or params.base_kb: # This is the block to modify extensively
                # Case 3.2: Weak Acid (Ka) + Strong Base (no Kb)
                if params.acid_ka and not params.base_kb:
                    is_weak_acid_calc = True
                    ka_val_used = params.acid_ka
                    Ka = ka_val_used

                    # mols_h_initial here represents initial mols of HA (weak acid)
                    # mols_oh_initial here represents mols of OH- (strong base) added

                    # Check for equivalence point with a small tolerance
                    # Tolerance should be relative to the scale of mols, e.g., a fraction of total_volume_l
                    # or a very small absolute number if volumes are consistent.
                    # Using a small absolute tolerance for mols comparison here.
                    if abs(mols_h_initial - mols_oh_initial) < 1e-9:
                        status_val = "Básica (Hidrólise de A⁻ no P.E.)"
                        # At P.E., all HA converted to A-. Concentration of A- is initial HA mols / total volume
                        C_anion = mols_h_initial / total_volume_l if total_volume_l > 1e-9 else 0
                        if C_anion > 1e-9:
                            Kb_anion = KW / Ka
                            x = solve_quadratic(1, Kb_anion, -Kb_anion * C_anion) # x = [OH-] from hydrolysis
                            if x is not None and x > 1e-15:
                                final_poh = -math.log10(x)
                                final_ph = 14.0 - final_poh
                            else:
                                message_val = "Erro no cálculo de hidrólise do ânion A⁻ (raiz inválida)."
                                final_ph = -1.0
                        else: # Concentration of anion is negligible
                            final_ph = 7.0
                            message_val = "Ponto de equivalência com concentração de ânion desprezível, pH neutro."
                        excess_reactant_val = "Nenhum (P.E.)"

                    elif mols_oh_initial < mols_h_initial: # Before P.E. - Buffer region HA/A-
                        status_val = "Ácida (Tampão HA/A⁻)"
                        mols_HA_remaining = mols_h_initial - mols_oh_initial
                        mols_A_minus_formed = mols_oh_initial
                        C_HA = mols_HA_remaining / total_volume_l if total_volume_l > 1e-9 else 0
                        C_A_minus = mols_A_minus_formed / total_volume_l if total_volume_l > 1e-9 else 0

                        if C_A_minus > 1e-9 and C_HA > 1e-9: # Henderson-Hasselbalch applicable
                            final_ph = -math.log10(Ka) + math.log10(C_A_minus / C_HA)
                        elif C_HA > 1e-9 : # Mostly HA, very little A- (e.g., start of titration)
                            # Use quadratic for HA dissociation as if it's a pure weak acid solution at this new C_HA
                            x = solve_quadratic(1, Ka, -Ka * C_HA) # x = [H+]
                            final_ph = -math.log10(x) if (x is not None and x > 1e-15) else -1.0
                            if final_ph == -1.0: message_val = "Erro no cálculo do tampão (principalmente HA)."
                        else: # Should imply C_HA is very low, meaning near P.E. or error
                             message_val = "Erro no cálculo do tampão HA/A⁻ (concentração de HA muito baixa, não P.E.)."
                             final_ph = -1.0
                        excess_reactant_val = "HA/A⁻"

                    else: # mols_oh_initial > mols_h_initial (After P.E. - Excess of Strong Base)
                        status_val = "Básica (Excesso de OH⁻)"
                        mols_OH_excess_strong = mols_oh_initial - mols_h_initial
                        conc_OH_final = mols_OH_excess_strong / total_volume_l if total_volume_l > 1e-9 else 0
                        if conc_OH_final > 1e-15:
                            final_poh = -math.log10(conc_OH_final)
                            final_ph = 14.0 - final_poh
                        else: # Excess OH- is negligible, should have been caught by P.E.
                            final_ph = 7.0 # Or -1.0 if error state preferred
                            message_val = "Excesso de base forte desprezível, pH tratado como neutro (ou erro no P.E.)."
                        excess_reactant_val = "OH⁻ (excesso)"

                # Case 3.3: Strong Acid (no Ka) + Weak Base (Kb)
                elif not params.acid_ka and params.base_kb:
                    is_weak_base_calc = True
                    kb_val_used = params.base_kb
                    Kb = kb_val_used

                    # mols_oh_initial here represents initial mols of B (weak base)
                    # mols_h_initial here represents mols of H+ (strong acid) added

                    if abs(mols_oh_initial - mols_h_initial) < 1e-9: # Equivalence Point
                        status_val = "Ácida (Hidrólise de BH⁺ no P.E.)"
                        C_cation = mols_oh_initial / total_volume_l if total_volume_l > 1e-9 else 0 # mols BH+ formed = mols B initial
                        if C_cation > 1e-9:
                            Ka_cation = KW / Kb
                            x = solve_quadratic(1, Ka_cation, -Ka_cation * C_cation) # x = [H+] from hydrolysis
                            if x is not None and x > 1e-15:
                                final_ph = -math.log10(x)
                            else:
                                message_val = "Erro no cálculo de hidrólise do cátion BH⁺ (raiz inválida)."
                                final_ph = -1.0
                        else: # Concentration of cation is negligible
                            final_ph = 7.0
                            message_val = "Ponto de equivalência com concentração de cátion desprezível, pH neutro."
                        excess_reactant_val = "Nenhum (P.E.)"

                    elif mols_h_initial < mols_oh_initial: # Before P.E. - Buffer region B/BH+
                        status_val = "Básica (Tampão B/BH⁺)"
                        mols_B_remaining = mols_oh_initial - mols_h_initial
                        mols_BH_plus_formed = mols_h_initial
                        C_B = mols_B_remaining / total_volume_l if total_volume_l > 1e-9 else 0
                        C_BH_plus = mols_BH_plus_formed / total_volume_l if total_volume_l > 1e-9 else 0

                        if C_BH_plus > 1e-9 and C_B > 1e-9: # Henderson-Hasselbalch for base buffer
                            # pOH = pKb + log([BH+]/[B])
                            final_poh = -math.log10(Kb) + math.log10(C_BH_plus / C_B)
                            final_ph = 14.0 - final_poh
                        elif C_B > 1e-9: # Mostly B, very little BH+ (e.g., start of titration)
                            # Use quadratic for B dissociation
                            x = solve_quadratic(1, Kb, -Kb * C_B) # x = [OH-]
                            if x is not None and x > 1e-15:
                                final_poh = -math.log10(x)
                                final_ph = 14.0 - final_poh
                            else:
                                final_ph = -1.0
                                message_val = "Erro no cálculo do tampão (principalmente B)."
                        else:
                            message_val = "Erro no cálculo do tampão B/BH⁺ (concentração de B muito baixa, não P.E.)."
                            final_ph = -1.0
                        excess_reactant_val = "B/BH⁺"

                    else: # mols_h_initial > mols_oh_initial (After P.E. - Excess of Strong Acid)
                        status_val = "Ácida (Excesso de H⁺)"
                        mols_H_excess_strong = mols_h_initial - mols_oh_initial
                        conc_H_final = mols_H_excess_strong / total_volume_l if total_volume_l > 1e-9 else 0
                        if conc_H_final > 1e-15:
                            final_ph = -math.log10(conc_H_final)
                        else:
                            final_ph = 7.0 # Or -1.0
                            message_val = "Excesso de ácido forte desprezível, pH tratado como neutro (ou erro no P.E.)."
                        excess_reactant_val = "H⁺ (excesso)"

                # Case 3.4: Weak Acid (Ka) + Weak Base (Kb)
                elif params.acid_ka and params.base_kb:
                    is_weak_acid_calc = True
                    is_weak_base_calc = True
                    ka_val_used = params.acid_ka
                    kb_val_used = params.base_kb
                    message_val = "Cálculo para ácido fraco vs. base fraca não é suportado nesta versão."
                    final_ph = -1.0
                    status_val = "Indeterminado (WA vs WB)"

                else: # Should not happen if logic is structured correctly (e.g. one is weak, other must be strong or also weak)
                    message_val = "Combinação de ácido/base fraco não reconhecida para mistura (lógica interna). Contate o suporte."
                    final_ph = -1.0
                    status_val = "Erro Interno"

            else: # Fallback for any unhandled strong/weak mix - this should ideally not be reached if above logic is complete
                message_val = "Combinação de ácido/base não reconhecida para mistura (fallback geral). Contate o suporte."
                final_ph = -1.0
                status_val = "Erro Interno"
        else: # Should be covered by Scenario 0, but as a fallback
            if not (final_ph == 7.0 and status_val == "Neutra (água pura)"):
                final_ph = 7.0
                status_val = "Neutra (água)"
                message_val = message_val or "Configuração de entrada não resultou em reação calculável ou foi tratada como água."

        # pH and pOH constraints and rounding
        if final_ph is not None and final_ph != -1.0: # If pH was calculated and not an error
            if final_ph < 0.0: final_ph = 0.0
            if final_ph > 14.0: final_ph = 14.0
            final_ph = round(final_ph, 2)

            # Calculate pOH from pH if pH is valid and pOH wasn't directly set or needs update
            # For pure base cases or strong base excess, pOH is set directly.
            # For other cases where pH is primary, pOH is derived.
            if final_ph >= 0.0 and final_ph <= 14.0:
                 if final_poh is None or not ((is_base_present_active and not is_acid_present_active and params.base_kb) or \
                                             (is_acid_present_active and is_base_present_active and not params.acid_ka and not params.base_kb and mols_oh_initial > mols_h_initial) or \
                                             (is_acid_present_active and is_base_present_active and params.acid_ka and not params.base_kb and mols_oh_initial > mols_h_initial) or \
                                             (is_acid_present_active and is_base_present_active and not params.acid_ka and params.base_kb and mols_h_initial < mols_oh_initial and abs(mols_oh_initial - mols_h_initial) > 1e-9) ) : # check if pOH was primary calc
                    final_poh = round(14.0 - final_ph, 2)
                 elif final_poh is not None: # pOH was primary, ensure it's rounded
                    final_poh = round(final_poh, 2)
            else: # pH is out of typical range (should be clamped, but defensive)
                 final_poh = None

        elif final_ph == -1.0 : # Error case explicitly indicated by final_ph = -1.0
            final_poh = None # No valid pOH if pH calculation failed or indicated error

        # Indicator color logic
        indicator_color_val: Optional[str] = None
        if params.indicator_name and final_ph is not None and final_ph != -1.0:
            indicator_name_lower = params.indicator_name.lower().strip()
            if indicator_name_lower == "fenolftaleína":
                if final_ph < 8.2: indicator_color_val = "Incolor"
                elif final_ph <= 10.0: indicator_color_val = "Rosa claro/Róseo"
                else: indicator_color_val = "Carmim/Magenta"
            elif indicator_name_lower == "azul de bromotimol":
                if final_ph < 6.0: indicator_color_val = "Amarelo"
                elif final_ph <= 7.6: indicator_color_val = "Verde"
                else: indicator_color_val = "Azul"
            elif indicator_name_lower == "vermelho de metila":
                if final_ph < 4.4: indicator_color_val = "Vermelho"
                elif final_ph <= 6.2: indicator_color_val = "Laranja"
                else: indicator_color_val = "Amarelo"
            elif indicator_name_lower == "alaranjado de metila":
                if final_ph < 3.1: indicator_color_val = "Vermelho"
                elif final_ph <= 4.4: indicator_color_val = "Laranja"
                else: indicator_color_val = "Amarelo"
            else:
                indicator_color_val = "Indicador não reconhecido"
                current_message = f"Indicador '{params.indicator_name}' não suportado."
                message_val = f"{message_val} {current_message}".strip() if message_val else current_message

        # Determine actual total volume for result reporting
        # For pure substances, total_volume_l was not used for pH calculation, but for reporting it's the volume of that substance
        reported_total_volume_ml: float
        if is_acid_present_active and not is_base_present_active:
            reported_total_volume_ml = acid_volume_l * 1000
        elif is_base_present_active and not is_acid_present_active:
            reported_total_volume_ml = base_volume_l * 1000
        elif is_acid_present_active and is_base_present_active: # Mixture
            reported_total_volume_ml = total_volume_l * 1000
        else: # Pure water / no active reactants
            reported_total_volume_ml = 0 # Or could be sum of volumes if they were non-zero but concentrations were zero

        return AcidBaseSimulationResult(
            final_ph=final_ph if final_ph is not None else -1.0, # Ensure -1.0 for error if None slips through
            final_poh=final_poh,
            total_volume_ml=round(reported_total_volume_ml, 3),
            mols_h_plus_initial=round(mols_h_initial, 9),
            mols_oh_minus_initial=round(mols_oh_initial, 9),
            excess_reactant=excess_reactant_val,
            status=status_val,
            indicator_color=indicator_color_val,
            message=message_val,
            parameters_used=params.model_dump(),
            is_weak_acid_calculation=is_weak_acid_calc,
            is_weak_base_calculation=is_weak_base_calc,
            ka_used=ka_val_used if is_weak_acid_calc else None,
            kb_used=kb_val_used if is_weak_base_calc else None
        )
