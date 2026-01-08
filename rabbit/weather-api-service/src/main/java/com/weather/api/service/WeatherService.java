package com.weather.api.service;

import com.weather.api.dto.AggregatedWeatherReport;
import com.weather.api.dto.WeatherMessage;
import com.weather.api.dto.WeatherRequestDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

/**
 * Сервис для обработки запросов на получение прогнозов погоды.
 * Реализует паттерн Request-Reply через RabbitMQ с использованием correlation ID.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class WeatherService {

    private final RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.exchange.weather}")
    private String exchangeName;

    @Value("${rabbitmq.routing-key.request}")
    private String requestRoutingKey;

    /**
     * Хранилище для ожидающих ответов запросов.
     * Key: correlationId, Value: CompletableFuture для асинхронного получения результата
     */
    private final Map<String, CompletableFuture<AggregatedWeatherReport>> pendingRequests = 
            new ConcurrentHashMap<>();

    /**
     * Обрабатывает запрос на получение прогнозов погоды для списка городов.
     * 
     * Алгоритм работы:
     * 1. Генерирует уникальный correlation ID для запроса
     * 2. Создает CompletableFuture для асинхронного ожидания результата
     * 3. Отправляет отдельное сообщение в RabbitMQ для каждого города
     * 4. Ожидает агрегированный результат с таймаутом
     * 
     * @param requestDto DTO с списком городов
     * @return Агрегированный отчет о погоде
     * @throws Exception если произошла ошибка или превышен таймаут
     */
    public AggregatedWeatherReport processWeatherRequest(WeatherRequestDto requestDto) throws Exception {
        String correlationId = UUID.randomUUID().toString();
        log.info("Processing weather request with correlation ID: {}", correlationId);
        log.info("Cities requested: {}", requestDto.getCities());

        // Создаем CompletableFuture для ожидания результата
        CompletableFuture<AggregatedWeatherReport> future = new CompletableFuture<>();
        pendingRequests.put(correlationId, future);

        // Отправляем сообщение для каждого города
        int totalCities = requestDto.getCities().size();
        for (String city : requestDto.getCities()) {
            WeatherMessage message = new WeatherMessage(
                    correlationId,
                    city,
                    totalCities,
                    LocalDateTime.now()
            );

            log.debug("Sending message for city: {} with correlation ID: {}", city, correlationId);
            rabbitTemplate.convertAndSend(exchangeName, requestRoutingKey, message);
        }

        // Ожидаем агрегированный результат с таймаутом 60 секунд
        try {
            AggregatedWeatherReport report = future.get(60, TimeUnit.SECONDS);
            log.info("Received aggregated report for correlation ID: {}", correlationId);
            return report;
        } catch (Exception e) {
            log.error("Error or timeout waiting for aggregated report: {}", e.getMessage());
            throw new Exception("Failed to get weather data: " + e.getMessage());
        } finally {
            // Удаляем из хранилища после получения результата
            pendingRequests.remove(correlationId);
        }
    }

    /**
     * Слушатель для получения агрегированных отчетов из RabbitMQ.
     * Использует correlation ID для сопоставления ответа с исходным запросом.
     * 
     * @param report Агрегированный отчет о погоде
     */
    @RabbitListener(queues = "${rabbitmq.queue.aggregated}")
    public void receiveAggregatedReport(AggregatedWeatherReport report) {
        log.info("Received aggregated report for correlation ID: {}", report.getCorrelationId());
        log.debug("Report details: {} cities, {} successful, {} failed", 
                report.getTotalCities(), report.getSuccessCount(), report.getFailureCount());

        // Находим ожидающий CompletableFuture и завершаем его с результатом
        CompletableFuture<AggregatedWeatherReport> future = 
                pendingRequests.get(report.getCorrelationId());
        
        if (future != null) {
            future.complete(report);
            log.debug("Completed future for correlation ID: {}", report.getCorrelationId());
        } else {
            log.warn("No pending request found for correlation ID: {}", report.getCorrelationId());
        }
    }
}
