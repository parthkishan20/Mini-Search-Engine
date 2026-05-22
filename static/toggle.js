function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark');
  const mode = body.classList.contains('dark') ? 'dark' : 'light';
  localStorage.setItem('mode', mode);
}

window.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('mode') === 'dark') {
    document.body.classList.add('dark');
  }

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', toggleDarkMode);
  }
});
