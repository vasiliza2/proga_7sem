package com.weather.aggregator.service;

import com.weather.aggregator.dto.AggregatedWeatherReport;
import com.weather.aggregator.dto.WeatherData;
import com.weather.aggregator.dto.WeatherResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Сервис агрегации ответов о погоде.
 * Реализует паттерн Aggregator из Enterprise Integration Patterns.
 * 
 * Паттерн Aggregator решает задачу сбора связанных сообщений в единое целое.
 * 
 * Основные компоненты паттерна:
 * 1. Correlation ID - идентификатор для связи сообщений
 * 2. Aggregation Store - хранилище для накопления сообщений
 * 3. Completion Strategy - стратегия определения завершенности агрегации
 * 4. Aggregation Algorithm - алгоритм формирования итогового сообщения
 * 
 * В данной реализации:
 * - Correlation ID: UUID, генерируемый API Service
 * - Aggregation Store: ConcurrentHashMap для потокобезопасного хранения
 * - Completion Strategy: счетчик полученных сообщений == totalCities
 * - Aggregation Algorithm: формирование списка WeatherData
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class WeatherAggregatorService {

    private final RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.exchange.weather}")
    private String exchangeName;

    @Value("${rabbitmq.routing-key.aggregated}")
    private String aggregatedRoutingKey;

    @Value("${aggregator.timeout}")
    private long timeoutSeconds;

    /**
     * Хранилище для агрегации ответов.
     * Key: correlationId
     * Value: AggregationContext с накопленными данными
     */
    private final Map<String, AggregationContext> aggregationStore = new ConcurrentHashMap<>();

    /**
     * Внутренний класс для хранения контекста агрегации.
     * Содержит все необходимые данные для формирования итогового отчета.
     */
    private static class AggregationContext {
        String correlationId;
        int totalCities;
        int receivedCount;
        List<WeatherData> weatherDataList;
        LocalDateTime startTime;
        int successCount;
        int failureCount;

        AggregationContext(String correlationId, int totalCities) {
            this.correlationId = correlationId;
            this.totalCities = totalCities;
            this.receivedCount = 0;
            this.weatherDataList = new ArrayList<>();
            this.startTime = LocalDateTime.now();
            this.successCount = 0;
            this.failureCount = 0;
        }

        /**
         * Добавляет ответ в контекст агрегации.
         * 
         * @param response Ответ от Consumer Service
         */
        void addResponse(WeatherResponse response) {
            WeatherData data = new WeatherData();
            data.setCity(response.getCity());
            data.setTemperature(response.getTemperature());
            data.setDescription(response.getDescription());
            data.setHumidity(response.getHumidity());
            data.setWindSpeed(response.getWindSpeed());
            data.setSuccess(response.isSuccess());
            data.setErrorMessage(response.getErrorMessage());

            weatherDataList.add(data);
            receivedCount++;

            if (response.isSuccess()) {
                successCount++;
            } else {
                failureCount++;
            }
        }

        /**
         * Проверяет, завершена ли агрегация (получены все ответы).
         * Это ключевая часть Completion Strategy.
         * 
         * @return true если все ответы получены
         */
        boolean isComplete() {
            return receivedCount >= totalCities;
        }

        /**
         * Формирует итоговый агрегированный отчет.
         * Это реализация Aggregation Algorithm.
         * 
         * @return Агрегированный отчет
         */
        AggregatedWeatherReport buildReport() {
            AggregatedWeatherReport report = new AggregatedWeatherReport();
            report.setCorrelationId(correlationId);
            report.setTotalCities(totalCities);
            report.setReports(weatherDataList);
            report.setTimestamp(LocalDateTime.now());
            report.setSuccessCount(successCount);
            report.setFailureCount(failureCount);
            return report;
        }
    }

    /**
     * Слушатель очереди ответов от Consumer Service.
     * Реализует логику накопления и агрегации сообщений.
     * 
     * Алгоритм:
     * 1. Получает ответ из очереди
     * 2. Находит или создает контекст агрегации по correlation ID
     * 3. Добавляет ответ в контекст
     * 4. Проверяет условие завершенности (Completion Strategy)
     * 5. Если все ответы получены - формирует и отправляет агрегированный отчет
     * 6. Удаляет контекст из хранилища
     * 
     * @param response Ответ от Consumer Service
     */
    @RabbitListener(queues = "${rabbitmq.queue.response}")
    public void aggregateWeatherResponse(WeatherResponse response) {
        log.info("Received weather response for city: {} (correlation ID: {})",
                response.getCity(), response.getCorrelationId());

        String correlationId = response.getCorrelationId();

        // Получаем или создаем контекст агрегации
        AggregationContext context = aggregationStore.computeIfAbsent(
                correlationId,
                id -> {
                    log.info("Creating new aggregation context for correlation ID: {}", id);
                    return new AggregationContext(id, response.getTotalCities());
                }
        );

        // Синхронизируем доступ к контексту для потокобезопасности
        synchronized (context) {
            // Добавляем ответ в контекст
            context.addResponse(response);

            log.debug("Aggregation progress for {}: {}/{} responses received",
                    correlationId, context.receivedCount, context.totalCities);

            // Проверяем условие завершенности
            if (context.isComplete()) {
                log.info("All responses received for correlation ID: {}. Building aggregated report.",
                        correlationId);

                // Формируем агрегированный отчет
                AggregatedWeatherReport report = context.buildReport();

                log.info("Aggregated report ready: {} total, {} successful, {} failed",
                        report.getTotalCities(), report.getSuccessCount(), report.getFailureCount());

                // Отправляем агрегированный отчет
                rabbitTemplate.convertAndSend(exchangeName, aggregatedRoutingKey, report);

                log.info("Aggregated report sent for correlation ID: {}", correlationId);

                // Удаляем контекст из хранилища
                aggregationStore.remove(correlationId);
                log.debug("Aggregation context removed for correlation ID: {}", correlationId);
            }
        }
    }

    /**
     * Периодическая задача для очистки устаревших контекстов агрегации.
     * Предотвращает утечку памяти в случае неполучения всех ответов.
     * 
     * Выполняется каждые 30 секунд и удаляет контексты старше заданного таймаута.
     */
    @Scheduled(fixedDelay = 30000) // Каждые 30 секунд
    public void cleanupExpiredAggregations() {
        LocalDateTime now = LocalDateTime.now();
        List<String> expiredIds = new ArrayList<>();

        // Находим устаревшие контексты
        aggregationStore.forEach((correlationId, context) -> {
            long secondsElapsed = java.time.Duration.between(context.startTime, now).getSeconds();
            if (secondsElapsed > timeoutSeconds) {
                log.warn("Aggregation context expired for correlation ID: {} (elapsed: {}s, timeout: {}s)",
                        correlationId, secondsElapsed, timeoutSeconds);
                expiredIds.add(correlationId);
            }
        });

        // Удаляем устаревшие контексты
        expiredIds.forEach(id -> {
            AggregationContext context = aggregationStore.remove(id);
            if (context != null) {
                log.info("Removed expired aggregation context: {} ({}/{} responses received)",
                        id, context.receivedCount, context.totalCities);

                // Можно отправить частичный отчет или уведомление об ошибке
                // В данной реализации просто удаляем контекст
            }
        });
    }
}
