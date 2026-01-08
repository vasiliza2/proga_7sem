package com.weather.api.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Конфигурация RabbitMQ для Weather API Service.
 * Определяет очереди, exchange и bindings для маршрутизации сообщений.
 */
@Configuration
public class RabbitMQConfig {

    @Value("${rabbitmq.queue.request}")
    private String requestQueueName;

    @Value("${rabbitmq.queue.aggregated}")
    private String aggregatedQueueName;

    @Value("${rabbitmq.exchange.weather}")
    private String exchangeName;

    @Value("${rabbitmq.routing-key.request}")
    private String requestRoutingKey;

    @Value("${rabbitmq.routing-key.aggregated}")
    private String aggregatedRoutingKey;

    /**
     * Очередь для отправки запросов на получение погоды.
     * Durable = true означает, что очередь сохранится при перезапуске RabbitMQ.
     */
    @Bean
    public Queue requestQueue() {
        return new Queue(requestQueueName, true);
    }

    /**
     * Очередь для получения агрегированных результатов.
     */
    @Bean
    public Queue aggregatedQueue() {
        return new Queue(aggregatedQueueName, true);
    }

    /**
     * Topic Exchange для маршрутизации сообщений по routing key.
     * Topic exchange позволяет использовать паттерны в routing keys.
     */
    @Bean
    public TopicExchange weatherExchange() {
        return new TopicExchange(exchangeName);
    }

    /**
     * Binding для связи очереди запросов с exchange.
     */
    @Bean
    public Binding requestBinding(Queue requestQueue, TopicExchange weatherExchange) {
        return BindingBuilder
                .bind(requestQueue)
                .to(weatherExchange)
                .with(requestRoutingKey);
    }

    /**
     * Binding для связи очереди агрегированных результатов с exchange.
     */
    @Bean
    public Binding aggregatedBinding(Queue aggregatedQueue, TopicExchange weatherExchange) {
        return BindingBuilder
                .bind(aggregatedQueue)
                .to(weatherExchange)
                .with(aggregatedRoutingKey);
    }

    /**
     * Конвертер сообщений для автоматической сериализации/десериализации в JSON.
     * Использует Jackson для преобразования Java объектов в JSON и обратно.
     */
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    /**
     * RabbitTemplate с настроенным JSON конвертером.
     * Используется для отправки и получения сообщений.
     */
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(jsonMessageConverter());
        return template;
    }
}
