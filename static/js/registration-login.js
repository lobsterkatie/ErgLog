$(document).ready(function () {

    /* Clear the forms on pageload */
    /*var regLoginForms = $(".reg-login-form");
    for (var i = 0; i < regLoginForms.length; i++) {
        regLoginForms[i].reset();
    }*/
    $("#registration-form")[0].reset();
    $("#login-form")[0].reset();
    

    /* Clear the forms on hide */
    //TODO only clear the form on the modal that was just closed
    $('body').on('hidden.bs.modal', '.modal', function (evt) {

        //clear the form data
        $("#registration-form")[0].reset();
        $("#login-form")[0].reset();
        //clear any markup from previous validation
        $("label.validation-error").hide();
        $(".validation-error").removeClass("validation-error");
        $("span.form-validation-error").html("");
    });

    /* Trigger the datepicker for DOB */
    $('#dob-datepicker .input-group.date')
        .datepicker({format: "M d, yyyy",
                     endDate: "0d",
                     startView: 2,
                     autoclose: true});

    /* Set up form validation rules and handlers*/
    jQuery.validator.addMethod("validUsername",
                               function(value, element) {
                                    // allow A-Z, a-z, 0-9, and _
                                    answer = this.optional(element) ||
                                             /^\w+$/.test(value);
                                    return answer;
                                    },
                               "Usernames can only contain A-Z, a-z, _, and 0-9.");


    jQuery.validator.addMethod("validUsernameOrEmail",
                               function(value, element) {
                                    // allow valid usernames or emails
                                    answer = this.optional(element) ||
                                             /^\w+$/.test(value) ||
                                             $.validator.methods.email
                                                        .call(this,
                                                              value,
                                                              element);
                                    console.log("answer: " + answer);
                                    return answer;
                                    },
                               "This is not a valid username or email.");

    //TODO move invalidHandler function up here once it's clear how to
    //only add the message to the span on the modal in question (on event object?)
    /*function ifInvalid (event, validator) {
        // body...
    }*/


    /* Validate registration form data */
    var registrationValidator = $("#registration-form").validate({

        invalidHandler: function(event, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                console.log("errors = " + errors);
                $("#registration-form-validation-error").show();
            }
            //TODO remove this and the submitHandler below if it seems safe
            /*else {
                $("#registration-form-validation-error").hide();
            }*/
        }, // end of invalidHandler

        /*submitHandler: function(form) {
            form.submit();
        },*/

        unhighlight: function(element, errorClass) {
            $(element).removeClass(errorClass);
            //if that was the last error, hide the overall form error message
            var errors = registrationValidator.numberOfInvalids();
            if (!errors) {
                $("#registration-form-validation-error").hide();
            }
        },

        errorClass: "validation-error",

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
                remote: "/email-not-found"
            },
            username: {
                required: true,
                validUsername: true,
                remote: "/username-not-found"
            },
            password: "required",
            password2: {
                required: true,
                equalTo: "#password-original"
            },
            weight: "required"
        }, //end of rules

        messages: {
            firstname: "Please enter your firstname.",
            lastname: "Please enter your lastname.",
            gender: "Please enter a gender.",
            birthdate: "Please enter your birthdate.",
            zipcode: {
                required: "Please enter a zipcode.",
                rangelength: "Zipcodes must be exactly 5 digits.",
                digits: "Zipcodes must contain only digits."
            },
            email: {
                required: "Please enter an email address.",
                email: "Please enter a valid email address.",
                remote: "A user with this email address already exists. " +
                        "Please use the link below to log in instead."
            },
            username: {
                required: "Please enter a username address.",
                validUsername: "Usernames can only contain A-Z, a-z, _, and 0-9.",
                remote: "This username is taken. Please choose another. \n" +
                        "Or, if you've already registered, please use the " +
                        "link below to log in."
            },
            password: "Please enter a password.",
            password2: "Please ensure that your passwords match.",
            weight: "Please enter your weight."
        } //end of messages
    }); //end validating registration form data


    /* Validate lgin form data */
    var loginValidator = $("#login-form").validate({

        invalidHandler: function(event, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                console.log("errors = " + errors);
                $("#login-form-validation-error").show();
            }
            //TODO remove the else if nothing seems broken
            /*else {
                $("#login-form-validation-error").hide();
            }*/
        }, // end of invalidHandler

        //TODO remove this if everything is working
        /*submitHandler: function(form) {
            form.submit();
        },*/

        errorClass: "validation-error",

        unhighlight: function(element, errorClass) {
            $(element).removeClass(errorClass);
            //if that was the last error, hide the overall form error message
            var errors = loginValidator.numberOfInvalids();
            if (!errors) {
                $("#login-form-validation-error").hide();
            }
        },

        rules: {
            username_or_email: {
                required: true,
                validUsernameOrEmail: true/*,
                remote: "/email-not-found"*/
            },
            password: "required"
        }, //end of rules

        messages: {
            username_or_email: {
                required: "Please enter a username or email address.",
                validUsernameOrEmail: "This is not a valid username or email."/*,
                remote: "This username is taken. Please choose another. \n" +
                        "Or, if you've already registered, please use the " +
                        "link below to log in."*/
            },
            password: "Please enter a password."
        } //end of messages
    }); //end validating login form data

});

