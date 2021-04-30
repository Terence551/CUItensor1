$(document).ready(function(){
    $("#typingForm").on("submit", function(event) {
        console.log("entering typingForm");
        var rawText = $("#text").val();
        var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
        $("#text").val("");
        $("#chatbox").append(userHtml);
        document.getElementById("userInput").scrollIntoView({
            block: "start",
            behavior: "smooth",
        });
        $.ajax({
            data: {
                msg: rawText,
                'continue': " ",
            },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            var botHtml = '<pre><p class="botText"><span>' + data + "</span></p></pre>";
            $("#chatbox").append($.parseHTML(botHtml));
            document.getElementById("userInput").scrollIntoView({
                block: "start",
                behavior: "smooth",
            });
        });
        event.preventDefault();
    });

    $("#clickingForm").on("submit", function(event) {
        try{
            console.log("entering clickingForm");
            var rawText = document.getElementById('text2').textContent;
            var rawValue = document.getElementById('text3').textContent;
            var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
            $("#text2").val("");
            $("#text3").val("");
            $("#chatbox").append(userHtml);
            document.getElementById("userInput").scrollIntoView({
                block: "start",
                behavior: "smooth",
            });
            $.ajax({
                data: {
                    msg: " ",
                    'continue': rawValue,
                },
                type: "POST",
                url: "/get",
            }).done(function(data) {
                var botHtml = '<pre><p class="botText"><span>' + data + "</span></p></pre>";
                $("#chatbox").append($.parseHTML(botHtml));
                document.getElementById("userInput").scrollIntoView({
                    block: "start",
                    behavior: "smooth",
                });
            });
        }
        catch(error){
            console.log("error: " + error);
        }

        event.preventDefault();
    });

});

function myFunction(msg, value){
    console.log("msg is " + msg);
    document.getElementById("text2").innerHTML = msg;
    document.getElementById("text3").innerHTML = value;

}
