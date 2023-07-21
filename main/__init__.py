from otree.api import *
import json, math, time, datetime, operator
from random import randrange
import numpy as np

from main.income_distributions import IncomeDistributions

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = 6
    civilians_per_group = 5
    NUM_ROUNDS = 12

    # CIVILIAN_START_BALANCE = 1000

    """Number of defend tokens officer starts with"""
    defend_token_total = 8

    """Fine when convicted"""
    civilian_fine_amount = 120
    """number of grain earned per second of stealing"""
    civilian_steal_rate = 16

    """Probability that an intersection outcome will be reviewed"""
    officer_review_probability = .25

    """P punishment for officer if innocent civilian is punished"""
    l = 1
    m = 200
    h = 800
    # treatment variables including tutorial
    officer_reprimand_amount = [l,l,l,l,l,l,l,m,m,m,m,m]

    """Officer income (bonus). One for each group"""
    officer_income = 50

    """ 
    this is the size of the tokens and maps are defined. 
    """
    defend_token_size = 150
    civilian_map_size = 200 * 1.5

    """Probability innocent and guilty are calculated when the number of investigation tokens is >= this number"""
    a_max = 6
    """todo: label this correctly... find out where this is from and why it is needed...."""
    beta = 18
    """
    Tutorial, game and results modal durations are defined here and passed to frontend
    """
    tutorial_duration_seconds = 1800
    game_duration_seconds = 180

    """"This defines how long after defend tokens have been placed, and when they can be moved again"""
    defend_pause_duration = 2000
    """
    this defines how long a steal token remains on a map before resetting to the 'steal home'
    """
    steal_timeout_milli = 2000
    """
    This is how long the steal token can actively steal continuously before being reset to the 'steal home'
    """
    steal_pause_duration = 1000
    """
    Steal tokens positions defines the number of slots inside the 'steal home' rectangle. Steal tokens can be loaded or 
    reset to any of the slots 
    """
    steal_token_slots = 20

    officer_start_balance = 1400
    civilian_start_balance = 1400

        # probability calculations
    # key=#probabilities -> innocent, culprit, prob nobody
    # the index
    calculated_probabilities = [
        (.2, .2, .2), # 0 defense tokens tokens
        (.18, .26, .2), # 1 defense ...
        (.16, .32, .2), # 2 ...
        (.14, .38, .2), # 3 ...
        (.12, .44, .2), # 4 ...
        (.10, .50, .2), # 5 ...
        (.08, .56, .2), # 6 ...
        (.06, .62, .2), # 7 ...
        (.04, .68, .2), # 8 ...
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

    game_start = models.FloatField(initial=0)
    officer_bonus = models.IntegerField(initial=0)

    # counters
    officer_bonus_total = models.IntegerField(initial=0)
    civilian_fine_total = models.IntegerField(initial=0)
    officer_reprimand_total = models.IntegerField(initial=0)
    intercept_total = models.IntegerField(initial=0)

    officer_reprimand_amount = models.IntegerField() # dynamic treatment variable that can change round to round

    def round_end(self):
        end_time = time.time()

        game_data_dict = {
            'event_time': end_time,
            'event_type': 'round_end',
            'player': 1,
        }

        # final calculation of player balances for results page
        for player in self.get_players():
            player.balance = player.get_balance(end_time)

        GameData.create(
            event_time=end_time,
            p=1,
            group=self,
            s=self.session_id,
            round_number=self.round_number,
            jdata=json.dumps(game_data_dict)
        )

    def intersection_update(self, bonus, fine, reprimand, intercept):
        self.officer_bonus_total += bonus
        self.civilian_fine_total += fine
        self.officer_reprimand_total += reprimand
        self.intercept_total += intercept
        return dict(
                bonus=self.officer_bonus_total, 
                fine=self.civilian_fine_total, 
                reprimand=self.officer_reprimand_total, 
                intercept=self.intercept_total
            )


    def balance_update(self, time):
        balance_update = {}
        active_maps = {}

        for i in range(1, C.PLAYERS_PER_GROUP+1):
            active_maps[i] = 0

        for player in self.get_players():
            if player.map > 0:
                active_maps[player.map] += 1

            balance_update[player.id_in_group] = dict(
                balance=player.get_balance(time),
                map=player.map,
                victim_count=player.victim_count,
                steal_count=player.steal_count,
            )
            balance_update['active_maps'] = active_maps

        return balance_update
    
    def is_tutorial(self):
        return self.round_number == 1
    
    def generate_results(self):
        players = self.get_players()

        # Initial civilian steal locations for csv
        player_ids_in_session = []
        steal_starts = []
        for p in players:
            steal_starts.append(p.participant.vars['steal_start'])
            player_ids_in_session.append(p.participant.id_in_session)

        officer_participant = self.get_player_by_id(1).participant
        officer_bonus = officer_participant.vars['officer_bonus']
        group_id = officer_participant.vars['group_id']

        config_key = self.session.config['civilian_income_config']
        incomes = IncomeDistributions.get_group_income_distribution(config_key, self.round_number)

        meta_data = dict(
            round_number=self.subsession.round_number,
            session_id=self.subsession.session_id,
            steal_starts=steal_starts,
            session_start=self.session.vars['session_start'],
            session_date=self.session.vars['session_date'],
            group_pk=self.id,
            group_id=group_id,
            officer_bonus=officer_bonus,
            income_distribution=incomes,  # todo: this needs to reflect values not keys
            player_ids_in_session=player_ids_in_session,
            reprimand=self.officer_reprimand_amount, # group reprimand amount
        )

        # get data
        game_data = GameData.filter(group=self)
        sorted(game_data, key=lambda x: x.event_time)

        # import here to avoid circular import
        from helpers import generate_data
        generate_data.GenerateCsv(C, game_data, self.session, self.subsession, meta_data, ).generate_csv()


def randomize_location():
    """return a random location for civilian steal token"""
    return randrange(C.steal_token_slots)+1


class Player(BasePlayer):
    x = models.FloatField(initial=0)
    y = models.FloatField(initial=0)
    map = models.IntegerField(initial=0)
    last_updated = models.FloatField(blank=True)
    roi = models.IntegerField(initial=0)
    balance = models.FloatField(initial=C.civilian_start_balance)
    harvest_status = models.IntegerField(initial=0)
    harvest_screen = models.BooleanField(initial=True)
    income = models.IntegerField(initial=40)
    steal_start = models.IntegerField(initial=randomize_location)
    steal_count = models.IntegerField(initial=0)
    victim_count = models.IntegerField(initial=0)
    steal_total = models.FloatField(initial=0)
    victim_total = models.FloatField(initial=0)
    ready = models.BooleanField(initial=False)

    def print(self):
        """player print method for debugging"""
        print(f"ID: {self.id_in_group}, x: {self.x}, y: {self.y}, map: {self.map}, ROI: {self.roi}, BALANCE: {self.balance}")

    def get_balance(self, time):
        if self.roi == 0:
            return self.balance
        elif not self.last_updated:
            return -99
        else:
            seconds_passed = time - self.last_updated
            return self.balance + (self.roi * seconds_passed)
    
    def increase_roi(self, time, direct):
        """
            direct argument determines which status count variable to update
        """
        # calculate balance
        self.balance = self.get_balance(time)  # we need to set balance with event time here boi
        self.last_updated = time
        # update roi
        # todo: why is this explicit conversion required here?
        self.roi = int(self.roi + C.civilian_steal_rate)

        if direct:
            # victim no longer being stolen from by a player
            self.steal_count += 1
        else:
            # culprit stealing from a victim
            self.victim_count -= 1


    def decrease_roi(self, time, direct):

        # calculate balance
        self.balance = self.get_balance(time)
        self.last_updated = time
        # update roi
        self.roi = int(self.roi - C.civilian_steal_rate)

        if direct:
            self.steal_count -= 1
        else:
            self.victim_count += 1

    def civilian_fine(self):
        self.balance -= C.civilian_fine_amount

    def is_officer(self):
        """officer always has id_in_group of 1"""
        return self.id_in_group == 1
    
    def civilian_harvest(self):
        self.balance += self.income

    def officer_bonus(self):
        self.balance += self.income

    def officer_reprimand(self):
        self.balance -= self.group.officer_reprimand_amount


class DefendToken(ExtraModel):
    group = models.Link(Group)
    number = models.IntegerField()
    map = models.IntegerField(initial=0)
    x = models.FloatField(initial=0)
    y = models.FloatField(initial=0)
    x2 = models.FloatField(initial=0)
    y2 = models.FloatField(initial=0)
    last_updated = models.FloatField(blank=True)
    slot = models.IntegerField(initial=-1)

    def to_dict(self):
        return {"number": self.number, "map": self.map, "x": self.x, "y": self.y}
    

class GameData(ExtraModel):
    group = models.Link(Group)
    event_time = models.FloatField()
    p = models.IntegerField(initial=0)
    s = models.IntegerField(initial=0)
    round_number = models.IntegerField(initial=0)
    jdata = models.StringField()

    def set_jdata(self, dict):
        """convert dict of game data to a string before saving in database"""
        self.jdata = json.dumps(dict)

    def get_jdata(self):
        """get jdata string in json format"""
        return json.loads(self.jdata)


# FUNCTIONS
def creating_session(subsession: Subsession):
    """
    Initialie balances and incomes for officers and players for tutorial, practice, 
    and all other rounds.
    Initialize session variables like date and relative group id
    """

    # get time in miliseconds
    time_now = time.time()
    # set session start time
    subsession.session.vars['session_start'] = time_now
    subsession.session.vars['session_date'] = datetime.datetime.today().strftime('%Y%m%d')

    # get configurations from settings.py
    config_key = subsession.session.config['civilian_income_config']

    round_incomes = IncomeDistributions.get_group_income_distribution(config_key, subsession.round_number)

    # this code is the terrible way that officer income is determined for session
    if subsession.round_number == 1:
        for index, group in enumerate(subsession.get_groups()):
            officer = group.get_player_by_id(1)
            officer.participant.vars['officer_bonus'] = officer.income = C.officer_income

            # save group id relative to session, not all groups in database
            officer.participant.vars['group_id'] = index+1

            for p in group.get_players():
                if not p.is_officer():
                    p.income = subsession.session.config['tutorial_civilian_income']

    for group in subsession.get_groups():

        group.officer_reprimand_amount = C.officer_reprimand_amount[group.round_number - 1]

        for p in group.get_players():

            # initialize balances list
            p.participant.vars['balances'] = []
            p.participant.vars['steal_start'] = p.steal_start

            if p.is_officer():
                p.balance = C.officer_start_balance

        # ==========================================================================

            # demo session does not need further configuration
            if C.NUM_ROUNDS != 1:

                # check if round is tutorial or trial round
                if group.round_number < 3:
                    if p.id_in_group > 1:
                        p.income = p.session.config['tutorial_civilian_income']
                    else:
                        p.income = p.session.config['tutorial_officer_bonus']
                else:
                    # set harvest amount for civilians
                    if p.id_in_group > 1:
                        income_index = p.id_in_group-2
                        p.income = round_incomes[income_index]
                    else:
                        # is officer
                        p.income = p.participant.vars['officer_bonus']

        # create defend tokens for current round for each group
        for i in range(C.defend_token_total):
            DefendToken.create(number=i+1, group=group,)


# PAGES
class Wait(WaitPage):
    pass

class StartWait(WaitPage):
    pass

class Main(Page):

    @staticmethod
    def get_timeout_seconds(player: Player):
        return None if player.round_number == 1 else 15

    @staticmethod
    def vars_for_template(player: Player):
        if player.id_in_group == 1 and player.group.game_start == 0:
            player.group.game_start = event_time = time.time()

            game_data_dict = {
                'event_time': event_time,
                'event_type': 'round_start',
                'player': 1,
            }

            x = GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )
    
        return dict(
            tutorial=C.NUM_ROUNDS > 1 and player.round_number == 1
        )

    @staticmethod
    def js_vars(player):
        
        officer_tokens = DefendToken.filter(group=player.group)
        defend_tokens = results = [obj.to_dict() for obj in officer_tokens]

        config_key = player.session.config['civilian_income_config']
        low_to_high = player.session.config['civilian_income_low_to_high']

        civilian_ids = [x + C.PLAYERS_PER_GROUP - C.civilians_per_group for x in
            range(1, C.PLAYERS_PER_GROUP + 1)]
        
        if player.round_number < 3:  # tutorial or practice round
            tut_civ_income = player.session.config['tutorial_civilian_income']
            tut_o_bonus = player.session.config['tutorial_officer_bonus']

            incomes = [tut_civ_income] * C.civilians_per_group
            incomes_dict = dict(zip(civilian_ids, incomes))
            incomes_dict = dict(sorted(incomes_dict.items(), key=operator.itemgetter(1)))

            start_modal_object = dict(
                civilian_incomes=incomes_dict,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=tut_o_bonus,
                officer_reprimand=player.group.officer_reprimand_amount,
            )
        else:
            incomes = IncomeDistributions.get_group_income_distribution(config_key, player.round_number)
            incomes_dict = dict(zip(civilian_ids, incomes))
            sorted(incomes_dict.values())

            start_modal_object = dict(
                civilian_incomes=incomes_dict,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=player.group.get_player_by_id(1).participant.vars['officer_bonus'],
                officer_reprimand=player.group.officer_reprimand_amount,
            )
        
        return dict(
            defend_tokens=defend_tokens,
            start_modal_object=start_modal_object,
            harvest_screen=player.harvest_screen,
            balance_update_rate=player.session.config['balance_update_rate'],
            player=dict(
                    id=player.id,
                    idInGroup=player.id_in_group,
                    groupId=player.group_id,
                    round=player.round_number,
                    harvestScreen=player.harvest_screen,
                    sessionId=player.session_id,
                    income=player.income,
                )
        )
    
    @staticmethod
    def live_method(player, data):

        event_time = time.time()
    
        if data.get('balance'):
            balance_update = player.group.balance_update(event_time)
            return {0: {'balance': balance_update}}

        elif data.get('harvest'):

            game_data_dict = {}
            harvest_status = player.harvest_status = data['harvest']['status']

            harvest_income = 0

            if player.harvest_status == 4:
                # increase balance
                harvest_income = player.income
                player.balance += player.income
                player.harvest_status = 0

            game_data_dict.update({
                "event_type": "harvest",
                "event_time": event_time,
                "production_inputs": harvest_status,  # don't update from player object in case it was reset to 0
                "player": player.id_in_group,
                "balance": player.balance,
                "harvest_income": harvest_income
            })

            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

        elif data.get('toggle'):

            game_data_dict = {}

            toggle_status = data['toggle']

            if not toggle_status['harvest']:
                # reset harvest status
                player.harvest_status = 0
                player.harvest_screen = False
            else:
                player.harvest_screen = True
                game_data_dict.update({
                    "steal_reset": toggle_status["steal_reset"]
                })
                
                if player.map != 0:
                    victim = Player.group.get_player_by_id(id_in_group=player.map)

                    victim.increase_roi(event_time, False)

                    game_data_dict.update({
                        "victim": victim.id_in_group,
                        "victim_roi": victim.roi,
                        "victim_balance": victim.balance,
                    })

                    player.decrease_roi(event_time, True)
                else:
                    pass
                player.map = 0

            game_data_dict.update({
                "event_type": "toggle",
                "event_time": event_time,
                "harvest_screen": player.harvest_screen,  # else steal
                "player": player.id_in_group,
                "player_roi": player.roi,
                "player_balance": player.balance,
            })

            GameData.create(
                event_time=event_time,
                p=player.id,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )
            
        elif data.get('defend_token_drag'):

            dtoken = data['defend_token_drag']
            token_num = dtoken['number']

            try:
                token = DefendToken.filter(group=player.group, number=token_num)[0]
            except:
                token = None

            # # check if token was removed from investigations
            investigation_change = False
            if token.map == 11:
                investigation_change = True

            # # set token to no map while it is being dragged
            token.map = token.x = token.y = token.x2 = token.y2 = 0

            game_data_dict = {
                "event_type": "defend_token_drag",
                "event_time": event_time,
                "token_number": token_num,
                "map": 0,
                "player": player.id_in_group,
            }
            # token count is calculated so we save gamedata here
            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                jdata=json.dumps(game_data_dict)
            )

            # # update users with investigation token count
            if investigation_change:
                token_count = len(DefendToken.filter(group=player.group, map=11))

                # send token count to group
                return {0: {'investigation_update': token_count}}

        elif data.get('steal_token_timeout'):
            
            location = data['steal_token_timeout']['steal_location']

            game_data_dict = {
                "event_type": "steal_token_timeout",
                "player": player.id_in_group,
                "event_time": event_time,
                "steal_reset": location,
            }

            victim = player.group.get_player_by_id(player.map)

            victim.increase_roi(event_time, False)

            game_data_dict.update({
                "victim": victim.id_in_group,
                "victim_roi": victim.roi,
                "victim_balance": victim.balance
            })

            # update player roi
            player.decrease_roi(event_time, True)

            game_data_dict.update({
                "player_roi": player.roi,
                "player_balance": player.balance,
            })

            player.x = player.y = player.map = 0

            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

        elif data.get('steal_token_drag'):

            game_data_dict = {
                "event_type": "steal_token_drag",
                "player": player.id_in_group,
                "event_time": event_time,
                "map": 0,
            }

            if player.map > 0:
                # update victim roi
                victim = player.group.get_player_by_id(player.map)
                victim.increase_roi(event_time, False)

                game_data_dict.update({
                    "victim": victim.id_in_group,
                    "victim_roi": victim.roi,
                    "victim_balance": victim.balance
                })

                # update player roi
                player.decrease_roi(event_time, True)

                game_data_dict.update({
                    "player_roi": player.roi,
                    "player_balance": player.balance,
                })

            else:
                pass

            player.x = player.y = player.map = 0

            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

        elif data.get('defend_token_reset'):

            token_number = data['defend_token_reset']['number']
            token_slot = data['defend_token_reset']['slot']

            game_data_dict = {
                "event_type": "defend_token_reset",
                "event_time": event_time,
                "player": player.id_in_group,
                "token_number": token_number,
                "defend_reset": token_slot,
            }
            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

        elif data.get('steal_token_reset'):

            game_data_dict = {
                "event_type": "steal_token_reset",
                "event_time": event_time,
                "player": player.id_in_group,
                "steal_reset": data["steal_token_reset"]["steal_location"]
            }
            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

        elif data.get('investigation_update'):

            i_token = data['investigation_update']
            token_num = i_token['number']

            try:
                token = DefendToken.filter(group=player.group, number=token_num)[0]
            except:
                token = None

            token.x = token.y = token.x2 = token.y2 = -1
            token.map = 11
            token.last_updated = event_time
            # get investigation token count
            token_count = len(DefendToken.filter(group=player.group, map=11))

            game_data_dict = {
                "event_type": "investigation_update",
                "event_time": event_time,
                "player": player.id_in_group,
                "token_number": token_num,
                "investigation_count": token_count,
            }
            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

            return {0: {'investigation_update': token_count}}
        else:

            game_data_dict = {}

            # root level variables
            map = -1
            x = -1
            y = -1
            intersections = []

            if data.get('defend_token_update'):
                token_update = data['defend_token_update']
                token_num = token_update['number']

                x = token_update['x']
                y = token_update['y']
                map = token_update['map']

                try:
                    token = DefendToken.filter(group=player.group, number=token_num)[0]
                except:
                    token = None

                token.map = map
                token.x = x
                token.y = y
                token.x2 = x + C.defend_token_size
                token.y2 = y + C.defend_token_size

                game_data_dict.update({
                    "event_type": "defend_token_update",
                    "player": player.id_in_group,
                    "event_time": event_time,
                    "token_number": token_num,
                    "map": token.map,
                    "token_x": token.x,
                    "token_y": token.y,
                    "token_x2": token.x2,
                    "token_y2": token.y2,
                })

                # todo check why this was changing the roi and updating the balance for the officer incorrectly?
                players_in_prop = [p for p in player.group.get_players() if p.id_in_group > 1 and p.map == token.map]

                if players_in_prop:
                    for p in players_in_prop:

                        if token.x <= p.x <= token.x2 and \
                                token.y <= p.y <= token.y2:

                            # update culprit
                            p.decrease_roi(event_time, True)

                            # update victim
                            # map here represents the player id in group since they line up in every group/game
                            victim = player.group.get_player_by_id(p.map)
                            victim.increase_roi(event_time, False)

                            # we do this here so we don't reset player data to -1 in which case the ui can't display intersection dots.
                            # create intersection data
                            data = {
                                # police log info
                                'event_time': event_time,

                                'culprit': p.id_in_group,
                                'culprit_y': p.y,
                                'culprit_x': p.x,
                                'culprit_balance': p.balance,
                                'map': p.map,
                                'victim': victim.id_in_group,
                                'victim_roi': victim.roi,
                                'victim_balance': victim.balance,
                                'token_x': token.x,
                                'token_y': token.y,
                                'token_x2': token.x2,
                                'token_y2': token.y2,
                                'steal_reset': randomize_location()
                            }

                            # update player info
                            p.map = 0
                            p.x = p.y = -1

                            intersections.append(data)

            elif data.get('steal_token_update'):

                steal_location = data['steal_token_update']

                x = steal_location['x']
                y = steal_location['y']
                map = steal_location['map']

                player.x = x
                player.y = y
                player.map = map

                game_data_dict.update({
                    "event_type": "steal_token_update",
                    "event_time": event_time,
                    "player": player.id_in_group,
                    "culprit": player.id_in_group,
                    "map": map,
                    "token_x": x,
                    "token_y": y,
                })

                # check for intersections
                tokens = DefendToken.filter(group=player.group, map=player.map)#.order_by('last_updated')
                # todo: test that the list sorts in the correct order
                tokens = sorted(tokens, key=lambda x: x.last_updated if x.last_updated is not None else float('inf'))

                if tokens:
                    for token in tokens:
                        if token.x <= player.x <= token.x2 and token.y <= player.y <= token.y2:

                            # create intersection data
                            data = {
                                # police log info
                                'event_time': event_time,

                                'culprit': player.id_in_group,
                                'map': map,  # ?
                                'token_number': token.number,

                                # data for displaying intersections
                                'culprit_y': y,
                                'culprit_x': x,

                                'token_x': token.x,
                                'token_y': token.y,
                                'token_x2': token.x2,
                                'token_y2': token.y2,
                                'steal_reset': randomize_location()
                            }
                            intersections.append(data)

                            # update player info
                            player.map = 0
                            player.x = 0
                            player.y = 0

                            break

                # if there was no intersection -> update the roi of player and victim
                if player.map != 0:
                    # update player roi
                    player.increase_roi(event_time, True)

                    game_data_dict.update({
                        "culprit_roi": player.roi,
                        "culprit_balance": player.balance,
                    })

                    # get victim object and update roi
                    victim = player.group.get_player_by_id(player.map)
                    victim.decrease_roi(event_time, False)

                    game_data_dict.update({
                        "victim": victim.id_in_group,
                        "victim_roi": victim.roi,
                        "victim_balance": victim.balance,
                    })

            num_investigators = len(DefendToken.filter(group=player.group, map=11))

            # intersection objects for Game Data
            game_data_intersections = []

            # increased for each investigated intersection and civilian fine
            officer_bonus = 0
            civilian_fine = 0
            total_reprimand = 0

            for inter in intersections:

                culprit = inter["culprit"]
                innocent = inter["map"]  # also victim

                # probability no player player convicted
                probability_none = C.calculated_probabilities[num_investigators][2]

                if num_investigators >= C.a_max:
                    innocent_prob = 0
                    # get largest probability since they are all the same after 6 tokens
                    guilty_prob = C.calculated_probabilities[-1][1]
                else:
                    innocent_prob = C.calculated_probabilities[num_investigators][0]

                    guilty_prob = C.calculated_probabilities[num_investigators][1]


                # todo: this should be dynamic or documented that it is tied to num_civilians
                multi = [0, innocent_prob, innocent_prob, innocent_prob, innocent_prob, innocent_prob, probability_none]

                # subtract 1 for 0 based index
                multi[culprit - 1] = guilty_prob
                multi[innocent - 1] = 0

                result = np.random.multinomial(1, multi, 1)[0]

                # which player was convicted from result
                for index, i in enumerate(result):  # search array for result ex; [0,1,0,0,0,0,0]
                    if i == 1:

                        if index == C.PLAYERS_PER_GROUP:
                            # nobody punished, no officer bonus
                            convicted_pid = None
                        else:
                            # no need to add calculable value to game data
                            convicted_pid = int(index + 1)
                        break

                if convicted_pid:
                    convicted_player = player.group.get_player_by_id(convicted_pid)
                    convicted_player.civilian_fine()

                    # increment counter
                    civilian_fine += 1

                    # check if guilty player was convicted
                    # todo: this can be simplified!
                    wrongful_conviction = True
                    if convicted_pid == culprit:
                        wrongful_conviction = False
                    else:
                        pass

                    # UPDATE OFFICER BALANCE
                    if player.id_in_group == 1:
                        officer = player
                    else:
                        officer = player.group.get_player_by_id(1)
                    officer.officer_bonus()

                    # increment counter
                    officer_bonus += 1

                    audit = np.random.binomial(1, C.officer_review_probability)

                    officer_reprimand = 0

                    if audit:
                        if wrongful_conviction:
                            officer.officer_reprimand()
                            officer_reprimand = player.group.officer_reprimand_amount
                            total_reprimand += 1

                    # update intersection object
                    inter.update({
                        "innocent": innocent,  # ?
                        "multi_input": multi,
                        "multi_result": str(result),
                        "guilty": convicted_pid,
                        "wrongful_conviction": wrongful_conviction,
                        "audit": str(audit),

                        # notification log info
                        "officer_bonus": officer.income,
                        "officer_reprimand": officer_reprimand,
                    })

                    game_data_intersections.append(inter)

                else:
                    game_data_intersections.append(inter)

            # send down intersections
            total_inter = len(game_data_intersections)
            if total_inter > 0:

                # update group counters
                officer_history = player.group.intersection_update(officer_bonus, civilian_fine, total_reprimand, total_inter)

                game_data_dict["intersections"] = game_data_intersections


            GameData.create(
                event_time=event_time,
                p=player.id_in_group,
                group=player.group,
                s=player.session_id,
                round_number=player.round_number,
                jdata=json.dumps(game_data_dict)
            )

            if total_inter > 0:
                return {0: {'intersections': intersections,
                        'officer_history': officer_history}}

