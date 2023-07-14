import random
import csv
import math
from helpers.time import write_session_dir
from helpers.generate_data import * 


def get_path(group):
    if 'session_identifier' in group.subsession.session.config:
        path = write_session_dir(group.subsession.session.config['session_identifier'])
    else:
        path = 'data/'
    return path


def calculate_payout(balance, showup_payment):
    payout = balance
    if balance < 0:
        payout = showup_payment
    else:
        payout += showup_payment

    return round(payout, 2)


def grain_to_dollars(group, grain):
    return grain * group.subsession.session.config['grain_conversion']


def generate_payouts(group):
    path = get_path(group)

    # todo: add exception so the session does not crash
    showup_payment = group.subsession.session.config.get('showup_payment', -999)

    for player in group.get_players():
        # create row for participant and display the participant name
        participant_balances = player.participant.vars.get('balances', [])
        # participant_balances_recorded = len(player.participant.vars.get('balances', []))
        if 'balances' in player.participant.vars.keys() and len(participant_balances) > 1:

            balance = grain_to_dollars(group, random.choice(participant_balances))

            payout = calculate_payout(balance, showup_payment)

        elif len(participant_balances) == 1:
            balance = grain_to_dollars(group, participant_balances[0])
            payout = calculate_payout(balance, showup_payment)
        else:
            payout = -1

        player.participant_code = player.participant.code
        player.id_in_session = player.participant.id_in_session
        player.payoff = payout


def generate_survey_csv(group):
    path = get_path(group)
    session_id = group.subsession.session_id
    session_start = math.floor(group.session.vars.get('session_start', 999))
    session_date = group.session.vars.get('session_data', 999)
    file_name = "{}results{}__{}_{}.csv".format(path, session_id, session_date, session_start)

    f = open(file_name, 'w', newline='')
    with f:
        writer = csv.writer(f)
        header = ['participant', 'payoff', 'firstname', 'lastname', 'strategy', 'feedback']

        writer.writerow(header)

        for p in group.get_players():
            survey_row = [p.participant.id_in_session, p.payoff, p.first_name, p.last_name, p.strategy, p.feedback]
            writer.writerow(survey_row)

