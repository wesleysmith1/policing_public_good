import csv, math, datetime, json

from helpers import time # TimeFormatter
# from main.helpers import write_session_dir, TimeFormatter

import logging
log = logging.getLogger(__name__)

class GenerateCsv:

    def __init__(self, C, game_data, session, subsession, meta_data):
        self.C = C
        self.game_data = game_data
        self.session = session
        self.subsession = subsession
        self.meta_data = meta_data

    def generate_csv(self):

        if not self.meta_data:
            player_ids_in_session = []
            steal_starts = []
            for i in range(self.C.PLAYERS_PER_GROUP):
                player_ids_in_session.append(1)
                steal_starts.append(1)

            group_id = 9
            group_pk = None
            round_number = 9
            session_id = 9
            session_start = 0
            session_date = "1992_0414"
            officer_bonus = -1
            income_distribution = [-1, -1, -1, -1, -1]
        else:
            steal_starts = self.meta_data['steal_starts']
            player_ids_in_session = self.meta_data['player_ids_in_session']
            group_id = self.meta_data['group_id']
            group_pk = self.meta_data['group_pk']
            round_number = self.subsession.round_number
            session_id = self.subsession.session_id
            session_start = self.meta_data['session_start']
            session_date = self.meta_data['session_date']
            officer_bonus = self.meta_data['officer_bonus']
            income_distribution = self.meta_data['income_distribution']

        # log.info("HERE IS THE ROUND NUMBER {}".format(round_number))

        # session_start is assigned to this
        round_start = -1

        defend_tokens = self.init_defend_tokens()

        try:
            tf = time.TimeFormatter(self.game_data[0].event_time)
        except:
            tf = None
            
        starting_balances=self.meta_data['starting_balances']

        players = self.init_players(session_start, steal_starts, player_ids_in_session, starting_balances, tf)

        for event in self.game_data:
            # get JSON data
            data = json.loads(event.jdata)
            event_type = data['event_type']
            player_id = data['player']
            event_time = data['event_time']

            # determine event type
            if event_type == 'harvest':
                # update player into
                player = players[player_id]

                # if harvest complete
                if data['production_inputs'] == 4:
                    player.balance += data['harvest_income']

                player.production_inputs = data['production_inputs']

                player.civilian_row(event_type, event_time)

                # reset harvest
                player.production_inputs = 0

            elif event_type == 'toggle':

                # update player into
                player = players[player_id]
                player.screen = self.format_screen(data['harvest_screen'])

                player.production_inputs = 0

                # update steal token
                if data.get('steal_reset'):
                    player.steal_token.update(player_id, data['steal_reset'], 0, 0)

                # check if there was a victim & update
                if data.get('victim'):
                    # update player into
                    victim_id = data['victim']
                    victim = players[victim_id]
                    victim.increase_roi(event_time)
                    player.decrease_roi(event_time)

                    victim.civilian_row(event_type, event_time)

                # add civilian row
                player.civilian_row(event_type, event_time)

            elif event_type == 'steal_token_reset':
                # update player info
                player = players[player_id]

                # update steal token
                player.steal_token.update(player_id, data['steal_reset'], 0, 0)

                # add civilian row
                player.civilian_row(event_type, event_time)

            elif event_type == 'steal_token_drag':
                # update player info
                player = players[player_id]

                # update steal token
                player.steal_token.update(player_id, 0, 0, 'NA')

                if data.get('victim'):
                    victim_id = data['victim']
                    victim = players[victim_id]

                    # update roi
                    victim.increase_roi(event_time)
                    player.decrease_roi(event_time)

                    # update victim data
                    victim.civilian_row(event_type, event_time, '0')

                # add civilian row
                player.civilian_row(event_type, event_time)

            elif event_type == 'steal_token_timeout':
                # update player info
                player = players[player_id]

                # update steal token
                player.steal_token.update(player_id, data['steal_reset'], 0, 'NA')

                if data.get('victim'):
                    victim_id = data['victim']
                    victim = players[victim_id]

                    # update roi
                    victim.increase_roi(event_time)
                    player.decrease_roi(event_time)

                    # update victim data
                    victim.civilian_row(event_type, event_time, '0')

                # add civilian row
                player.civilian_row(event_type, event_time)

            elif event_type == 'defend_token_reset':
                # get officer
                officer = players[1]

                # reset defend token
                token_number = data['token_number']
                token_slot = data['defend_reset']
                defend_tokens[token_number] = self.format_defend_token(token_number, token_slot, 0, 0, 0, 0)

                # add officer row
                officer.officer_row(event_type, event_time, self.formatted_defend_tokens(defend_tokens))

            elif event_type == 'defend_token_drag':

                # get officer
                officer = players[1]

                # reset defend token
                token_number = data['token_number']
                defend_tokens[token_number] = self.format_defend_token(token_number, 0, 0, 0, 0, 'NA')

                # add officer row
                officer.officer_row(event_type, event_time, self.formatted_defend_tokens(defend_tokens))

            elif event_type == 'investigation_update':

                # get officer
                officer = players[1]

                # reset defend token
                token_number = data['token_number']
                defend_tokens[token_number] = self.format_defend_token(token_number, 0, 0, 0, 0, -1)
                event_defend_tokens = self.formatted_defend_tokens(defend_tokens)

                # add officer row
                officer.officer_row(event_type, event_time, event_defend_tokens)

            elif event_type == 'defend_token_update':

                # get officer
                officer = players[1]
                officer_reprimand_total = 0
                formatted_intersections = 'NA'
                officer_data = {
                    'intersection_events': 'NA'
                }

                # update token data
                token_number = data['token_number']
                token_x1 = data['token_x']
                token_y1 = data['token_y']
                token_x2 = data['token_x2']
                token_y2 = data['token_y2']
                defend_map = data['map']

                defend_tokens[token_number] = self.format_defend_token(token_number, token_x1, token_y1, token_x2, token_y2, defend_map)
                event_defend_tokens = self.formatted_defend_tokens(defend_tokens)

                # check for intersections
                if data.get('intersections'):
                    intersection_data = []

                    # get victim so we can update the roi for each intersection
                    victim_id = defend_map
                    victim = players[victim_id]

                    updated_players = [victim_id]
                    steal_reset_data = {}
                    punished_players = []

                    # update intersection event data
                    for intersection in data['intersections']:

                        culprit_id = steal_token_id = intersection['culprit']
                        culprit = players[culprit_id]

                        steal_reset_data[culprit_id] = intersection['steal_reset']

                        # add culprit to updated_players list
                        if culprit_id not in updated_players:
                            updated_players.append(culprit_id)

                        culprit.decrease_roi(event_time)
                        victim.increase_roi(event_time)

                        investigation = True if intersection.get('guilty') else False

                        if investigation:
                            guilty_id = intersection['guilty']
                            guilty = players[guilty_id]

                            # add guilty
                            punished_players.append(guilty_id)

                            # add guilty to updated_players list
                            if guilty_id not in updated_players:
                                updated_players.append(guilty_id)

                            audit = intersection['audit']
                            reprimanded = 1 if intersection['officer_reprimand'] > 0 else 0
                            if reprimanded:
                                officer_reprimand_total += 1
                            wrongful_conviction = 1 if intersection['wrongful_conviction'] else 0

                            # officer bonus
                            officer.balance += intersection['officer_bonus']

                            i = self.format_intersection(token_number, culprit_id, steal_token_id, defend_map, guilty_id, audit,
                                                    reprimanded)

                            # wrongful conviction
                            if wrongful_conviction:

                                # officer reprimand
                                officer.balance -= intersection['officer_reprimand']

                                guilty.balance -= self.C.civilian_fine_amount

                            else:
                                # guilty culprit punishment
                                culprit.balance -= self.C.civilian_fine_amount

                        else:
                            i = self.format_intersection(token_number, culprit_id, steal_token_id, defend_map, 'NA', 0, 0)

                        # log.info("CULPRIT_ID: {}".format(culprit_id))

                        # end of intersection code
                        intersection_data.append(i)

                    # add formatted intersection data
                    formatted_intersections = self.format_intersections(intersection_data)

                    for pid in updated_players:
                        u_player = players[pid]

                        u_player.civilian_row(event_type, event_time,
                                            punished=str(punished_players.count(pid)))

                    # reset culprit steal tokens for csv rows after intersection
                    for cid in steal_reset_data:  # hey
                        players[cid].steal_token.update(cid, steal_reset_data[cid], 0, 0)

                    officer_data['intersection_events'] = formatted_intersections

                # update officer data
                officer.officer_row(event_type, event_time, event_defend_tokens,
                                                        intersection_data=str(formatted_intersections),
                                                        punished=str(officer_reprimand_total))

            elif event_type == 'steal_token_update':
                culprit_id = data['culprit']
                culprit = players[culprit_id]

                token_x = data['token_x']
                token_y = data['token_y']
                steal_map = data['map']
                culprit_punished = 'NA'
                steal_reset = None

                victim_id = data['map']
                victim = players[victim_id]

                # changed if there is intersection
                defend_token_number = 'NA'
                # formatted_tokens
                event_defend_tokens = 'NA'
                formatted_intersection = 'NA'

                officer = players[1]
                officer_reprimand = 'NA'

                if data.get('intersections'):

                    officer_reprimand = 0

                    event_defend_tokens = self.formatted_defend_tokens(defend_tokens)
                    intersection = data['intersections'][0]  # only one intersection possible
                    defend_token_number = intersection['token_number']
                    steal_token_id = culprit_id  # same for first delegated_punishment experiment
                    steal_reset = intersection['steal_reset']

                    # check if there were investigation tokens
                    investigation = True if intersection.get('guilty') else False

                    if investigation:
                        guilty_id = intersection['guilty']

                        audit = intersection['audit']
                        reprimanded = 1 if intersection['officer_reprimand'] > 0 else 0
                        if reprimanded:
                            officer_reprimand = 1

                        wrongful_conviction = 1 if intersection['wrongful_conviction'] else 0

                        # officer bonus
                        officer.balance += intersection['officer_bonus']

                        #todo clean this logic up
                        i = self.format_intersection(
                            defend_token_number,
                            culprit_id,
                            steal_token_id,
                            steal_map,
                            'NA' if guilty_id == 0 else guilty_id,
                            audit,
                            reprimanded
                        )

                        # if wrongful conviction
                        if wrongful_conviction:
                            guilty = players[guilty_id]

                            # officer reprimand
                            officer.balance -= intersection['officer_reprimand']

                            guilty.balance -= self.C.civilian_fine_amount

                            culprit_punished = 0
                            guilty.civilian_row(event_type, event_time, punished='1')
                        else:
                            culprit_punished = 1
                            culprit.balance -= self.C.civilian_fine_amount

                    else:
                        i = self.format_intersection(defend_token_number, culprit_id, steal_token_id, steal_map, 'NA', 0, 0)

                    formatted_intersection = "[{}]".format(i)  # single intersection

                else:
                    culprit.increase_roi(event_time)
                    victim.decrease_roi(event_time)

                victim.civilian_row(event_type, event_time, punished='0')

                officer.officer_row(event_type, event_time, self.formatted_defend_tokens(defend_tokens),
                                    intersection_data=formatted_intersection, punished=str(officer_reprimand))

                culprit.steal_token.update(player_id, token_x, token_y, steal_map)

                culprit.civilian_row(event_type, event_time, punished=str(culprit_punished))

                # set steal reset location
                if steal_reset:
                    # steal_tokens[culprit_id].x = steal_reset
                    culprit.steal_token.x = steal_reset


            elif event_type == 'round_start':
                round_start = event_time
                log.info(f'START TIME FOR EXPERIMENT:{round_start}')
                for i in range(1, self.C.PLAYERS_PER_GROUP+1):

                    if i > 1:
                        players[i].civilian_row(event_type, event_time)
                    else:
                        players[i].officer_row(event_type, event_time, self.formatted_defend_tokens(defend_tokens))

            elif event_type == 'round_end':
                for i in range(1, self.C.PLAYERS_PER_GROUP+1):

                    # add end time to csv
                    if i > 1:
                        players[i].civilian_row(event_type, event_time)
                    else:
                        players[i].officer_row(event_type, event_time, self.formatted_defend_tokens(defend_tokens))

                # any events after this should not be included
                break

            else:
                log.info('ERROR: EVENT TYPE NOT RECOGNIZED')

        # generate file directory
        if 'session_identifier' in self.session.config:
            file_path = time.write_session_dir(self.session.config['session_identifier'])
        else:
            file_path = 'data/'

            # log out csv files
        for i in range(1, self.C.PLAYERS_PER_GROUP+1):
            start = math.floor(session_start)
            file_name = "{}Session_{}_Group_{}_Player_{}_{}_{}.csv".format(file_path, session_id, self.meta_data['group_id'], i, session_date, start)

            # csv file output per player
            f = open(file_name, 'a', newline='')
            with f:
                writer = csv.writer(f)
                # write header
                if round_number == 4:
                    writer.writerow(self.csv_header())
                for row in players[i].rows:
                    writer.writerow(self.format_row(i, row, round_start, self.meta_data, players[i].id_in_session))


    def csv_header(self):
        labels = [
            'EventType',
            'Session_ID',
            'Session_GlobalParameters',
            'Group_ID',
            'Group_BonusAmount',
            'Group_IncomeDistribution',
            'Player_Starting_Balances',
            'Player_ID',
            'Participant_ID',  # participant.id_in_session
            'Player_Role',
            'Period_ID',
            'Period_CurrentTime',
            'ROI',
            'Player_Balance',
            'Player_Screen',
            'Player_StealToken',
            'Player_ProductionInputs',
            'Player_Punished',
            'Player_DefendTokens',
            'Group_PunishmentEvents',
            'Group_PK',
            'Group_ReprimandAmount',
            'Group_stealTechnology',
            'Player_HarvestAmount',
            'Group_ID_Description',
        ]
        return labels


    def format_row(self, pid, r, round_start, meta_data, id_in_session):

        return [
            r['event_type'],
            meta_data['session_id'],
            [
                self.C.civilian_steal_rate,
                self.C.civilian_fine_amount,
                meta_data['total_defend_tokens'],
                "a min 1 , a max 10",
                self.C.defend_token_size,
                self.C.civilian_map_size,
                self.C.officer_reprimand_amount,
                self.C.officer_review_probability,
                datetime.datetime.fromtimestamp(meta_data['session_start']).strftime('%d/%m/%Y %H:%M:%S')
            ],  # session global params
            meta_data['group_id'],
            meta_data['officer_bonus'],
            meta_data['income_distribution'],  # group_income_distribution
            meta_data['starting_balances'],
            pid,
            id_in_session,  # participant_id
            1 if pid > 1 else 0,
            meta_data['round_number'],
            r['event_time'],
            r['roi'],
            r['balance'],
            r['screen'],
            r['steal_token'],
            r['production_inputs'],
            r['punished'],
            r['defend_tokens'],
            r['intersection_events'],
            meta_data['group_pk'],
            meta_data['reprimand'], #Group_ReprimandAmount, #Group_ReprimandAmount,
            'Constant',
            0 if pid == 1 else meta_data['income_distribution'][pid-2], #Player_HarvestAmount
            'Constant - M/H', #todo: make dynamic
        ]
    
    def init_defend_tokens(self):
        x = {}
        for i in range(1, self.meta_data['total_defend_tokens']+1):
            x[i] = "[{}, {}, {}, {}, {}, {}]".format(i, 0, 0, 0, 0, 'NA')
        return x


    def init_players(self, start, steal_starts, player_ids_in_session, starting_balances, tf):
        x = {}
        for i in range(1, self.C.PLAYERS_PER_GROUP+1):
            x[i] = CPlayer(start, i, steal_starts[i-1], player_ids_in_session[i-1], starting_balances[i-1], tf, self.C)

        return x


    def format_steal_token(self, token_number, x, y, steal_map, defend_token):
        return "[{}, {}, {}, {}, {}]".format(token_number, x, y, steal_map, defend_token)


    def format_defend_token(self, token_number, x1, y1, x2, y2, defend_map):
        return "[{}, {}, {}, {}, {}, {}]".format(token_number, x1, y1, x2, y2, defend_map)


    def formatted_defend_tokens(self, defend_dict):
        result = "["

        for num, value in defend_dict.items():
            result += value
            # add separator
            if num != len(defend_dict) - 1:
                result += ';'

        result += "]"
        return result


    def format_intersection(self, token_number, culprit_id, steal_token_id, intersection_map, guilty_player_id, audit, reprimanded):
        """ for now culprit_id and steal_token_id are the same """
        return "[{}, {}, {}, {}, {}, {}, {}]".format(token_number, culprit_id, steal_token_id, intersection_map,
                                                    guilty_player_id, audit, reprimanded)


    def format_intersections(self, i_list):
        result = "[" + ";".join(i_list) + "]"
        return result


    def format_screen(self, s):
        return 1 if s else 0


