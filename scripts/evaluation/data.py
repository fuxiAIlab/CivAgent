import math
import re
import os

civ_str = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
civ_str_list = {'none': [], 'workflow': [], 'simlator': [], 'reflexion': []}
decision_num = {'none': {'yes': 0, 'no': 0},
                'workflow': {'yes': 0, 'no': 0},
                'simlator': {'yes': 0, 'no': 0},
                'reflexion': {'yes': 0, 'no': 0}}
try_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
replace_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
declar_war_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
form_ally_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
form_ally_agree = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
form_ally_reject = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
seek_peace_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
seek_peace_agree = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
seek_peace_reject = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
change_closeness_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
change_closeness_agree = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
change_closeness_reject = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
research_agreement_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
research_agreement_agree = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
research_agreement_reject = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
common_enemy_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
common_enemy_agree = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
common_enemy_reject = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}

cheat_num = {'none': 0, 'workflow': 0, 'simlator': 0, 'reflexion': 0}
civ_name_str = {"rome": 0, "aztecs": 0, "greece": 0, "egypt": 0}

folder_path = 'Log'
file_paths = []

used_declare_war = "used the declare_war skill"
used_change_closeness = "used the change_closeness skill"
used_seek_peace = "used the seek_peace skill"
used_cheat = "used the cheat skill"
used_form_ally = "used the form_ally skill"
used_research_agreement = "used the research_agreement skill"
used_common_enemy = "used the common_enemy skill"

agree_change_closeness = "agreed to change_closeness"
agree_seek_peace = "agreed to seek_peace"
agree_form_ally = "agreed to form_ally"
agree_research_agreement = "agreed to research_agreement"
agree_common_enemy = "agreed to common_enemy"

rejected_change_closeness = "rejected change_closeness"
rejected_seek_peace = "rejected seek_peace"
rejected_form_ally = "rejected form_ally"
rejected_research_agreement = "rejected research_agreement"
rejected_common_enemy = "rejected common_enemy"


def get_agree_probability(agree_dict, reject_dict):
    agree_probability = {}
    for k in agree_dict.keys():
        agree_probability[k] = agree_dict[k] / (agree_dict[k] + reject_dict[k])
    return agree_probability


for foldername, subfolders, filenames in os.walk(folder_path):
    for filename in filenames:
        file_paths.append(os.path.join(foldername, filename))

effective_game_num = 0

civ_work_num = {"rome": 0, "aztecs": 0, "greece": 0, "egypt": 0}

for path in file_paths:
    with open(path, 'r', encoding='latin-1') as file:
        lines = file.readlines()
        if "replace" not in lines[-1]:
            continue
        effective_game_num += 1
        argument_str = lines[0]
        pattern = r"\[([^\[\]]*)\]"
        result = re.search(pattern, argument_str)
        if result:
            argument_list = result.group(1).split(", ")
        argument_list = [re.sub(r"('|\")", '', item) for item in argument_list]
        ref = {}
        ref[argument_list[5]] = "reflexion"
        ref[argument_list[10]] = "simlator"
        ref[argument_list[15]] = "workflow"
        ref[argument_list[20]] = "none"
        for line in lines:
            if used_declare_war in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                declar_war_num[ref[civ_name]] += 1
            if used_change_closeness in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                change_closeness_num[ref[civ_name]] += 1
            if used_seek_peace in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                seek_peace_num[ref[civ_name]] += 1
            if used_cheat in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                cheat_num[ref[civ_name]] += 1
            if used_form_ally in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                form_ally_num[ref[civ_name]] += 1
            if used_research_agreement in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                research_agreement_num[ref[civ_name]] += 1
            if used_common_enemy in line:
                civ_name = line.replace("'", ",").split(',')[1].replace(" ", "")
                common_enemy_num[ref[civ_name]] += 1

            if agree_change_closeness in line:
                civ_name = line.replace(",", "").split(' ')[9]
                change_closeness_agree[ref[civ_name]] += 1
            if agree_seek_peace in line:
                civ_name = line.replace(",", "").split(' ')[9].replace(" ", "")
                seek_peace_agree[ref[civ_name]] += 1
            if agree_form_ally in line:
                civ_name = line.replace(",", "").split(' ')[9].replace(" ", "")
                form_ally_agree[ref[civ_name]] += 1
            if agree_research_agreement in line:
                civ_name = line.replace(",", "").split(' ')[9].replace(" ", "")
                research_agreement_agree[ref[civ_name]] += 1
            if agree_common_enemy in line:
                civ_name = line.replace(",", "").split(' ')[9].replace(" ", "")
                common_enemy_agree[ref[civ_name]] += 1

            if rejected_change_closeness in line:
                civ_name = line.replace(",", "").split(' ')[8].replace(" ", "")
                change_closeness_reject[ref[civ_name]] += 1

            if rejected_seek_peace in line:
                civ_name = line.replace(",", "").split(' ')[8].replace(" ", "")
                seek_peace_reject[ref[civ_name]] += 1

            if rejected_form_ally in line:
                civ_name = line.replace(",", "").split(' ')[8].replace(" ", "")
                form_ally_reject[ref[civ_name]] += 1

            if rejected_research_agreement in line:
                civ_name = line.replace(",", "").split(' ')[8].replace(" ", "")
                research_agreement_reject[ref[civ_name]] += 1

            if rejected_common_enemy in line:
                civ_name = line.replace(",", "").split(' ')[8].replace(" ", "")
                common_enemy_reject[ref[civ_name]] += 1

        game_result = lines[-4]
        decision_result = lines[-3]
        try_result = lines[-2]
        replace_result = lines[-1]
        pattern = r"{.*}"
        game_result_dict_str = re.search(pattern, game_result).group()
        decision_result_dict_str = re.search(pattern, decision_result).group()
        try_result_dict_str = re.search(pattern, try_result).group()
        replace_result_dict_str = re.search(pattern, replace_result).group()

        game_result_dict = eval(game_result_dict_str)
        decision_result_dict = eval(decision_result_dict_str)
        try_result_dict = eval(try_result_dict_str)
        replace_result_dict = eval(replace_result_dict_str)
        count = 0
        for civ in game_result_dict:
            if isinstance(game_result_dict[civ], list):
                civ_str[ref[civ]] += game_result_dict[civ][-1]
                civ_name_str[civ] += game_result_dict[civ][-1]
                count += game_result_dict[civ][-1]
            else:
                civ_str[ref[civ]] += game_result_dict[civ]
                civ_name_str[civ] += game_result_dict[civ]
                count += game_result_dict[civ]
        for civ in game_result_dict:
            if isinstance(game_result_dict[civ], list):
                civ_str_list[ref[civ]].append(game_result_dict[civ][-1] / count)
            else:
                civ_str_list[ref[civ]].append(game_result_dict[civ] / count)

        for civ in decision_result_dict:
            decision_num[ref[civ]]['yes'] += decision_result_dict[civ]['yes']
            decision_num[ref[civ]]['no'] += decision_result_dict[civ]['no']

        for civ in try_result_dict:
            try_num[ref[civ]] += try_result_dict[civ]

        for civ in replace_result_dict:
            replace_num[ref[civ]] += replace_result_dict[civ]

