"use strict";
$(document).ready(function () {

    /*************** things that actually *happen* on page load ***************/

    //everything else (below this section) is functions and event listeners

    //pull user's data from the database for quick reference later on
    var gUser = {}, gTemplates = {}, gResults = {};
    gUser.upToDate = gTemplates.upToDate = gResults.upToDate = false;
    $.get("/get-user-and-stats.json", function(data) {
        gUser = data;
        gUser.upToDate = true;
    });
    $.get("/get-workout-templates.json", function(data) {
        gTemplates = data;
        gTemplates.upToDate = true;
    });
    $.get("/get-workout-results.json", function(data) {
        gResults = data;
        gResults.upToDate = true;
    });

    //reset all forms
    resetForms();

    //capture the initial states of the create-a-workout and add-results modals
    var gCAWModalInitial = $("#create-a-workout-modal").html();
    var gARModalInitial = $("#add-results-modal").html();
    var gARModalHeaderInitial = $("#ar-modal-header").html();
    var gARModalChooserInitial = $("#ar-choose-workout").html();
    var gARModalFormInitial = $("#add-results-form").html();
    var gWDModalInitial = $("#workout-details-modal").html();

    //set defaults for datepickers
    $.fn.datepicker.defaults.format = "D, M d, yyyy";
    $.fn.datepicker.defaults.endDate = "0d";
    $.fn.datepicker.defaults.todayBtn = true;
    $.fn.datepicker.defaults.autoclose = true;
    $.fn.datepicker.defaults.todayHighlight = true;
    $.fn.datepicker.defaults.orientation = "right";




    /************************* random helper functions ************************/

    //Reset all forms on the page
    function resetForms () {
        //get all the forms
        var forms = $("form");

        //reset them
        for (var i = 0; i < forms.length; i++) {
            forms[i].reset();
        }
    } //end resetForms()


    //Return an array containing the given object's values
    function getValues (obj) {
        var values = Object.keys(obj || {}) //in case obj is undefined/null
                           .map(function (key) {
                                    return obj[key];
                                });
        return values;
    } //end getValues()

    //Create and return a <td> with the given attributes and content (content
    //and its attributes can either be given singly or as arrays). Note that
    //even if given singly, attributes are objects of the form
    //{"attribute": "value", "attribute": "value", ...}
    function createTableCell(cellAttributes, cellComment, content,
                                   contentAttributes)
    {

        //create the cell, and give it attributes and a comment, if any
        var cell = $("<td>");
        if (cellAttributes) {
            cell.attr(cellAttributes);
        }
        if (cellComment) {
            cell.append(cellComment);
        }

        //see if the content was passed in as an array, and if so, loop over
        //its elements, adding any attributes, then adding each element to
        //the cell in order
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
    } //end createTableCell()



    /************ functions dealing with the create-a-workout modal ***********/

    //Navigate between panes in the create-a-workout modal
    $(document).on("click", "#caw-overall-next-button", function() {
        $("#caw-overall-description").hide();
        $("#caw-warmup").show();
    });
    $(document).on("click", "#caw-warmup-previous-button", function() {
        $("#caw-warmup").hide();
        $("#caw-overall-description").show();
    });
    $(document).on("click", "#caw-warmup-next-button", function() {
        $("#caw-warmup").hide();
        $("#caw-main").show();
    });
    $(document).on("click", "#caw-main-previous-button", function() {
        $("#caw-main").hide();
        $("#caw-warmup").show();
    });
    $(document).on("click", "#caw-main-next-button", function() {
        $("#caw-main").hide();
        $("#caw-cooldown").show();
    });
    $(document).on("click", "#caw-cooldown-previous-button", function() {
        $("#caw-cooldown").hide();
        $("#caw-main").show();
    });



    //Make is so that closing the create-a-workout modal resets it to its
    //initial state
    $("#create-a-workout-modal").on("hidden.bs.modal", function (evt) {
        $("#create-a-workout-modal").html(gCAWModalInitial);
        $("#create-a-workout-form")[0].reset();
    });


    //add a piece to the create-a-workout form
    $(document).on("click", ".caw-add-piece-button", function() {

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
            placeholderUnits = "H:M:S";
        }
        else if (pieceType === "distance") {
            placeholderUnits = "m";
        }
        var cell, cellAttributes, cellComment, cellContent, contentAttributes;


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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //overall ordinal cell (hidden but submitted with the form)
        cellAttributes = {"hidden": ""};
        cellComment = "<!-- overall ordinal -->";
        cellContent = $("<input>");
        contentAttributes = {
            "type": "text",
            "name": "ordinal-piece-" + pieceNum,
            "value": pieceNum,
            "aria-label": "ordinal-piece-" + pieceNum,
            "readonly": ""
        };
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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
        cell = createTableCell(cellAttributes, cellComment,
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


        //add the now-complete row to the end of the table body
        parentTableBody.append(row);

        //focus the first input in the new row
        parentTableBody.find("input[name=zone-piece-" + pieceNum + "]")
                       .focus();
    }); //end $(".caw-add-piece-button").click()


    //repeat pieces x through y on create-a-workout form
    $(document).on("click", ".caw-repeat-go-button", function() {

        //TODO CODE ME! (repeat go button on CAW modal)
    }); //end $(".caw-repeat-go-button").click()


    //show or hide input for split length based on checkbox status
    //(written as a listener on a class-filtered part of the document so that
    //it will apply to current *and future* instances of the class)
    $(document).on("change", ".caw-split-bool", function() {
        //figure out which row the checkbox is in
        var pieceNum = $(this).data("pieceNum");

        //based on the checkbox's checked-ness, show or hide input for
        //split length
        if ($(this).prop("checked")) {
            $("#caw-split-length-piece-" + pieceNum).show();
        }
        else {
            $("#caw-split-length-piece-" + pieceNum).hide();
        }
    }); //end $(".caw-split-bool").change()


    //save a new workout template in the database
    $(document).on("click", ".caw-save-button", function() {

        //figure out which save button was clicked, so we know what to do
        //once we've saved the workout
        var whenToAddResults = $(this).data("when");

        //we're about to change the set of all workout templates for this
        //user, so unset the upToDate flag on our front-side store thereof
        gTemplates.upToDate = false;

        //get data from the form, then hide and clear it
        var formData = $("#create-a-workout-form").serialize();
        $("#create-a-workout-modal").modal("hide");
        $("#create-a-workout-modal").html(gCAWModalInitial);
        $("#create-a-workout-form")[0].reset();

        //save the workout to the database, update gTemplates, and redirect
        //to adding results, if requested
        $.post("/save-workout-template.json", formData, function(data) {

            //update our client-side storage of workout templates
            gTemplates = data;
            gTemplates.upToDate = true;

            //if the user has asked to add results now, open the add-results
            //modal with blanks for the just-added workout pre-loaded
            if (whenToAddResults === "now") {
                //get the id of the just-added workout and pass it to the
                //function which populates the form
                var workoutID = (gTemplates.newest.workout_template
                                                  .workout_template_id);
                populateAddResultsForm(workoutID);

                //the workout-chooser pane of the add-results modal is what's
                //showing by default, so hide it and show the correct pane
                $("#ar-choose-workout").hide();
                $("#ar-overall-results").show();

                //now that everything's ready, show the modal
                $('#add-results-modal').modal('show');
            }
        });
    }); //end $(".caw-save-button").click()



    /************** functions dealing with the add-results modal **************/

    //Make is so that closing the add-results modal resets it to its
    //initial state
    $("#add-results-modal").on("hidden.bs.modal", function (evt) {
        $("#add-results-modal").html(gARModalInitial);
        $("#add-results-form")[0].reset();
    });



    //navigate between panes in the add-results modal
    $(document).on("click", "#ar-overall-next-button", function() {
        $("#ar-overall-results").hide();
        $("#ar-warmup-results").show();
    });

    $(document).on("click", "#ar-warmup-previous-button", function() {
        $("#ar-warmup-results").hide();
        $("#ar-overall-results").show();
    });

    $(document).on("click", "#ar-warmup-next-button", function() {
        $("#ar-warmup-results").hide();
        $("#ar-main-results").show();
    });

    $(document).on("click", "#ar-main-previous-button", function() {
        $("#ar-main-results").hide();
        $("#ar-warmup-results").show();
    });

    $(document).on("click", "#ar-main-next-button", function() {
        $("#ar-main-results").hide();
        $("#ar-cooldown-results").show();
        $("#ar-save-results-buttons").show();
    });

    $(document).on("click", "#ar-cooldown-previous-button", function() {
        $("#ar-save-results-buttons").hide();
        $("#ar-cooldown-results").hide();
        $("#ar-main-results").show();
    });




    //Populate the first pane of the add-results modal and show the modal
    $("#open-add-results-modal").click(function(evt) {

        //if our stored set of workout templates is up to date, use them to
        //populate the first pane of the modal, and then show it
        if (gTemplates.upToDate) {
            populateAndShowARWorkoutChooser();
        }

        //otherwise, get the current set from the database, update our
        //stored version, and then populate and show the modal
        else {
            $.get("/get-workout-templates.json", function(data) {
                gTemplates = data;
                gTemplates.upToDate = true;
                populateAndShowARWorkoutChooser();
            });
        }
    }); //end $("#add-results-button").click()



    //Pull workout template descriptions and id's, use them to populate
    //workout-chooser on the add-results modal, and show it
    function populateAndShowARWorkoutChooser() {

        //reset workout chooser to its initial state, in case it's been
        //left populated by a previous operation
        $("#ar-choose-workout").html(gARModalChooserInitial);

        //split templates up based on presence/absence of results and,
        //in the latter case, creation date
        var noResultsRecent = getValues(gTemplates.no_results_recent);
        var noResultsOlder = getValues(gTemplates.no_results_older);
        var withResults = getValues(gTemplates.with_results);

        //sort each array of templates by date_added
        noResultsRecent.sort(descByDateAdded);
        noResultsOlder.sort(descByDateAdded);
        withResults.sort(descByDateAdded);

        //find the spots where the descriptions will get added
        var nrRecentDropdown = $("#ar-workout-choice-no-results-recent");
        var nrOlderDropdown = $("#ar-workout-choice-no-results-older");
        var withResultsDropdown = $("#ar-workout-choice-with-results");

        //populate each dropdown with the appropriate template descriptions
        addARWorkoutChooserOptions(noResultsRecent, nrRecentDropdown);
        addARWorkoutChooserOptions(noResultsOlder, nrOlderDropdown);
        addARWorkoutChooserOptions(withResults, withResultsDropdown);

        //make sure the first pane is the one showing
        $("#ar-choose-workout").show();
        $("#ar-warmup-results").hide();
        $("#ar-main-results").hide();
        $("#ar-cooldown-results").hide();

        //now that it's all ready, show the add-results modal
        $('#add-results-modal').modal('show');
    } //end populateARWorkoutChooser()



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



    //On the add-results modal, once the user has chosen a workout to which
    //to add results, get their choice, then populate the form accordingly
    //and show it
    $(document).on("click", ".ar-add-results-button", function(evt) {

        //given that this code can run on either 'add results' button,
        //figure out which dropdown it was next to and pull the workout
        //template's id from the selected option in that dropdown
        var workoutID = $(evt.target).siblings("select").val();

        //if the user hasn't actually selected a workout (the dropdown
        //is still on the 'Choose a workout...' option), show an error
        if (workoutID === "choose-a-workout") {
            alert("Please choose a workout to which to add results.");
            return;
        }

        //popualate the form for adding results
        populateAddResultsForm(workoutID);

        //now that the adding-results panes are fully populated, show the first
        //one and hide the workout-chooser pane
        $("#ar-choose-workout").hide();
        $("#ar-overall-results").show();
    }); //end $(".ar-add-results-button").click()


    //Given a workout template ID, populate the add-results form with
    //the right blanks
    function populateAddResultsForm (workoutID) {

        //find the workout template object associated with the given ID
        //(using the || operator since it will appear in exactly one
        //of no_results_recent, no_results_older, and with_results)
        var templateObj = gTemplates.no_results_recent[workoutID] ||
                         gTemplates.no_results_older[workoutID] ||
                         gTemplates.with_results[workoutID];

        //split the template into its workout template and its piece
        //templates for each phase (grouped by type, sorted by ordinal)
        var workoutTemplate = templateObj.workout_template;
        var warmupTemplates = pieceTemplatesByPhase(templateObj, "warmup");
        var mainTemplates = pieceTemplatesByPhase(templateObj, "main");
        var cooldownTemplates = pieceTemplatesByPhase(templateObj, "cooldown");

        //add the workout description, primary zone, and total distance
        //to the header, and show all three
        var workoutDescription = workoutTemplate.description;
        var primaryZone = workoutTemplate.primary_zone;
        $("#ar-workout-description").append(workoutDescription);
        if (primaryZone) {
            $("#ar-workout-description").append(" (" + primaryZone + ")");
        }
        $("#ar-header-while-adding-results").show();

        //add the given workout template ID and the number of pieces in the
        //workout to their respective spots on the form
        $("#ar-workout-template-id").val(workoutID);
        $("#ar-num-pieces").val(workoutTemplate.num_pieces);

        //populate a table for each phase with descriptive data (format,
        //stroke rates, and notes) given when the workout was created
        populateARDescData(workoutTemplate, "warmup");
        populateARDescData(workoutTemplate, "main");
        populateARDescData(workoutTemplate, "cooldown");

        //find the distance and time piece tables for each phase and
        //populate (or hide) them appropriately
        var warmupTimeTable = $("#ar-warmup-time-table");
        var warmupDistTable = $("#ar-warmup-distance-table");
        var mainTimeTable = $("#ar-main-time-table");
        var mainDistTable = $("#ar-main-distance-table");
        var cooldownTimeTable = $("#ar-cooldown-time-table");
        var cooldownDistTable = $("#ar-cooldown-distance-table");
        populateARPieceTable(warmupTimeTable, warmupTemplates);
        populateARPieceTable(warmupDistTable, warmupTemplates);
        populateARPieceTable(mainTimeTable, mainTemplates);
        populateARPieceTable(mainDistTable, mainTemplates);
        populateARPieceTable(cooldownTimeTable, cooldownTemplates);
        populateARPieceTable(cooldownDistTable, cooldownTemplates);

        //now that all distance pieces have been added to the form, update
        //the total-meters field in the header
        updateTotalMeters(false);
    } //end populateAddResultsForm()


    //Given a verbose objectified version of a workout template, return an
    //object containing its piece templates, filtered by the given phase,
    //grouped by type (distance or time), and sorted by ordinal.
    function pieceTemplatesByPhase(templateObj, phase) {

        var distTemplates = [];
        var timeTemplates = [];

        //unpack the layers of the workout template object and go through
        //the piece templates one by one, adding those with the correct phase
        //to the phaseTemplates array
        var piecesObject = templateObj.pieces;
        var numPieces = Object.keys(piecesObject).length;
        for (var i = 0; i < numPieces; i++) {
            var template = piecesObject[i+1].template;
            if (template.phase === phase)
            {
                if (template.piece_type === "distance") {
                    distTemplates.push(template);
                }
                else if (template.piece_type === "time") {
                    timeTemplates.push(template);
                }
            }
        }
        //note that since piecesObject is keyed by ordinal, and pieces are
        //added to distTemplates or timeTemplates [arrays, so they preserve
        //order] in increasing order by key, no additional sort is needed

        //create the object to be returned, add the templates to it, and
        //return it
        var phaseTemplates = {};
        phaseTemplates.distance = distTemplates;
        phaseTemplates.time = timeTemplates;
        return phaseTemplates;
    } //end pieceTemplatesByPhase()



    //Populate the appropriate tables on the add-results modal with descriptive
    //data (format, stroke rates, and notes) given when the workout was created
    function populateARDescData (workoutTemplate, phase) {

        //if format data was given for this phase, add that data to the row
        //and unhide it
        var phaseFormat = workoutTemplate[phase + "_format"];
        if (phaseFormat) {
                $("#ar-" + phase + "-format").text(phaseFormat);
                $("#ar-" + phase + "-format-row").show();
        }

        //if stroke rate data was given for this phase, add that data to the
        //row and unhide it
        var phaseSR = workoutTemplate[phase + "_stroke_rates"];
        if (phaseSR) {
                $("#ar-" + phase + "-sr").text(phaseSR);
                $("#ar-" + phase + "-sr-row").show();
        }

        //if notes data was given for this phase, add that data to the row
        //and unhide it
        var phaseNotes = workoutTemplate[phase + "_notes"];
        if (phaseNotes) {
                $("#ar-" + phase + "-notes").text(phaseNotes);
                $("#ar-" + phase + "-notes-row").show();
        }
    } //end populateARDescData()



    //Pull the appropriate pieces out of the given templates object and use
    //them to populate the given table on the add-results modal
    //If there are no appropriate pieces, hide the table instead
    function populateARPieceTable(table, phaseTemplates) {

        //first, check if we have any pieces to work with, and if we don't,
        //hide the table and be done
        var pieceType = table.data("pieceType");
        if (phaseTemplates[pieceType].length === 0) {
            $("#" + table.data("divId")).hide();
            return;
        }

        //now that we know we have pieces to work with, create some variables
        //for convenience
        var tableBody = table.find("tbody");
        var templates = phaseTemplates[pieceType];
        var placeholderUnits;
        if (pieceType === "time") {
            placeholderUnits = "m";
        }
        else if (pieceType === "distance") {
            placeholderUnits = "H:M:S";
        }

        //loop through the templates, creating a row for each one and then
        //adding it to the table
        for (var i = 0; i < templates.length; i++) {

            //a few more variables for convenience
            var template = templates[i];
            var pieceNum = template.ordinal;
            var cell, cellAttributes, cellComment;
            var cellContent, contentAttributes;


            //create the new row
            var row = $("<tr>");
            row.attr({"id": "ar-piece-result-row-piece-" + pieceNum});


            row.append("<!-- hidden info fields -->");


            //piece template id cell (hidden but submitted with the form)
            cellAttributes = {"hidden": ""};
            cellComment = "<!-- piece template id -->";
            cellContent = $("<input>");
            contentAttributes = {
                "type": "text",
                "name": "piece-template-id-piece-" + pieceNum,
                "value": template.piece_template_id,
                "aria-label": "piece-template-id-piece-" + pieceNum,
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //overall ordinal cell (hidden but submitted with the form)
            cellAttributes = {"hidden": ""};
            cellComment = "<!-- overall ordinal -->";
            cellContent = $("<input>");
            contentAttributes = {
                "type": "text",
                "name": "ordinal-piece-" + pieceNum,
                "value": pieceNum,
                "aria-label": "ordinal-piece-" + pieceNum,
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //both time and distance will get submitted with the form, but
            //only the non-predetermined one will be visible to the user
            //(the predetermined one will be used to create a label for the
            //piece, but that's separate from the <input> holding it)
            //therefore, create both cells now and append the correct one
            //here in the hidden-field section, and the other where the user
            //can see it

            //time cell
            cellAttributes = undefined;
            cellComment = "<!-- time -->";
            contentAttributes = {
                "class": "ar-dist-time",
                "type": "text",
                "name": "time-piece-" + pieceNum,
                "value": template.time_string,
                "placeholder": placeholderUnits,
                "aria-label": "time-piece-" + pieceNum
            };
            cellContent = $("<input>");
            var timeCell = createTableCell(cellAttributes, cellComment,
                                                cellContent, contentAttributes);


            //distance cell
            cellAttributes = undefined;
            cellComment = "<!-- distance -->";
            contentAttributes = {
                "class": "ar-dist-time ar-dist-field",
                "type": "text",
                "name": "distance-piece-" + pieceNum,
                "value": template.distance,
                "placeholder": placeholderUnits,
                "aria-label": "distance-piece-" + pieceNum
            };
            cellContent = $("<input>");
            var distanceCell = createTableCell(cellAttributes,
                                                    cellComment,
                                                    cellContent,
                                                    contentAttributes);


            //make the correct cell readonly and hidden, and append it here
            if (pieceType === "time") {
                timeCell.find("input").attr({"readonly": ""});
                timeCell.attr({"hidden": ""});
                row.append(timeCell);
            }
            else if (pieceType === "distance") {
                distanceCell.find("input").attr({"readonly": ""});
                distanceCell.attr({"hidden": ""});
                row.append(distanceCell);
            }


            row.append("<!-- input fields for piece " + pieceNum + " -->");


            //ordinal-in-phase cell
            cellAttributes = undefined;
            cellComment = "<!-- ordinal in phase -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-ordinal",
                "type": "text",
                "name": "ordinal-in-phase-piece-" + pieceNum,
                "value": template.ordinal_in_phase,
                "aria-label": "ordinal-in-phase-piece-" + pieceNum,
                "onfocus": "this.blur()",
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //label cell
            cellAttributes = undefined;
            cellComment = "<!-- label -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-label",
                "type": "text",
                "value": template.label,
                "aria-label": "label-piece-" + pieceNum,
                "onfocus": "this.blur()",
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //here's where we add the other, non-hidden distance or time cell
            if (pieceType === "time") {
                row.append(distanceCell);
            }
            else if (pieceType === "distance") {
                row.append(timeCell);
            }


            //avg split cell
            cellAttributes = undefined;
            cellComment = "<!-- avg split -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-split",
                "type": "text",
                "name": "avg-split-piece-" + pieceNum,
                "placeholder": "M:S",
                "aria-label": "avg-split-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg stroke rate cell
            cellAttributes = undefined;
            cellComment = "<!-- avg SR -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-sr",
                "type": "text",
                "name": "avg-sr-piece-" + pieceNum,
                "aria-label": "avg-sr-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg watts cell
            cellAttributes = undefined;
            cellComment = "<!-- avg watts -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-watts",
                "type": "text",
                "name": "avg-watts-piece-" + pieceNum,
                "aria-label": "avg-watts-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg heart rate cell
            cellAttributes = undefined;
            cellComment = "<!-- avg HR -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-hr",
                "type": "text",
                "name": "avg-hr-piece-" + pieceNum,
                "aria-label": "avg-hr-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //add splits cell
            cellAttributes = undefined;
            cellComment = "<!-- add splits -->";
            cellContent = $("<a>").append(template.split_length_string ||
                                          "Add");
            contentAttributes = {
                "class": "ar-add-splits",
                "href": "#",
                "aria-label": "add-splits-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //skipped cell
            cellAttributes = undefined;
            cellComment = "<!-- skipped checkbox -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-skipped-bool",
                "type": "checkbox",
                "name": "skipped-bool-piece-" + pieceNum,
                "value": "false",
                "aria-label": "if-skipped-piece-" + pieceNum,
                "data-piece-num": pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //add the now-complete row to the end of the table body
            tableBody.append(row);
        }
    } //end populateARPieceTable()


    //if the user indicates that they skipped a piece, disable the inputs
    //in that row and gray it out
    $(document).on("change", ".ar-skipped-bool", function() {
        //figure out which row the checkbox is in
        var pieceNum = $(this).data("pieceNum");
        var row = $("#ar-piece-result-row-piece-" + pieceNum);

        //based on the checkbox's checked-ness, enable or disable inputs
        if ($(this).prop("checked")) {
            //TODO CODE ME (skipped piece on add-results modal)
        }
        else {
            //ME, TOO!
        }
    }); //end $(".caw-split-bool").change()


    //every time a user enters meters on the add-results modal, update
    //the total-meter field in the header
    //(written as a listener on a class-filtered part of the document so that
    //it will apply to current *and future* instances of the class)
    $(document).on("blur", ".ar-dist-field",
                   {"highlight": true}, updateTotalMetersHandler);
    function updateTotalMetersHandler(evt) {
        var highlight = evt.data.highlight;
        updateTotalMeters(highlight);
    } //end updateTotalMetersHandler()

    //event handler called whenever meters are entered (also called when
    //add-results modal is first populated with workout-specific fields)
    function updateTotalMeters(highlight) {

        var total = 0;

        //find all distance results fields (both pre-supplied for distance
        //pieces and user-inputted for time pieces) and loop over them to
        //find their sum
        var fields = $(".ar-dist-field");
        for (var i = 0; i < fields.length; i++) {
            total += Number($(fields[i]).val());
        }

        //update the field in the add-results header
        $("#ar-total-meters").val(total);

        //if the highlight option is chosen, highlight the change
        if (highlight) {
            $("#ar-total-meters").effect("highlight",
                                             {color: "#ff0000"},
                                             400);
        }
    } //end updateTotalMeters()


    //Show the comments input for that phase when the user clicks on 'Add notes'
    //on the add-results modal
    $(document).on("click", ".ar-add-comments", function() {
        var commentsDivID = $(this).data("commentsDivId");
        $(this).hide();
        $("#" + commentsDivID).show();
        $("#" + commentsDivID).find("textarea").focus();
    }); //end $(".ar-add-comments").click()


    //Save workout results and, if user has requested to do so, go back to
    //the workout chooser pane
    $(document).on("click", ".ar-save-button", function() {

        //figure out which save button was clicked, so we know what to do
        //once we've saved the results
        var addMoreResults = $(this).data("addAnother");

        //we're about to change the set of all workout results for this
        //user, so unset the upToDate flag on our front-side store thereof
        gResults.upToDate = false;

        //this will also make our front-side store of templates out of date
        //(because potentially one that didn't have results now will), so
        //flag that so that the next code that needs it will know to update
        //it first
        gTemplates.upToDate = false;

        //get data from the form
        var formData = $("#add-results-form").serialize();

        //save the workout to the database, update gResults, and add the
        //workout to the table on the log page
        $.post("/save-workout-results.json", formData, function(data) {
            gResults = data;
            gResults.upToDate = true;

            //make the new result appear in the log table, in the
            //right spot given its date
            var newRow = createLogTableRow(gResults.newest);
            insertLogTableRow(newRow);
        });

        //if the user has asked to add more results, flip back to the
        //workout-chooser pane (where the template we just added results to
        //should now appear in the 'with results' menu, if it wasn't
        //there already)
        if (addMoreResults) {
            //we know our gTemplates is out of date, so update it and use
            //the results to populate the workout chooser
            $.get("/get-workout-templates.json", function(data) {

                //update gTemplates
                gTemplates = data;
                gTemplates.upToDate = true;

                //TODO FINISH CODING ME!!

            });
        }

        //otherwise, close and reset the modal, and update gTemplates in
        //the background
        else {
            //close and reset the modal
            $('#add-results-modal').modal('hide');
            $("#add-results-modal").html(gARModalInitial);
            $("#add-results-form")[0].reset();

            //update gTemplates
            $.get("/get-workout-templates.json", function(data) {
                gTemplates = data;
                gTemplates.upToDate = true;
            });
        }
    }); //end $(".ar-save-button").click()



    //given a workoutResult object, create a filled-in <tr> representing
    //which can then be added to the log table
    function createLogTableRow(resultObj) {

        //grab data from the given result object for storage in and
        //on the row
        var resultID = resultObj.workout_result.workout_result_id;
        var resultDistance = resultObj.workout_result.total_meters;
        var resultDescription = resultObj.workout_template.description;

        //grab the date (as a parsable date, for comparison, and as a
        //formatted string, for display)
        var resultDate = resultObj.workout_result.date;
        var dateString = resultObj.workout_result.date_string;

        //create a new row and give the required data
        var row = $("<tr>").data({
            "date": resultDate,
            "workout-id": resultID
        });

        //define some variables for convenience
        var cell, cellAttributes, cellComment, cellContent, contentAttributes;

        //date/click-for-details cell
        cellAttributes = undefined;
        cellComment = undefined;
        cellContent = $("<a>").append(dateString);
        contentAttributes = {"class": "log-table-date-link"};
        cell = createTableCell(cellAttributes, cellComment,
                               cellContent, contentAttributes);
        row.append(cell);

        //description cell
        cellAttributes = {"class": "log-table-description"};
        cellComment = undefined;
        cellContent = resultDescription;
        contentAttributes = undefined;
        cell = createTableCell(cellAttributes, cellComment,
                               cellContent, contentAttributes);
        row.append(cell);

        //distance cell
        cellAttributes = {"class": "log-table-meters"};
        cellComment = undefined;
        cellContent = resultDistance + " m";
        contentAttributes = undefined;
        cell = createTableCell(cellAttributes, cellComment,
                               cellContent, contentAttributes);
        row.append(cell);

        //edit cell
        cellAttributes = undefined;
        cellComment = undefined;
        cellContent = $("<a>").append("Edit");
        contentAttributes = {"class": "log-table-edit-link"};
        cell = createTableCell(cellAttributes, cellComment,
                               cellContent, contentAttributes);
        row.append(cell);

        //delete cell
        cellAttributes = undefined;
        cellComment = undefined;
        cellContent = $("<a>").append("Delete");
        contentAttributes = {"class": "log-table-delete-link"};
        cell = createTableCell(cellAttributes, cellComment,
                               cellContent, contentAttributes);
        row.append(cell);

        //now that the row's finished, return it
        return row;
    } //end createLogTableRow()


    //given a filled out row of the log table, insert it into the table,
    //preserving reverse chronological order
    function insertLogTableRow(rowToInsert) {

        //find the body of the log table and figure out how many rows
        //it currently has
        var tableBody = $("#main-log-table-body");
        var numRows = tableBody.find("tr").length;

        //get the date of the result we're trying to insert
        var resultDate = Date.parse(rowToInsert.data("date"));

        //loop through each row, checking its date against that of the
        //given result; when a date less than given result's date is found,
        //make a note of it and break out of the loop
        var rowBelow;
        for (var i = 1; i <= numRows; i++) {
            //get the date of the current row
            var ithRow = tableBody.find("tr:nth-of-type(" + i + ")");
            var ithRowDate = Date.parse(ithRow.data("date"));

            //if it's less (earlier) than the given result's date,
            //grab this row and exit the loop
            if (ithRowDate < resultDate) {
                    rowBelow = ithRow;
                    break;
            }
        }

        //if we've found a row with an earlier date, insert the new
        //row above it
        if (rowBelow) {
            rowToInsert.insertBefore(rowBelow);
        }
        //otherwise, add the new row to the end of the table
        else {
            tableBody.append(rowToInsert);
        }
    } //end insertLogTableRow()

    $("#testtest").click(function() {

    });


    /************ functions dealing with the workout details modal ************/

    //When a date in the log table is clicked, populate the workout details
    //modal with the details of the corresponding workout and show it
    $(document).on("click", ".log-table-date-link", function() {

        //get the workout id for the workout the user chose, and pull the
        //corresponding result object from local storage
        var workoutID = $(this).closest("tr").data("workoutId");
        var resultObj = gResults[workoutID];

        //unpack the result object
        var workoutTemplate = resultObj.workout_template;
        var workoutResult = resultObj.workout_result;
        var pieces = resultObj.pieces;
        var warmupPieces = pieceResultsByPhase(resultObj, "warmup");
        var mainPieces = pieceResultsByPhase(resultObj, "main");
        var cooldownPieces = pieceResultsByPhase(resultObj, "cooldown");

        //create a title for the modal (description and primary zone) and
        //add it in the appropriate place
        var description = resultObj.workout_template.description;
        var primaryZone = resultObj.workout_template.primary_zone;
        var title = description;
        if (primaryZone) {
            title = title + " (" + primaryZone + ")";
        }
        $("#wd-workout-title").append(title);

        //add the date, time, and total meters to the header
        var dateString = workoutResult.date_string;
        var timeString = workoutResult.time_string;
        var totalMeters = workoutResult.total_meters;
        $("#wd-date").val(dateString);
        $("#wd-time-of-day").val(timeString);
        $("#wd-total-meters").val(totalMeters);

        //do a little magic to get the total distance to right align itself
        $("#wd-total-meters-util").text(totalMeters);
        var totalMetersWidth = $("#wd-total-meters-util").width();
        console.log("totalMetersWidth", $("#wd-total-meters-util").width());
        $("#wd-total-meters").css("width", totalMetersWidth);

        //populate subheading info (format, stroke rates, notes) for
        //each phase
        populateWDPhaseInfo(workoutTemplate, "warmup");
        populateWDPhaseInfo(workoutTemplate, "main");
        populateWDPhaseInfo(workoutTemplate, "cooldown");

        //find and populate the piece tables for each phase (or hide the
        //phase entirely if there are no pieces in that phase)
        var warmupPieceTable = $("#wd-warmup-table");
        var mainPieceTable = $("#wd-main-table");
        var cooldownPieceTable = $("#wd-cooldown-table");
        populateWDPieceTable(warmupPieceTable, warmupPieces);
        populateWDPieceTable(mainPieceTable, mainPieces);
        populateWDPieceTable(cooldownPieceTable, cooldownPieces);

        //populate the notes for each section, as well as the goals and
        //notes for the overall workout
        populateWDPhaseNotes(workoutResult, "warmup");
        populateWDPhaseNotes(workoutResult, "main");
        populateWDPhaseNotes(workoutResult, "cooldown");
        populateWDOverallNotes(workoutResult);

        //populate calories and overall average HR
        $("#wd-avg-hr").val(workoutResult.avg_hr);
        $("#wd-calories").val(workoutResult.calories);

        //find all the fields on the modal and disable them
        $(".wd-field").attr({
            "onfocus": "this.blur()",
            "readonly": ""
        });
        $(".wd-skipped").hide();

        //now that it's all ready, show the modal
        $("#workout-details-modal").modal("show");
        console.log("totalMetersWidth", $("#wd-total-meters-util").width());
    });


    //Given a verbose objectified version of a workout result, return an
    //array containing its verbose (including templates and splits) piece
    //results, filtered by the given phase and sorted by ordinal.
    function pieceResultsByPhase(resultObj, phase) {

        var phasePieces = [];

        //unpack the layers of the workout results object and go through
        //the pieces one by one, adding those with the correct phase
        //to the phasePieces array
        var piecesObject = resultObj.pieces;
        var numPieces = Object.keys(piecesObject).length;
        for (var i = 0; i < numPieces; i++) {
            var template = piecesObject[i+1].template;
            if (template.phase === phase)
            {
                phasePieces.push(piecesObject[i+1]);
            }
        }
        //note that since piecesObject is keyed by ordinal, and pieces are
        //added to phasePieces [an array, so it preserves order] in
        //increasing order by key, no additional sort is needed

        return phasePieces;
    } //end pieceTemplatesByPhase()


    //Populate phase info (format, stroke rates, notes) for the given
    //phase on the workout details modal
    function populateWDPhaseInfo(workoutTemplate, phase) {

        //find the div into which the info will go
        var div = $("#wd-" + phase + "-phase-info");

        //get the pieces out of which we'll build the html which will
        //go in the div
        var format = workoutTemplate[phase + "_format"];
        var rates = workoutTemplate[phase + "_stroke_rates"];
        var notes = workoutTemplate[phase + "_notes"];
        var content = "";

        //lack of info in any of the three categories is represented by an
        //empty string, so we can add all three to the string regardless, and
        //it'll just function as a no-op if the info's not there
        content += format;
        if (format) {
            content += (" (" + rates + ")");
        }
        else {
            content += rates;
        }
        if ((format || rates) && notes) {
            content += ("<br>" + notes);
        }
        else {
            content += notes;
        }

        //add the content to the div
        div.html(content);
    } //end populateWDPhaseInfo()


    //Pull the appropriate pieces out of the given templates object and use
    //them to populate the given table on the add-results modal
    //If there are no appropriate pieces, hide the table instead
    function populateWDPieceTable(table, phaseResults) {

        //first, check if we have any pieces to work with, and if we don't,
        //hide the section and be done
        if (phaseResults.length === 0) {
            $("#" + table.data("sectionDivId")).hide();
            return;
        }

        //now that we know we have pieces to work with, create some variables
        //for convenience
        var tableBody = table.find("tbody");

        //loop through the results, creating a row for each one and then
        //adding it to the table
        for (var i = 0; i < phaseResults.length; i++) {

            //a few more variables for convenience
            var template = phaseResults[i].template;
            var result = phaseResults[i].result;
            var pieceNum = template.ordinal;
            var pieceType = template.piece_type;
            var placeholderUnits;
            if (pieceType === "time") {
                placeholderUnits = "m";
            }
            else if (pieceType === "distance") {
                placeholderUnits = "H:M:S";
            }
            var cell, cellAttributes, cellComment;
            var cellContent, contentAttributes;


            //create the new row
            var row = $("<tr>");
            row.attr({"id": "wd-piece-result-row-piece-" + pieceNum});


            row.append("<!-- hidden info fields -->");


            //piece template id cell (hidden but submitted with the form)
            cellAttributes = {"hidden": ""};
            cellComment = "<!-- piece result id -->";
            cellContent = $("<input>");
            contentAttributes = {
                "type": "text",
                "name": "piece-result-id-piece-" + pieceNum,
                "value": result.piece_result_id,
                "aria-label": "piece-result-id-piece-" + pieceNum,
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            row.append("<!-- input fields for piece " + pieceNum + " -->");


            //ordinal-in-phase cell
            cellAttributes = undefined;
            cellComment = "<!-- ordinal in phase -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-ordinal text-right",
                "type": "text",
                "name": "ordinal-in-phase-piece-" + pieceNum,
                "value": template.ordinal_in_phase,
                "aria-label": "ordinal-in-phase-piece-" + pieceNum,
                "onfocus": "this.blur()",
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //label cell
            cellAttributes = undefined;
            cellComment = "<!-- label -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-label",
                "type": "text",
                "value": template.label,
                "aria-label": "label-piece-" + pieceNum,
                "onfocus": "this.blur()",
                "readonly": ""
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //both time and distance will be displayed on the workout
            //details/edit results modal, but one will be shown as the
            //piece label (whichever one is in the template) instead of
            //being shown as data (that one also can't change, and so
            //doesn't need to be submitted with the form)
            if (pieceType === "time") {
                //distance cell
                cellAttributes = undefined;
                cellComment = "<!-- distance -->";
                contentAttributes = {
                    "class": "ar-dist-time ar-dist-field wd-field text-right",
                    "type": "text",
                    "name": "distance-piece-" + pieceNum,
                    "value": result.total_meters  || "-",
                    "placeholder": placeholderUnits,
                    "aria-label": "distance-piece-" + pieceNum
                };
                cellContent = $("<input>");
                cell = createTableCell(cellAttributes,
                                                   cellComment,
                                                   cellContent,
                                                   contentAttributes);
                row.append(cell);
            }
            else if (pieceType === "distance") {
                //time cell
                cellAttributes = undefined;
                cellComment = "<!-- time -->";
                contentAttributes = {
                    "class": "ar-dist-time wd-field text-right",
                    "type": "text",
                    "name": "time-piece-" + pieceNum,
                    "value": result.total_time_string  || "-",
                    "placeholder": placeholderUnits,
                    "aria-label": "time-piece-" + pieceNum
                };
                cellContent = $("<input>");
                cell = createTableCell(cellAttributes, cellComment,
                                               cellContent, contentAttributes);
                row.append(cell);
            }


            //avg split cell
            cellAttributes = undefined;
            cellComment = "<!-- avg split -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-split wd-field text-right",
                "type": "text",
                "name": "avg-split-piece-" + pieceNum,
                "value": result.avg_split_string || "-",
                "placeholder": "M:S",
                "aria-label": "avg-split-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg stroke rate cell
            cellAttributes = undefined;
            cellComment = "<!-- avg SR -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-sr wd-field text-right",
                "type": "text",
                "name": "avg-sr-piece-" + pieceNum,
                "value": result.avg_sr  || "-",
                "aria-label": "avg-sr-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg watts cell
            cellAttributes = undefined;
            cellComment = "<!-- avg watts -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-watts wd-field text-right",
                "type": "text",
                "name": "avg-watts-piece-" + pieceNum,
                "value": result.avg_watts  || "-",
                "aria-label": "avg-watts-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //avg heart rate cell
            cellAttributes = undefined;
            cellComment = "<!-- avg HR -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-hr wd-field text-right",
                "type": "text",
                "name": "avg-hr-piece-" + pieceNum,
                "value": result.avg_hr || "-",
                "aria-label": "avg-hr-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                        cellContent, contentAttributes);
            row.append(cell);


            //add splits cell
            cellAttributes = {"class": "text-right"};
            cellComment = "<!-- add splits -->";
            cellContent = $("<a>").append(template.split_length_string ||
                                          "-");
            contentAttributes = {
                "class": "ar-add-splits",
                "href": "#",
                "aria-label": "add-splits-piece-" + pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                   cellContent, contentAttributes);
            row.append(cell);


            //skipped cell
            cellAttributes = {"class": "wd-skipped"};
            cellComment = "<!-- skipped checkbox -->";
            cellContent = $("<input>");
            contentAttributes = {
                "class": "ar-skipped-bool wd-field",
                "type": "checkbox",
                "name": "skipped-bool-piece-" + pieceNum,
                "value": !result.completed,
                "aria-label": "if-skipped-piece-" + pieceNum,
                "data-piece-num": pieceNum
            };
            cell = createTableCell(cellAttributes, cellComment,
                                   cellContent, contentAttributes);
            row.append(cell);


            //add the now-complete row to the end of the table body
            tableBody.append(row);
        }
    } //end populateARPieceTable()


    //Populate the notes field for the given phase on the workout details
    //modal
    function populateWDPhaseNotes(workoutResult, phase) {

        //get the notes (if any) for the given phase from the
        //workoutResult object
        var notes = workoutResult[phase + "_comments"];

        //if there are no results, show the 'add notes' link but then
        //hide the entire notes div (this is so that when a user switches
        //to edit mode, the link will be what's showing when we show the
        //whole div)
        if (!notes) {
            var link = $("#wd-add-" + phase + "-comments");
            link.show();
            link.closest("div.row").hide();
        }
        //otherwise, populate and show the notes heading and field
        else {
            $("#wd-" + phase + "-comments").val(notes);
            $("#wd-" + phase + "-comments-div").show();
        }
    } //end populateWDPhaseNotes()


    //Populate the overall goals and notes fields on the workout details modal
    //(or hide the whole section if neither is filled in)
    function populateWDOverallNotes(workoutResult) {

        //get the goals and notes (if any) from the workoutResult object
        var goals = workoutResult.goals;
        var comments = workoutResult.comments;

        //if neither exist, hide the whole section
        if (!(goals || comments)) {
            $("#wd-notes").hide();
        }
        //otherwise, populate (or hide) the individual sections as needed
        else {
            if (goals) {
                $("#wd-overall-goals").val(goals);
            }
            else {
                $("#wd-overall-goals-div").hide();
            }
            if (comments) {
                $("#wd-overall-comments").val(comments);
            }
            else {
                $("#wd-overall-comments-div").hide();
            }
        }
    } //end populateWDOverallNotes()


    //TODO trigger all modals via javascript to avoid weird post-modal focusing
    //behavior; make inserted row flash when its inserted


});

