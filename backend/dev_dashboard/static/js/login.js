$("form").on("submit", function (event) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "/api/auth/token",
        data: $(this).serialize(),
        success: function (data) {
            localStorage.setItem('jwt_token', data.access_token);
            localStorage.setItem('jwt_token_refresh', data.refresh_token);
            window.location.href = "/api/__hidden_dev_dashboard";
        }
    });
});