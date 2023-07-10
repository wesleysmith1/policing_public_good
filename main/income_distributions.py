class IncomeDistributions:
    civilian_incomes = [10, 15, 20, 25, 30]

    one = (
        (1,5,4,3,2),
        (2,3,5,4,1),
        (3,2,1,5,4),
        (4,1,3,2,5),
        (5,4,2,1,3,),

        (2,1,5,4,3),
        (1,2,3,5,4),
        (4,3,2,1,5),
        (5,4,1,3,2),
        (3,5,4,2,1),
    )

    configurations = {1: one}

    @classmethod
    def get_group_incomes(cls, round_num):
        """return high or low incomes based off round"""
        return cls.civilian_incomes

    @classmethod
    def format_round(cls, round_num):
        """round number is offset by tutorial and practice rounds"""
        return round_num - 3

    @classmethod
    def get_group_income_keys(cls, config, round_num):
        """return row from configuration"""
        return cls.configurations[config][cls.format_round(round_num)]

    @classmethod
    def get_group_income_distribution(cls, config, round_num):
        """return list of civilian income values"""

        income_keys = cls.get_group_income_keys(config, round_num)
        income_values = cls.get_group_incomes(round_num)

        results = []
        for i in income_keys:
            key = i-1
            civilian_income = income_values[key]
            results.append(civilian_income)

        return results