
function logout() {
    window.localStorage.removeItem('jwt_token');
    window.localStorage.removeItem('jwt_token_refresh');
    window.location.href = "/__user/dashboard";
}


