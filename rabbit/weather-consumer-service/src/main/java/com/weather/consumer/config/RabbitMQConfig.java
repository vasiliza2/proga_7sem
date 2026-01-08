package com.weather.consumer.config;

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
import org.springframework.web.client.RestTemplate;

/**
 * Конфигурация RabbitMQ для Weather Consumer Service.
 */
@Configuration
public class RabbitMQConfig {

    @Value("${rabbitmq.queue.request}")
    private String requestQueueName;

    @Value("${rabbitmq.queue.response}")
    private String responseQueueName;

    @Value("${rabbitmq.exchange.weather}")
    private String exchangeName;

    @Value("${rabbitmq.routing-key.response}")
    private String responseRoutingKey;

    /**
     * Очередь для получения запросов на погоду
     */
    @Bean
    public Queue requestQueue() {
        return new Queue(requestQueueName, true);
    }

    /**
     * Очередь для отправки ответов с данными о погоде
     */
    @Bean
    public Queue responseQueue() {
        return new Queue(responseQueueName, true);
    }

    /**
     * Topic Exchange для маршрутизации сообщений
     */
    @Bean
    public TopicExchange weatherExchange() {
        return new TopicExchange(exchangeName);
    }

    /**
     * Binding для очереди ответов
     */
    @Bean
    public Binding responseBinding(Queue responseQueue, TopicExchange weatherExchange) {
        return BindingBuilder
                .bind(responseQueue)
                .to(weatherExchange)
                .with(responseRoutingKey);
    }

    /**
     * JSON конвертер для сообщений
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

    /**
     * RestTemplate для HTTP запросов к Weather API
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
