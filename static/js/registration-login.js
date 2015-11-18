$(document).ready(function () {

    /* Event listener for login to change navbar*/
    /*$("#login-form").onsubmit()*/

    /* Clear the forms on pageload */
    /*var regLoginForms = $(".reg-login-form");
    for (var i = 0; i < regLoginForms.length; i++) {
        regLoginForms[i].reset();
    }*/
    $("#registration-form")[0].reset();
    $("#login-form")[0].reset();


    /* Clear the forms on hide */
    //TODO only clear the form on the modal that was just closed
    $('body').on('hidden.bs.modal', '.modal', function(evt) {

        //clear the form data
        $("#registration-form")[0].reset();
        $("#login-form")[0].reset();
        //clear any markup from previous validation
        $("label.validation-error").hide();
        $(".validation-error").removeClass("validation-error");
        $("span.form-validation-error").hide();
    });

    /* Trigger the datepicker for DOB */
    $('#dob-datepicker .input-group.date')
        .datepicker({format: "M d, yyyy",
                     endDate: "0d",
                     startView: 2,
                     autoclose: true});

    /* A hash function to hash the passwords */
    /* NOT CURRENTLY BEING USED */
    /* Based on code from
    http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/*/
    var hashString = function(rawString) {
        var hashValue = 0;
        var currentCharCode = null;
        var stringLength = rawString.length;

        //interate through the string, updating hash value
        for (var i = 0; i < stringLength; i++) {
            currentCharCode  = rawString.charCodeAt(i);
            hashValue = ((hashValue << 5) - hashValue) + currentCharCode;
            hashValue |= 0; // Convert to 32bit integer
        }

        return hashValue;
    };

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
                                    return answer;
                                    },
                               "This is not a valid username or email.");


    /* Validate registration form data */
    var registrationValidator = $("#registration-form").validate({

        errorClass: "validation-error",

        errorContainer: "#registration-form-validation-error",

        //TODO client-side hashing
        /*submitHandler: function(form) {
            var pw = $("#registration-password-original").val();
            var hashedPW = hashString(pw);
            $("#registration-password-original").val(hashedPW);
            $("#registration-password-confirmation").val(hashedPW);
            formData=$("#registration-form").serialize();
            console.log(formData);
            $.post("/register-user",
                   formData,
                   function(){console.log("here");} );
            $.ajax({
                    type: 'POST',
                    url: "/register-user",
                    data: formData,
                    success: function(){console.log("here");}
                   });
            return false;

        }, //end submitHandler*/

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
                equalTo: "#registration-password-original"
            },
            weight: {
                required: true,
                number: true,
                max: 999
            }
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
                required: "Please enter a username.",
                validUsername: "Usernames can only contain A-Z, a-z, _, and 0-9.",
                remote: "This username is taken. Please choose another. \n" +
                        "Or, if you've already registered, please use the " +
                        "link below to log in."
            },
            password: "Please enter a password.",
            password2: {
                required: "Please reenter your password.",
                equalTo: "Passwords must match."
            },
            weight: {
                required: "Please enter your weight.",
                number: "Weight must be a number.",
                max: "Weight must be less than 1000."
            }
        } //end of messages
    }); //end registration form validation


    /* Validate login form data */
    var loginValidator = $("#login-form").validate({

        errorClass: "validation-error",

        errorContainer: "#login-form-validation-error",

        //TODO client-side hashing
        submitHandler: function(form) {
            form.submit();
            $(".logged-out-nav-buttons").hide();
            $(".logged-in-nav-buttons").show();
        },

        /*onkeyup: function(element) {
            var element_name = $(element).attr('name');
            if (this.settings.rules[element_name].onkeyup !== false) {
                $.validator.defaults.onkeyup.apply(this, arguments);
            }
        },*/

        /*onkeyup: false,*/

        rules: {
            username_or_email: {
                required: true,
                validUsernameOrEmail: true,
                remote: "/username-or-email-found"/*,
                onkeyup: false*/
            },
            password: {
                required: true,
                remote: {
                    url: "/password-matches-credential",
                    type: "POST",
                    data: {
                        credential: function() {
                            return $("#login-credential").val();
                            }/*,
                        //TODO client-side hashing
                        password: function () {
                            pw = $("#login-password").val();
                            return hashString(pw);
                        }*/
                    }
                }
            } //end of password rule
        }, //end of rules

        messages: {
            username_or_email: {
                required: "Please enter a username or email address.",
                validUsernameOrEmail: "This is not a valid username or email.",
                remote: "Not a registered email or username."
            },
            password: {
                required: "Please enter a password.",
                remote: "Incorrect password. Please try again."
            }
        } //end of messages
    }); //end login form validation

});

