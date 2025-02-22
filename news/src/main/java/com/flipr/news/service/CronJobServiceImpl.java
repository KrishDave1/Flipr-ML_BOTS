package com.flipr.news.service;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class CronJobServiceImpl implements CronJobService {
    private static final String CRON_JOB_URL = "";
    @Override
    @Scheduled(fixedRate = 300000)
    public void cronJob() {

    }
}
