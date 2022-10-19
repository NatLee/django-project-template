

function logout() {
    window.localStorage.removeItem('jwt_token');
    window.localStorage.removeItem('jwt_token_refresh');
    window.location.href = "/api/__hidden_dev_dashboard";
}

