function Confirm(title, msg, $true, $false, callback) {
    var $content =  "<div class='dialog-ovelay'>" +
                        "<div class='dialog'>"+
					        "<header>" +
                        		"<h3>" + title + "</h3>" +
                        		"<i class='fa fa-close'></i>" +
                     		"</header>" +
                     	    "<div class='dialog-msg'>" +
                        		    "<p>" + msg + "</p>" +
                    		"</div>" +
                     		"<footer>" +
                         	    "<div class='controls'>" +
                             		"<button class='button button-danger doAction'>" + $true + "</button> " +
                             		"<button class='button button-default cancelAction'>" + $false + "</button> " +
                        		"</div>" +
                     		"</footer>" +
                  		"</div>" +
                	"</div>";
    $('body').prepend($content);
      $('.doAction').click(function () {
	      $(this).parents('.dialog-ovelay').fadeOut(300, function () {
		      $(this).remove();
		      callback();
	      });
      });

      $('.cancelAction, .fa-close').click(function () {
	      $(this).parents('.dialog-ovelay').fadeOut(300, function () {
		      $(this).remove();
	      });
      });
}

function Alert(title, msg) {
    var $content =  "<div class='dialog-ovelay'>" +
                        	"<div class='dialog'>"+
					            "<header>" +
                        			"<h3>" + title + "</h3>" +
                        			"<i class='fa fa-close'></i>" +
                     			"</header>" +
                     			"<div class='dialog-msg'>" +
                        			"<p>" + msg + "</p>" +
                    			"</div>" +
                     			"<footer>" +
                         			"<div class='controls'>" +
                             				"<button class='button button-default cancelAction'>OK</button> " +
                        			"</div>" +
                     			"</footer>" +
                  		"</div>" +
                	"</div>";
    $('body').prepend($content);
    $('.cancelAction, .fa-close').click(function () {
	      $(this).parents('.dialog-ovelay').fadeOut(300, function () {
		      $(this).remove();
	      });
      });
}

function addMsgToDiv(selector, msg) {
	$(selector).html(msg);
	$(selector).fadeIn();
	setTimeout(function() {
		$(selector).fadeOut();
	}, 4000);
}

