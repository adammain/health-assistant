$(document).ready(function() {
    // Use a "/timer" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/timer';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // Dynamically generate new rooms for each new entry to match dynamically gen css id's
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        // After page refresh, all buttons are reset to 'Start'
            // On connect, send emit asking for active_timer
            // If active timer exists, update styling & button

        socket.emit('no_server_handler_built_yet', {data: 'I\'m connected!'});
    });

    // IF CLICKED BUTTON IS RUNNING, STOP IT. IF NOT, START IT AND TURN OFF OTHER TIMERS.
    // After page refresh, all buttons are reset to 'Start'
        // On connect, send emit asking for active_timer
        // If active timer exists, update styling & button
    $('form#timer').submit(function(event) {
        clickedTimerID = $(this).attr('value');
        clickedTimerType = $(this).attr('type');
        console.log("TIMER TYPE: ", clickedTimerType)
        clickedButtonA = $('#timer_btn_text_'+clickedTimerType+clickedTimerID);
        clickedButtonParentList = clickedButtonA.closest('li');
        startClickedTimer = true;

        console.log("Clicked Button #", clickedTimerID)
        console.log("ClickedButtonParentList: ", clickedButtonParentList)
        console.log("clickedButtonA: ", clickedButtonA)
        if (clickedButtonA.hasClass('is-running')) {
            console.log("Clicked Timer Already Running.  Stopping Timer #", clickedTimerID)
            // if "clicked timer" is running, stop it
            clickedButtonA.text('Start')
            $("button.is-running > svg").removeClass("is-running");
            clickedButtonA.removeClass('is-running')
            clickedButtonA.parentsUntil('div.container').removeClass('is-running')
            socket.emit('deactivate_timer', {type: clickedTimerType, room: $(this).attr('value')});
            $('#log').append('<br>' + $('<div/>').text('Client Sent Stop Timer Request..' + clickedTimerType + $(this).attr('value')).html());
            startClickedTimer = false;  // Clicked timer was running, stopped. Next time clicked, start.
        } else if (clickedButtonParentList.siblings('li').hasClass('is-running')) {
            // if another timer is running, stop it
            runningTimerList = clickedButtonParentList.siblings('li.is-running')
            runningTimerForm = runningTimerList.find('form#timer')
            runningTimerType = runningTimerForm.attr('type')
            runningTimerID = runningTimerForm.attr('value')
            console.log("Other Timer Already Running.  Stopping Timer #", runningTimerID)
            runningTimerBtn = runningTimerForm.find('span.is-running')
            runningTimerBtn.text('Start')
            $("button.is-running > svg").removeClass("is-running");
            runningTimerBtn.removeClass('is-running')
            runningTimerBtn.parentsUntil('div.container').removeClass('is-running')
            socket.emit('deactivate_timer', {type: runningTimerType, room: runningTimerID});
            $('#log').append('<br>' + $('<div/>').text('Client Sent Stop Timer Request..' + runningTimerType + runningTimerID).html());
            startClickedTimer = true;
        }

        // if no other timer is running, start clicked timer
        if (startClickedTimer) {
            console.log("Started Timer #", clickedTimerID);
            console.log("Click Timer TYPE", clickedTimerType);
            clickedButtonA.text('Stop');
            clickedButtonA.addClass('is-running');
            clickedButtonA.parentsUntil('div.container').addClass('is-running');
            $("button.is-running > svg").addClass("is-running");
            socket.emit('activate_timer', {type: clickedTimerType, room: clickedTimerID});
            $('#log').append('<br>' + $('<div/>').text('Client Sent Start Timer Request.. ' + clickedTimerType + $(this).attr('value')).html());
        }

        return false;
    });

    // Timer response event handler
    pageReloadedTimerResponse = true
    socket.on('timer_response', function(msg) {

        // Update button text for active timer after page refresh
        activeTimerID = msg.active_timer
        if (activeTimerID && pageReloadedTimerResponse) {
            console.log("CURRENT ACTIVE TIMER: ", msg.active_timer)
            console.log("ACTIVE TIMER ID:", activeTimerID)
            activeTimerBtn = $('#timer_btn_text_'+activeTimerID);
            activeTimerBtn.text('Stop')
            activeTimerBtn.addClass('is-running')
            activeTimerBtn.parentsUntil('div.container').addClass('is-running')
            $("button.is-running > svg").addClass("is-running");
            $('#log').append('<br>' + $('<div/>').text('Client Sent Start Timer Request.. ' + activeTimerID).html());
            pageReloadedTimerResponse = false
        }

        // Active timer response
        $('#time_'+activeTimerID).text(msg.count);
        $('#time_btn_'+activeTimerID).attr('data-activity-duration', msg.count)
    });

    // LOG Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('connect_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Websocket Status: ' + msg.data + '. Active Timer: ' + msg.active_timer).html());
    });

    socket.on('my_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Timer Update For: ' + msg.active_timer + ': ' + msg.data).html());
    });
});
