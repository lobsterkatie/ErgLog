$(document).ready(function () {
    /*Trigger the datepicker for DOB*/
    $('#sandbox-container .input-group.date')
        .datepicker({format: "M d, yyyy",
                     endDate: "0d",
                     startView: 2,
                     autoclose: true});


    /*Clear the registration form on hide*/
    $('body').on('hidden.bs.modal', '.modal', function () {
         $("#registration-form")[0].reset();
    });

    /*Clear the registration form on pageload*/
    $("#registration-form")[0].reset();

    /*validate form data*/
    $("registration-button").click(function (evt) {
        evt.preventDefault();
        /*validation stuff here*/


        
    });
});

