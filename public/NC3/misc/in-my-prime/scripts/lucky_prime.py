import socket
import pickle
import sys
from collections import Counter

def get_question_from_server(socket_connection):
    data = socket_connection.recv(1024).decode('utf-8')
    lines = data.strip().split('\n')
    last_line = lines[-1].strip() if lines else ""
    try:
        question_number = int(last_line)
    except ValueError:
        print("Error while parsing question number!")
        question_number = None
    return question_number

def load_results(filename):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}

def save_questions(questions, filename):
    with open(filename, 'wb') as file:
        pickle.dump(questions, file)

def submit_answer(socket_connection, answer):
    try:
        socket_connection.sendall(str(answer).encode('utf-8'))
        response = socket_connection.recv(1024).decode('utf-8')
        return response
    except socket.error as e:
        print(f"Socket error: {e}")
        return ""

def challenge_solved(response):
    challenge_timeout_answer = "Sorry, too slow. Please try again."
    return response != challenge_timeout_answer and response != ""

def main():
    server_address = ('inmyprime.nc3', 3119)
    challenge_wrong_answer_message = "Nope, wrong answer. Please try again."
    result_not_pre_calculated_message = "Result not pre-calculated :(... Disconnecting and trying again!"
    results_filename = 'results.pkl'
    questions_filename = 'questions.pkl'
    results = load_results(results_filename)
    questions = load_results(questions_filename)
    question_count = Counter(questions)
    attempts = 0

    print("Welcome to Adamino's automagic prime solver! Let's go!")
    response_from_server = ""

    while not challenge_solved(response_from_server):
        attempts += 1
        print("\nAttempt {}...".format(attempts))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(server_address)
            question_number = get_question_from_server(s)

            if question_number is not None:
                question_count[question_number] += 1
                if len(question_count) % 1000 == 0:
                    save_questions(list(question_count.elements()), questions_filename)
                    print(f"Saved {len(question_count)} questions to {questions_filename}")
                    repeat_count = sum(1 for count in question_count.values() if count > 1)
                    print(f"Numbers seen more than once: {repeat_count}")

            result = results.get(question_number, result_not_pre_calculated_message)
            if result == result_not_pre_calculated_message:
                print(result_not_pre_calculated_message)
                continue
            else:
                response_from_server = submit_answer(s, result)

            if response_from_server == challenge_wrong_answer_message:
                print("Oh noes! Wrong answer! How could this happen!? :( Stopping process, because you need to fix this!")
                sys.exit(1)

    print(f"\nOMFG.. this print either means that something bad happened... or YOU'RE DA FUCKING MAN!: {response_from_server}")

if __name__ == "__main__":
    main()
