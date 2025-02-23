package com.flipr.news.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Service
public class CronJobServiceImpl implements CronJobService {
    private static final String CRON_JOB_URL = "http://localhost:5000/cronjob";

    @Autowired
    private RestTemplate restTemplate;

    @Override
    @Scheduled(fixedRate = 120000)
    public void cronJob() {
        System.out.println("Entered the pinging cron job.");
        ResponseEntity<String> response = restTemplate.getForEntity(CRON_JOB_URL, String.class);
        System.out.println(response);
    }
}
