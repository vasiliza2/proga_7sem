package com.weather.aggregator.config;

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
 * Конфигурация RabbitMQ для Weather Aggregator Service.
 */
@Configuration
public class RabbitMQConfig {

    @Value("${rabbitmq.queue.response}")
    private String responseQueueName;

    @Value("${rabbitmq.queue.aggregated}")
    private String aggregatedQueueName;

    @Value("${rabbitmq.exchange.weather}")
    private String exchangeName;

    @Value("${rabbitmq.routing-key.aggregated}")
    private String aggregatedRoutingKey;

    /**
     * Очередь для получения ответов от Consumer Service
     */
    @Bean
    public Queue responseQueue() {
        return new Queue(responseQueueName, true);
    }

    /**
     * Очередь для отправки агрегированных отчетов
     */
    @Bean
    public Queue aggregatedQueue() {
        return new Queue(aggregatedQueueName, true);
    }

    /**
     * Topic Exchange
     */
    @Bean
    public TopicExchange weatherExchange() {
        return new TopicExchange(exchangeName);
    }

    /**
     * Binding для очереди агрегированных отчетов
     */
    @Bean
    public Binding aggregatedBinding(Queue aggregatedQueue, TopicExchange weatherExchange) {
        return BindingBuilder
                .bind(aggregatedQueue)
                .to(weatherExchange)
                .with(aggregatedRoutingKey);
    }

    /**
     * JSON конвертер
     */
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    /**
     * RabbitTemplate с JSON конвертером
     */
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(jsonMessageConverter());
        return template;
    }
}
