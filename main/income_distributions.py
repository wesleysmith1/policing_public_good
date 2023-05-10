class IncomeDistributions:
    civilian_incomes_low = [32,33,34,35,38]
    civilian_incomes_high = [29,31,33,36,43]

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
    def get_group_incomes(cls, low_to_high, round_num):
        """return high or low incomes based off round"""
        if round_num < 7:
            if low_to_high:
                return cls.civilian_incomes_low
            else:
                return cls.civilian_incomes_high
        else:
            if low_to_high:
                return cls.civilian_incomes_high
            else:
                return cls.civilian_incomes_low

    @classmethod
    def format_round(cls, round_num):
        """round number is offset by tutorial and practice rounds"""
        return round_num - 3

    @classmethod
    def get_group_income_keys(cls, config, round_num):
        """return row from configuration"""
        return cls.configurations[config][cls.format_round(round_num)]

    @classmethod
    def get_group_income_distribution(cls, config, low_to_high, round_num):
        """return list of civilian income values"""

        income_keys = cls.get_group_income_keys(config, round_num)
        income_values = cls.get_group_incomes(low_to_high, round_num)

        results = []
        for i in income_keys:
            key = i-1
            civilian_income = income_values[key]
            results.append(civilian_income)

        return results


def test_income_config():
    group_incomes = IncomeDistributions.get_group_incomes(3)
    print(f"group incomes: {group_incomes}")

    group_keys = IncomeDistributions.get_group_income_keys(1,3)
    print(f"group income keys: {group_keys}")

    income_distribution = IncomeDistributions.get_group_income_distribution(1, 3)
    print(f"group income distribution {income_distribution}")

