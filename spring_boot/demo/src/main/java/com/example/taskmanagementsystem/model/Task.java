package com.example.taskmanagementsystem.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.time.LocalDateTime;
import lombok.Data; // Импортируем Lombok

@Entity
@Data // Аннотация @Data автоматически создает геттеры, сеттеры, toString(), equals(), hashCode() и конструктор NoArgsConstructor
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String description;
    private String status;
    private LocalDateTime createdAt;
    
    // Lombok сгенерирует public void setCreatedAt(LocalDateTime createdAt)
}
