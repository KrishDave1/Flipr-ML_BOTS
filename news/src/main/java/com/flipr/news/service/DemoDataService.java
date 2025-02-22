package com.flipr.news.service;

import com.flipr.news.entity.Article;
import com.flipr.news.repository.ArticleRepository;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class DemoDataService {

    private final ArticleRepository articleRepository;

    public DemoDataService(ArticleRepository articleRepository) {
        this.articleRepository = articleRepository;
    }

    @PostConstruct
    @Transactional
    public void insertDemoData() {
        System.out.println("✅ Entered insert demo data.");

        // Creating Articles
        Article article1 = new Article();
        article1.setTitle("Neo4j in Spring Boot");
        article1.setContent("A guide to integrating Neo4j with Spring Boot.");
        article1.setKeywords(List.of("Neo4j", "Spring Boot", "Graph Database"));

        Article article2 = new Article();
        article2.setTitle("Graph Databases");
        article2.setContent("Understanding graph databases and their applications.");
        article2.setKeywords(List.of("GraphDB", "Nodes", "Relationships"));

        // Establishing a bidirectional relationship
        article1.addArticle(article2);

        // Saving to Neo4j
        articleRepository.save(article1);
        articleRepository.save(article2);

        System.out.println("✅ Demo Articles inserted successfully into Neo4j!");
    }
}