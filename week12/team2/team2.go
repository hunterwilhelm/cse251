/* ---------------------------------------
Course: CSE 251
Lesson Week: ?12
File: team.go
Author: Brother Comeau

Purpose: team activity - finding primes

Instructions:

- Process the array of numbers, find the prime numbers using goroutines

worker()

This goroutine will take in a list/array/channel of numbers.  It will place
prime numbers on another channel


readValue()

This goroutine will display the contents of the channel containing
the prime numbers

--------------------------------------- */
package main

import (
	"fmt"
	"math/rand"
	"time"
  "sync"
)

const FINISHED = -1

func isPrime(n int) bool {
	// Primality test using 6k+-1 optimization.
	// From: https://en.wikipedia.org/wiki/Primality_test

	if n <= 3 {
		return n > 1
	}

	if n%2 == 0 || n%3 == 0 {
		return false
	}

	i := 5
	for (i * i) <= n {
		if n%i == 0 || n%(i+2) == 0 {
			return false
		}
		i += 6
	}
	return true
}

func worker(wg *sync.WaitGroup, inputch chan int, outputch chan int) {
  num := <-inputch
  fmt.Println("Working started")
	for num != FINISHED {

		if isPrime(num) {
			outputch <- num
		}
		num = <-inputch
	}
  inputch <- FINISHED

  wg.Done()
	// TODO - process numbers on one channel and place prime number on another
}

func readValues(wg *sync.WaitGroup, outputch chan int) {
  value := <-outputch
	for value != FINISHED {
    fmt.Println(value)
    value = <-outputch
	}
  fmt.Println(">>Reading finished")  
  wg.Done()
}

func main() {

	workers := 10
	numberValues := 100
  // "barrier"
  var worker_wg sync.WaitGroup
  var reader_wg sync.WaitGroup

  inputch := make(chan int, 10)
  outputch := make(chan int, 10)

	// create workers
	for w := 1; w <= workers; w++ {
    worker_wg.Add(1)
		go worker(&worker_wg, inputch, outputch) // Add any arguments
	}
  
	rand.Seed(time.Now().UnixNano())
	for i := 0; i < numberValues; i++ {
		inputch <- rand.Int()
	}
  inputch <- FINISHED
  
  reader_wg.Add(1)
	go readValues(&reader_wg, outputch) // Add any arguments
  
  worker_wg.Wait()
  outputch <- FINISHED
  reader_wg.Wait()

	fmt.Println("All Done!")
}
