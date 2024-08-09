// 測試JWT是否有效
function refreshJWT(){
    var jwt_token = localStorage.getItem("access_token");
    var jwt_token_refresh = localStorage.getItem("refresh_token");
    $.ajax({
      type: "POST",
      url: "/api/auth/token/refresh",
      data: {
        refresh: jwt_token_refresh,
      },
      success: function (data) {
        localStorage.setItem("access_token", data.access_token);
        const jwt_token = data.access_token;
        // 測試 JWT verify API是否有效
        $.ajax({
          type: "POST",
          url: "/api/auth/token/verify",
          data: { token: jwt_token },
          headers: {
            Authorization: "Bearer" + " " + jwt_token,
          },
          success: function (data) {
            var json_string = JSON.stringify(data, null, 2);
            console.log(data);
            $("#token").text("Bearer " + jwt_token);
            $("#token").css("color", "green");
            if (json_string) {
              $("#result").text(" Token verified successfully!");
            }
            $("#result").css("color", "blue").css("white-space", "pre-line");
          },
          error: function (data) {
            var result = "please login " + data.responseText;
            $("#result").text(result).css("color", "red");
          },
        });
      },
      error: function (data) {
        var result = "please login " + data.responseText;
        $("#result").text(result).css("color", "red");
      },
    });
}
  
// 更新登入狀態
function updateLoginStatus() {
    refreshJWT();
    if (localStorage.getItem('access_token')) {
        document.getElementById('token').textContent = 'Bearer ' + localStorage.getItem('access_token');
        document.getElementById('token').style.color = 'green';
        document.getElementById('result').textContent = 'Token verified successfully!';
        document.getElementById('result').style.color = 'blue';
    } else {
        document.getElementById('token').textContent = 'Have not login with JWT token!';
    }
}
  
// 獲取用戶綁定的社交帳號
function fetchSocialAccounts() {
    var socialAccounts = document.getElementById('socialAccounts');
  
    fetch('/api/allauth/social/accounts', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        let accountsHtml = '<h2>已綁定的社交帳號</h2>';
        // 範例資料：
        // data.social_accounts = [
        //     { id: 1, provider: 'google', uid: '123456789' },
        //     { id: 2, provider: 'microsoft', uid: '987654321' }
        // ];
        data.social_accounts.forEach(account => {
            accountsHtml += `
                <div class="account-item">
                    <p>提供商: ${account.provider}</p>
                    <p>UID: ${account.uid}</p>
                    <button class="unbind-btn" data-id="${account.id}">解除綁定</button>
                </div>
            `;
        });
        socialAccounts.innerHTML = accountsHtml;
  
        // 為每個解除綁定按鈕添加點擊事件
        document.querySelectorAll('.unbind-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                unbindSocialAccount(this.dataset.id);
            });
        });
    })
    .catch(error => console.error('Error:', error));
}
  
// 解除綁定社交帳號
function unbindSocialAccount(accountId) {
    fetch('/api/allauth/social/accounts', {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            account_id: accountId
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // 範例：'社交帳號解除綁定成功'
        fetchSocialAccounts(); // 重新獲取社交帳號列表
    })
    .catch(error => console.error('Error:', error));
}

// 更新登入狀態
function handleLoginSuccess() {
    console.log('第三方登入成功');
    var accessToken = localStorage.getItem('access_token');
    var refreshToken = localStorage.getItem('refresh_token');
  
    // 範例 token：
    // accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    // refreshToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  
    if (accessToken) {
        console.log('Access token 已儲存');
    }
    if (refreshToken) {
        console.log('Refresh token 已儲存');
    }
  
    fetchSocialAccounts();
    updateLoginStatus();
}
  
document.addEventListener('DOMContentLoaded', function() {
    // 為每個社交登入按鈕添加點擊事件
    var socialLoginButtons = document.querySelectorAll('.btn-social');
    socialLoginButtons.forEach(function(button) {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        var url = this.href;
        localStorage.removeItem('loginStatus');
  
        // 打開彈出窗口進行社交登入
        var popup = window.open(url, 'socialLogin', 'width=600,height=600');
  
        // 檢查登入狀態
        var loginCheckInterval = setInterval(function() {
          if (localStorage.getItem('loginStatus') === 'success') {
            clearInterval(loginCheckInterval);
            localStorage.removeItem('loginStatus');
            handleLoginSuccess();
          }
        }, 1000);
      });
    });
  
    // 初始化：更新登入狀態
    updateLoginStatus();
    fetchSocialAccounts();
});