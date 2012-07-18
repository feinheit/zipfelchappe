/* Modernizr custom build of 1.7: csstransitions | hashchange | history */
;window.Modernizr=function(a,b,c){function G(){}function F(a,b){var c=a.charAt(0).toUpperCase()+a.substr(1),d=(a+" "+p.join(c+" ")+c).split(" ");return!!E(d,b)}function E(a,b){for(var d in a)if(k[a[d]]!==c&&(!b||b(a[d],j)))return!0}function D(a,b){return(""+a).indexOf(b)!==-1}function C(a,b){return typeof a===b}function B(a,b){return A(o.join(a+";")+(b||""))}function A(a){k.cssText=a}var d="1.7",e={},f=!0,g=b.documentElement,h=b.head||b.getElementsByTagName("head")[0],i="modernizr",j=b.createElement(i),k=j.style,l=b.createElement("input"),m=":)",n=Object.prototype.toString,o=" -webkit- -moz- -o- -ms- -khtml- ".split(" "),p="Webkit Moz O ms Khtml".split(" "),q={svg:"http://www.w3.org/2000/svg"},r={},s={},t={},u=[],v,w=function(a){var c=b.createElement("style"),d=b.createElement("div"),e;c.textContent=a+"{#modernizr{height:3px}}",h.appendChild(c),d.id="modernizr",g.appendChild(d),e=d.offsetHeight===3,c.parentNode.removeChild(c),d.parentNode.removeChild(d);return!!e},x=function(){function d(d,e){e=e||b.createElement(a[d]||"div");var f=(d="on"+d)in e;f||(e.setAttribute||(e=b.createElement("div")),e.setAttribute&&e.removeAttribute&&(e.setAttribute(d,""),f=C(e[d],"function"),C(e[d],c)||(e[d]=c),e.removeAttribute(d))),e=null;return f}var a={select:"input",change:"input",submit:"form",reset:"form",error:"img",load:"img",abort:"img"};return d}(),y=({}).hasOwnProperty,z;C(y,c)||C(y.call,c)?z=function(a,b){return b in a&&C(a.constructor.prototype[b],c)}:z=function(a,b){return y.call(a,b)},r.hashchange=function(){return x("hashchange",a)&&(b.documentMode===c||b.documentMode>7)},r.history=function(){return !!(a.history&&history.pushState)},r.csstransitions=function(){return F("transitionProperty")};for(var H in r)z(r,H)&&(v=H.toLowerCase(),e[v]=r[H](),u.push((e[v]?"":"no-")+v));e.input||G(),e.crosswindowmessaging=e.postmessage,e.historymanagement=e.history,e.addTest=function(a,b){a=a.toLowerCase();if(!e[a]){b=!!b(),g.className+=" "+(b?"":"no-")+a,e[a]=b;return e}},A(""),j=l=null,e._enableHTML5=f,e._version=d,g.className=g.className.replace(/\bno-js\b/,"")+" js "+u.join(" ");return e}(this,this.document);


// TODO use something else
var el = document.getElementsByTagName('html')[0];
var supports = {
    hashchange: el.className.indexOf('no-hashchange') == -1,
    history: el.className.indexOf('no-history') == -1,
    transitions: el.className.indexOf('no-csstransitions') == -1
    };


