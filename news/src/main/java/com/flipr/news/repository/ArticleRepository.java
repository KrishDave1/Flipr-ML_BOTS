package com.flipr.news.repository;

import com.flipr.news.entity.Article;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ArticleRepository extends Neo4jRepository<Article, Long> {
}
