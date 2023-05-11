from otree.api import *
import operator
from random import randrange
import json
import time, datetime

from main.income_distributions import IncomeDistributions


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = 6
    civilians_per_group = 5
    NUM_ROUNDS = 10

    CIVILIAN_START_BALANCE = 1000

    """Number of defend tokens officer starts with"""
    defend_token_total = 8

    """Fine when convicted"""
    civilian_fine_amount = 120
    """number of grain earned per second of stealing"""
    civilian_steal_rate = 13

    """Probability that an intersection outcome will be reviewed"""
    officer_review_probability = .1
    """P punishment for officer if innocent civilian is punished"""
    officer_reprimand_amount = 10

    """Officer incomes. One for each group"""
    officer_incomes = [180, 180, 180]

    """ 
    this is the size of the tokens and maps are defined. 
    """
    defend_token_size = 68 * 1.5
    civilian_map_size = 200 * 1.5

    """
    Probability innocent and guilty are calculated when the number of 
    investigation tokens is >= this number
    """
    a_max = 6
    """Guilty probability when """
    beta = .9

    """
    Tutorial, game and results modal durations are defined here and passed to frontend
    """
    tutorial_duration_seconds = 1800
    game_duration_seconds = 198
    results_modal_seconds = 30
    start_modal_seconds = 15

    """
    this defines how long a steal token remains on a map before resetting to the 'steal home'
    """
    steal_timeout_milli = 1000

    """
    Steal tokens positions defines the number of slots inside the 'steal home' rectangle. 
    Steal tokens can be loaded or reset to any of the slots 
    """
    steal_token_slots = 20

    officer_start_balance = 0
    civilian_start_balance = 0


class Subsession(BaseSubsession):
    pass


class GameStatus:
    SYNC = 0
    INFO = 1
    ACTIVE = 2
    RESULTS = 3
    CHOICES = (
        (SYNC, 'Sync'),
        (INFO, 'Start'),
        (ACTIVE, 'Active'),
        (RESULTS, 'Results'),
    )


class Group(BaseGroup):
    game_start = models.FloatField(blank=True)
    officer_bonus = models.IntegerField(initial=0)
    # counters
    officer_bonus_total = models.IntegerField(initial=0)
    civilian_fine_total = models.IntegerField(initial=0)
    officer_reprimand_total = models.IntegerField(initial=0)
    intercept_total = models.IntegerField(initial=0)

    game_status = models.IntegerField(choices=GameStatus.CHOICES, initial=GameStatus.SYNC)


def randomize_location():
    """return a random location for civilian steal token"""
    return randrange(C.steal_token_slots)+1


class Player(BasePlayer):
    x = models.FloatField(initial=0)
    y = models.FloatField(initial=0)
    map = models.IntegerField(initial=0)
    last_updated = models.FloatField(blank=True)
    roi = models.IntegerField(initial=0)
    balance = models.FloatField(initial=C.CIVILIAN_START_BALANCE)
    harvest_status = models.IntegerField(initial=0)
    harvest_screen = models.BooleanField(initial=True)
    income = models.IntegerField(initial=40)
    steal_start = models.IntegerField(initial=randomize_location)
    steal_count = models.IntegerField(initial=0)
    victim_count = models.IntegerField(initial=0)
    steal_total = models.FloatField(initial=0)
    victim_total = models.FloatField(initial=0)
    ready = models.BooleanField(initial=False)

    def is_officer(self):
        """officer always has id_in_group of 1"""
        return self.id_in_group == 1
    

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
    event_time = models.FloatField()
    p = models.IntegerField(initial=0)
    g = models.IntegerField(initial=0)
    s = models.IntegerField(initial=0)
    round_number = models.IntegerField(initial=0)
    # jdata = models.


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
    low_to_high = subsession.session.config['civilian_income_low_to_high']
    income_config = subsession.session.config['civilian_income_config']

    round_incomes = IncomeDistributions.get_group_income_distribution(
        income_config, low_to_high, subsession.round_number)

    # this code is the terrible way that officer income is determined for session
    if subsession.round_number == 1:
        for index, group in enumerate(subsession.get_groups()):
            officer = group.get_player_by_id(1)
            officer.participant.vars['officer_bonus'] = officer.income = C.officer_incomes[index]

            # save group id relative to session, not all groups in database
            officer.participant.vars['group_id'] = index+1

            for p in group.get_players():
                if not p.is_officer():
                    p.income = subsession.session.config['tutorial_civilian_income']

    for group in subsession.get_groups():
        for p in group.get_players():

            # initialize balances list
            p.participant.vars['balances'] = []
            p.participant.vars['steal_start'] = p.steal_start

            if p.is_officer():
                p.balance = C.officer_start_balance

            # check if round is tutorial or practice period
            if group.round_number < 3:
                if p.is_officer():
                    p.income = subsession.session.config['tutorial_officer_bonus']
                else:
                    p.income = subsession.session.config['tutorial_civilian_income']
            else:
                # set harvest amount for civilians
                if not p.is_officer():
                    p.income = round_incomes[p.id_in_group-2]
                else:
                    p.income = p.participant.vars['officer_bonus']

        # create defend tokens for current round for each group
        for i in range(C.defend_token_total):
            DefendToken.create(number=i+1, group=group,)


# PAGES
class Main(Page):

    @staticmethod
    def vars_for_template(player: Player):
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
                officer_reprimand=C.officer_reprimand_amount,
            )
        else:
            incomes = IncomeDistributions.get_group_income_distribution(config_key, low_to_high, player.round_number)
            incomes_dict = dict(zip(civilian_ids, incomes))
            sorted(incomes_dict.values())

            start_modal_object = dict(
                civilian_incomes=incomes_dict,
                steal_rate=C.civilian_steal_rate,
                civilian_fine=C.civilian_fine_amount,
                officer_bonus=player.group.get_player_by_id(1).participant.vars['officer_bonus'],
                officer_reprimand=C.officer_reprimand_amount,
            )
        
        return dict(
            defend_tokens=defend_tokens,
            balance_update_rate=player.session.config['balance_update_rate'],
            start_modal_object=start_modal_object,
            game_status=player.group.field_maybe_none('game_status'),
            harvest_screen=player.harvest_screen,
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
    

page_sequence = [Main]
