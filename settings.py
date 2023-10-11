from os import environ


SESSION_CONFIGS = [
    dict(
        name='main',
        display_name="mechanism_and_public_good",
        app_sequence=['welcome', 'main', 'survey_payment'],
        num_demo_participants=6,
        showup_payment=7,
        grain_conversion=.011111,
        civilian_income_low_to_high=True,
        civilian_income_config=1,
        tutorial_civilian_income=20,
        tutorial_officer_bonus=50,
        session_identifier=0,
        balance_update_rate=100,
    ),
    dict(
        name='survey_payment',
        app_sequence=['survey_payment'],
        num_demo_participants=1,
        showup_payment=7,
        grain_conversion=.011111,
        civilian_income_low_to_high=True,
        civilian_income_config=1,
        tutorial_civilian_income=20,
        tutorial_officer_bonus=50,
        session_identifier=0,
        balance_update_rate=100,
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['officer_bonus', 'group_id', 'balances', 'steal_start']
SESSION_FIELDS = ['session_start', 'session_date', 'incomes']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '6441528843247'

INSTALLED_APPS = ['otree']
