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
    $(".messageform").off("keypress");
    $(".messageform").on("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });

    $(".youtubeform").off("submit");
    $(".youtubeform").on("submit", function() {
        newMessage($(this));
        return false;
    });
    $(".youtubeform").off("keypress");
    $(".youtubeform").on("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });


    $(".lovemessage").off("click");
    $(".lovemessage").on("click", function() {
        index = Math.floor(Math.random() * lovecomments.length);
        $("form:last").find("input[type=text]").val(lovecomments[index]);
        $("form:last").submit();
        return false;
    });
};

function newMessage(form, threadid) {
    
    var message = form.formToDict();
    var imagefile = "false";
    formid = form.attr("id");

    if(formid.match(/messageform/)) {
        if ($('#image').get(0).files.length === 0) {
            console.log("No files selected.");
        } else {
            var file = document.getElementById('image').files[0];
            updater.socketfile.binaryType = 'arraybuffer';
            var reader = new FileReader();
            var rawData = new ArrayBuffer();
            reader.loadend = function() {
            }
            reader.onload = function(e) {
                rawData = e.target.result;
                updater.socketfile.send(rawData);
                console.log("the File has been transferred.")
            }

            if(formid.match(/messageform/)) {
                message["id"] = formid.replace("messageform", "");
                message["imagefile"] = "true";
                updater.socket.send(JSON.stringify(message));
            }

            reader.readAsArrayBuffer(file);
            imagefile = "true";
        }
    }

    if(formid.match(/messageform/)) {
        message["id"] = formid.replace("messageform", "");
        message["imagefile"] = "false";
        updater.socket.send(JSON.stringify(message));
    }else if(formid.match(/youtubeform/)) {
        message["id"] = formid.replace("youtubeform", "");
        updater.youtubesocket.send(JSON.stringify(message));
    }

    form.find("input[type=file]").val("");
    form.find("input[type=text]").val("").select();
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
        var url = "ws://" + location.host + "/chatsocket";
        var urlyoutube = "ws://" + location.host + "/youtubesocket";
        var urlfile = "ws://" + location.host + "/chatsocketfile";
        var urlnum = "ws://" + location.host + "/chatsocketnum";
        var urllove = "ws://" + location.host + "/chatsocketlove";
        var urlthread = "ws://" + location.host + "/chatsocketthread";
        var urlpersonal = "ws://" + location.host + "/chatsocketpersonal";
        updater.socket = new WebSocket(url);
        updater.youtubesocket = new WebSocket(urlyoutube);
        updater.socketfile = new WebSocket(urlfile);
        updater.socketnum = new WebSocket(urlnum);
        updater.socketlove = new WebSocket(urllove);
        updater.socketthread = new WebSocket(urlthread);
        updater.socketpersonal = new WebSocket(urlpersonal);

        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
        updater.youtubesocket.onmessage = function(event) {
            updater.showImage(JSON.parse(event.data));
        }
        updater.socketfile.onmessage = function(event) {
            updater.showImage(JSON.parse(event.data));
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
        var existing = $("#m" + message.number);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide().prependTo("#messagetable" + message.threadid).slideDown("slow");

        if (message.threadid != "0") {
           commentnum = $("#commentnum" + message.threadid); 
           commentnum.text(message.commentnum + "レス");
        }
    }, 

    showImage: function(message) {
        if ($('#image' + message.id)[0]) {
            var node = $(message.html);
            $('#image' + message.id).html(node);
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
    }

};

function loveClick(id){
    var message = {
        id: id
    }
    updater.socketlove.send(JSON.stringify(message));
}

function imageClick(id){
    loveClick(id)
    var message = {
        id: id,
        type: "image"
    };
    updater.socketthread.send(JSON.stringify(message));
}

function youtubeClick(id){
    loveClick(id)
    var message = {
        id: id,
        type: "youtube",
        imagefile: "false"
    };
    updater.socketthread.send(JSON.stringify(message));
}

function deleteClick(id) {
    var message = {
        id: id,
        delete: 1,
        imagefile: "false"
    };
    updater.socket.send(JSON.stringify(message));
}
function deleteYoutubeClick(id) {
    var message = {
        id: id,
        delete: 1,
        imagefile: "false"
    };
    updater.youtubesocket.send(JSON.stringify(message));
}

var lovecomments = [
    "かわいいな", "あーかわいすぎて鼻血でそう",
    "完全に天使でワロタ", "完全に天使で草生えるwww",
    "もっとみたいなー。ぱんちゅとかみたいなー",
    "これはかわいすぎて犯罪やわ", "女児とセックスしてー。でも我慢やな",
    "かわいい女児さらってみたいわ。でも現実でやると捕まるから我慢＞＜",
    "女子小学生中学生が最高ってはっきり分かるんだよね",
    "女児は肌の張りが違うからな。やっぱりそこがすごいと思うわ",
    "女児ペロペロしたい", "ばばあはやっぱりいらんな。女児やな女児",
    "時代の最先端をいく女児", "この女児を抱いて一日中寝てたいわ",
    "メジャーリーグ級のかわいさの女児やな", "女児わな、国宝やとおもわんか？",
    "今年の流行語は女児かわいすぎてきゃわわきゃわわに決定やな", "女児がかわいすぎてメルトダウンしそうや",
    "女児がかわいすぎて発電とまんない。これじゃ電力過剰供給でせつびこわれちゃうー＞＜", "わい、女児がかわいすぎて震える", "わい、女児に心奪われて胸がドキドキする",
    "こういうかわいい女の子が家にほしいな～", "女児wwwかわゆす",
    "女の子のかわいさは若さから産まれるってわかるな。。ババアは死ね", "早く女児と結婚できる世の中がきますように", "この子にお兄ちゃんって言われてえ・・・",
    "キスしてあげたい", "女児っていうキーワードで興奮する",
    "女児に無理やり乱暴しても許される世の中になりますように",
    "女児とラブラブセックスしても許される世の中になりますように",
    "女児は心に癒しを与えるセラピストだと思うわ",
    "小学校低学年～中学生までがストライクゾーン。これ以外はばばあ",
    "JSJCの写真でご飯3杯食べれるな", "JSJCの魅力で気がついたら画像を見つめて24時間経ってた",
    "女児ってすごい。一家に一台女児だよ",
    "こんなにかわいい女児と恋愛したら犯罪という世の中。頭おかしいのか",
    "女児と恋愛してもいいだろ。こんなにかわいいんだぜ？", "こういう画像見ると女児と恋愛するぐらい許してもいいと思うわ",
    "わりとまじでかわいい女児をイスラム国辺りに送ったら戦争解決できるんじゃない？", "あー女児の手足の細さがいいわ。岩とかけて女児はロック",
    "女児画像祭り誰かしてくれないかなー。ちらっちらっ", "女児のぱんつ生で見てーなー", "JSのパンツかぶりながら永眠してー", "JSのきゃわわな服の匂い嗅ぎながら永眠してー",
    "あー女児脳内麻薬物質がやべー。麻薬所持でつかまるかも",
    "あー女児脳内麻薬物質が足りねーよ。禁断症状でちゃう", "女児の細長い手足に触れてみたいですぞ！", "女児のかわいいお口にキスしてみたいですぞ！",
    "女児のかわいいお口と真剣なお付き合いしてみたい", "そろそろロリコンに目覚めそうやわ", "女児のお家で飼ってほしい",
    "女児 is Cool Japan", "女児といっしょにどこか南の島いきてー", "女児と一日中ベッドでゴロゴロしてー", "女児をかばんにつめていっしょに旅行にいきてー",
    "女児ってかわいいね！", "JSJCと一回だけでいいからキスしたい", "なんでJSJCと付き合っちゃいけないんだよ!こんなにかわいいなじゃにか！",
    "JSJCってのは愛でるもんだと思う。愛でたい", "JSJCと一番触れ合える仕事に就きたい。突き合いたい",
    "JSJCと突き合えるなら1000万ぐらいなら払っちゃう", "昔はこんな子供が嫁にでてたんだよな", "この子のパパになりたい", "もっといろんなところみたい", "もっとJSJCと遊んでおけばよかったな",
    "俺もカメラ買おうかなってこの掲示板で思った", "わい、この掲示板をみてカメラ購入を決意", "JSのぱんつってすごい目を引くよな。なんかなんだろ。なぜか心地よい",
    "JSJCこそがこの日本を救う最後のファクター",
    "JSJCのおぱんちゅ100000000000万円で飼いたいです"
];
 
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-56678010-16', 'auto');
ga('send', 'pageview');

