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
    private static final String SUMMARY_URL = "http://localhost:5000/generate-summary";

    @Autowired
    private RestTemplate restTemplate;

    @Override
    @Scheduled(fixedRate = 300000)
    public void cronJob() {
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(CRON_JOB_URL, String.class);
        } catch (Exception e) {
            log.error(String.valueOf(e));
        }
    }

    @Override
    @Scheduled(fixedRate = 600000)
    public void summaryCronJob() {
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(SUMMARY_URL, String.class);
        } catch (Exception e) {
            log.error(String.valueOf(e));
        }
    }
}
