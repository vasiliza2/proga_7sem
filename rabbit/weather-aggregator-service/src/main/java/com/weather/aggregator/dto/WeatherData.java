package com.weather.aggregator.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * DTO для данных о погоде одного города в агрегированном отчете.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class WeatherData implements Serializable {
    
    private String city;
    private double temperature;
    private String description;
    private int humidity;
    private double windSpeed;
    private boolean success;
    private String errorMessage;
}
