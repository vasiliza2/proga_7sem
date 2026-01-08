package com.weather.api.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * DTO для данных о погоде одного города.
 * Используется как часть агрегированного отчета.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class WeatherData implements Serializable {
    
    /**
     * Название города
     */
    private String city;
    
    /**
     * Температура в градусах Цельсия
     */
    private double temperature;
    
    /**
     * Описание погодных условий (например, "Clear sky", "Cloudy")
     */
    private String description;
    
    /**
     * Влажность в процентах
     */
    private int humidity;
    
    /**
     * Скорость ветра в м/с
     */
    private double windSpeed;
    
    /**
     * Флаг успешности получения данных
     */
    private boolean success;
    
    /**
     * Сообщение об ошибке (если success = false)
     */
    private String errorMessage;
}
