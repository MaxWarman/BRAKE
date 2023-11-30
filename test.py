import os
from main import execute_BRAKE


def test_correct_samples(test_result_directory):
    test_correct_samples_filepath = "test_correct_samples_50000.csv"

    START_CORRECT_SAMPLES = 8
    END_CORRECT_SAMPLES = 44
    NUMBER_OF_UNLOCKING_ROUNDS = 50000
    TESTS_FOR_SAMPLE = 25
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

    test_correct_samples(test_result_directory=test_result_directory)


if __name__ == "__main__":
    main()
