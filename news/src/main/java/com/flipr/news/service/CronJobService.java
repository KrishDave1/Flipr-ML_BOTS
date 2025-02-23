package com.flipr.news.service;

import com.flipr.news.entity.Article;
import com.flipr.news.response.FlaskResponse;

import java.util.List;

public interface CronJobService {
    FlaskResponse cronJob();
}
