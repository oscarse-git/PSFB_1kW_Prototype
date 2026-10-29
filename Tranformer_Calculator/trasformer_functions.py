import numpy as np
import math

def diameter(sec): return np.round(np.sqrt(sec * 4 / np.pi),2)

def section(diam): return np.round(np.pi * diam**2 / 4, 2)

def current_density(I, sec): return I / sec

def current_windings(P, V, ratio):
    Is = P/V
    Ip = Is * ratio
    return np.round(Ip, 2), np.round(Is, 2)

def winding_surface(sec1, sec2, n1 , n2, fillFactor): 
    return np.round((sec1 * n1 + sec2 * n2) / fillFactor, 2)

def windings(Vmax, ratio, Ton, Bmax, Ae):
    n1 = Vmax * Ton / (2 * abs(Bmax) * Ae)
    n2 = n1 * ratio

    return math.ceil(n1), math.ceil(n2)

def correct_transformer_Aw(transformer):
    if transformer['type_id'] == 'TOROID': return transformer['Aw']
    else: return transformer['Aw']*2

def calculate_loss_const(P1, f1, P2, f2, Btest):
    alpha1 = f1 * (Btest ** 2)
    alpha2 = f2 * (Btest ** 2)

    beta1 = (f1 ** 2) * (Btest ** 2)
    beta2 = (f2 ** 2) * (Btest ** 2)

    kf = ((alpha1 * P2) - (alpha2 * P1)) / ((beta2 * alpha1) - (beta1 * alpha2))
    kh = (P1 - kf * beta1) / alpha1

    return kh, kf

def check_geom_windings(surfaceReal, surface_available): 
    if surface_available > surfaceReal: return True
    else: return False

def calculate_induction(Vmax, Ton, n1, Ae): 
    return np.round(Vmax * Ton / (2 * n1 * Ae), 4)

def calculate_inductance(AL, n1, n2):
    Lp = AL * n1**2
    Ls = AL * n2**2

    return Lp, Ls

def avg_len_sqrt_core(diamP, diamS, n1, n2, height, wide, depth, sleeveThickness):
    startPerim = 2 * wide + 2 * depth + 8 * sleeveThickness

    maxHeighS = height - sleeveThickness * 2
    stackedPrimary = math.ceil(diamP * n1 / (maxHeighS))
    stackedSecondary = math.ceil(diamS * n2 / (maxHeighS))

    primaryThick = diamP * stackedPrimary
    secondaryThick = diamS * stackedSecondary

    # secondary in the inside
    avgPrimaryLength = startPerim + secondaryThick * 8 + primaryThick * 4
    avgSecondaryLength =  startPerim + secondaryThick * 4

    return avgPrimaryLength, avgSecondaryLength

def core_loss_estimation(volume, lossMeas, fMeas, BmaxMeas, fOperation, BmaxOperation):
    # Based on steimetz equation P_density = kh * f * Bmax^2 + kf * f^2 * Bmax^2
    # If f2 = alpha * f1 and Bmax2 = beta * Bmax1:
    #   
    #   P_density_2 <= P_density_1 * alpha^2 * beta^2
    #   P_density_2 >= P_density_1 * alpha * beta


    alpha = fOperation / fMeas
    beta = BmaxOperation / BmaxMeas

    upper = np.round(volume * lossMeas * (alpha ** 2) * (beta ** 2), 4)
    lower = np.round(volume * lossMeas * (alpha) * (beta), 4)

    return [lower, upper]

def avg_len_round_core(diamP, diamS, n1, n2, height, diameter, sleeveThickness):
    startRadius = diameter / 2

    maxHeighS = height - sleeveThickness * 2
    stackedPrimary = math.ceil(diamP * n1 / (maxHeighS))
    stackedSecondary = math.ceil(diamS * n2 / (maxHeighS))

    primaryThick = diamP * stackedPrimary
    secondaryThick = diamS * stackedSecondary

    # seconday in the inside
    avgPrimaryLength = 2 * np.pi * (startRadius + secondaryThick + primaryThick/2)
    avgSecondaryLength = 2 * np.pi * (startRadius + secondaryThick / 2)

    return avgPrimaryLength, avgSecondaryLength

def calculate_resistance(transformer, secP, secS, n1, n2, sleeveThickness = 0, 
                         resistivity = 1.724e-8, secConst = 1):

    diamP = diameter(secP)
    diamS = diameter(secS)

    if transformer['type_id'] == 'EFD':
        avgPlength, avgSlength = avg_len_sqrt_core(diamP, diamS, n1, n2,
                            transformer['D']*2, transformer['F'], transformer['K'], sleeveThickness)
        
    elif transformer['type_id'] == 'ETD':
        avgPlength, avgSlength = avg_len_round_core(diamP, diamS, n1, n2,
                            transformer['D'] * 2, transformer['F'], sleeveThickness)

        
    elif transformer['type_id'] == 'PQ':
        avgPlength, avgSlength = avg_len_round_core(diamP, diamS, n1, n2,
                    transformer['D'] * 2, transformer['F'], sleeveThickness)


    elif transformer['type_id'] == 'TOROID':
        avgPlength = 0
        avgSlength = 0

    elif transformer['type_id'] == 'RM':
        avgPlength, avgSlength = avg_len_round_core(diamP, diamS, n1, n2,
                    transformer['D'] * 2, transformer['F'], sleeveThickness)

    else:
        avgPlength = 0
        avgSlength = 0

    Rp = secConst * resistivity * avgPlength / secP
    Rs = secConst * resistivity * avgSlength / secS

    return Rp, Rs

