import sys
import os
import pickle
import numpy as np
import socket

# https://www.geeksforgeeks.org/sieve-of-eratosthenes/
def compute_primes_up_to_limit_with_sieve_of_eratosthenes(n):
    x = np.ones((n+1,), dtype=bool)
    x[0] = False
    x[1] = False
    for i in range(2, int(n**0.5)+1):
        if x[i]:
            x[2*i::i] = False

    primes = np.where(x)[0][::-1]  # In reverse order, so largest is first index!
    return primes

# Extract every second prime, beginning with first number of collection!
def extract_every_second_prime(prime_numbers):
    return prime_numbers[0::2]

# Extract every second prime, beginning with third number of collection!
def extract_every_third_prime(prime_numbers):
    return prime_numbers[0::3]

# Summing up the most and least significant digits of each prime number
# So with 23 as prime example we would get this array with every second prime
#[23, 17, 11, 5, 2]
#Based on that the sum would be calculated like so
#2+3 + 1+7 + 1+1 + 5+5 + 2+2 = 29
def sum_most_and_least_significant(prime_array):
    total_sum = 0
    for num in prime_array:
        num_str = str(num)
        if len(num_str) == 1:
            total_sum += num + num
        else:
            total_sum += int(num_str[0]) + int(num_str[-1])
    return total_sum

def decimals_to_base_7(decimals):
    base_7_results = []

    for decimal_number in decimals:
        result = ""

        while decimal_number > 0:
            remainder = decimal_number % 7
            result = str(remainder) + result
            decimal_number //= 7

        base_7_results.append(int(result) if result else 0)

    return base_7_results

# https://stackoverflow.com/questions/14939953/sum-the-digits-of-a-number-python
def sum_of_digits(number):
    return sum(int(digit) for digit in str(number))

# Calculate the sum of digits of every base_7 representation
# Example
#  base_7(23) = 32 -> 3 + 2  =  5
#  base_7(13) = 16 -> 1 + 6  =  7
#  base_7(5)  =  5 -> 5      =  5
def calculate_base_7_sums(decimals):
    return [sum_of_digits(base_7_result) for base_7_result in decimals]

def solve_first_calculation(prime_numbers):
    # Extract primes in orders (beginning with first!)
    every_second_prime = extract_every_second_prime(prime_numbers)
    # Calculate most and least significant sums of every second prime
    return sum_most_and_least_significant(every_second_prime)

def solve_second_calculation(prime_numbers):
    # Extract primes in orders (beginning with third!)
    every_third_prime = extract_every_third_prime(prime_numbers)
    # Calculate base_7 representations of every third prime
    base_7_results = decimals_to_base_7(every_third_prime)
    # Calculate the sum of digits of every base_7 representation
    base_7_sums = calculate_base_7_sums(base_7_results)
    # Calculate the sum of all base_7 sums
    return sum(base_7_sums)

# For every fifth prime number from N down to 0: Let p1 be this prime number and p2 the nearest smaller prime number.
# Calculate (p1 * p2) mod 31337 and count the number of odd digits.
# Add up the results.
def solve_third_calculation(primes):
    sum_of_odd_digits = 0

    # For every fifth prime number, along with its next lower prime number
    # Implement loop that starts with first and takes every fifth prime number
    for i in range(0, len(primes) -1, 5):
        # Calculate the product of the two primes modulo 31337
        result = primes[i] * primes[i + 1] % 31337
        # Count the number of odd digits in the product
        odd_digit_count = sum(1 for digit in str(result) if int(digit) % 2 == 1)
        sum_of_odd_digits += odd_digit_count

    return sum_of_odd_digits

def calculate_results(prime_numbers):
    result_a = solve_first_calculation(prime_numbers)
    result_b = solve_second_calculation(prime_numbers)
    result_c = solve_third_calculation(prime_numbers)
    return result_a + result_b + result_c

# Load pre-calculated results from file, written in pickle format
def load_results(filename):
    print("Checking if we have pre-calculated results...")
    if os.path.exists(filename):
        print("We do! Loading pre-calculated results from file...")
        with open(filename, 'rb') as file:
            results = pickle.load(file)
            print("Done loading!... ")
            # Let's be a bit cocky if we have a lot of results already computed...
            if len(results) > 100:
                attempts = len(results)
                print("Jesus, we have {} results already computed... not your first time trying this huh!? :D".format(attempts))
            return results
    else:
        print("No pre-calculated results found!")
        return {}

def get_question_from_server(socket_connection):
    data = socket_connection.recv(1024).decode('utf-8')

    # Extract the last line from the response
    lines = data.strip().split('\n')
    last_line = lines[-1].strip() if lines else ""

    # Ensure it's a valid integer
    try:
        question_number = int(last_line)
    except ValueError:
        print("Error while parsing question number!")
        question_number = None

    print(f"Received question: {question_number}")
    return question_number

def submit_answer(socket_connection, answer):
    socket_connection.sendall(str(answer).encode('utf-8'))

    # Receive and print the server's reply
    data = socket_connection.recv(1024).decode('utf-8')
    print(f"Server's reply: {data}")
    return data

def challenge_solved(response):
    challenge_timeout_answer = "Sorry, too slow. Please try again."
    return response != challenge_timeout_answer and response != ""

def main():
    server_address = ('inmyprime.nc3', 3119)
    challenge_wrong_answer_message = "Nope, wrong answer. Please try again."
    result_not_pre_calculated_message = "Result not pre-calculated :(... Let's calculate it now!"
    results = {}
    attempts = 0

    print("Welcome to Adamino's automagic prime solver! Let's go!")

    # Load pre-calculated results from file
    results_filename = 'results.pkl'
    results = load_results(results_filename)
    attempts = len(results)

    # Request prime number from server and provide response
    response_from_server = ""

    while not challenge_solved(response_from_server):
        attempts += 1
        print("\nAttempt {}...".format(attempts))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(server_address)

            # Get the question number from the server
            limit = get_question_from_server(s)

            # Check if the answer is in the results
            result = results.get(limit, result_not_pre_calculated_message)

            # If the result is not pre-calculated, calculate it now
            if result == result_not_pre_calculated_message:
                print(result_not_pre_calculated_message)

                precalculated_primes = compute_primes_up_to_limit_with_sieve_of_eratosthenes(limit)

                result = calculate_results(precalculated_primes)

                # Add the result in the results dictionary
                results[limit] = result

                response_from_server = submit_answer(s, result)

                # Save the results to file (should happen after submitting to server for faster execution!)
                with open(results_filename, 'wb') as file:
                    pickle.dump(results, file)

                print("The result is: {} and was added to known results!".format(result))
            else:
                # Send the answer to the server
                response_from_server = submit_answer(s, result)

        if response_from_server == challenge_wrong_answer_message:
            print("Oh noes! Wrong answer! How could this happen!? :( Stopping process, because you need to fix this!")
            sys.exit(1)

    print(f"\nOMFG.. this print either means that something bad happened... or YOU'RE DA FUCKING MAN!: {response_from_server}")

if __name__ == "__main__":
    main()