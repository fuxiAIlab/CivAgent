import copy
import math
import re
import os

cheat_data = {}
bargain_data = {}
bargain_avg = {}
cheat_avg = {}
bargain_data_num = {}
file_paths = []
folder_path = 'Log'
for foldername, subfolders, filenames in os.walk(folder_path):
    for filename in filenames:
        file_paths.append(os.path.join(foldername, filename))

effective_game_num = 0


def cheat():
    for path in file_paths:
        with open(path, 'r', encoding='latin-1') as file:
            lines = file.readlines()
            argument_str = lines[0]
            pattern = r"\[([^\[\]]*)\]"
            result = re.search(pattern, argument_str)
            if result:
                argument_list = result.group(1).split(", ")
            if "bargain" in argument_list[0]:
                continue
            argument_list = [re.sub(r"('|\")", '', item) for item in argument_list]
            attenk = argument_list[2]
            defense = argument_list[3]
            # ref = {}
            if attenk not in cheat_data:
                cheat_data[attenk] = {}
                cheat_avg[attenk] = {}
                cheat_data[attenk][defense] = {"True": 0, "False": 0}
                cheat_avg[attenk][defense] = []
            if defense not in cheat_data[attenk]:
                cheat_data[attenk][defense] = {"True": 0, "False": 0}
                cheat_avg[attenk][defense] = []
            game_result = lines[-1]
            if "True" not in game_result:
                continue
            pattern = r"{.*}"
            game_result_dict_str = re.search(pattern, game_result).group()
            game_result_dict = eval(game_result_dict_str)
            count = 0
            count += game_result_dict["True"]
            count += game_result_dict["False"]
            cheat_avg[attenk][defense].append(game_result_dict["True"] / count)
            cheat_data[attenk][defense]["True"] += game_result_dict["True"]
            cheat_data[attenk][defense]["False"] += game_result_dict["False"]
    cheat_data_num = copy.deepcopy(cheat_data)
    for attenk in cheat_data_num:
        for defense in cheat_data_num[attenk]:
            total = sum(cheat_data_num[attenk][defense].values())
            cheat_data_num[attenk][defense] = total
    for attenk in cheat_data:
        for defense in cheat_data[attenk]:
            total = sum(cheat_data[attenk][defense].values())
            cheat_data[attenk][defense] = cheat_data[attenk][defense]["True"] / total
    for attenk in cheat_avg:
        for defense in cheat_avg[attenk]:
            len_num = len(cheat_avg[attenk][defense])
            num = 0
            mean_num = 0
            squared_diff = []
            for x in cheat_avg[attenk][defense]:
                num += 1
                mean_num += x
                if len_num < 5 and num == len_num:
                    squared_diff.append((mean_num / len_num))
                if num % 5 == 0:
                    squared_diff.append((mean_num / 5))
                    mean_num = 0
                    len_num -= 5
            squared_diff_num = sum((x - cheat_data[attenk][defense]) ** 2 for x in squared_diff)
            if len(squared_diff) == 0:
                standard_deviation = 0
            else:
                standard_deviation = math.sqrt(squared_diff_num / len(squared_diff))
            print(" Deceiver :", attenk, " Recognizer :", defense, "Standard deviation :", standard_deviation / 2)

    for attenk in cheat_data_num:
        for defense in cheat_data_num[attenk]:
            print(" Deceiver :", attenk, " Recognizer :", defense, " Innings :", cheat_data_num[attenk][defense])
    print("##################################################")
    for attenk in cheat_data:
        for defense in cheat_data[attenk]:
            print(" Deceiver :", attenk, " Recognizer :", defense, " Deception success rate :",
                  cheat_data[attenk][defense])


