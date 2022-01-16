import { CONFIG } from "./config/config.js";
import { Chat } from "./chat/Chat.js";
var wss;
var server_obj;
var BODY = document.getElementsByTagName("BODY")[0]
var key;
var usertoken;
var uId; /* Pseudo-Random for identification of client session                */
/* but not the session key!!!   
                                     */

var server = getServer();
var wsServer = `${server.protocoll.match('http://') ? 'ws' : 'wss'}://${server.server}${CONFIG.service}`;
var urlObj;
var chat = null

var socketlink = "ws://localhost:9393/service.py";
var ws;
console.log("socket ->", socketlink);
var diagramManager

var active = false

document.addEventListener("freeze", () => {
    console.log("freezing...");
    FreezeOverlay.render()

})
document.addEventListener("unfreeze", () => {
    console.log("unfreezing...");
    FreezeOverlay.remove()

})

function open_wss() {
    uId = Math.random().toString(36).substring(2) + Date.now().toString(36);
    ws = new WebSocket(socketlink);
    ws.onopen = function (evt) { wss_onopen(evt) };
    ws.onclose = function (evt) { wss_onclose(evt) };
    ws.onmessage = function (evt) { wss_onmessage(evt) };
    ws.onerror = function (evt) { wss_onerror(evt) };
}

function wss_onerror(evt) {
    console.log("wss_onerror => " + evt.data);
}

function wss_onopen(evt) {
    console.log("websocket is open");
    let data = getUrlData()
    var open_session = { name: "init", uId: uId, token: data.token, application: data.application, domain: data.domain };
    ws.send(JSON.stringify(open_session));


}

function wss_onmessage(evt) {
    try {
        let response = JSON.parse(evt.data);
        console.log("response:", response);

        if (response.name == "init") {
            //alert("hello")
            chat = new Chat(BODY, ws, response["address"], response["port"], response["baud"])
            //diagramManager.getData("2020-01-01", "2020-12-07")
        } else if (response.name == "service-message") {
            chat.renderMessage(response.message, "in")
        }

        else if (response.name == "message") {
            console.log("response text:", response.text, "message", response.message)
            if (response.hasOwnProperty("viewType")) {
                if (response.viewType == "default")
                    chat.renderMessage(`last hop node: ${response.prevHopAddress}, destination: ${response.destAddress} | message: ${response.text}`, "in")
                else if (response.default == "bridge")
                    chat.renderMessage(`(bridge) last hop node: ${response.prevHopAddress}, destination: ${response.destAddress} | message: ${response.text}`, "in")
            } else
                if (response.hasOwnProperty("message"))
                    chat.renderMessage(`${response.message}`, "in")
                else
                    chat.renderMessage(`${response.text}`, "in")
        }
        else if (response.name == "set-config")
            chat.renderMessage(`${response.message} ${response.status}`, "system")
        else if (response.name == "reset") {
            chat.renderMessage(`${response.message} ${response.status}`, "system")
            chat.functionbar.dispatchEvent(new Event("config"))
        } else if (response.name == "routing-table") {
            chat.renderRoutingTableRows(response.data)
        } else if (response.name == "reverse-routing-table") {
            chat.renderReverseRoutingTableRows(response.data)
        } else if (response.name == "error") {
            chat.renderMessage(`${response.message}`, "system")
            //chat.functionbar.dispatchEvent(new Event("config"))
        } else if (response.name == "system-message") {
            console.log("# sytem message");
            chat.renderMessage(`${response.message}`, "system")
        }

    } catch (e) {

    }
}

function wss_onclose(evt) {
    //	console.log("wss_onclose => " + evt.data);

    console.log("websocket was closed");
    close_wss();
}

function send_wss(msg) {
    //	console.log("message => " + msg);
    ws.send(msg);
}

function close_wss() {
    ws.close();
}



function getServer(removePort) {
    // end of protocoll (ie: http://)
    var protocollEnd = document.location.href.indexOf('/') + 2;
    var protocoll = document.location.href.substr(0, protocollEnd);

    // server name (or ip) & port (ie: http://localhost:8080)
    var server = document.location.href.substr(protocollEnd,
        document.location.href.substr(protocollEnd).indexOf('/'));

    // remove port
    if (removePort && server.indexOf(':') >= 0) {
        server = server.substr(0, server.indexOf(':'));
    }

    return { protocoll, server };
}
function getUrlData() {


    var currUrl = new URL(window.location.href);
    var user_token = currUrl.searchParams.get('token');
    var user_domain = currUrl.searchParams.get('domain');
    var user_application = currUrl.searchParams.get('application');

    var mode = currUrl.searchParams.get('mode');
    var objId = currUrl.searchParams.get('obj');
    var p = currUrl.searchParams.get('p');
    usertoken = user_token;
    var urlData = {
        'token': user_token,
        'domain': user_domain,
        'application': user_application,
        'mode': mode,
        'obj': objId
    }
    return urlData;
}

function start() {
    //WICHTIG, BEI PRODUKTIV in Config test auf false setzen
    /*load("Verbindung wird hergestellt")
    if (CONFIG.test)
        ws = new WebSocket(socketlink)
    else ws = new WebSocket(wsServer)*/
    ws = new WebSocket(wsServer)
}
//start()
open_wss()