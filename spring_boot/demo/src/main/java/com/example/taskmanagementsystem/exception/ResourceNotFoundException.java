package com.example.taskmanagementsystem.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Custom exception для обработки случая, когда ресурс (например, Task) 
 * не найден в базе данных. Аннотация @ResponseStatus гарантирует, что 
 * Spring Framework автоматически вернет клиенту HTTP статус 404 (Not Found).
 */
@ResponseStatus(value = HttpStatus.NOT_FOUND)
public class ResourceNotFoundException extends RuntimeException {

    // Конструктор, который принимает сообщение об ошибке
    public ResourceNotFoundException(String message) {
        // Передает сообщение в конструктор базового класса RuntimeException
        super(message);
    }
}
