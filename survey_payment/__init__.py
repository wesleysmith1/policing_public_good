from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey_payment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    first_name = models.StringField()
    last_name = models.StringField()

    strategy = models.StringField(label="How did you make your decisions during the experiment?")
    feedback = models.StringField(label="Is there anything else you would like to tell the experimenters about this experiment?")

    participant_code = models.StringField()
    id_in_session = models.IntegerField()


# PAGES
class Introduction(Page):
    timeout_seconds = 20
    timer_text = 'Please wait to begin survey'


class SurveyWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # generate results here
        from helpers.payment import generate_payouts
        generate_payouts(self.group)


class FinalWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # check if session includes generating data (otherwise just a survey demo most likely)
        if self.group.session.vars.get('session_start', 0):
            from helpers.payment import generate_survey_csv
            generate_survey_csv(self.group)


class FinalPage(Page):
    pass


class MainSurvey(Page):
    form_model = 'player'
    form_fields = ['first_name', 'last_name', 'strategy', 'feedback']


page_sequence = [SurveyWaitPage, Introduction, MainSurvey, FinalWaitPage, FinalPage]