def bargain():
    for path in file_paths:
        with open(path, 'r', encoding='latin-1') as file:
            lines = file.readlines()
            argument_str = lines[0]
            pattern = r"\[([^\[\]]*)\]"
            result = re.search(pattern, argument_str)
            if result:
                argument_list = result.group(1).split(", ")
            if "cheat" in argument_list[0]:
                continue
            argument_list = [re.sub(r"('|\")", '', item) for item in argument_list]
            buyer_name = argument_list[2].capitalize()
            buyer = argument_list[3]
            settler_name = argument_list[4].capitalize()
            settler = argument_list[5]
            if len(lines) > 2:
                if "bargain" in lines[-1]:
                    bargain_num = lines[-1]
                    bargain_result = lines[-2]
                else:
                    bargain_result = lines[-1]
                    bargain_num = lines[-2]
            if bargain_result == bargain_num:
                continue
            if buyer not in bargain_data:
                bargain_avg[buyer] = {}
                bargain_avg[buyer][settler] = []
                bargain_data[buyer] = {}
                bargain_data[buyer][settler] = {"True": 0, "False": 0}
            if settler not in bargain_data[buyer]:
                bargain_avg[buyer][settler] = []
                bargain_data[buyer][settler] = {"True": 0, "False": 0}

            if buyer not in bargain_data_num:
                bargain_data_num[buyer] = {}
                bargain_data_num[buyer][settler] = {"True": 0, "False": 0}
            if settler not in bargain_data_num[buyer]:
                bargain_data_num[buyer][settler] = {"True": 0, "False": 0}

            if "True" not in bargain_result and "fails" not in bargain_num:
                continue

            pattern = r"{.*}"
            bargain_result_dict_str = re.search(pattern, bargain_result).group()
            bargain_num_dict_str = re.search(pattern, bargain_num).group()
            bargain_result_dict = eval(bargain_result_dict_str)
            bargain_num_dict = eval(bargain_num_dict_str)
            count = 0
            count += bargain_result_dict[buyer_name]
            count += bargain_result_dict[settler_name]
            if count != 0:
                bargain_avg[buyer][settler].append(bargain_result_dict[buyer_name] / count)

            bargain_data[buyer][settler]["True"] += bargain_result_dict[buyer_name]
            bargain_data[buyer][settler]["False"] += bargain_result_dict[settler_name]
            bargain_data_num[buyer][settler]["True"] += bargain_num_dict["The bargain succeeds!"]
            bargain_data_num[buyer][settler]["False"] += bargain_num_dict["The bargain fails!"]
    for buyer in bargain_data:
        for settler in bargain_data[buyer]:
            total = sum(bargain_data[buyer][settler].values())
            if total == 0:
                bargain_data[buyer][settler] = 0
            else:
                bargain_data[buyer][settler] = bargain_data[buyer][settler]["True"] / total
    bargain_data_num_f = copy.deepcopy(bargain_data_num)
    for buyer in bargain_data_num_f:
        for settler in bargain_data_num_f[buyer]:
            total = sum(bargain_data_num_f[buyer][settler].values())
            bargain_data_num_f[buyer][settler] = bargain_data_num_f[buyer][settler]["False"] / total

    for buyer in bargain_data_num:
        for settler in bargain_data_num[buyer]:
            total = sum(bargain_data_num[buyer][settler].values())
            bargain_data_num[buyer][settler] = total
    for buyer in bargain_data:
        for settler in bargain_data[buyer]:
            print(" buyer :", buyer, " seller :", settler, " odds :", bargain_data[buyer][settler])
    print("##################################################")
    for buyer in bargain_avg:
        for settler in bargain_avg[buyer]:
            len_num = len(bargain_avg[buyer][settler])
            num = 0
            mean_num = 0
            squared_diff = []
            for x in bargain_avg[buyer][settler]:
                num += 1
                mean_num += x
                if len_num < 5:
                    squared_diff.append((mean_num / len_num))
                if num % 5 == 0:
                    squared_diff.append((mean_num / 5))
                    mean_num = 0
                    len_num -= 5
            squared_diff_num = sum((x - bargain_data[buyer][settler]) ** 2 for x in squared_diff)
            if len(bargain_avg[buyer][settler]) == 0:
                standard_deviation = 0
            else:
                standard_deviation = math.sqrt(squared_diff_num / len(squared_diff))
            print(" Buyer :", buyer, " Seller :", settler, " Standard deviation :", standard_deviation / 2)
    print("##################################################")
    for buyer in bargain_data_num:
        for settler in bargain_data_num[buyer]:
            print(" Buyer :", buyer, " Seller :", settler, " Number of trades :", bargain_data_num[buyer][settler])
    print("##################################################")
    for buyer in bargain_data_num_f:
        for settler in bargain_data_num_f[buyer]:
            print(" Buyer :", buyer, " Seller :", settler, " Failed transaction rate :",
                  bargain_data_num_f[buyer][settler])


if __name__ == '__main__':
    # cheat()
    bargain()
