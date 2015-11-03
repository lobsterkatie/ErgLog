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
            gender: "required", //enum constraint handled by dropdown
            birthdate: "required", //format constraint handled by datepicker
            zipcode: {
                required: true,
                rangelength: [5, 5],
                digits: true
            },
            email: {
                required: true,
                email: true,
                remote: "/check-email"
            },
            username: {
                required: true,
                remote: "/check-username"
            },
            password: "required",
            weight: "required"
        }, //end rules

        messages: {
            firstname: "Please enter your firstname",
            lastname: "Please enter your lastname",
            gender: "Please enter a gender",
            birthdate: "Please enter a birthdate",
            zipcode: {
                required: "Please enter a zipcode",
                rangelength: "Zipcodes must be exactly 5 digits",
                digits: "Zipcodes must contain only digits"
            },
            email: {
                required: "Please enter an email address",
                email: "Please enter a valid email address",
                remote: ("A user with this email address already exists. " +
                         "Please use the link below to log in instead.")
            },
            username: {
                required: "Please enter a username address",
                remote: "This username is taken. Please choose another."
            },
            password: "Please enter a password",
            weight: "Please enter your weight"
        } //end messages
    });



});

