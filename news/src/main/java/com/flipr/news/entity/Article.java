package com.flipr.news.entity;

import com.flipr.news.enums.Domain;
import com.flipr.news.repository.ArticleRepository;
import jakarta.annotation.PostConstruct;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.neo4j.core.schema.GeneratedValue;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Node
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class Article {
    @Id
    @GeneratedValue
    private Long id;

    @Relationship(type = "IS_RELATED_TO", direction = Relationship.Direction.OUTGOING)
    private List<Article> related_Articles = new ArrayList<>();

    private List<String> keywords = new ArrayList<>();
    private String content;
    private String title;
    private Domain domain;

    public void addArticle(Article article) {
        this.getRelated_Articles().add(article);
        article.getRelated_Articles().add(this);
    }
}
