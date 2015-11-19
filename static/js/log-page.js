"use strict";
$(document).ready(function () {

    /**************** reset all forms on the page (on pageload) ***************/
    resetForms();

    function resetForms () {
        //get all the forms
        var forms = $("form");

        //reset them
        for (var i = 0; i < forms.length; i++) {
            forms[i].reset();
        }
    }


    /*********** navigate between panes in the create-a-workout form **********/

    $("#caw-overall-next-button").click(function() {
        $("#caw-overall-description").hide();
        $("#caw-warmup").show();
    });

    $("#caw-warmup-previous-button").click(function() {
        $("#caw-warmup").hide();
        $("#caw-overall-description").show();
    });

    $("#caw-warmup-next-button").click(function() {
        $("#caw-warmup").hide();
        $("#caw-main").show();
    });

    $("#caw-main-previous-button").click(function() {
        $("#caw-main").hide();
        $("#caw-warmup").show();
    });

    $("#caw-main-next-button").click(function() {
        $("#caw-main").hide();
        $("#caw-cooldown").show();
    });

    $("#caw-cooldown-previous-button").click(function() {
        $("#caw-cooldown").hide();
        $("#caw-main").show();
    });



    /**************** add a piece to the create-a-workout form ****************/

    $(".caw-add-piece-button").click(function() {
        //get jquery DOM elements to use in the function
        var parentTable = $(this).closest("table");
        var parentTableBody = parentTable.find("tbody");
        var totalPiecesField = $("#caw-num-pieces");
        var phasePiecesField = $("#" + parentTable.data("phasePiecesId"));

        //get data from the DOM to use in the function
        var phase = parentTable.data("phase");
        var pieceType = $(this).data("pieceType");
        var piecesInPhase = Number(phasePiecesField.val()) + 1;
        var totalPieces = Number(totalPiecesField.val()) + 1;

        //a few more variables for convenience
        var pieceNum = totalPieces;
        var pieceNumInPhase = piecesInPhase;
        var placeholderUnits;
        if (pieceType === "time") {
            placeholderUnits = "h:m:s";
        }
        else if (pieceType === "distance") {
            placeholderUnits = "m";
        }
        var cell, cellAttributes, cellComment, cellContent, contentAttributes;

        //console.log("pieceNum: " + pieceNum, "pieceNumInPhase: " + pieceNumInPhase);
        //console.log("totalPieces: " + totalPieces, "piecesInPhase: " + piecesInPhase);

        //create the new row
        var row = $("<tr>").attr("id", "caw-piece-" + pieceNum + "-row");


        row.append("<!-- hidden info fields -->");

        //phase cell (hidden but submitted with the form)
        cellAttributes = {"hidden": ""};
        cellComment = "<!-- phase -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "phase-piece-" + pieceNum,
            "value": phase,
            "aria-label": "phase-piece-" + pieceNum,
            "readonly": ""
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //piece type cell (hidden but submitted with the form)
        cellAttributes = {"hidden": ""};
        cellComment = "<!-- type -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "type-piece-" + pieceNum,
            "value": pieceType,
            "aria-label": "type-piece-" + pieceNum,
            "readonly": ""
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //overall ordinal cell (hidden but submitted with the form)
        cellAttributes = {"hidden": ""};
        cellComment = "<!-- overall ordinal -->";
        cellContent = $("<input>");
        contentAttributes = {
            "class": "caw-ordinal",
            "type": "text",
            "name": "ordinal-piece-" + pieceNum,
            "value": pieceNum,
            "aria-label": "ordinal-piece-" + pieceNum,
            "readonly": ""
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);

        row.append("<!-- input fields for piece " + pieceNum + " -->");


        //ordinal-in-phase cell
        cellAttributes = undefined;
        cellComment = "<!-- ordinal in phase -->";
        cellContent = $("<input>");
        contentAttributes = {
            "class": "caw-ordinal",
            "type": "text",
            "name": "ordinal-in-phase-piece-" + pieceNum,
            "value": pieceNumInPhase,
            "aria-label": "ordinal-in-phase-piece-" + pieceNum,
            "onfocus": "this.blur()",
            "readonly": ""
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //zone cell
        cellAttributes = undefined;
        cellComment = "<!-- zone -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "zone-piece-" + pieceNum,
            "aria-label": "zone-piece-" + pieceNum
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //distance or time cell
        cellAttributes = undefined;
        if (pieceType === "time") {
            cellComment = "<!-- time -->";
            contentAttributes = {
                "class": "caw-dist-time",
                "type": "text",
                "name": "time-piece-" + pieceNum,
                "placeholder": placeholderUnits,
                "aria-label": "time-piece-" + pieceNum
            };
        }
        else if (pieceType === "distance") {
            cellComment = "<!-- distance -->";
            contentAttributes = {
                "class": "caw-dist-time",
                "type": "text",
                "name": "distance-piece-" + pieceNum,
                "placeholder": placeholderUnits,
                "aria-label": "distance-piece-" + pieceNum
            };
        }
        cellContent = $("<input>");
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //rest cell
        cellAttributes = undefined;
        cellComment = "<!-- rest -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "rest-piece-" + pieceNum,
            "aria-label": "rest-piece-" + pieceNum
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //splits cell
        cellAttributes = {"class": "caw-split-td"};
        cellComment = "<!-- splits -->";
        cellContent = [$("<input>"), $("<input>")];
        contentAttributes = [
            {
                "id": "caw-split-length-piece-" + pieceNum,
                "class": "caw-split-length",
                "type": "text",
                "name": "split-length-piece-" + pieceNum,
                "placeholder": placeholderUnits,
                "aria-label": "split-length-piece-" + pieceNum,
                "hidden": ""
            },
            {
                "class": "caw-split-bool",
                "type": "checkbox",
                "name": "split-bool-piece-" + pieceNum,
                "aria-label": "splits-desired-piece-" + pieceNum,
                "data-piece-num": pieceNum
            }
        ];
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //notes cell
        cellAttributes = undefined;
        cellComment = "<!-- notes -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "notes-piece-" + pieceNum,
            "aria-label": "notes-piece-" + pieceNum
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //delete button cell
        cellAttributes = undefined;
        cellComment = "<!-- delete button -->";
        cellContent = $("<a>").append("Delete");
        contentAttributes = {
            "href": "#",
            "aria-label": "delete-piece-" + pieceNum,
            "data-piece-num": pieceNum
        };
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //if this is the first piece in the phase, the table header and the
        //table footer row allowing repeats will be hidden, so show them
        if (piecesInPhase === 1) {
            parentTable.find("thead").show();
            parentTable.find(".caw-footer-repeat").show();
        }


        //update the count of both total pieces in the workout and pieces in
        //the current phase, each in the relevant place in the DOM
        totalPiecesField.val(totalPieces);
        phasePiecesField.val(piecesInPhase);

        //console.log("totalPieces field is now " + totalPiecesField.val());
        //console.log("piecesInPhase field is now " + phasePiecesField.val());


        //add the now-complete row to the end of the table body
        parentTableBody.append(row);

        //focus the first input in the new row
        parentTableBody.find("input[name=zone-piece-" + pieceNum + "]")
                       .focus();
    });



    /*********** repeat pieces x through y on create-a-workout form ***********/

    $(".caw-repeat-go-button").click(function() {
        //TODO CODE ME! (repeat go button on CAW modal)
    });



    /******************** create-a-workout helper functions *******************/


    /* create and return a <td> with the given attributes and content (content
       and its attributes can either be given singly or as arrays)

       Note that even if given singly, attributes are objects of the form
       {"attribute": "value", "attribute": "value", ...} */
    function createPieceTableCell (cellAttributes,
                                   cellComment,
                                   content,
                                   contentAttributes) {

        //create the cell, and give it attributes and a comment, if any
        var cell = $("<td>");
        if (cellAttributes) {
            cell.attr(cellAttributes);
        }
        if (cellComment) {
            cell.append(cellComment);
        }

        //see if the content was passed in as an array, and if so, loop over
        //its elements, adding any given attributes, then adding each element
        //to the cell, in order
        if (Array.isArray(content))
        {
            //if any attributes were given for the content, add them
            if (contentAttributes) {
                for (var i = 0; i < content.length; i++) {
                    content[i].attr(contentAttributes[i]);
                }
            }

            //add each content element to the cell
            for (var i = 0; i < content.length; i++) {
                cell.append(content[i]);
            }
        }
        //if it's not an array, see if it exits at all
        //if it does, add the given attributes (if any), and add it to the cell
        else if (content)
        {
            if (contentAttributes) {
                content.attr(contentAttributes);
            }
            cell.append(content);
        }

        return cell;
    }


    //show or hide input for split length based on checkbox status
    $(document).on("change", ".caw-split-bool", function() {
        //figure out which row the checkbox is in
        var pieceNum = $(this).data("pieceNum");

        console.log("pieceNum: " + pieceNum);

        //based on the checkbox's checked-ness, show or hide input for
        //split length
        if ($(this).prop("checked")) {
            $("#caw-split-length-piece-" + pieceNum).show();
        }
        else {
            $("#caw-split-length-piece-" + pieceNum).hide();
        }
        });


    /****************** save workout for later results-adding *****************/

    $("#caw-add-results-later").click(function(evt) {

        //get data from the form, then hide and clear it
        var formData = $("#create-a-workout-form").serialize();
        $("#create-a-workout-modal").modal("hide");
        $("#create-a-workout-form")[0].reset();

        //save the workout to the database
        $.post("/save-workout-template.json",
               formData,
               function(data) {console.log(data);});
            //TODO finish me!
    });



    /************** functions dealing with the add-results modal **************/

    //populate, show, and handle user interaction with the add-results modal
    $("#add-results-button").click(function(evt) {
        //get user's workout templates from the database
        $.get("/get-workout-templates.json", function(data) {
            var templates = data;

            //populate the workout-chooser
            populateARWorkoutChooser(templates);

            //bind click-handlers to the add-results buttons, to populate
            //the add-results form
            $(".ar-add-results-button").click(templates, handleARChoice);

            //now that it's all ready, show the add-results modal
            $('#add-results-modal').modal('show');
        });





    }); //end $("#add-results-button").click()



    //pull workout template descriptions and id's and use them to populate
    //workout-chooser on the add-results modal
    function populateARWorkoutChooser (templates) {
        //split templates up based on presence/absence of results and,
        //in the latter case, creation date
        var noResultsRecent = getValues(templates.no_results_recent);
        var noResultsOlder = getValues(templates.no_results_older);
        var withResults = getValues(templates.with_results);

        //sort each array of templates by date_added
        noResultsRecent.sort(descByDateAdded);
        noResultsOlder.sort(descByDateAdded);
        withResults.sort(descByDateAdded);

        //find the spots where the descriptions will get added
        var nrRecentDropdown = $("#ar-workout-choice-no-results-recent");
        var nrOlderDropdown = $("#ar-workout-choice-no-results-older");
        var withResultsDropdown = $("#ar-workout-choice-with-results");

        //empty each of those spots so opening the modal multiple times
        //won't result in one copy of each workout for every time the modal
        //is opened
        nrRecentDropdown.empty();
        nrOlderDropdown.empty();
        withResultsDropdown.empty();

        //add 'Choose a workout...' direction to the top of the withResults
        //dropdown (since the other two are secretly <optgroups> in the same
        //dropdown, their overall dropdown, with its top direction, is left
        //intact by the emptying)
        withResultsDropdown.append($("<option>").append("Choose a workout..."));

        //populate each dropdown with the appropriate template descriptions
        addARWorkoutChooserOptions(noResultsRecent, nrRecentDropdown);
        addARWorkoutChooserOptions(noResultsOlder, nrOlderDropdown);
        addARWorkoutChooserOptions(withResults, withResultsDropdown);
    } //end populateARWorkoutChooser()



    //Return an array containing the given object's values
    function getValues (obj) {
        var values = Object.keys(obj || {}) //in case obj is undefined/null
                           .map(function (key) {
                                    return obj[key];
                                });
        return values;
    } //end getValues()



    //Compare two workout templates for a descending sort on date_added
    function descByDateAdded(template1, template2) {
        var date1 = Date.parse(template1.workout_template.date_added);
        var date2 = Date.parse(template2.workout_template.date_added);
        return date2 - date1;
    } //end descByDateAdded()



    //Add an <option> for each template to the given dropdown
    function addARWorkoutChooserOptions (templates, dropdown) {
        //if templates is an empty list, indicate that in the dropdown menu
        if (templates.length === 0)
        {
            var optionAttributes = {
                "style": "font-style: italic",
                "disabled": ""
            };
            var optionText = "None";
            var option = createOptionElement(optionAttributes,
                                                      optionText);
            dropdown.append(option);
        }
        //otherwise, add each template's description to the menu
        else
        {
            for (var i = 0; i < templates.length; i++) {
                //collect the description and template ID
                var template = templates[i].workout_template;
                var templateID = template.workout_template_id;
                var optionAttributes = {"value": templateID};
                var optionText = template.description;

                //create the <option> and add it to the dropdown
                var option = createOptionElement(optionAttributes,
                                                 optionText);
                dropdown.append(option);
            }
        }
    } //end addARWorkoutChooserOptions()



    // Create and return an <option> element with the given attributes and
    // content. (Note that 'attributes' is an object of the form
    // {"attribute": "value", "attribute": "value", ...}.)
    function createOptionElement (optionAttributes, optionText) {

        //create the <option>, and give it attributes, if any
        var option = $("<option>");
        if (optionAttributes) {
            option.attr(optionAttributes);
        }

        //add the text of the option (visible to the user)
        option.append(optionText);

        //return the completed <option> element
        return option;
    } //end createOptionElement()



    //Get the user's workout choice, look it up in the given templates object,
    //populate the form allowing results-adding, and show the form
    function handleARChoice (evt) {
        //the ajax-retrieved templates object was passed into the event
        //handler as .data
        var allTemplates = evt.data;

        //given that this code can run on either 'add results' button,
        //figure out which dropdown it was next to and pull the workout
        //template's id from the selected option in that dropdown
        var workoutID = $(evt.target).siblings("select").val();

        //find the workout_template object associated with that id
        //(using the || operator since it will appear in exactly one
        //of no_results_recent, no_results_older, and with_results)
        var template = allTemplates.no_results_recent[workoutID] ||
                       allTemplates.no_results_older[workoutID] ||
                       allTemplates.with_results[workoutID];

        //split the template into its workout template and its piece
        //templates, and capture the number of pieces, just for convenience
        var workoutTemplate = template.workout_template;
        var pieceTemplates = template.pieces;
        var numPieces = workoutTemplate.num_pieces;

        //IN THE MORNING
        //remake database, add in a workout or two
        //input for overall workout results (incl description) which shows
        //the whole time, then:
        //make a div for warmup, incl descriptive stuff and overall description
        //pattern the above on the create-a-workout modal
        //do the same for main and cooldown?
        //or for the moment, put it all in one div and see how long it is
        //have a total distance field which is a dummy input but which
        //updates on blur of distance fields
        //put a note on prev and next buttons that data will be saved
        //button to add notes to any given piece, then show text box and
        //focus it (width of whole table row? notes/piece, notes/phase)


    } //end handleARChoice()









    /* event listener/handler to populate workout details modal, passing the
       workout id to an ajax request */
    $("#workout-details-modal").on("show.bs.modal", function (evt) {

        //get data-workout-id attribute of the clicked date
        var workoutID = $(evt.relatedTarget).data("workoutId");

        /*//populate the hidden workoutID textbox
        $(evt.currentTarget).find("#workout-details-workout-id").val(workoutID);*/

        //do an ajax request to get workout details based on id
        var request_string = "show.bs.modal/" + workoutID + ".json";
        $.get(request_string, displayWorkoutDetails);

    });

    //add workout details to the modal's DOM
    function displayWorkoutDetails (data) {
        // TODO CODE ME!!! (displayWorkoutDetails)

    }

    $("#caw-add-time-piece").click(function(evt) {

    });






});

