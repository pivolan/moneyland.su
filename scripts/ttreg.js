function checkLogin(){
	var login = $('input[name=login]').val();
	$.ajax({
		cache:false,
		type:"POST",
		url:"handler/ajax.php?a=login",
		data:"login="+login,
		success: function(html){
			if(html==0)
				$('#er11').html(''); 
			else {
				$('#er11').html(html);
			}
		}
	})
}

$(document).ready(function(){              // по окончанию загрузки страницы
    $('input[name=email]').change(function(){
        var login = $(this).val();
        $.ajax({
			cache:false,
			type:"POST",
			url:"handler/ajax.php?a=email",
			data:"login="+login,
			success: function(html){
				if(html==0)
					$('#er8').html(''); 
				else {
					$('#er8').html(html);
				}
			}
        })
    });
	$('#pass').change(function(){
        var login = $(this).val();
        $.ajax({
              cache:false,
              type:"POST",
              url:"ajax.php?a=pass",
              data:"pass="+login,
              success: function(html){if(html==0)$('div.pass').css("background-image","url(images/true.png)").attr("title",""); else $('div.pass').css("background-image","url(images/false.png)").attr("title",html);}
        })
        var value1 = $(this).val();
		var value2= $("#conf").val();
		if(value1==value2)$('div.conf').css("background-image","url(images/true.png)"); else $('div.conf').css("background-image","url(images/false.png)").attr("title",html);
	});	
	$('#conf').change(function(){
        var value1 = $(this).val();
		var value2= $("#pass").val();
		if(value1==value2)$('div.conf').css("background-image","url(images/true.png)"); else $('div.conf').css("background-image","url(images/false.png)");
    });
	$('#email').change(function(){
        var login = $(this).val();
        $.ajax({
              cache:false,
              type:"POST",
              url:"ajax.php?a=email",
              data:"email="+login,
              success: function(html){if(html==0)$('div.email').css("background-image","url(images/true.png)").attr("title",""); else $('div.email').css("background-image","url(images/false.png)").attr("title",html);}
        })
    });
	$('#captcha').change(function(){
        var login = $(this).val();
        $.ajax({
              cache:false,
              type:"POST",
              url:"ajax.php?a=captcha",
              data:"captcha="+login,
              success: function(html){if(html==0)$('div.captcha').css("background-image","url(images/true.png)").attr("title",""); else $('div.captcha').css("background-image","url(images/false.png)").attr("title",html);}
        })
    });
});