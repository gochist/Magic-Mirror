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
                var twit_url = "http://twitter.com/" + json.screen_name;
                name = json.name + "<br/>";
                scr_name = "<a href='" + twit_url + "'>@" + json.screen_name + "</a><br/>"
                img = "<img class='user_img' src='" + json.img_url + "'>";
                score = "score: " + json.final_score + "<br/>";
                $('.homelink_overlay', this).text("");
                $('.homelink_overlay', this).append(img + name + scr_name + score);
            },
            error: function(xhr, textStatus, errorThrown){
            
            }
        })
        
    }, function(){
        $(this).find("div:last").remove();
    });
}
$(document).ready(init);
