var init = function(){
    $("span.user_pop").hover(function(){
        var name = $('a.homelink', this).text();
        var text = "<div class='homelink_overlay space round'></div>";
        $(this).append(text);
        $.ajax({
            type: 'GET',
            url: '/user/' + name + ".json",
            dataType: 'json',
            context: $(this),
            success: function(json, textStatus){
                img = "<img src='" + json.img_url + "'>";
                score = "score: <strong>" + json.final_score + "</strong>";
                $('.homelink_overlay', this).text("");
                $('.homelink_overlay', this).append(img + score);
            },
            error: function(xhr, textStatus, errorThrown){
            
            }
        })
        
    }, function(){
        $(this).find("div:last").remove();
    });
}
$(document).ready(init);
