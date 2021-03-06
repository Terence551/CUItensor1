$(document).ready(function(){
    $("#typingForm").on("submit", function(event) {
        console.log("entering typingForm");
        var rawText = $("#text").val();
        var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
        $("#text").val("");
        $("#chatbox").append(userHtml);
        document.getElementById('loader').hidden = false;
        $.ajax({
            data: {
                msg: rawText,
                'continue': " ",
                'topic': " ",
            },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            document.getElementById('loader').hidden = true;
            try{
    //          clearing content
                try{
                    document.getElementById("yeschoice").remove();
                    document.getElementById("nochoice").remove();
                }catch(err){console.log("choice error: "+err);}
                try{
                    document.getElementById("butclick").remove();
                }catch(err){console.log("butclick error: "+err);}
                try{
                    document.getElementById("recommended").remove();
                    document.getElementById("norecommended").remove();
                }catch(err){console.log("recommend error: "+err);}
                try{
                    document.getElementById("topic_1").remove();
                    document.getElementById("topic_2").remove();
                    document.getElementById("topic_3").remove();
                    document.getElementById("topic_4").remove();
                    document.getElementById("notopic").remove();
                }catch(err){console.log("topic error: "+err);}
                try{
                    document.getElementById("dbft").remove();
                    document.getElementById("cip").remove();
                    document.getElementById("dba").remove();
                    document.getElementById("dsf").remove();
                    document.getElementById("dcs").remove();
                    document.getElementById("dit").remove();
                    document.getElementById("nocourse").remove();
                }catch(err){console.log("course error: "+err);}
                try{
                    document.getElementById("c35").remove();
                    document.getElementById("c36").remove();
                    document.getElementById("c43").remove();
                    document.getElementById("c54").remove();
                    document.getElementById("c80").remove();
                    document.getElementById("c85").remove();
                }catch(err){console.log("compare error: "+err);}
                $("#textvrec").textContent = "";
                $("#textvcou").textContent = "";
                $("#textvtop").textContent = "";
                $("#textvcho").textContent = "";
                $("#textvcom").textContent = "";
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
            document.getElementById('firstrequest').remove();
            var recT = document.querySelector("input[name=recommended]") === null ? ' ' : $("input[type='radio'][name='recommended']:checked").val() + "<br>";
            //or document.querySelector("input[name=recommended]:checked").value
            var couT = document.querySelector("input[name=course]") === null ? ' ' : $("input[type='radio'][name='course']:checked").val() + "<br>";
            var topT = document.querySelector("input[name=topic]") === null ? ' ' : $("input[type='radio'][name='topic']:checked").val() + "<br>";
            var choT = document.querySelector("input[name=choice]") === null ? ' ' : $("input[type='radio'][name='choice']:checked").val() + "<br>";

            var recV = document.getElementById('textvrec') === null ? ' ' : document.getElementById('textvrec').textContent;
            var couV = document.getElementById('textvcou') === null ? ' ' : document.getElementById('textvcou').textContent;
            var topV = document.getElementById('textvtop') === null ? ' ' : document.getElementById('textvtop').textContent;
            var choV = document.getElementById('textvcho') === null ? ' ' : document.getElementById('textvcho').textContent;
            var rawText = recT + topT + couT + choT;
            var rawValue = first_requestV + " " + recV + " " + topV + " " + couV + " " + choV;
            console.log("rawV: " + rawValue);
            var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
            $("#chatbox").append(userHtml);
            document.getElementById('loader').hidden = false;
            $.ajax({
                data: {
                    msg: " ",
                    'continue': rawValue,
                    'topic': topV,
                },
                type: "POST",
                url: "/get",
            }).done(function(data) {
                document.getElementById('loader').hidden = true;
                var botHtml = '<pre><p class="botText"><span>' + data + "</span></p></pre>";
                $("#chatbox").append($.parseHTML(botHtml));
                document.getElementById("userInput").scrollIntoView({
                    block: "start",
                    behavior: "smooth",
                });
//              clearing content
                try{
                    document.getElementById("yeschoice").remove();
                    document.getElementById("nochoice").remove();
                }catch(err){console.log("choice error: "+err);}
                try{
                    document.getElementById("butclick").remove();
                }catch(err){console.log("butclick error: "+err);}
                try{
                    document.getElementById("recommended").remove();
                    document.getElementById("norecommended").remove();
                }catch(err){console.log("recommend error: "+err);}
                try{
                    document.getElementById("topic_1").remove();
                    document.getElementById("topic_2").remove();
                    document.getElementById("topic_3").remove();
                    document.getElementById("topic_4").remove();
                    document.getElementById("notopic").remove();
                }catch(err){console.log("topic error: "+err);}
                try{
                    document.getElementById("dbft").remove();
                    document.getElementById("cip").remove();
                    document.getElementById("dba").remove();
                    document.getElementById("dsf").remove();
                    document.getElementById("dcs").remove();
                    document.getElementById("dit").remove();
                    document.getElementById("nocourse").remove();
                }catch(err){console.log("course error: "+err);}
                try{
                    document.getElementById("c35").remove();
                    document.getElementById("c36").remove();
                    document.getElementById("c43").remove();
                    document.getElementById("c54").remove();
                    document.getElementById("c80").remove();
                    document.getElementById("c85").remove();
                }catch(err){console.log("compare error: "+err);}
                $("#textvrec").textContent = "";
                $("#textvcou").textContent = "";
                $("#textvtop").textContent = "";
                $("#textvcho").textContent = "";
                $("#textvcom").textContent = "";
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

    //model
    // Get the modal
    var modal = document.getElementById("myModal");
    // Get the button that opens the modal
    var btn = document.getElementById("myBtn");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];


    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }

});
//modal
function myDisplay(msg){
    // Get the modal
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
    document.getElementById("model-text").innerHTML = msg;
//    console.log("writeup: "+msg);
}

//filter
function myFunction(value, context){
//    console.log("context: " + context + "| value is " + value);
    if (context == "recommended"){
        document.getElementById("textvrec").innerHTML = value;
    }
    else if (context == "topic"){
        document.getElementById("textvtop").innerHTML = value;
    }
    else if (context == "course"){
        document.getElementById("textvcou").innerHTML = value;
    }
    else if (context == "choice"){
        document.getElementById("textvcho").innerHTML = value;
    }
    else if (context == "compare"){
        document.getElementById("textvcom").innerHTML = value;
    }

}
