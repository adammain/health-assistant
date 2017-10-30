$(document).ready(function() {

    // MEAL MODAL JS.
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editMealModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let duration = button.data('activity-duration');
        let health = button.data('activity-health');
        let description = button.data('activity-description')
        let starch_rich = button.data('activity-starch')
        let sucrose_rich = button.data('activity-sucrose')

        // Slice seconds off edit time input
        if (duration.length == 8)
            duration = duration.slice(0, 5)
        else
            duration = duration.slice(0, 4)

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-time').append('<input id="time" name="time" type="text" value='+duration+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: 'meal', id: id, year: year, month: month, day: day }));
        $('#health').val(health)
        $('#description').val(description)

        if (starch_rich == 'True')
            $('#starch_rich').prop('checked')
        if (sucrose_rich == 'True')
            $('#sucrose_rich').prop('checked');

        // Delete meal entry
        $('#editMealModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: 'meal', id: id, year: year, month: month, day: day }));
        $('#delete-meal-entry').click(function(e) {
            console.log("DELETE CLICKED EVENT")
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editMealModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editMealModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editMealModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-meal-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    })


    // SLEEP MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editSleepModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let duration = button.data('activity-duration');

        // Slice seconds off edit time input
        if (duration.length == 8)
            duration = duration.slice(0, 5)
        else
            duration = duration.slice(0, 4)

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-time').append('<input id="time" name="time" type="text" value='+duration+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: 'sleep', id: id, year: year, month: month, day: day }));

        // Delete sleep entry
        $('#editSleepModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: 'sleep', id: id, year: year, month: month, day: day }));
        $('#delete-sleep-entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editSleepModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editSleepModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editSleepModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-sleep-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });


    // WORKOUT MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editWorkoutModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let entryType = 'workout'
        let button = $(event.relatedTarget);
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let duration = button.data('activity-duration');
        let light = button.data('activity-light')
        let intense = button.data('activity-intense')
        let interval = button.data('activity-interval')
        let endurance = button.data('activity-endurance')

        // Slice seconds off edit time input
        if (duration.length == 8)
            duration = duration.slice(0, 5)
        else
            duration = duration.slice(0, 4)

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-time').append('<input id="duration" name="duration" type="text" value='+duration+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: entryType, id: id, year: year, month: month, day: day }));

        if (light == 'True')
            $('input:radio[name=intensity]').filter('[value=light]').prop('checked', true)
        else
            $('input:radio[name=intensity]').filter('[value=intense]').prop('checked', true)

        if (interval == 'True')
            $('input:radio[name=workout_type]').filter('[value=interval]').prop('checked', true)
        else
            $('input:radio[name=workout_type]').filter('[value=endurance]').prop('checked', true)


        // Delete workout entry
        $('#editWorkoutModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: entryType, id: id, year: year, month: month, day: day }));
        $('#delete-workout-entry').click(function(e) {
            console.log("DELETE CLICKED EVENT")
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editWorkoutModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editWorkoutModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editWorkoutModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-workout-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });

    // WEIGHT MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editWeightModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let weight = button.data('activity-weight');

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-weight').append('<input id="weight" name="weight" type="text" value='+weight+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: 'weight', id: id, year: year, month: month, day: day }));

        // Delete weight entry
        $('#editWeightModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: 'weight', id: id, year: year, month: month, day: day }));
        $('#delete-weight-entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editWeightModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editWeightModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editWeightModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-weight-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });


    // BLOOD PRESSURE MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editBloodPressureModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let type = 'bloodpressure'
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let systolic = button.data('activity-systolic');
        let diastolic = button.data('activity-diastolic');

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-systolic').append('<span>Sys</span><input id="systolic" name="systolic" placeholder="systolic" type="text" value='+systolic+'>').html();
        $('form#edit-entry p#modal-diastolic').append('<span>Dia</span><input id="diastolic" name="diastolic" placeholder="diastolic" type="text" value='+diastolic+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editBloodPressureModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete-bloodpressure-entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editBloodPressureModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editBloodPressureModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editBloodPressureModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-bp-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });


    // BLOOD SUGAR MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editBloodSugarModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let type = 'bloodsugar'
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY')
        let month = date.format('MM')
        let day = date.format('DD')
        let glucose_level = button.data('activity-glucose-level');
        let insulin_level = button.data('activity-insulin-level');

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-glucose-level').append('<span>Glucose (mmol/L)</span><input id="glucose_level" name="glucose_level" placeholder="glucose_level" type="text" value='+glucose_level+'>').html();
        $('form#edit-entry p#modal-insulin-level').append('<span>Insulin (pmol/L)</span><input id="insulin_level" name="insulin_level" placeholder="insulin_level" type="text" value='+insulin_level+'>').html();
        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editBloodSugarModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete-bloodsugar-entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editBloodSugarModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editBloodSugarModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editBloodSugarModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-bp-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });


    // HEART RATE MODAL JS
    // Bind to bootstrap modal instance opening.  Fill form with timer data.
    $('#editHeartRateModal').on('show.bs.modal', function (event) {
        let modal = $(this)
        let button = $(event.relatedTarget);
        let type = 'heartrate'
        let id = button.data('activity-id');
        let date = moment(button.data('activity-date'));
        let year = date.format('YYYY');
        let month = date.format('MM');
        let day = date.format('DD');
        let bpm = button.data('activity-bpm')
        let resting = button.data('activity-resting');
        let active = button.data('activity-active');

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit-entry p#modal-date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit-entry p#modal-bpm').append('<input id="bpm" name="bpm" placeholder="Beats Per Minute BPM" type="text" value='+bpm+'>').html();

        console.log("RESTING?: ", resting)
        if (resting == 'True')
            $('input:radio[name=measurement_type]').filter('[value=resting]').prop('checked', true)
        else
            $('input:radio[name=measurement_type]').filter('[value=active]').prop('checked', true)

        $('form#edit-entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editHeartRateModal .confirm-delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete-heartrate-entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed-delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editHeartRateModal #initial-delete').replaceWith('<button action="#" class="entry-delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editHeartRateModal').on('hidden.bs.modal', function (e) {
        $('form#edit-entry p input').remove();
        $('#editHeartRateModal button.entry-delete').replaceWith('<div id="initial-delete"><a id="delete-bp-entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });
})
