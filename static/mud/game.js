
//*********************************************************************
$(document).ready(function(){
    // If the user wants to end session
    $("#exit").click(function() {
        var exit = confirm("Are you sure you want to end the session?");
        if (exit == true)
        {
            window.location = HOME_URL;
        }
    });
    $("#message_submit").click(function() {
        var user_text = $("#user_text");
        var client_message = user_text.val();
        $.post(AJAX_URL, {text: client_message}, function (response) {
            if (response.success) {
                console.log("success");
            }
            else {
                console.log("fail");
            }
            console.log(response);
        });
        user_text.attr("value", "");
        return false;
    });

    // Reload data every 700ms
    //setInterval(get_data, 2700);
});

//*********************************************************************
function get_data() {
    // Scroll height before the request
    var message_box = $("#message_box");
    var old_scroll_height = message_box.attr("scrollHeight") - 20;
    $.ajax({
        url: AJAX_URL,
        cache: false,
        success: function(html) {
            // Insert chat log into the #message_box div
            message_box.html(message_box.html() + html);

            // Auto-scroll
            // Scroll height after the request
            var new_scroll_height = message_box.attr("scrollHeight") - 20;
            if (new_scroll_height > old_scroll_height) {
                // Auto-scroll to bottom of div
                message_box.animate({scrollTop: new_scroll_height}, "normal");
            }
        }
    });
}
