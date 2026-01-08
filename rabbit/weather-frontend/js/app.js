const API_URL = 'http://localhost:8080/api/weather/forecast';

function fetchWeather() {
    const citiesInput = document.getElementById('citiesInput');
    const fetchButton = document.getElementById('fetchButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('resultsSection');
    const resultsBody = document.getElementById('resultsBody');
    const statsText = document.getElementById('statsText');

    // Получаем список городов из textarea
    const citiesText = citiesInput.value.trim();
    if (!citiesText) {
        showError('Пожалуйста, введите хотя бы один город');
        return;
    }

    // Разбиваем на массив городов (по строкам)
    const cities = citiesText
        .split('\n')
        .map(city => city.trim())
        .filter(city => city.length > 0);

    if (cities.length === 0) {
        showError('Пожалуйста, введите хотя бы один город');
        return;
    }

    // Скрываем предыдущие результаты и ошибки
    errorMessage.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    fetchButton.disabled = true;

    // Отправляем запрос
    fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cities: cities })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loadingIndicator.classList.add('hidden');
        fetchButton.disabled = false;
        
        displayResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        loadingIndicator.classList.add('hidden');
        fetchButton.disabled = false;
        showError('Ошибка при получении данных: ' + error.message);
    });
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsBody = document.getElementById('resultsBody');
    const statsText = document.getElementById('statsText');

    // Очищаем предыдущие результаты
    resultsBody.innerHTML = '';

    // Отображаем статистику
    const totalCities = data.totalCities || 0;
    const processedCount = data.processedCount || 0;
    statsText.textContent = `Обработано городов: ${processedCount} из ${totalCities}`;

    // Получаем данные о погоде
    const weatherData = data.weatherData || {};
    const processedCities = data.processedCities || [];

    // Создаем строки таблицы
    processedCities.forEach(city => {
        const row = document.createElement('tr');
        
        // Проверяем, есть ли ошибка в названии города
        if (city.includes('(error:')) {
            row.classList.add('error-row');
            const cityName = city.split('(error:')[0].trim();
            row.innerHTML = `
                <td>${escapeHtml(cityName)}</td>
                <td colspan="6" style="color: #c33;">${city}</td>
            `;
        } else {
            const cityData = weatherData[city];
            if (cityData) {
                row.innerHTML = `
                    <td>${escapeHtml(city)}</td>
                    <td>${formatTemperature(cityData.temperature)}</td>
                    <td>${formatTemperature(cityData.feelsLike)}</td>
                    <td>${escapeHtml(cityData.description || 'N/A')}</td>
                    <td>${cityData.humidity || 'N/A'}%</td>
                    <td>${cityData.pressure || 'N/A'} hPa</td>
                    <td>${formatWindSpeed(cityData.windSpeed)}</td>
                `;
            } else {
                row.innerHTML = `
                    <td>${escapeHtml(city)}</td>
                    <td colspan="6" style="color: #999;">Данные не получены</td>
                `;
            }
        }
        
        resultsBody.appendChild(row);
    });

    // Показываем секцию результатов
    resultsSection.classList.remove('hidden');
}

function formatTemperature(temp) {
    if (temp === null || temp === undefined) {
        return 'N/A';
    }
    return `${Math.round(temp)}°C`;
}

function formatWindSpeed(speed) {
    if (speed === null || speed === undefined) {
        return 'N/A';
    }
    return `${speed.toFixed(1)} m/s`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Разрешаем отправку по Enter (Ctrl+Enter)
document.getElementById('citiesInput').addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        fetchWeather();
    }
});