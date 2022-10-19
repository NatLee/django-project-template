var jwt_token = localStorage.getItem('jwt_token');
var jwt_token_refresh = localStorage.getItem('jwt_token_refresh');


data = {
    "refresh": jwt_token_refresh
};


$.ajax({
    type: "POST",
    url: "/api/auth/token/refresh",
    data: data,
    success: function (data) {
        localStorage.setItem('jwt_token', data.access_token);
        $.ajax({
            type: "GET",
            url: "/api/users/me",
            headers: {
                "Authorization": "Bearer" + " " + localStorage.getItem('jwt_token')
            },
            success: function (data) {
                var json_string = JSON.stringify(data, null, 2);
                console.log(data);
                $('#token').append('Bearer ' + jwt_token);
                $('#result').append(json_string).css('color', 'blue').css('white-space', 'pre-line');
            },
            error: function (data) {
                var result = "please login " + data.responseText;
                $("#result").text(result).css('color', 'red');
            }
        });
    },
    error: function (data) {
        var result = "please login " + data.responseText;
        $("#result").text(result).css('color', 'red');
    }
});