class StealToken:
    def __init__(self, number, start):
        self.number = number
        self.x = start
        self.y = 0
        self.map = 0

    def update(self, number, x, y, smap):
        self.number = number
        self.x = x
        self.y = y
        self.map = smap

    def format(self):
        return "[{}, {}, {}, {}]".format(self.number, self.x, self.y, self.map)


class CPlayer:
    def __init__(self, start, id, steal_start, id_in_session, starting_balance, time_formatter, C):
        self.id_in_session = id_in_session
        self.last_updated = start
        self.player_id = id
        self.C = C
        self.starting_balance = starting_balance
        self.balance = self.starting_balance

        self.roi = 0
        self.t_formatter = time_formatter

        # officer
        if self.player_id == 1:
            self.player_role = 0
            self.screen = 0
            self.production_inputs = 'NA'
            self.steal_token = None
        # civilian
        else:
            self.player_role = 1
            self.screen = 1
            self.production_inputs = '0'
            self.steal_token = StealToken(self.player_id, steal_start)

        self.rows = []

    def civilian_row(self, event_type, event_time, punished='NA'):
        row_data = {
            'event_type': event_type,
            'event_time': self.t_formatter.format(event_time),
            'balance': self.update_balance(event_time),
            'roi': self.roi,
            'screen': self.screen,
            'steal_token': self.steal_token.format(),
            'production_inputs': self.production_inputs,
            'punished': punished,
            'defend_tokens': 'NA',
            'intersection_events': 'NA'
        }
        self.rows.append(row_data)

    def officer_row(self, event_type, event_time, defend_tokens, intersection_data='NA', punished='NA', ):
        if self.player_id != 1:
            return
        row_data = {
            'event_type': event_type,
            'event_time': self.t_formatter.format(event_time),
            'balance': self.update_balance(event_time),
            'roi': self.roi,
            'screen': self.screen,
            'steal_token': 'NA',
            'production_inputs': self.production_inputs,
            'punished': punished,
            'defend_tokens': defend_tokens,
            'intersection_events': intersection_data
        }
        self.rows.append(row_data)

    def increase_roi(self, event_time):
        self.balance = self.update_balance(event_time)
        self.last_updated = event_time
        self.roi += self.C.civilian_steal_rate

    def decrease_roi(self, event_time):
        self.balance = self.update_balance(event_time)
        self.last_updated = event_time
        self.roi -= self.C.civilian_steal_rate

    def update_balance(self, event_time):
        # return calculated balance
        if self.roi == 0:
            return self.balance
        elif not event_time or not self.last_updated:
            log.error('ERROR: START DATE OR END DATE MISSING WHEN CALCULATING')
            return -99
        else:
            return self.balance + self.roi * (event_time - self.last_updated)