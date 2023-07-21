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

def calculate_costs(N, gam, E, qq, mechanism="OGL", r=0):
    E = np.array(E)
    # n = len(E)
    n = 4 if mechanism == "OGL" else 2
    cost_baseshare = qq/N*sum(E) - r
    cost_theta = np.array([])
        
    if mechanism == 'MPT':
        cost = cost_baseshare
        return [cost for i in range(n)]
    elif mechanism == 'MGL':        
        cost_varpenalty = gam/2*(n/(n-1))*(E-mean(E))**2
        return cost_baseshare + cost_varpenalty
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
        em.append(E[id-1])
    E = em

    # n = len(E)
    n = 4 if mechanism == "OGL" else 2
    cost_baseshare = qq/N*sum(E) - r
    cost_theta = np.array([])

    # print(f"E {E}, e {e}")
    
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

def calculate_utility(
        N, 
        price, 
        gam, 
        e, 
        r=0, 
        betai = np.array([1700, 2000, 2000, 2300]), 
        n_id = np.array([1, 3]), 
        mechanism = "OGL"
    ):

    if (mechanism == "OGL"):
        n_id = np.array([1,2,3,4])
              
    em = []
    for id in n_id:
        em.append(e[id-1])
        
    n = len(n_id)  
            
    if (mechanism == "OGL"):
        participant_costs = calculate_costs(N, gam, em, price, r=r, mechanism = mechanism)
        
        nonparticipant_tax = rebate = np.repeat(a = 0, repeats = N)

    else:
                
        # this is a bad way to get the participant costs array to grow to N, where indexes not included in n_id are 0
        participant_costs = calculate_costs(N, gam, em, price, r=r, mechanism = mechanism)
        residual_costs = sum(em) * price - sum(participant_costs)

        mgl_rebate = 0 if mechanism == "MGL" else 0
        
        # this is for csv only ========================
        nonparticipant_tax = np.repeat( a = residual_costs / (N - n) + mgl_rebate, repeats = N)
        nonparticipant_tax[[i-1 for i in n_id]] = 0
            
        # rebate is added for nonparticipants here
        rebate = np.repeat(a = -mgl_rebate, repeats = N)
        rebate[[i-1 for i in n_id]] = -mgl_rebate
        # =============================================
        
        # initialize costs for all participants. rebate deducted for nonparticipants here
        temp_costs = np.repeat( a = residual_costs / (N - n) + mgl_rebate, repeats = N)
        temp_costs[[ i-1 for i in n_id]] = participant_costs
        participant_costs = temp_costs
                                    
    xi = betai - participant_costs

    xi_with_negative = xi.copy()
    xi[xi < 0] = 0

    ui = np.sqrt(xi) * np.sqrt(sum(em))
    
    return dict(
        participant_costs=participant_costs,
        quantity_ind_commodity=xi,
        quantity_ind_commodity_with_negatives=xi_with_negative,
        utility=ui,
        participant_rebate=rebate,
        nonparticipant_tax=nonparticipant_tax,
        group_quantities=e,
        starting_points=betai,
        gamma=gam,
        price=price,
        n_id=n_id
    )

# ====================================================================================

def format_decimal(d):
    return str(d).rstrip('0').rstrip('.')


class SurveyMechanism:

    def __init__(self):
        pass

    def csv_header(self, input_range):
        header = f"Player_Id, Participant_Id, Group_Id,"
        for i in range(1, input_range + 1):
            header += f"{i},"

        return [header]

    def generate_csv(self, survey_responses, filename, input_range):

        # csv file output per player
        f = open(filename, 'a', newline='')
        with f:
            writer = csv.writer(f)
            # write header

            writer.writerow(self.csv_header(input_range))

            for r in survey_responses:
                row = r.survey_row()
                writer.writerow(row)

    def start_vars(self, id_in_group, total, cost, response=None):

        if id_in_group == 1:
            return dict(defend_token_total=total)
        else:
            return dict(
                defend_token_total=total,
                defend_token_cost=format_decimal(cost),
                your_tax=format_decimal(response.tax),
            )

    def result_vars(self, group, player, response=None):
        if player.id_in_group == 1:
            return dict(
                defend_token_total=group.defend_token_total,
                fine_total=group.civilian_fine_total,
                bonus_total=group.officer_bonus_total,
            )
        else:
            if response is not None:
                # participant
                return dict(
                    # token
                    defend_token_total=group.defend_token_total,
                    defend_token_cost=format_decimal(group.defend_token_cost),
                    # your_tax

                    # results
                    balance=format_decimal(Decimal(player.balance) - response.tax),
                    before_tax=format_decimal(player.balance),
                    your_tax=format_decimal(response.tax),
                )
            else:
                # this would be an error
                pass


