package com.flipr.news.service;

import com.flipr.news.response.FlaskResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Service
public class CronJobServiceImpl implements CronJobService {
    private static final String CRON_JOB_URL = "http://127.0.0.1:5000/cronjob";

    @Autowired
    private RestTemplate restTemplate;

    @Override
    @Scheduled(fixedRate = 120000) // Runs every 2 minutes
    public FlaskResponse cronJob() {
        try {
            log.info("Calling Flask API at: {}", CRON_JOB_URL);
            FlaskResponse response = restTemplate.getForObject(CRON_JOB_URL, FlaskResponse.class);
            log.info("Received response from Flask API: {}", response);
            return response;
        } catch (Exception e) {
            log.error("Failed to call Flask API: {}", e.getMessage());
            throw new RuntimeException("Failed to call Flask API", e);
        }
    }
}