class StartModal(Page):
    timeout_seconds = 15 
    
    @staticmethod
    def vars_for_template(player: Player):
        # income configuration number
        config_key = player.session.config['civilian_income_config']
        lth = player.session.config['civilian_income_low_to_high']

        civilian_ids = [x + C.PLAYERS_PER_GROUP - C.civilians_per_group for x in
               range(1, C.PLAYERS_PER_GROUP + 1)]

        if player.round_number < 3:  # tutorial or practice round
            tut_civ_income = player.session.config['tutorial_civilian_income']
            tut_o_bonus = player.session.config['tutorial_officer_bonus']

            incomes = [tut_civ_income] * C.civilians_per_group
            incomes_dict = dict(zip(civilian_ids, incomes))
            incomes_dict = dict(sorted(incomes_dict.items(), key=operator.itemgetter(1)))

            start_modal_object = dict(
                civilian_incomes=incomes_dict,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=tut_o_bonus,
                officer_reprimand=player.group.officer_reprimand_amount,
            )
        else:
            incomes = IncomeDistributions.get_group_income_distribution(config_key, player.round_number)
            incomes_dict = dict(zip(civilian_ids, incomes))
            sorted(incomes_dict.values())

            start_modal_object = dict(
                civilian_incomes=incomes_dict,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=player.group.get_player_by_id(1).participant.vars['officer_bonus'],
                officer_reprimand=player.group.officer_reprimand_amount,
            )

        return dict(
                start_modal_object=start_modal_object,
            )


