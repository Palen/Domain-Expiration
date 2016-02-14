$(document).ready(function () {

   $("#submitDomain").submit(function(e){
        submitDomain(e, $(this));
   });   
   $(".update").click(function(e){

        updateDomain(e, $(this));
   });
   $('[data-toggle=modal-form]').on('click', function(e){
        e.preventDefault();
        $('#myModal').modal('show');
   });
});

/**
 * Submit new domain through AJAX
 * @param e event
 * @param form $form
 */
function submitDomain(e, form){
    e.preventDefault();
    $.ajax({
        url: "/add/",
        type: "POST",
        dataType: "json",
        data: form.serialize(),
        success: function (data){
            if (data.response == 'KO'){
                var $error = $(".text-error");
                $error.text(data.message);
                $error.removeClass("hide");
            } else if (data.response == 'OK') {
                location.reload()

            }
        },

        error: function (){

            alert("Some error occurred.")
        }

    });

}

/**
 * Update all info related with a domain
 * @param e event
 * @param name Domain name
 */
function updateDomain(e, $element){
    e.preventDefault();
    var name = $element.data('name');
    var image = $element.find('.img');
    var gif = $element.find('.gif');
    image.addClass('hide');
    gif.removeClass('hide');

    $.ajax({
        url: "/update/",
        type: "POST",
        dataType: "json",
        data: {"name": name},
        success: function (data){
            if (data.response == 'KO'){
                gif.removeClass('hide');
                image.addClass("hide");
               alert("Some error occurred: " + data.message)
            } else if (data.response == 'OK') {
                gif.removeClass('hide');
                image.addClass("hide");
                location.reload()

            } else {
            gif.removeClass('hide');
            image.addClass("hide");
            alert("Some error occurred.")

            }
        },

        error: function (){
            gif.removeClass('hide');
            image.addClass("hide");
            alert("Some error occurred.")
        }

    })
}

