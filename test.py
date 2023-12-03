import os
from main import execute_BRAKE
from time import perf_counter as pc

def test_time(test_result_directory):
    test_correct_samples_filepath = f"test_time.csv"

    CORRECT_SAMPLES = 44
    TEST_CLIENT_PROFILE_FILEPATH = "./server_db/1.json"
    TESTS_FOR_NUMBER = 10
    NUMBERS_OF_UNLOCKING_ROUNDS = [5, 50, 500, 5000, 50000, 500000, 5000000, 50000000, 500000000, 5000000000]
    
    with open(f"{test_result_directory}{test_correct_samples_filepath}", "w") as f:
        f.write(f"time;unlocking_rounds\n")

    for i in range(TESTS_FOR_NUMBER):
        for NUMBER_OF_UNLOCKING_ROUNDS in NUMBERS_OF_UNLOCKING_ROUNDS:
            e = 0
            s = pc()
            try:
                execute_BRAKE(
                    correct_samples=CORRECT_SAMPLES,
                    number_of_unlocking_rounds=NUMBER_OF_UNLOCKING_ROUNDS,
                )
                e = pc()
            except:
                e = pc()
                if os.path.exists(TEST_CLIENT_PROFILE_FILEPATH):
                    os.remove(TEST_CLIENT_PROFILE_FILEPATH)

            with open(f"{test_result_directory}{test_correct_samples_filepath}", "a") as f:
                f.write(
                    f"{e-s};{NUMBER_OF_UNLOCKING_ROUNDS}\n"
                )

                print(f"####### Test for {NUMBER_OF_UNLOCKING_ROUNDS} completed... #######")
    
def test_correct_samples(test_result_directory):
    NUMBER_OF_UNLOCKING_ROUNDS = 5000
    test_correct_samples_filepath = f"test_correct_samples_{NUMBER_OF_UNLOCKING_ROUNDS}_32bit_small_template.csv"

    START_CORRECT_SAMPLES = 8
    END_CORRECT_SAMPLES = 44
    TESTS_FOR_SAMPLE = 1
    TEST_CLIENT_PROFILE_FILEPATH = "./server_db/1.json"

    SAMPLES_RANGE = range(START_CORRECT_SAMPLES, END_CORRECT_SAMPLES + 1)

    with open(f"{test_result_directory}{test_correct_samples_filepath}", "w") as f:
        f.write(f"success;failure;total;correct_samples\n")

    for CORRECT_SAMPLES in SAMPLES_RANGE:
        success_counter = 0
        failure_counter = 0

        for i in range(TESTS_FOR_SAMPLE):
            try:
                execute_BRAKE(
                    correct_samples=CORRECT_SAMPLES,
                    number_of_unlocking_rounds=NUMBER_OF_UNLOCKING_ROUNDS,
                )
                success_counter += 1
            except:
                if os.path.exists(TEST_CLIENT_PROFILE_FILEPATH):
                    os.remove(TEST_CLIENT_PROFILE_FILEPATH)
                failure_counter += 1

        with open(f"{test_result_directory}{test_correct_samples_filepath}", "a") as f:
            f.write(
                f"{success_counter};{failure_counter};{TESTS_FOR_SAMPLE};{CORRECT_SAMPLES}\n"
            )

        print(f"####### Test for {CORRECT_SAMPLES} completed... #######")


def main():
    test_result_directory = "./test_results/"
    if not os.path.exists(test_result_directory):
        os.makedirs(test_result_directory)

    #test_correct_samples(test_result_directory=test_result_directory)
    test_time(test_result_directory)

if __name__ == "__main__":
    main()
