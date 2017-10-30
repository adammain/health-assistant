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

        console.log("starch_rich: ", typeof(starch_rich))
        console.log("sucrose_rich: ", sucrose_rich)

        // Slice seconds off edit time input
        if (duration.length == 8)
            duration = duration.slice(0, 5)
        else
            duration = duration.slice(0, 4)

        // Modal heading with date
        modal.find('.modal-title').text('Edit entry: ' + date.format('dddd, Do MMM'))

        // Inject Flask-wtf form inputs
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__time').append('<input id="time" name="time" type="text" value='+duration+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: 'meal', id: id, year: year, month: month, day: day }));
        $('#health').val(health)
        $('#description').val(description)

        if (starch_rich == 'True')
            $('#starch_rich').prop('checked', true)
        if (sucrose_rich == 'True')
            $('#sucrose_rich').prop('checked', true);

        // Delete meal entry
        $('#editMealModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: 'meal', id: id, year: year, month: month, day: day }));
        $('#delete_meal_entry').click(function(e) {
            console.log("DELETE CLICKED EVENT")
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editMealModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editMealModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editMealModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_meal_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__time').append('<input id="time" name="time" type="text" value='+duration+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: 'sleep', id: id, year: year, month: month, day: day }));

        // Delete sleep entry
        $('#editSleepModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: 'sleep', id: id, year: year, month: month, day: day }));
        $('#delete_sleep_entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editSleepModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editSleepModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editSleepModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_sleep_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__time').append('<input id="duration" name="duration" type="text" value='+duration+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: entryType, id: id, year: year, month: month, day: day }));

        if (light == 'True')
            $('input:radio[name=intensity]').filter('[value=light]').prop('checked', true)
        else
            $('input:radio[name=intensity]').filter('[value=intense]').prop('checked', true)

        if (interval == 'True')
            $('input:radio[name=workout_type]').filter('[value=interval]').prop('checked', true)
        else
            $('input:radio[name=workout_type]').filter('[value=endurance]').prop('checked', true)


        // Delete workout entry
        $('#editWorkoutModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: entryType, id: id, year: year, month: month, day: day }));
        $('#delete_workout_entry').click(function(e) {
            console.log("DELETE CLICKED EVENT")
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editWorkoutModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editWorkoutModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editWorkoutModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_workout_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__weight').append('<input id="weight" name="weight" type="text" value='+weight+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: 'weight', id: id, year: year, month: month, day: day }));

        // Delete weight entry
        $('#editWeightModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: 'weight', id: id, year: year, month: month, day: day }));
        $('#delete_weight_entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editWeightModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editWeightModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editWeightModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_weight_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__systolic').append('<span>Sys</span><input id="systolic" name="systolic" placeholder="systolic" type="text" value='+systolic+'>').html();
        $('form#edit_entry p#modal__diastolic').append('<span>Dia</span><input id="diastolic" name="diastolic" placeholder="diastolic" type="text" value='+diastolic+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editBloodPressureModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete_bloodpressure_entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editBloodPressureModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editBloodPressureModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editBloodPressureModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_bloodpressure_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__glucose_level').append('<span>Glucose (mmol/L)</span><input id="glucose_level" name="glucose_level" placeholder="glucose_level" type="text" value='+glucose_level+'>').html();
        $('form#edit_entry p#modal__insulin_level').append('<span>Insulin (pmol/L)</span><input id="insulin_level" name="insulin_level" placeholder="insulin_level" type="text" value='+insulin_level+'>').html();
        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editBloodSugarModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete_bloodsugar_entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editBloodSugarModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editBloodSugarModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editBloodSugarModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_bloodsugar_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
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
        $('form#edit_entry p#modal__date').append('<input id="date" name="date" type="text" value='+date.format('MM/DD/YYYY')+'>').html();
        $('form#edit_entry p#modal__bpm').append('<input id="bpm" name="bpm" placeholder="Beats Per Minute BPM" type="text" value='+bpm+'>').html();

        if (resting == 'True')
            $('input:radio[name=measurement_type]').filter('[value=resting]').prop('checked', true)
        else
            $('input:radio[name=measurement_type]').filter('[value=active]').prop('checked', true)

        $('form#edit_entry').attr('action', flask_util.url_for('editEntry', {type: type, id: id, year: year, month: month, day: day }));

        // Delete blood pressure entry
        $('#editHeartRateModal .confirm_delete').attr('action', flask_util.url_for('deleteEntry', {type: type, id: id, year: year, month: month, day: day }));
        $('#delete_heartrate_entry').click(function(e) {
            e.preventDefault();
            let content = $('<button class="confirmed_delete" href="#" type="submit">Confirm Delete?</button>').html();
            $('#editHeartRateModal #initial_delete').replaceWith('<button action="#" class="entry__delete" method="POST">' + content + '</button>');
        });
    });

    // Reset form values when closed.
    $('#editHeartRateModal').on('hidden.bs.modal', function (e) {
        $('form#edit_entry p input').remove();
        $('#editHeartRateModal button.entry__delete').replaceWith('<div id="initial_delete"><a id="delete_heartrate_entry" href="#">Delete<span class="fa fa-trash"></span></a></div>')
    });
})
