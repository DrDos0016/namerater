$(document).ready(function (){
    $("a[name=vote]").click(function (){
        vote($(this).data("key"));
    });
});

function vote(key)
{
    ajax_url = '/ajax/vote/'+key;
    $.ajax({
        url: ajax_url,
        success: function(data) {
            data = JSON.parse(data);
            console.log(data);
            
            if (data.result == "SUCCESS")
            {
                $("span[name=score-"+data.key+"]").css("color", "#0F0");
                $("span[name=score-"+data.key+"]").text(data.score);
            }
            else
            {
                $("span[name=score-"+data.key+"]").css("color", "#F00");
            }
        }
    });
}