package com.flipr.news.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

public class SummaryServiceImpl implements  SummaryService {
    @Autowired
    private RestTemplate restTemplate;

    private final String SUMMARY_URL = "http://localhost:5000/generate-summary";

    @Override
    @Scheduled(fixedRate = 300000)
    public void fetchSummary() {
        System.out.println("Entered the fetch summary cron job.");
        ResponseEntity<Map> response = restTemplate.getForEntity(SUMMARY_URL, Map.class);
        response.getBody().forEach((key, value) -> {
            System.out.println(key + ":" + value);
        });
    }
}
