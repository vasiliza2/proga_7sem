package com.example.taskmanagementsystem.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.taskmanagementsystem.model.Task;

@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {
    // Для дополнительного задания: поиск по статусу
    // List<Task> findByStatus(String status); 
}
