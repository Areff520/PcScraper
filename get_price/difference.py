import pandas as pd


def calculate_worth(succesfulL_dict):
    """Takes dict

    :return
    dict {price added to values}
    """
    passed_dicts = {}
    for key, values in succesfulL_dict.items():
        link = values[2]
        original_price = int(values[3])
        solo_price = int(values[4])
        difference = original_price-solo_price

        #Getting difference to return as lsit
        if difference:
            difference = 100 * difference / solo_price
            difference = str(difference).split('.')
            difference = int(difference[0])
            values.append(difference)
            passed_dicts[key] = values

    return passed_dicts