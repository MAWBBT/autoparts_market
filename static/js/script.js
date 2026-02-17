// Пример простого JavaScript кода (по примеру PDF)
console.log('Сайт АвтоДеталь загружен!');

document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll('.btn-primary');
  buttons.forEach(function(button) {
    if (button.textContent.trim().indexOf('Подробнее') !== -1) {
      button.addEventListener('click', function(e) {
        if (!button.getAttribute('href') || button.getAttribute('href') === '#') {
          e.preventDefault();
          alert('Функционал кнопки "Подробнее" будет добавлен позже!');
        }
      });
    }
  });
});
