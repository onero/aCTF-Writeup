from itertools import product
import re

flag_valid_chars = "NC3{_abcdefghijklmnopqrstuvwxyz}"
flag_valid_chars_int =[] 
for c in flag_valid_chars:
    flag_valid_chars_int.append(ord(c))

all_results = []
with open("addiplikation_results.txt", "r") as f:
    for line in f:
        all_results.append(int(line))

calculated_results = all_results.copy()

def find_highest_candidate_char(results):
    possible_candidates = {} 

    for current_number in results:
        for test_char_int in flag_valid_chars_int:
            #print(chr(test_char_int) + ":" + str(current_number) + "%" + str(test_char_int) + " = " + str(current_number % test_char_int))
            if current_number % test_char_int == 0:
                test_char = chr(test_char_int)
                if (test_char in possible_candidates):
                    possible_candidates[test_char] += 1
                else: 
                    possible_candidates[test_char] = 1

    sorted_poss_cand = sorted(possible_candidates.items(), key=lambda item: item[1], reverse=True)
    #print(sorted_poss_cand)
    return sorted_poss_cand[0][0]

def recalculate_results(results_to_recalculate, new_char):
    new_char_int = ord(new_char)
    #print(f"Known char: {new_char} ({new_char_int})")

    new_results = [] 
    for current_number in results_to_recalculate:
        if current_number % new_char_int == 0:
            #print(f"Divide: {current_number}/{new_char_int} = {current_number/new_char_int}")
            new_results.append(current_number // new_char_int)
        else:
            #print(f"Minus: {current_number}-{new_char_int} = {current_number-new_char_int}")
            new_results.append(current_number - new_char_int)
        
    return new_results

flag = ''
reversed_flag = ''
flag_found = False
chars_found = 0
while True:
    new_char = find_highest_candidate_char(calculated_results)
    print('Most likely character: ' + new_char)

    calculated_results = recalculate_results(calculated_results, new_char)
    if not calculated_results:
        print("No more cadidate characters found before flag is done - not enough data?")
        break

    reversed_flag += new_char
    
    flag = reversed_flag[::-1]
    
    if re.match("NC3{.*}", flag):
        print('Flag found!')
        break

    chars_found += 1
    if chars_found > 100:
        print("100 chars found, breaking loop")
        break
print("Final flag: " + flag)