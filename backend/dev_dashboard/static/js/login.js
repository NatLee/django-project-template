document.addEventListener('DOMContentLoaded', function() {
  const jwtLoginBtn = document.getElementById('jwtLoginBtn');
  const messageDiv = document.getElementById('message');

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
  }

  jwtLoginBtn.addEventListener('click', function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.access_token && data.refresh_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        showMessage('JWT Login successful!', 'success');
        window.location.href = '/api/__hidden_dev_dashboard';
      } else {
        showMessage('JWT Login failed. Please check your credentials.', 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage('An error occurred during JWT login.', 'error');
    });
  });

  // Session login is handled by default form submission
});