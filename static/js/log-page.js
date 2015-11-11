$(document).ready(function () {

    /* event listener/handler to show workout details modal, passing the
       workout id to an ajax request */
    $("#workout-details-modal").on("show.bs.modal", function (evt) {

        //get data-workout-id attribute of the clicked date
        var workoutID = $(evt.relatedTarget).data("workout-id");

        /*//populate the hidden workoutID textbox
        $(evt.currentTarget).find("#workout-details-workout-id").val(workoutID);*/

        //do an ajax request to get workout details based on id
        request_string = "show.bs.modal/" + workoutID + ".json";
        $.get(request_string, displayWorkoutDetails);

    });

    
    //add workout details to the modal's DOM
    function displayWorkoutDetails (data) {
        // TODO CODE ME!!! (displayWorkoutDetails)
    }






});

