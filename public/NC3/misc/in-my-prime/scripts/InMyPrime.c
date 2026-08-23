#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>

void sieveOfEratosthenes(int n, bool prime[]) {
	for (int i = 0; i <= n; i++) {
		prime[i] = true;
	}

	prime[0] = false;
	prime[1] = false;
	for (int i = 2; i * i <= n; i++) {
		if (prime[i]) {
			for (int j = i * i; j <= n; j += i) {
				prime[j] = false;
			}
		}
	}
}

int getprimenumbers(int n, int primenumbers[]) {
	bool *prime = malloc((n+1) * sizeof(bool));
	sieveOfEratosthenes(n, prime);
	int primenumberscount = 0;

	for (int i = 0; i <= n; i++) {
		if (prime[i]) {
			primenumbers[primenumberscount++] = i;
		}
	}
	return primenumberscount;
}

int sumeveryother(int primenumbers[], int primenumberscount) {
	int sum = 0;
	for (int i = primenumberscount -1; i >= 0; i-=2) {
		//sum most significant digit and least significant digit
		/*
		int len = snprintf(NULL, 0, "%d", primenumbers[i]);
		char str[len + 1];
		sprintf(str, "%d", primenumbers[i]);
		sum += str[0] - '0';
		sum += str[len - 1] - '0';
		*/
		int num = primenumbers[i];
		int last = num % 10;
		while (num > 9) {
			num /= 10;
		}
		int first = num;
		sum += first + last;
	}
	return sum;
}

int sumbase7(int primenumbers[], int primenumberscount) {
	int sum = 0;
	for (int i = primenumberscount -1; i >= 0; i-=3) {
		int num = primenumbers[i];
		while (num > 0) {
			sum += num % 7;
			num /= 7;
		}
	}
	return sum;
}

int fifth(int primenumbers[], int primenumberscount) {
	int sum = 0;
	for (int i = primenumberscount -1; i > 0; i-=5) {
		long num = (primenumbers[i] * (long)(primenumbers[i-1])) % 31337;
		//count uneven digits
		int count = 0;
		while (num > 0) {
			if (num % 2 == 1) {
				count++;
			}
			num /= 10;
		}
		sum += count;
	}
	return sum;
}

int solve(int n) {
	int *primenumbers = malloc(n * sizeof(int));
	int primenumberscount = getprimenumbers(n, primenumbers);
	int sum = sumeveryother(primenumbers, primenumberscount);
	sum += sumbase7(primenumbers, primenumberscount);
	sum += fifth(primenumbers, primenumberscount);
	return sum;
}


void test() {
	int N = 23;
	int primenumbers[N];
	int primenumberscount = getprimenumbers(N, primenumbers);
	for (int i = primenumberscount -1; i >= 0; i--) {
		printf("%d ", primenumbers[i]);
	}
	printf("\n");
	for (int i = primenumberscount -1; i >= 0; i-=2) {
		printf("%d ", primenumbers[i]);
	}
	printf("\n");
	for (int i = primenumberscount -1; i >= 0; i-=3) {
		printf("%d ", primenumbers[i]);
	}
	printf("\n");
	for (int i = primenumberscount -1; i >= 0; i-=5) {
		printf("%d ", primenumbers[i]);
	}
	printf("\n");
	int sum = sumeveryother(primenumbers, primenumberscount);
	printf("%d\n", sum);
	sum = sumbase7(primenumbers, primenumberscount);
	printf("%d\n", sum);
	sum = fifth(primenumbers, primenumberscount);
	printf("%d\n", sum);

	sum = solve(N);
	printf("%d\n", sum);

	sum = solve(97);
	printf("%d\n", sum);

	sum = solve(997);
	printf("%d\n", sum);

	sum = solve(549979);
	printf("%d\n", sum);
}



int main(void) {
    int num;
    scanf("%d", &num);

    clock_t start_time = clock(); // Record the start time

    int sum = solve(num);

    clock_t end_time = clock(); // Record the end time

    double execution_time = (double)(end_time - start_time) / CLOCKS_PER_SEC;

    printf("Result for N = %d: %d\n", num, sum);
    printf("Calculation time: %.2lf seconds.\n", execution_time);

    return 0;
}
