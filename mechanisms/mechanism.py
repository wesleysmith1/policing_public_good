import math
import csv
from decimal import Decimal
import numpy as np

from mechanisms.helpers import format_template_numbers

def mean(l):
    return sum(l)/len(l)

def calculate_thetas(E,gam, n):
    """return list of thetas"""
    results = []
    for i, e_i in enumerate(E):
        copy = E.copy()
        E_others = np.delete(copy, i)
        
        theta = sum([(e_j - sum(E_others)/(n-1))**2 for e_j in E_others])
        
        theta *= (gam/2)*(1/(n-2))
        
        results.append(theta)
    return results

def calculate_theta(E, e, gam, n):
    """
    calculate only one theta
    
    E = vector of quantities
    e = quantity of player to calculate
    gam = constant
    n = number of participants
    """
    
    copy = E.copy()
    i = list(E).index(e)
    E_others = np.delete(copy, i)
    
    theta = sum([(e_j - sum(E_others)/(n-1))**2 for e_j in E_others])
        
    theta *= (gam/2)*(1/(n-2))
    
    return theta

def calculate_costs(N, gam, E, qq, n_id=np.array([1, 3]), mechanism="OGL", r=0):
    E = np.array(E)
    # n = len(E)
    n = 5 if mechanism == "OGL" else 2
    cost_baseshare = qq/N*sum(E) - r
    cost_theta = np.array([])

    em = []
    for id in n_id:
        em.append(E[id-2])
    E = em

    if mechanism == 'MGL':
        cost_varpenalty = gam/2*(n/(n-1))*(E-mean(E))**2

        participant_costs = np.repeat( 0, repeats = N)
        participant_costs[[ i-2 for i in n_id]] = cost_baseshare + cost_varpenalty
        return participant_costs
    elif mechanism == 'OGL':
        cost_varpenalty = gam/2*(n/(n-1))*(E-mean(E))**2

        cost_theta = np.array(calculate_thetas(E, gam, n))

        return cost_baseshare + cost_varpenalty - cost_theta


def calculate_cost(N, gam, E, e, qq, n_id, mechanism="OGL", r=0):
    """
    return just one value of cost function
    
    E = vector of quantities
    e = quantity of player to calculate
    gam = constant
    n = number of participants
    """
    E = np.array(E)

    em = []
    for id in n_id:
        em.append(E[id-2])
    E = em

    # n = len(E)
    n = 5 if mechanism == "OGL" else 2
    cost_baseshare = qq/N*sum(E) - r
    cost_theta = np.array([])
    
    i = list(E).index(e)
        
    if mechanism == 'MPT':
        cost = cost_baseshare
        return cost
    elif mechanism == 'MGL':        
        cost_varpenalty = gam/2*(n/(n-1))*(e-mean(E))**2
        return cost_baseshare + cost_varpenalty
    elif mechanism == 'OGL':
        cost_varpenalty = gam/2*(n/(n-1))*(e-mean(E))**2
                
        cost_theta = calculate_theta(E, e, gam, n)
            
        return cost_baseshare + cost_varpenalty - cost_theta
    
def calculate_nonparticipant_tax(
        N, 
        price, 
        gam, 
        e, 
        costs,
        r=0, 
        n_id = np.array([1, 3]),
        mechanism = "OGL"
    ):
    
    if (mechanism == "OGL"):
        n_id = np.array([2,3,4,5,6])
        
    em = []
    for id in n_id:
        em.append(e[id-2])
        
    n = len(n_id)  
            
    if (mechanism == "OGL"):
        participant_costs = costs
        
        nonparticipant_tax = rebate = np.repeat(a = 0, repeats = N)

    else:
                
        # this is a bad way to get the participant costs array to grow to N, where indexes not included in n_id are 0
        participant_costs = costs
        residual_costs = sum(em) * price - sum(participant_costs)

        mgl_rebate = 0 if mechanism == "MGL" else 0
        
        # this is for csv only ========================
        nonparticipant_tax = np.repeat( a = residual_costs / (N - n) + mgl_rebate, repeats = N)
        nonparticipant_tax[[i-2 for i in n_id]] = 0
    
    return nonparticipant_tax