class EndWait(WaitPage):
    
    @staticmethod
    def after_all_players_arrive(group: Group):

        # make end_token
        group.round_end()

        if C.NUM_ROUNDS > 1 and group.round_number < 3:
            # dont generate results for the tutorial and trial period
            pass
        else:
            group.generate_results()

            # only for periods 3-10
            if group.round_number > 2 or C.NUM_ROUNDS == 1:
                for player in group.get_players():
                    player.participant.vars['balances'].append(math.floor(player.balance))
    
class ResultsModal(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        """Players must be advanced past the practice round"""
        return None if player.round_number == 1 else 15

    @staticmethod
    def vars_for_template(player: Player):

        # get title for results modal
        title = 'Round Results'
        if player.group.is_tutorial():
            title = "Tutorial results"

        results_object = dict(balance=player.balance, title=title)

        if player.is_officer():
            officer_results = dict(

                officer_base_pay=C.officer_start_balance,
                fines=player.group.civilian_fine_total,
                reprimands=player.group.officer_reprimand_total,
                officer_reprimand_amount=player.group.officer_reprimand_amount,
            )

            results_object.update(officer_results)

        return dict(results_object=results_object)
    
class Intermission(Page):
    timeout_seconds = 80
    timer_text = 'Please wait for round to start'

    @staticmethod
    def is_displayed(player: Player):

        if C.NUM_ROUNDS > 1 and (player.round_number == 2 or player.round_number == 3 or player.round_number == 8):
            return True
        else:
            return False

    @staticmethod
    def vars_for_template(player: Player):

        config_key = player.session.config['civilian_income_config']
        group_incomes = IncomeDistributions.get_group_income_distribution(config_key, player.round_number)

        if player.round_number < 3:  # tutorial or practice round

            tut_civ_income = player.session.config['tutorial_civilian_income']
            tut_o_bonus = player.session.config['tutorial_officer_bonus']

            vars_dict = dict(
                civilian_incomes=[tut_civ_income] * C.civilians_per_group,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=tut_o_bonus,
                officer_reprimand=player.group.officer_reprimand_amount,
            )
        else:
            vars_dict = dict(
                civilian_incomes=group_incomes,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=player.group.get_player_by_id(1).participant.vars['officer_bonus'],
                officer_reprimand=player.group.officer_reprimand_amount,
            )

        if player.round_number == 2:
            vars_dict['officer_bonus'] = player.session.config['tutorial_officer_bonus']
            info = 'We are about to perform a practice period to ensure everyone is familiar with the computer interface.'
        else:
            info = 'We are about to perform 4 rounds sequentially.'

        vars_dict['info'] = info
        vars_dict['officer_review_probability'] = C.officer_review_probability*100

        return vars_dict
    

class AfterTrialAdvancePage(Page):
    def is_displayed(self):
        if self.round_number == 2 or self.round_number == 7:
            return True

        return False


page_sequence = [
        Wait, 
        Intermission, 
        StartModal, 
        StartWait, 
        Main, 
        EndWait, 
        ResultsModal,
        AfterTrialAdvancePage,
    ]
