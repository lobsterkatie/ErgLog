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
        //get data to use in the function
        var parentTable = $(this).closest("table");
        var parentTableBody = parentTable.find("tbody");
        var phase = parentTable.data("phase");
        var piecesInPhase = parentTable.data("piecesInPhase");
        var pieceNum = $(this).closest("form").data("nextPieceNum");
        var pieceType = $(this).data("pieceType");
        var placeholderUnits;
        if (pieceType === "time") {
            placeholderUnits = "h:m:s";
        }
        else if (pieceType === "distance") {
            placeholderUnits = "m";
        }

        //console.log("nextPieceNum: " + pieceNum, "piecesInPhase: " + piecesInPhase);

        //create some variables to hold the pieces out of which we'll build
        //the new row
        var row = $("<tr>").attr("data-piece-num", pieceNum);
        var cell, cellAttributes, cellComment, cellContent, contentAttributes;


        row.append("<!-- hidden info fields -->");

        //phase cell
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
        //inputElement = $("<input>").attr(inputAttributes);
        //cell = $("<td>").attr(cellAttributes);
        //cell.append(inputElement);
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        //piece type cell
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
        //inputElement = $("<input>").attr(inputAttributes);
        //cell = $("<td>").attr(cellAttributes);
        //cell.append(inputElement);
        cell = createPieceTableCell(cellAttributes, cellComment,
                                    cellContent, contentAttributes);
        row.append(cell);


        row.append("<!-- input fields for piece " + pieceNum + " -->");


        //ordinal cell
        cellAttributes = undefined;
        cellComment = "<!-- ordinal -->";
        cellContent = $("<input>");
        contentAttributes = {
            "class": "caw-ordinal",
            "type": "text",
            "name": "ordinal-piece-" + pieceNum,
            "value": pieceNum,
            "aria-label": "ordinal-piece-" + pieceNum,
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
        if (piecesInPhase === 0) {
            parentTable.find("thead").show();
            parentTable.find(".caw-footer-repeat").show();
        }


        //update the count of both total pieces in the workout and pieces in
        //the current phase, each in the relevant place in the DOM and jquery's
        //cache
        var nextPieceNum = pieceNum + 1;
        var newPiecesInPhase = piecesInPhase + 1;
        var totalPieces = $("#caw-num-pieces").val();
        $(this).closest("form").attr("data-next-piece-num", nextPieceNum);
        $(this).closest("form").data("nextPieceNum", nextPieceNum);
        parentTable.attr("data-pieces-in-phase", newPiecesInPhase);
        parentTable.data("piecesInPhase", newPiecesInPhase);
        $("#caw-num-pieces").val(++totalPieces);
        console.log("numPieces is now " + (totalPieces));



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
       and its attributes can either be given singly or as arrays) */
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
        evt.preventDefault();
        var formData = $("#create-a-workout-form").serialize();
        $.post("/save-workout-template.json",
               formData,
               function(data) {console.log(data);});

    });



    /******** load workout template descriptions into add-results modal *******/



    //pull workout template descriptions and id's and use them to populate
    //workout-chooser on the add-results modal
    $("#add-results-modal").on("show.bs.modal", function(evt) {
        //TODO CODE ME!!!  (populate workouts on add results modal)
    });





    /*$(".modal").on("show.bs.modal", function (evt) {

        //
        $(evt.currentTarget).data("caller", $(evt.relatedTarget));



    });

    $(".modal").on("hidden.bs.modal", function (evt) {

        //
        console.log("here");
        $("#dummy-button").click();



    });*/



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

