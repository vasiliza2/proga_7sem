package com.weather.api.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Агрегированный отчет о погоде для всех запрошенных городов.
 * Формируется Aggregator Service и возвращается клиенту.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AggregatedWeatherReport implements Serializable {
    
    /**
     * Уникальный идентификатор корреляции запроса
     */
    private String correlationId;
    
    /**
     * Общее количество запрошенных городов
     */
    private int totalCities;
    
    /**
     * Список данных о погоде для каждого города
     */
    private List<WeatherData> reports;
    
    /**
     * Временная метка формирования отчета
     */
    private LocalDateTime timestamp;
    
    /**
     * Количество успешно обработанных запросов
     */
    private int successCount;
    
    /**
     * Количество неудачных запросов
     */
    private int failureCount;
}
