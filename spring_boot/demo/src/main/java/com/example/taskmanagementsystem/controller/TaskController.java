package com.example.taskmanagementsystem.controller;
import com.example.taskmanagementsystem.exception.ResourceNotFoundException;
import com.example.taskmanagementsystem.model.Task;
import com.example.taskmanagementsystem.repository.TaskRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    @Autowired
    private TaskRepository taskRepository;

    // ... (Методы GET, POST, PUT, DELETE)

    // Пример POST-метода
    @PostMapping
    public Task createTask(@RequestBody Task task) {
        task.setCreatedAt(LocalDateTime.now());
        return taskRepository.save(task);
    }
    
    // Пример GET-метода
   @GetMapping("/{id}") 
      public Task getTaskById(@PathVariable Long id) { 
        
        // Используем findById, который возвращает Optional
          return taskRepository.findById(id)
              .orElseThrow(() -> 
                  new ResourceNotFoundException("Task not found with id " + id)
              );
    }
// Пример GET-метода
    @GetMapping
    public List<Task> getAllTasks() {
        return taskRepository.findAll();
    }
   @DeleteMapping("/{id}")
       public void deleteTask(@PathVariable Long id) {
        
          if (!taskRepository.existsById(id)) {
               throw new ResourceNotFoundException("Task not found with id " + id);
           } 
           taskRepository.deleteById(id);
    }
    // Обработка 404
   
    @PutMapping("/{id}")
    public Task updateTask(@PathVariable Long id, @RequestBody Task updatedTask) {
    
    // Используем TaskRepository.findById(), который возвращает Optional<Task>
       return taskRepository.findById(id).map(task -> {
          task.setTitle(updatedTask.getTitle());
          task.setDescription(updatedTask.getDescription()); 
          task.setStatus(updatedTask.getStatus());
        // createdAt не обновляем
          return taskRepository.save(task);
       }).orElseThrow(() -> 
        // 🚨 Здесь лямбда-выражение создает и возвращает новый объект ResourceNotFoundException
          new ResourceNotFoundException("Task not found with id " + id) 
    );
}
}