print("effective_game_num:", effective_game_num)
total = sum(civ_str.values())

for k in civ_str:
    for decision in decision_num[k]:
        decision_num[k][decision] = int(decision_num[k][decision] / effective_game_num)
    civ_str[k] = civ_str[k] / total
    try_num[k] = int(try_num[k] / effective_game_num)
    replace_num[k] = int(replace_num[k] / effective_game_num)
    declar_war_num[k] = float(declar_war_num[k] / effective_game_num)
    form_ally_num[k] = float(form_ally_num[k] / effective_game_num)
    seek_peace_num[k] = float(seek_peace_num[k] / effective_game_num)
    change_closeness_num[k] = float(change_closeness_num[k] / effective_game_num)
    cheat_num[k] = float(cheat_num[k] / effective_game_num)
    research_agreement_num[k] = float(research_agreement_num[k] / effective_game_num)
    common_enemy_num[k] = float(common_enemy_num[k] / effective_game_num)
    change_closeness_agree[k] = int(change_closeness_agree[k] / effective_game_num)
    seek_peace_agree[k] = int(seek_peace_agree[k] / effective_game_num)
    form_ally_agree[k] = int(form_ally_agree[k] / effective_game_num)
    research_agreement_agree[k] = int(research_agreement_agree[k] / effective_game_num)
    common_enemy_agree[k] = int(common_enemy_agree[k] / effective_game_num)
    change_closeness_reject[k] = int(change_closeness_reject[k] / effective_game_num)
    seek_peace_reject[k] = int(seek_peace_reject[k] / effective_game_num)
    form_ally_reject[k] = int(form_ally_reject[k] / effective_game_num)
    research_agreement_reject[k] = int(research_agreement_reject[k] / effective_game_num)
    common_enemy_reject[k] = int(common_enemy_reject[k] / effective_game_num)

change_closeness_agree_p = get_agree_probability(change_closeness_agree, change_closeness_reject)
seek_peace_agree_p = get_agree_probability(seek_peace_agree, seek_peace_reject)
form_ally_agree_p = get_agree_probability(form_ally_agree, form_ally_reject)
research_agreement_agree_p = get_agree_probability(research_agreement_agree, research_agreement_reject)
common_enemy_agree_p = get_agree_probability(common_enemy_agree, common_enemy_reject)
for k in civ_str_list:
    squared_diff = sum((x - civ_str[k]) ** 2 for x in civ_str_list[k])
    print("variance:", k, squared_diff / len(civ_str_list[k]) / 2)
    standard_deviation = math.sqrt(squared_diff / len(civ_str_list[k]))
    print("Standard deviation:", k, standard_deviation / 2)

print("civ_str_list:", civ_str_list)
print("civ_name_str:", civ_name_str)
print("civ_str:", civ_str)
print("declar_war_num:", declar_war_num)
print("form_ally_num:", form_ally_num)
print("seek_peace_num:", seek_peace_num)
print("change_closeness_num:", change_closeness_num)
print("cheat_num:", cheat_num)
print("research_agreement_num:", research_agreement_num)
print("common_enemy_num:", common_enemy_num)
print("change_closeness_agree_p:", change_closeness_agree_p)
print("seek_peace_agree_p:", seek_peace_agree_p)
print("form_ally_agree_p:", form_ally_agree_p)
print("research_agreement_agree_p:", research_agreement_agree_p)
print("common_enemy_agree_p:", common_enemy_agree_p)
print("decision_num:", decision_num)
print("try_num:", try_num)
print("replace_num:", replace_num)
