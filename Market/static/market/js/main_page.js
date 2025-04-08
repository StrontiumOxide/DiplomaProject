document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления секций
    const sections = document.querySelectorAll('.api-section');
    sections.forEach((section, index) => {
      setTimeout(() => {
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
      }, index * 200);
    });
  
    // Интерактивность эндпоинтов
    const endpoints = document.querySelectorAll('.endpoint');
    endpoints.forEach(endpoint => {
      endpoint.addEventListener('click', function() {
        this.classList.add('active');
        setTimeout(() => {
          this.classList.remove('active');
        }, 300);
      });
    });
  });