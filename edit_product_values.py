import re
import the_dict


def make_additional_product_detail(product_dicts):
    additional_product_detail_dict = {}
    additional_product_detail_tuples_list = []
    for name, values in product_dicts.items():
        try:
            product_details_dict = values[0]
            product_site = values[2]
            cpu_shortened = ''
            motherboard_shortened = ''
            gpu_shortened = ''
            ram_shortened = ''
            ssd_shortened = ''
            if 'itopya' in product_site or 'gaming' in product_site:
                name_shortened = name.split('/')[0]
            elif 'sinerji' in product_site:
                name_splitted = name.split(' ')
                for index, word in enumerate(name_splitted):
                    if 'ryzen' == word.lower() or 'intel' == word.lower():
                        split_index = index
                name_shortened = ' '.join(word for word in name_splitted[0:split_index])
            elif 'pckolik' in product_site:
                name_shortened = name.split('Oyun')[0]
            elif 'gamegaraj' in product_site:
                name_shortened = name
            if len(name_shortened) > 99:
                name_splitted = name.split(' ')
                name_shortened = ' '.join(word for word in name_splitted[0:2])
            for key, value in product_details_dict.items():
                if key == 'i̇şlemci' or key == 'işlemci':
                    value_splitted = value.split(' ')
                    for index, word in enumerate(value_splitted):
                        if 'ghz' in word.lower() or 'mpk' == word.lower():
                            split_index = index
                            break
                    cpu_shortened = ' '.join(word for word in value_splitted[0:split_index+1])
                    #First two word start with uppercase and other words are fully upper case
                    input_string = ' '.join(word for word in value_splitted[0:split_index+1]
                                         if '.' not in word and 'ghz' not in word.lower())
                    input_string = input_string.replace('-', ' ')
                    words = input_string.split()
                    if len(words) >= 2:
                        words[0] = words[0].capitalize()
                        words[1] = words[1].capitalize()
                    formatted_string = ' '.join(words)
                    cpu_model = formatted_string
                    cpu_model = cpu_model.replace('MPK', '').replace('Core', '').replace('Amd', '').strip()
                    #Removing all kinds of white space
                    cpu_model = re.sub(r"^\s+|\s+$", "", cpu_model)
                    print(name_shortened)
                    print(f"it is  '{cpu_model}'")
                elif key == 'anakart':
                    pattern = re.compile(r'(?=.*[a-zA-Z])(?=.*\d)')
                    value_splitted = value.split(' ')
                    for word in value_splitted:
                        if pattern.search(word) and len(motherboard_shortened) == 0:
                            motherboard_shortened = word
                        elif 'ddr' in word.lower():
                            motherboard_shortened = f'{motherboard_shortened} {word}'
                    motherboard_shortened = f'{value_splitted[0]} {motherboard_shortened}'
                    motherboard_model = motherboard_shortened.split(' ')[1]
                    motherboard_shortened = motherboard_shortened.replace('DDR4 DDR4', 'DDR4')
                    motherboard_model = motherboard_model.replace('DDR4 DDR4', 'DDR4')
                elif key == 'ekran kartı':
                    #Removing typo additional spaces
                    value = ' '.join(value.split())

                    value_splitted = value.split(' ')
                    brand = ''
                    ti_info = ''
                    oc_info = ''
                    gb_info = ''
                    pattern_gpu = re.compile(r'^rtx\d', re.IGNORECASE)
                    pattern_gpu_gb = re.compile(r'^(?:[^a-zA-Z]*gb[^a-zA-Z]*)$', re.IGNORECASE)

                    split_index = -1
                    for index, word in enumerate(value_splitted):
                        if word.lower() == 'rtx' and split_index == -1 or pattern_gpu.search(word) and split_index == -1:
                            brand = 'nvdia'
                            split_index = index
                        elif word.lower() == 'rx' and split_index == -1:
                            brand = 'amd'
                            split_index = index
                        elif word.lower() == 'oc' and split_index == -1:
                            oc_info = word
                        elif word.lower() == 'arc' and split_index == -1:
                            split_index = index
                        elif pattern_gpu_gb.search(word):
                            gb_info = word
                        elif word.lower() == 'ti':
                            ti_info = word


                    if len(value_splitted[split_index]) > 3:
                        gpu_shortened = f'{value_splitted[0]} {value_splitted[split_index]} {ti_info} {oc_info} {gb_info}'
                    else:
                        gpu_shortened = f'{value_splitted[0]} {value_splitted[split_index]} {value_splitted[split_index+1]} {ti_info} {oc_info} {gb_info}'
                    gpu_shortened = ' '.join(word for word in gpu_shortened.split() if word)
                    gpu_model = ' '.join(word for word in gpu_shortened.split(' ')[1:]
                                         if 'oc' not in word.lower() and 'gb' not in word.lower())
                    gpu_shortened = gpu_shortened.replace('RTX3060TI', 'RTX 3060 Ti').replace('RTX 4060TI', 'RTX 4060 Ti')\
                        .replace('RTX 4060TI', 'RTX 4060Ti').replace('RTX 3060 TI', 'RTX 3060 Ti')\
                        .replace('RTX4070TI', 'RTX 4070 Ti').replace('RTX 4060 TI', 'RTX 4060 Ti')\
                        .replace('RTX4080', 'RTX 4080').replace('RTX4090', 'RTX 4090')
                    gpu_model = gpu_model.replace('RTX3060TI', 'RTX 3060 Ti').replace('RTX 4060TI', 'RTX 4060 Ti')\
                        .replace('RTX 4060TI', 'RTX 4060Ti').replace('RTX 3060 TI', 'RTX 3060 Ti')\
                        .replace('RTX4070TI', 'RTX 4070 Ti').replace('RTX 4060 TI', 'RTX 4060 Ti')\
                        .replace('RTX4080', 'RTX 4080').replace('RTX4090', 'RTX 4090').replace('ARC', 'Arc')


                elif key == 'ram':
                    value_splitted = value.split(' ')
                    for word in value_splitted:
                        if 'gb' in word.lower() and len(word) < 13 and len(ram_shortened) == 0:
                            ram_shortened = f'{word} '
                        elif '(' in word and ')' in word and len(word) < 8 or 'mhz' in word.lower() and len(word) < 8:
                            ram_shortened += f'{word} '
                    ram_shortened = f'{value_splitted[0]} {ram_shortened}'
                    if 'itopya' in product_site and '8GB' in ram_shortened and 'x' not in ram_shortened.lower():
                        ram_shortened = ram_shortened.replace('8GB', '16GB (2x8GB)')
                    ram_capacity = ' '.join (word.split('(')[0] for word in ram_shortened.split(' ')
                                             if 'gb' in word.lower())
                    ram_speed = ' '.join(word for word in ram_shortened.split(' ')
                                         if 'mhz' in word.lower())

                elif key == 'ssd':
                    pattern_ssd_speed = re.compile(r'\b\d+MB\b', re.IGNORECASE)
                    pattern_speed = []
                    value_splitted = value.split(' ')
                    for word in value_splitted:
                        if 'gb' in word.lower() and len(word) < 6 or 'tb' in word.lower() and len(word) < 6:
                            ssd_shortened = word
                        elif pattern_ssd_speed.search(word):
                            if '-' in word:
                                word = word.split('-')[0]
                            word = word.replace('(', '').replace(')', '')
                            pattern_speed.append(word)
                    if len(pattern_speed) > 1:
                        pattern_speed = '/'.join(word for word in pattern_speed)
                    else:
                        pattern_speed = ''
                    ssd_shortened = f'{value_splitted[0]} {ssd_shortened} {pattern_speed}'
                    ssd_capacity = ' '.join(word for word in ssd_shortened.split(' ')
                                            if 'gb' in word.lower())
            print(f'{name_shortened}')
            additional_product_detail_dict[name] = {'name_shortened': name_shortened, 'cpu_shortened': cpu_shortened,
                                                   'cpu_model':cpu_model,'gpu_shortened': gpu_shortened,'gpu_model':gpu_model,
                                                   'motherboard_shortened': motherboard_shortened, 'motherboard_model': motherboard_model,
                                                   'ram_shortened': ram_shortened, 'ram_speed': ram_speed, 'ram_capacity': ram_capacity,
                                                   'ssd_shortened': ssd_shortened, 'ssd_capacity': ssd_capacity}
            print('\n\n')
            print(name, values)
            for key, value in additional_product_detail_dict[name].items():
                print(f'{key} : {value}')
            additional_product_detail_tuples_list.append((name, name_shortened, cpu_shortened, cpu_model, gpu_shortened, gpu_model,
                                                         motherboard_shortened, motherboard_model, ram_shortened, ram_speed, ram_capacity,
                                                         ssd_shortened, ssd_capacity))
        except:
            print('Eror detected passing')

    return additional_product_detail_tuples_list


