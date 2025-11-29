use std::fs;
use std::time::Instant;

// https://www.geeksforgeeks.org/sieve-of-eratosthenes/
fn sieve_of_eratosthenes(n: usize) -> Vec<usize> {
    let mut x = vec![true; n + 1];
    x[0] = false;
    x[1] = false;
    for i in 2..=(n as f64).sqrt() as usize {
        if x[i] {
            x[2 * i..=n].iter_mut().step_by(i).for_each(|v| *v = false);
        }
    }

    let primes: Vec<usize> = x.into_iter().enumerate().filter_map(|(i, is_prime)| if is_prime { Some(i) } else { None }).rev().collect();
    primes
}

// Extract every second prime, beginning with first number of collection!
fn extract_every_second_prime(prime_numbers: &[usize]) -> Vec<usize> {
    prime_numbers.iter().cloned().step_by(2).collect()
}

fn extract_every_third_prime(prime_numbers: &[usize]) -> Vec<usize> {
    prime_numbers.iter().cloned().step_by(3).collect()
}

// Summing up the most and least significant digits of each prime number
// So with 23 as prime example we would get this array with every second prime
// [23, 17, 11, 5, 2]
// Based on that the sum would be calculated like so
// 2+3 + 1+7 + 1+1 + 5+5 + 2+2 = 29
fn sum_most_and_least_significant(prime_array: &[usize]) -> usize {
    let total_sum = prime_array.iter().map(|&num| {
        let num_str = num.to_string();
        if num_str.len() == 1 {
            num + num
        } else {
            num_str.chars().next().unwrap().to_digit(10).unwrap() as usize
                + num_str.chars().last().unwrap().to_digit(10).unwrap() as usize
        }
    }).sum();

    total_sum
}

fn decimals_to_base_7(decimals: &[usize]) -> Vec<usize> {
    decimals.iter().cloned().map(|decimal_number| {
        let mut result = Vec::new();
        let mut num = decimal_number;

        while num > 0 {
            let remainder = num % 7;
            result.push(remainder);
            num /= 7;
        }

        result.reverse();
        if result.is_empty() { 0 } else { result.iter().fold(0, |acc, &x| acc * 10 + x) }
    }).collect()
}

// https://stackoverflow.com/questions/14939953/sum-the-digits-of-a-number-python
fn sum_of_digits(number: usize) -> usize {
    number.to_string().chars().map(|c| c.to_digit(10).unwrap() as usize).sum()
}

// Calculate the sum of digits of every base_7 representation
// Example
// base_7(23) = 32 -> 3 + 2 = 5
// base_7(13) = 16 -> 1 + 6 = 7
// base_7(5)  = 5 -> 5 = 5
fn calculate_base_7_sums(decimals: &[usize]) -> Vec<usize> {
    decimals.iter().cloned().map(|base_7_result| sum_of_digits(base_7_result)).collect()
}

fn solve_first_calculation(prime_numbers: &[usize]) -> usize {
    // Extract primes in orders (beginning with first!)
    let every_second_prime = extract_every_second_prime(prime_numbers);
    // Calculate most and least significant sums of every second prime
    sum_most_and_least_significant(&every_second_prime)
}

fn solve_second_calculation(prime_numbers: &[usize]) -> usize {
    // Extract primes in orders (beginning with third!)
    let every_third_prime = extract_every_third_prime(prime_numbers);
    // Calculate base_7 representations of every third prime
    let base_7_results = decimals_to_base_7(&every_third_prime);
    // Calculate the sum of digits of every base_7 representation
    let base_7_sums = calculate_base_7_sums(&base_7_results);
    // Calculate the sum of all base_7 sums
    base_7_sums.iter().sum()
}

// For every fifth prime number from N down to 0: Let p1 be this prime number and p2 the nearest smaller prime number.
// Calculate (p1 * p2) mod 31337 and count the number of odd digits.
// Add up the results.
fn solve_third_calculation(primes: &[usize]) -> usize {
    let sum_of_odd_digits = primes
        .iter()
        .step_by(5)
        .filter_map(|&p1| primes.iter().cloned().find(|&p2| p2 < p1).map(|p2| (p1, p2)))
        .map(|(p1, p2)| {
            let result = (p1 * p2) % 31337;
            result.to_string().chars().filter(|&c| c.to_digit(10).unwrap() % 2 == 1).count()
        })
        .sum();

    sum_of_odd_digits
}

fn calculate_results(prime_numbers: &[usize]) -> usize {
    let result_a = solve_first_calculation(prime_numbers);
    let result_b = solve_second_calculation(prime_numbers);
    let result_c = solve_third_calculation(prime_numbers);

    result_a + result_b + result_c
}

fn main() {
    // Pre-calculate all primes up to theoretical limit
    let precalculated_primes = sieve_of_eratosthenes(100_000_000);

    // Check if results are precalculated, if not, calculate them
    let start_time = Instant::now();
    let result = calculate_results(&precalculated_primes);
    let end_time = Instant::now();

    println!(
        "Time to calculate result: {:.5} seconds",
        (end_time - start_time).as_secs_f64()
    );
    println!("The result is: {}", result);
}
