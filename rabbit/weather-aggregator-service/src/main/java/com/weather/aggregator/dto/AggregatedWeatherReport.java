package com.weather.aggregator.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Агрегированный отчет о погоде для всех запрошенных городов.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AggregatedWeatherReport implements Serializable {
    
    private String correlationId;
    private int totalCities;
    private List<WeatherData> reports;
    private LocalDateTime timestamp;
    private int successCount;
    private int failureCount;
}
