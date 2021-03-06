import os
import json
import webbrowser
from datetime import datetime

try:
    import constants
    import printer
    import builder
    import config
    import logger
except Exception:
    from startcp import constants, printer, builder, config, logger


rangebi = printer.Rangebi()
logger = logger.Logger()


def json_read(file_name):
    if file_name.is_file():
        with open(file_name) as f:
            return(json.load(f))


def json_write(file_name, data):
    with open(file_name, "w") as f:
        f.write(json.dumps(data))


user_progress_dict = {}

try:
    user_progress_dict = json_read(constants.startcp_practice_progress_file)
except Exception as e:
    print(e)
    user_progress_dict = {}


def add_problems_to_in_progress_state(problems_details):
    global user_progress_dict

    if user_progress_dict is None:
        user_progress_dict = {}
    if 'problems' not in user_progress_dict:
        user_progress_dict['problems'] = []

    for problem_details in problems_details:
        user_progress_dict['problems'].append(problem_details)
    json_write(constants.startcp_practice_progress_file, user_progress_dict)


def settle_pending_problems_debt():

    user_progress_dict = json_read(constants.startcp_practice_progress_file)
    pending_or_in_progress_problems = []

    if user_progress_dict is None or \
            'problems' not in user_progress_dict:
        return

    for problem_details in user_progress_dict['problems']:
        if problem_details['status'] == constants.problem_status_pending or \
                problem_details['status'] == constants.problem_status_in_progress:
            pending_or_in_progress_problems.append(problem_details)

    if len(pending_or_in_progress_problems) > 0:
        notify_and_update_pending_problems_debt(
            pending_or_in_progress_problems)


def notify_and_update_pending_problems_debt(pending_or_in_progress_problems, print_problems=True):
    if print_problems:
        printer.new_lines()
        print(rangebi.get_in_warning(
            "(StartCP) $ Practice Mode> "), end="")
        printer.new_lines()
        print(rangebi.get_in_info(
            "Problemes or updates are still pending from last practice mode."))
        printer.new_lines()
        print("======================================================================================")
        printer.new_lines()
        # print problems with description to update
        problem_i = 1

        for problem in pending_or_in_progress_problems:
            print("- [ ] " + str(problem_i) + " | Problem: " + problem['from_target'] + "_" + problem['id'] + " | Category: " + problem['category'] +
                  " | Difficulty: " + problem['difficulty'] + " | Dated: " + problem['date'][:-9])
            problem_i += 1

        printer.new_lines()
        print("======================================================================================")
        printer.new_lines()
        print(
            "-- eg. start 1                       -- to jump right into solving the problem")
        print("-- eg. solved all or solved 1 2 3 4  -- To Mark as Solved.")
        print("-- eg. skip all or skip 1 2 4        -- To Mark as Skipped.")
        print("-- eg. Enter 0. or exit or back to exit directly to practice mode")
        printer.new_lines()

    print(rangebi.get_in_warning(
        "(StartCP) $ Practice Mode> Pending Problems Update> "), end="")

    choice = input().strip().split()
    printer.new_lines()

    if choice[0] == "start":
        if len(choice) < 2:
            print("Please enter problem number to jump on")
        else:
            if builder.move_pointer():
                try:
                    # creating practice problem folder folder
                    if config.check_config_for(constants.practice_folder_name):
                        os.makedirs(config.get_config_for(constants.practice_folder_name),
                                    exist_ok=True)
                        os.chdir(config.get_config_for(
                            constants.practice_folder_name))
                        logger.info("Making if not exists and changing directory to: " +
                                    config.get_config_for(constants.practice_folder_name))
                    else:
                        os.makedirs(constants.practice, exist_ok=True)
                        os.chdir(constants.practice)
                        logger.info(
                            "Making if not exists and changing directory to: " + constants.practice)
                    os.chdir(pending_or_in_progress_problems[int(
                        choice[1]) - 1]['from_target'] + "_" + pending_or_in_progress_problems[int(choice[1]) - 1]['id'])
                    if config.check_config_for(constants.after_generation_command):
                        os.system(config.get_config_for(
                            constants.after_generation_command))
                    else:
                        if config.set_config_for(constant_name=constants.after_generation_command):
                            os.system(config.get_config_for(
                                constants.after_generation_command))

                    webbrowser.open(
                        pending_or_in_progress_problems[int(choice[1]) - 1]['url'])
                except Exception as e:
                    print(e)
        printer.new_lines()
    elif choice[0] in ["solved", "solve"]:
        if len(choice) == 1:
            print(
                rangebi.get_in_danger(
                    "Please give url as second paramter. eg. solved all, solve 1")
            )
        else:
            problem_ids = choice[1:]
            update_all = False

            if problem_ids[0] == "all":
                update_all = True

            if (update_status_in_pending_problems(pending_or_in_progress_problems, choice,
                constants.problem_status_solved, update_all)):
                print(
                    rangebi.get_in_success("Skipped.")
                )

    elif choice[0] in ["skip", "skipped"]:
        if len(choice) == 1:
            print(
                rangebi.get_in_danger(
                    "Please give url as second paramter. eg. solved all, solve 1")
            )
        else:
            problem_ids = choice[1:]
            update_all = False

            if problem_ids[0] == "all":
                update_all = True

            if (update_status_in_pending_problems(pending_or_in_progress_problems, choice,
                constants.problem_status_skipped, update_all)):
                print(
                    rangebi.get_in_success("Skipped.")
                )

    elif choice[0] == "exit" or choice[0] == "back" or choice[0] == "0":
        printer.new_lines()
        return
    else:
        print("Invalid choice. Please try again.")
    printer.new_lines()
    notify_and_update_pending_problems_debt(
        pending_or_in_progress_problems, False)


def update_status_in_pending_problems(pending_or_in_progress_problems, choice, required_status, update_all):
    try:
        for p_interator in range(len(pending_or_in_progress_problems)):
            if update_all or (str(p_interator + 1) in choice):
                pending_or_in_progress_problems[p_interator]["status"] = required_status
        user_progress_dict = json_read(constants.startcp_practice_progress_file)

        if user_progress_dict is None or \
                'problems' not in user_progress_dict:
            return

        for pending_problem in pending_or_in_progress_problems:
            for problem_i in range(len(user_progress_dict['problems'])):
                if user_progress_dict['problems'][problem_i]['id'] == pending_problem['id'] and \
                    user_progress_dict['problems'][problem_i]['from_target'] == pending_problem['from_target']:
                    user_progress_dict['problems'][problem_i] = pending_problem
        json_write(constants.startcp_practice_progress_file, user_progress_dict)
        return True
    except Exception as e:
        print(e)
        return False