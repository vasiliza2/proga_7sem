package com.weather.consumer.client;

import com.weather.consumer.dto.OpenWeatherMapResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

/**
 * Клиент для взаимодействия с OpenWeatherMap API.
 * Выполняет HTTP запросы для получения данных о погоде.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WeatherApiClient {

    private final RestTemplate restTemplate;

    @Value("${weather.api.url}")
    private String apiUrl;

    @Value("${weather.api.key}")
    private String apiKey;

    /**
     * Получает данные о погоде для указанного города.
     * 
     * Формат запроса:
     * https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&units=metric
     * 
     * Параметры:
     * - q: название города
     * - appid: API ключ
     * - units: система единиц (metric для Цельсия)
     * 
     * @param city Название города
     * @return Ответ от OpenWeatherMap API
     * @throws Exception если произошла ошибка при запросе
     */
    public OpenWeatherMapResponse getWeatherForCity(String city) throws Exception {
        log.debug("Fetching weather data for city: {}", city);

        try {
            // Построение URL с параметрами
            String url = UriComponentsBuilder.fromHttpUrl(apiUrl)
                    .queryParam("q", city)
                    .queryParam("appid", apiKey)
                    .queryParam("units", "metric") // Получаем температуру в Цельсиях
                    .toUriString();

            log.debug("API URL: {}", url.replace(apiKey, "***")); // Скрываем API ключ в логах

            // Выполнение GET запроса
            OpenWeatherMapResponse response = restTemplate.getForObject(url, OpenWeatherMapResponse.class);

            if (response != null) {
                log.debug("Successfully received weather data for city: {}", city);
                log.debug("Temperature: {}°C, Humidity: {}%, Wind: {} m/s",
                        response.getMain().getTemp(),
                        response.getMain().getHumidity(),
                        response.getWind().getSpeed());
            }

            return response;

        } catch (Exception e) {
            log.error("Error fetching weather data for city {}: {}", city, e.getMessage());
            throw new Exception("Failed to fetch weather data for " + city + ": " + e.getMessage());
        }
    }
}
