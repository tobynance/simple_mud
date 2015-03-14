
//*********************************************************************
function pressed_key(e) {
    if (e.keyCode == 13) {
        var user_text = $("#user_text");
        var client_message = user_text.val();
        var data = {player_id: PLAYER_ID, text: client_message, csrfmiddlewaretoken: CSRF_TOKEN};
        $.ajax({
            type: "POST",
            url: SUBMIT_COMMAND_URL,
            data: data,
            success: function (data) {
                console.log("success");
                console.log(data);
                user_text.val("");
                user_text.focus();
                get_data();
            },
            error: function (data) {
                console.log("fail");
                console.log(data);
                user_text.focus();
            }
        });
    }
}
$(document).ready(function(){
    // If the user wants to end session
    $("#exit").click(function() {
        var exit = confirm("Are you sure you want to end the session?");
        if (exit == true)
        {
            window.location = HOME_URL;
        }
    });

    $("#user_text").keypress(pressed_key);

    // Reload data every 700ms
    setInterval(get_data, 700);
});

//*********************************************************************
function starts_with (str1, substring) {
    return str1.slice(0, substring.length) == substring;
}

//*********************************************************************
function get_data() {
    // Scroll height before the request
    var message_box = $("#message_box");
    var old_scroll_height = message_box[0].scrollHeight - 20;
    var data = {player_id: PLAYER_ID, csrfmiddlewaretoken: CSRF_TOKEN};
    $.ajax({
        url: GET_MESSAGES_URL,
        type: "POST",
        cache: false,
        data: data,
        success: function(response) {
            var health = "[" + response.hit_points + "/" + response.max_hit_points + "]";
            $("#health_bar").text(health);
            if (response.messages.length > 0) {
                // Insert chat log into the #message_box div
                var message = "";
                for (var i = 0; i < response.messages.length; i++) {
                    var m = response.messages[i];
                    if (starts_with(m, "<clearscreen>")) {
                        m = m.slice(13);
                        message_box.html("");
                    }
                    message += m;
                }
                message_box.append(message);

                // Auto-scroll
                // Scroll height after the request
                var new_scroll_height = message_box[0].scrollHeight - 20;
                if (new_scroll_height > old_scroll_height) {
                    // Auto-scroll to bottom of div
                    message_box.animate({scrollTop: new_scroll_height}, "normal");
                }
            }
        }
    });
}
