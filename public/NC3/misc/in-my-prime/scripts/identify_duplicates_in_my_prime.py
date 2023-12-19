import socket
from collections import Counter

def get_question_and_number():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('inmyprime.nc3', 3119))
        data = s.recv(1024).decode('utf-8')

        # Extract the last line from the response
        lines = data.strip().split('\n')
        last_line = lines[-1].strip() if lines else ""

        # Ensure it's a valid integer
        try:
            question_number = int(last_line)
        except ValueError:
            question_number = None

    return question_number

def main():
    # Store numbers and their occurrences
    number_counter = Counter()

    # Track lowest and largest numbers
    lowest_number = float('inf')
    largest_number = float('-inf')

    # Make 10_000 calls
    for i in range(10_000):
        question_number = get_question_and_number()

        if question_number is not None:
            print(f"Call {i + 1}: Received question: {question_number}")

            # Count the occurrences
            number_counter[question_number] += 1

            # Update lowest and largest numbers
            lowest_number = min(lowest_number, question_number)
            largest_number = max(largest_number, question_number)

    # Find numbers asked more than once
    duplicates = {num: count for num, count in number_counter.items() if count > 1}

    print(f"\nFrom 1000 calls, the following numbers were asked more than once: {duplicates}")
    print(f"The lowest number asked: {lowest_number}")
    print(f"The largest number asked: {largest_number}")

if __name__ == "__main__":
    main()
