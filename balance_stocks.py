#!/usr/bin/env python3
import os
import sys
from collections import OrderedDict

IS_EXTENDED = False # Buying ETFs from now on
SHOULD_BALANCE = False

CURRENT_DIVISION = {
    'SMALL CAP (VTWO)': .10,
    'REIT (VNQI)': .05,
    'EMERGING (SCHE)': .40,
    'MISC (VYM)': .05,
    'DEV (VEA)': .40,
}

CURRENT_DIVISION_DETAILED = {
    'DEV': {
        'US': 0.646,
        'EU': 0.257,
        'JP': 0.097,
    }
}

EPSILON = 0.1

def signed(f):
    return ("+" if f > 0 else "") + str(round(f, 2))


def print_table(values, total, deposit):
    print("-" * 85)
    print("%-20s%-15s%-5s%-15s%-5s%-15s%8s" % ("NAME", "OLD AMOUNT", "%", "NEW AMOUNT", "%", "DIFFERENCE", "TARGET %"))
    print("-" * 85)
    for name, data in values.items():
        old_part = data['current_value'] / (total - deposit) * 100
        new_part = data['new_value'] / total * 100
        diff = signed(data['new_value'] - data['current_value'])

        print("%-20s%-15.2f%-5.1f%-15.2f%-5.1f%-15s%-8.1f" % (name, data['current_value'], old_part, data['new_value'], new_part, diff, data['target_part'] * 100))


def main():
    values = dict(CURRENT_DIVISION)
    for name, part in values.items():
        if IS_EXTENDED:
            if name in CURRENT_DIVISION_DETAILED.keys():
                for subname, subpart in CURRENT_DIVISION_DETAILED[name].items():
                    print(f"Current in {name} - {subname}: ", end='')
                    values["%s_%s" % (name, subname)] = (float(eval(input())), subpart * part)
                del values[name]
            else:
                print("Current in %s: " % name, end='')
                values[name] = (float(eval(input())), part)
        else:
            print("Current in %s: " % name, end='')
            values[name] = (float(eval(input())), part)
    print("Deposit: ", end='')
    deposit = float(input())
    
    total = sum(map(lambda x: x[0], values.values())) + deposit

    if SHOULD_BALANCE:
        print_table({name: {
            'current_value': value,
            'new_value': total * part,
            'target_part': part,
        } for name, (value, part) in values}, total, deposit)
    else:
        additions = dict(map(lambda x: (x, 0), values.keys()))
        remaining = deposit

        def diff_from_desired(item):
            name, (current_value, part) = item
            retval = part - ((current_value + additions[name]) / total)
            return retval if retval > 0 else 0

        while remaining > EPSILON and len(values) > 1:
            if len(values) < 2:
                additions[list(values.keys())[0]] += remaining
                remaining = 0
                break

            # Sort values by their distance from desired value
            values_by_distance = OrderedDict(reversed(sorted(values.items(), key=diff_from_desired)))

            # Try to compare the furthest to the second-furthest non-equal values
            balanced_items = [list(values_by_distance.items())[0]]
            prev_diff = diff_from_desired(balanced_items[0])
            for item in list(values_by_distance.items())[1:]:
                if round(diff_from_desired(item), 4) != round(prev_diff, 4):
                    break
                balanced_items.append(item)
                prev_diff = diff_from_desired(item)

            if len(balanced_items) == len(values):
                for name, _ in balanced_items:
                    additions[name] += remaining / len(balanced_items)
                remaining = 0
                break

            diff_to_target = diff_from_desired(balanced_items[0]) - diff_from_desired(list(values_by_distance.items())[len(balanced_items)])
            diff_to_target = diff_to_target * total / len(balanced_items)
            for name, _ in balanced_items:
                if remaining < EPSILON:
                    break

                addition = min(remaining, diff_to_target)
                additions[name] += addition
                remaining -= addition

        if remaining > 0:
            print(remaining)

        print_table({name: {
            'current_value': current_value,
            'new_value': current_value + additions[name],
            'target_part': part,
        } for name, (current_value, part) in values.items()}, total, deposit)
    
main()
