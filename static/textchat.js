$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    messagekeyenroll();
    $(".message").select();
    updater.start();
});

function messagekeyenroll() {
    $(".messageform").off("submit");
    $(".messageform").on("submit", function() {
        newMessage($(this));
        return false;
    });
};

function newMessage(form, threadid) {
    
    var message = form.formToDict();
    formid = form.attr("id");

    message["id"] = formid.replace("messageform", "");
    updater.socket.send(JSON.stringify(message));

    form.find("input[type=text]").val("");
    form.find("textarea").val("").select();
    form.find("textarea").val("");
    form.find("textarea").val("").select();
    //formElement = document.getElementById(formid);
    //formElement.reset();
}

jQuery.fn.formToDict = function() {

    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,
    socketfile: null,
    socketnum: null,

    start: function() {
        var url = "ws://" + location.host + "/textsocket";
        var urlfile = "ws://" + location.host + "/chatsocketfile";
        var urlnum = "ws://" + location.host + "/chatsocketnum";
        var urllove = "ws://" + location.host + "/chatsocketlove";
        var urlthread = "ws://" + location.host + "/chatsocketthread";
        var urlpersonal = "ws://" + location.host + "/chatsocketpersonal";
        updater.socket = new WebSocket(url);
        updater.socketnum = new WebSocket(urlnum);
        updater.socketlove = new WebSocket(urllove);
        updater.socketthread = new WebSocket(urlthread);
        updater.socketpersonal = new WebSocket(urlpersonal);

        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
        updater.socketnum.onmessage = function(event) {
            updater.showNum(JSON.parse(event.data));
        }
        updater.socketlove.onmessage = function(event) {
            updater.showLove(JSON.parse(event.data));
        }
        updater.socketthread.onmessage = function(event) {
            updater.showThread(JSON.parse(event.data));
        }
        updater.socketpersonal.onmessage = function(event) {
            updater.showPersonal(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
        if (message.type == "newress") {
            var existing = $("#m" + message.number);
            if (existing.length > 0) return;
            var node = $(message.html);
            node.hide().prependTo("#messagetable" + message.threadid).slideDown("slow");

            if (message.threadid != "0") {
               commentnum = $("#commentnum" + message.threadid); 
               commentnum.text(message.commentnum + "レス");
            }
        } else {
            var node = $(message.html);
            node.hide().prependTo("#threadlist").slideDown("slow");
            $("#newmessage").get(0).pause();
            $("#newmessage").get(0).currentTime = 0;
            $("#newmessage").get(0).play();
        }
    },
    showNum: function(message) {
        var node = $(message.html);
        $("#num").html(node);
    },
    showLove: function(message) {
        $("#" + message.id + "lovenum").text(message.lovenum );
    },
    showThread: function(message) {
        var node = $(message.html);
        node.hide();
        $("#threadbox").html(node);
        node.slideDown("fast");
        messagekeyenroll();
    },

    showPersonal: function(message) {
        $("#lolv").text(message.lolv);
    },

};


function threadClick(id){
    var message = {
        id: id,
        type: "text"
    };
    updater.socketthread.send(JSON.stringify(message));
}


(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-56678010-16', 'auto');
ga('send', 'pageview');