var FH = {
    on_document_ready: function () {
        /*
        if (supports.transitions) {
            $('.slides').moodboard({slide_time: 4000});
        } else {
            var $slides = $('.slides');
            $slides.moodboard({
                slide_time: 4000,
                _reveal: function($mb, data, newidx) {
                    data.slides[data.current].css({'z-index': 100}).animate({opacity: 0}, 800);
                    data.slides[newidx].css({'z-index': 101}).animate({opacity: 1}, 800, function() {
                        data.slides[newidx][0].style.removeAttribute('filter');
                    });
                    data.current = newidx;
                }
            });
        }
        */

        if (!supports.transitions) {
            // move div behind img, so that missing cleartext support in IE CSS
            // filters does not produce ugly artifacts
            $('.flip div').show().css('z-index', 99);
            $('.flip img').css('position', 'absolute').show().css('z-index', 110);

            // hide image instead of revealing colored layer on mouseover
            $('.flip').hover(function() {
                $('img', this).stop(true, true).animate({opacity:0.1}, 'fast');
            }, function() {
                $('img', this).stop(true, true).animate({opacity:1});
            });
        }

        $('a.facebox').facebox();
    },

    on_anchor_click: function(event) {
        event.preventDefault();

        var $elem = $('a[name=' + this.getAttribute('href').substr(1) + ']');
        if (!$elem.length)
            return true;

        var pos = $(window).scrollTop(), newpos = Math.max(0, $elem.offset().top - 50);
        var duration = Math.abs(newpos - pos) / 0.7;

        // html works in firefox, body in chrome... TODO test other browsers
        $('html, body').animate({scrollTop: newpos}, duration);

        if (this.getAttribute('href') == '#bottom') {
            setTimeout(function() {
                $('#footer').css('background', '#ffffff');
                setTimeout(function() {
                    $('#footer').css('background', '#e8f4f5');
                }, 500);
            }, duration / 3);
        }

        return false;
    },

    history_load: function(href) {
        $.get(href, function(data) {
            var elements = ['#navigation', '#moodboard', '#content'];

            // $data.filter('title').text() does not work in Safari... yay!
            document.title = data.match(/<title>([^<]*)/i)[1];

            var $data = $(data);

            $('#navigation').html($data.find('#navigation').html());
            $('#maincontent').hide().html($data.filter('#maincontent').html()).fadeIn();

            FH.on_document_ready();
        });
    },

    init_html5_history: function() {
        if (!supports.history)
            return;

        $('body').delegate('a', 'click', function() {
            if (this.href.indexOf(window.location.host) == -1 || this.href.indexOf('#') != -1)
                return true;

            FH.history_load(this.href);
            history.pushState({path: this.path}, '', this.href);

            return false;
        });

        $(window).bind('popstate', function() {
            FH.history_load(location.href);
        });
    }
};


var Parallax = {
    x_offset: function() {
        return window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft;
    },
    y_offset: function() {
        return window.pageYOffset || document.documentElement.scrollTop  || document.body.scrollTop;
    },
    init: function() {
        Parallax.x_start = Parallax.x_offset();
        Parallax.y_start = Parallax.y_offset();
        Parallax.layers = [
            document.getElementsByTagName('body')[0],
            document.getElementById('bg')
            ];
        Parallax.multipliers = [
            1.9 / 10.0,
            4.7 / 10.0
            ];
        Parallax.layers[0].style.backgroundAttachment = 'fixed';
        Parallax.layers[1].style.backgroundAttachment = 'fixed';
    },
    on_scroll: function() {
        var offset = Parallax.y_offset();
        Parallax.layers[0].style.backgroundPosition = 'center -' + (offset * Parallax.multipliers[0]) + 'px';
        Parallax.layers[1].style.backgroundPosition = 'center -' + (offset * Parallax.multipliers[1]) + 'px';
    }
};


var Dialog = {
    init: function() {
        $(document).bind('reveal.facebox', Dialog.on_reveal);

        $('#si-newsletter').bind('click', function() {
            Dialog.open(this.href);
            return false;
        });
    },

    open: function(url) {
        $.facebox({ajax: url});
    },

    first_run: true,
    on_reveal: function() {
        var $facebox = $('#facebox'),
            $form = $facebox.find('form');

        if (Dialog.first_run) {
            $facebox.delegate('a', 'click', function() {
                $.get(this.href, $.facebox);
                return false;
            });
            Dialog.first_run = false;
        }

        $form.bind('submit', function() {
            $.post(this.action, $form.serialize(), $.facebox);
            return false;
        });
    }
};


$(function() {
    // catch all anchor links
    $('body').delegate('a[href^=#]', 'click', FH.on_anchor_click);

    //FH.init_html5_history();
    FH.on_document_ready();

    Parallax.init();
    Dialog.init();
    $(window).bind('scroll', Parallax.on_scroll);
});
