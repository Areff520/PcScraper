import pandas as pd


def calculate_worth(succesfulL_dict):
    """Takes dict

    :return
    list
    """
    columns = ['Title','Org Price','Solo Price','Difference','link']
    df = pd.DataFrame(columns=columns)
    passed_dicts = []
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
            passed_dicts.append({key: values})
            new_row = {'Title': key, 'Org Price': original_price, 'Solo Price': solo_price,
                       'Difference': f'-{difference}',
                       'link': link}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    result = 'result.xlsx'
    df.to_excel(result, index=False)

    return passed_dicts