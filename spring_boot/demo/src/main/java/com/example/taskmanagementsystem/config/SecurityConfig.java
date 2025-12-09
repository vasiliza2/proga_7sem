package com.example.taskmanagementsystem.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig { // 💡 Больше не наследуется от WebSecurityConfigurerAdapter

    // 1. Конфигурация цепочки фильтров безопасности
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // 1.1 Отключение CSRF и Headers (необходимо для H2 console)
            .csrf(csrf -> csrf.disable())
            .headers(headers -> headers.frameOptions(frameOptions -> frameOptions.disable()))

            // 1.2 Настройка авторизации (кто имеет доступ)
            .authorizeHttpRequests(authorize -> authorize
                // Разрешить полный доступ к H2 Console без аутентификации
                .requestMatchers("/h2-console/**").permitAll() 
                
                // Требовать аутентификации для всех остальных запросов
                .anyRequest().authenticated()
            )
            // 1.3 Использование HTTP Basic Authentication
            .httpBasic(basic -> {}); 

        return http.build();
    }

    // 2. Настройка кодировщика паролей
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    // 3. Настройка пользователей в памяти (In-Memory Authentication)
    // Заменяет устаревший configure(AuthenticationManagerBuilder auth)
    @Bean
    public UserDetailsService userDetailsService() {
        UserDetails user = User.builder()
            .username("admin")
            // Пароль должен быть закодирован
            .password(passwordEncoder().encode("admin123")) 
            .roles("USER")
            .build();
        return new InMemoryUserDetailsManager(user);
    }
}
