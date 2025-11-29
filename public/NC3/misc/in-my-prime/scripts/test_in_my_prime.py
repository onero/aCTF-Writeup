import unittest
import pickle
from unittest.mock import patch, MagicMock, mock_open
from in_my_prime import (
    compute_primes_up_to_limit_with_sieve_of_eratosthenes,
    solve_first_calculation,
    solve_second_calculation,
    solve_third_calculation,
    get_question_from_server,
    load_results,
    main
    )

class PrimeSolverTests(unittest.TestCase):
    expected_primes = [23, 19, 17, 13, 11, 7, 5, 3, 2]

    def test_compute_primes_up_to_23(self):
        primes = compute_primes_up_to_limit_with_sieve_of_eratosthenes(23)
        self.assertEqual(primes.tolist(), self.expected_primes)

    def test_solve_first_calculation_with_known_primes(self):
        result = solve_first_calculation(self.expected_primes)
        expected_sum = 29
        self.assertEqual(result, expected_sum)

    def test_solve_second_calculation_with_known_primes(self):
        result = solve_second_calculation(self.expected_primes)
        expected_result = 17
        self.assertEqual(result, expected_result)

    def test_solve_third_calculation_with_known_primes(self):
        result = solve_third_calculation(self.expected_primes)
        expected_result = 4
        self.assertEqual(result, expected_result)

    def test_get_question_from_server_with_valid_input(self):
        question_number = 23
        mock_socket_connection = MagicMock()
        mock_socket_connection.recv.return_value = f"Hello there, are you ready?\nHere's the question: \n{question_number}".encode('utf-8')
        extracted_number = get_question_from_server(mock_socket_connection)
        self.assertEqual(extracted_number, question_number)


    def test_main_wrong_answer_response(self):
        question_number = 23
        wrong_answer = 1337
        pre_calculated_results = {question_number: wrong_answer}
        mock_file_read = mock_open(read_data=pickle.dumps(pre_calculated_results))
        with patch('socket.socket') as mock_socket, patch('builtins.open', mock_file_read):
            mock_socket_instance = MagicMock()
            mock_socket_instance.recv.side_effect = [
                f"Hello there, are you ready?\nHere's the question: \n{question_number}".encode('utf-8'),
                "Nope, wrong answer. Please try again.".encode('utf-8')
            ]
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            with self.assertRaises(SystemExit):
                main()

    def test_main_challenge_solved_with_flag(self):
        question_number = 23
        pre_calculated_results = {question_number: 50}
        mock_file_read = mock_open(read_data=pickle.dumps(pre_calculated_results))
        flag_message = "Correct. Here's your prize: NC3{th3_numb3rs_wh4t_d0_th3y_m3an?}"

        with patch('socket.socket') as mock_socket, patch('builtins.open', mock_file_read):
            mock_socket_instance = MagicMock()
            # Simulate server responses for initial question and receiving the flag
            mock_socket_instance.recv.side_effect = [
                f"Hello there, are you ready?\nHere's the question: \n{question_number}".encode('utf-8'),
                flag_message.encode('utf-8')
            ]
            mock_socket.return_value.__enter__.return_value = mock_socket_instance

            # Run the main function and check for the correct handling of the flag
            main()

if __name__ == '__main__':
    unittest.main()
