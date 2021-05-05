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
                'topic': " ",
//                'rec': " ",
//                'cou': " ",
//                'cho': " ",
            },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            try{
    //          clearing content
                document.getElementById("yeschoice").remove();
                document.getElementById("nochoice").remove();
                document.getElementById("butclick").remove();
                document.getElementById("recommended").remove();
                document.getElementById("norecommended").remove();
                document.getElementById("topic_1").remove();
                document.getElementById("topic_2").remove();
                document.getElementById("topic_3").remove();
                document.getElementById("topic_4").remove();
                document.getElementById("notopic").remove();
                document.getElementById("dbft").remove();
                document.getElementById("cip").remove();
                document.getElementById("dba").remove();
                document.getElementById("dsf").remove();
                document.getElementById("dcs").remove();
                document.getElementById("dit").remove();
                document.getElementById("nocourse").remove();
                $("#textsrec").val("");
                $("#textvrec").val("");
                $("#textscou").val("");
                $("#textvcou").val("");
                $("#textstop").val("");
                $("#textvtop").val("");
                $("#textscho").val("");
                $("#textvcho").val("");
            }
            catch(err){
                console.log("error: "+err);
            };
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
//            assigning var
            var first_requestV = document.getElementById('firstrequest').value;
            var recT = document.getElementById('textsrec').textContent + "<br>";
            var couT = document.getElementById('textscou').textContent + "<br>";
            var topT = document.getElementById('textstop').textContent + "<br>";
            var choT = document.getElementById('textscho').textContent + "<br>";
            var recV = document.getElementById('textvrec').textContent;
            var couV = document.getElementById('textvcou').textContent;
            var topV = document.getElementById('textvtop').textContent;
            var choV = document.getElementById('textvcho').textContent;
            var rawText = recT + topT + couT + choT;
            var rawValue = recV + " " + topV + " " + couV + " " + first_requestV + " " + choV;
            console.log("rawV: " + rawValue);
            var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
            $("#chatbox").append(userHtml);
            document.getElementById("userInput").scrollIntoView({
                block: "start",
                behavior: "smooth",
            });
            $.ajax({
                data: {
                    msg: " ",
                    'continue': rawValue,
                    'topic': topV,
//                    'rec': recV,
//                    'cou': couV,
//                    'cho': choV,
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
//              clearing content
                document.getElementById("yeschoice").remove();
                document.getElementById("nochoice").remove();
                document.getElementById("butclick").remove();
                document.getElementById("recommended").remove();
                document.getElementById("norecommended").remove();
                document.getElementById("topic_1").remove();
                document.getElementById("topic_2").remove();
                document.getElementById("topic_3").remove();
                document.getElementById("topic_4").remove();
                document.getElementById("notopic").remove();
                document.getElementById("dbft").remove();
                document.getElementById("cip").remove();
                document.getElementById("dba").remove();
                document.getElementById("dsf").remove();
                document.getElementById("dcs").remove();
                document.getElementById("dit").remove();
                document.getElementById("nocourse").remove();
                $("#textsrec").val("");
                $("#textvrec").val("");
                $("#textscou").val("");
                $("#textvcou").val("");
                $("#textstop").val("");
                $("#textvtop").val("");
                $("#textscho").val("");
                $("#textvcho").val("");
            });
        }
        catch(error){
            console.log("error: " + error);
        }

        event.preventDefault();
    });

});

function myFunction(msg, value, context){
    console.log("context: " + context + "| msg is " + msg);
    if (context == "recommended"){
        document.getElementById("textsrec").innerHTML = msg;
        document.getElementById("textvrec").innerHTML = value;
    }
    else if (context == "topic"){
        document.getElementById("textstop").innerHTML = msg;
        document.getElementById("textvtop").innerHTML = value;
    }
    else if (context == "course"){
        document.getElementById("textscou").innerHTML = msg;
        document.getElementById("textvcou").innerHTML = value;
    }
    else if (context == "choice"){
        document.getElementById("textscho").innerHTML = msg;
        document.getElementById("textvcho").innerHTML = value;
    }

}