class OglMechanism:

    def csv_header(self):
        header = f"Group_Id, Player_Id, Input, Created_At"

        return [header]

    def generate_csv(self, responses, filename):

        # csv file output per player
        f = open(filename, 'a', newline='')
        with f:
            # write header
            writer = csv.writer(f)

            writer.writerow(self.csv_header())

            for r in responses:
                row = r.gl_row()
                writer.writerow(row)

    def start_vars(self, id_in_group, total, cost, response=None):

        if id_in_group == 1:
            return dict(defend_token_total=total)
        else:
            return dict(
                defend_token_total=total,
                defend_token_cost=format_decimal(cost),
                your_tax=format_decimal(response.tax),
                your_tokens=response.total
            )

    def result_vars(self, group, player, response=None):
        if player.id_in_group == 1:
            return dict(
                defend_token_total=group.defend_token_total,
                fine_total=group.civilian_fine_total,
                bonus_total=group.officer_bonus_total,
            )
        else:
            if response is not None:
                # participant
                return dict(
                    # token
                    defend_token_total=group.defend_token_total,
                    defend_token_cost=format_decimal(group.defend_token_cost),
                    # your_tax

                    # results
                    balance=format_decimal(Decimal(player.balance) - response.tax),
                    before_tax=player.balance,
                    your_tax=format_decimal(response.tax),
                    your_tokens=response.total,
                )
            else:
                # todo: there is an error here
                return None


class OtherMechanism:

    def csv_header(self):
        header = f"Group_Id, Player_Id, Input, Created_At"

        return [header]

    def generate_csv(self, responses, filename):
        # csv file output per player
        f = open(filename, 'a', newline='')
        with f:
            writer = csv.writer(f)
            # write header

            writer.writerow(self.csv_header())

            # determine if players received 50 grain
            for r in responses:
                row = r.gl_row()
                writer.writerow(row)

    def start_vars(self, id_in_group, total, cost, response=None):

        if id_in_group == 1:
            return dict(defend_token_total=total)
        else:
            result = dict(
                defend_token_total=str(total),
                defend_token_cost=format_decimal(cost),
                your_tax=format_decimal(response.tax),
            )

            if response.participant:
                result['participant_rebate'] = response.participant_rebate
                result['your_tokens'] = str(response.total)

            return result

    def result_vars(self, group, player, response=None):
        if player.id_in_group == 1:
            return dict(
                defend_token_total=group.defend_token_total,
                fine_total=group.civilian_fine_total,
                bonus_total=group.officer_bonus_total,
            )
        else:
            if response is not None:
                result = dict(
                    # token
                    defend_token_total=group.defend_token_total,
                    defend_token_cost=format_decimal(group.defend_token_cost),
                    # your_tax

                    # results
                    balance=format_decimal(Decimal(player.balance) - response.tax + response.participant_rebate),
                    before_tax=player.balance,
                    your_tax=format_decimal(response.tax),
                )

                if response.participant:
                    result['participant_rebate'] = response.participant_rebate
                    result['your_tokens'] = response.total

                return result
            else:
                # todo: this would be an error
                return None


class MechCSVBuilder:

    def __init__(self, method, responses, filename, input_range=None):
        self.method = method
        self.responses = responses
        self.filename = filename

        self.input_range = input_range

    def write(self):
        if self.method == 0:
            if self.input_range is None:
                raise ValueError('mechanism csv builder requires input_range for survey mechanism')

            SurveyMechanism().generate_csv(self.responses, self.filename, self.input_range)
        elif self.method == 1:
            OglMechanism().generate_csv(self.responses, self.filename)
        elif self.method > 1:
            OtherMechanism().generate_csv(self.responses, self.filename)
        else:
            # error
            pass
