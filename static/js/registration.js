$(document).ready(function () {

    /* Clear the registration form on pageload */
    $("#registration-form")[0].reset();

    /* Clear the registration form on hide */
    $('body').on('hidden.bs.modal', '.modal', function () {
         $("#registration-form")[0].reset();
    });

    /* Trigger the datepicker for DOB */
    $('#dob-datepicker .input-group.date')
        .datepicker({format: "M d, yyyy",
                     endDate: "0d",
                     startView: 2,
                     autoclose: true});

    /* Set up form validation rules */


    /* Validate form data */
    /*jQuery.validator.addMethod("birthdate", function(value, element) {
        if 
    }
        );*/

    $("#registration-form").validate({

        invalidHandler: function(event, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                console.log("errors = " + errors);
                var message = "Please fix the errors below.";
                $("#registration-form-validation-error").html(message);
                $("#registration-form-validation-error").show();
            }
            else {
                $("#registration-form-validation-error").hide();
            }
        }, // end of invalidHandler

        submitHandler: function(form) {
            form.submit();
        },

        rules: {
            firstname: "required",
            lastname: "required",
            gender: "required",
            birthdate: {
                required: true,
                birthdate: true
            },
            zipcode: {
                required: true,
                rangelength: [5, 5],
                digits: true
            },
            email: {
                required: true,
                email: true
            },
            username: {
                required: true,

            }
        }
    });



});

