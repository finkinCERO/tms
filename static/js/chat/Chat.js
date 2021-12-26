export class Chat {
    constructor(parent, api, address, port, baud) {
        this.parent = parent
        this.api = api
        this.moduleAddress = address
        this.port = port
        this.baud = baud
        this.init()
    }
    init() {
        let settings = this.createSettings()

        let chat = document.createElement("div")
        chat.classList.add("flex-row", "chat", "no-select")
        let menu = document.createElement("div")
        menu.classList.add("chat-menu", "flex-colmn")

        let chatMessages = document.createElement("div")
        chatMessages.classList.add("chat-messages", "flex-colmn")
        chat.appendChild(menu)
        this.createRoutingTable(menu)
        this.createReverseRoutingTable(menu)
        chat.appendChild(chatMessages)
        let messagesIn = document.createElement("div")
        messagesIn.classList.add("chat-messages-in", "flex-colmn")
        let messagesOut = document.createElement("div")
        messagesOut.classList.add("messages-out", "flex-row")


        let targetInput = document.createElement("input")
        this.targetInput = targetInput
        targetInput.placeholder = 'message address'
        targetInput.classList.add("messages-address-input")
        targetInput.addEventListener("change", () => {
            this.verifyAddress()
        })
        targetInput.addEventListener("click", () => {
            if (targetInput.className.includes("messages-address-input-error")) {
                targetInput.classList.remove("messages-address-input-error")
            }
        })


        let textInput = document.createElement("input")
        //this.textInput = textInput
        textInput.classList.add("messages-out-input")
        textInput.placeholder = "send message"

        let sendButton = document.createElement("div")
        sendButton.classList.add("send-button", "flex-colmn-center")
        let sendIcons = document.createElement("i")
        sendIcons.classList.add("send-icon", "far", "fa-paper-plane")
        messagesOut.appendChild(targetInput)
        messagesOut.appendChild(textInput)
        messagesOut.appendChild(sendButton)
        sendButton.appendChild(sendIcons)
        chatMessages.appendChild(messagesIn)
        chatMessages.appendChild(messagesOut)
        this.messagesIn = messagesIn
        this.messageOut = textInput
        sendButton.addEventListener("click", () => {
            if (this.verifyAddress()) {
                this.sendOut(textInput.value, targetInput)
                this.renderMessage(textInput.value, "out", `, <b>message to: ${targetInput.value}</b>`)
                textInput.value = ""
            }


        })
        targetInput.addEventListener("keypress", (event) => {

            if (event.key === 'Enter') sendButton.click()
        })
        textInput.addEventListener("keypress", (event) => {

            if (event.key === 'Enter') sendButton.click()
        })
        this.parent.classList.add("flex-colmn")
        this.parent.appendChild(settings)

        this.parent.appendChild(this.createFunctions())
        this.parent.appendChild(chat)
        this.functionbar = settings
        settings.dispatchEvent(new Event("reset"))
    }
    verifyAddress() {
        let targetInput = this.targetInput
        targetInput.classList.remove("messages-address-input-error")
        targetInput.classList.remove("messages-address-input-aprroved")
        if (targetInput.value == "FFFFF" || targetInput.value == "fffff") {
            targetInput.classList.add("messages-address-input-aprroved")
            return true
        } else {
            try {
                let value = parseInt(targetInput.value)
                if (value.toString() == 'NaN') {
                    targetInput.classList.add("messages-address-input-error")
                    return false
                }
                console.log("value ->", value);
                if (value < 0 || value > 254) {
                    targetInput.classList.add("messages-address-input-error")
                    return false
                }


                targetInput.classList.add("messages-address-input-aprroved")
                return true


            } catch {
                targetInput.classList.add("messages-address-input-error")
                console.log("parse error: address value ")
                return false
            }
        }
    }

    createRoutingTable(parent) {
        let rountingTableWr = document.createElement("div")
        rountingTableWr.classList.add("routing-table-wrapper")
        rountingTableWr.innerHTML = `
        <div class="table-trigger no-select">routing table</div>
        <table class="routing-table">
            <thead class="routing-table-head">
                <tr><th>destination</th><th>next hop</th><th>precursors</th><th>metric</th><th>seq #</th><th>is valid</th></tr>
            </thead>
            <tbody class="routing-table-body">
            </tbody>
        </table>
        `
        parent.appendChild(rountingTableWr)
        this.rountingTableBody = rountingTableWr.getElementsByClassName("routing-table-body")[0]

        this.addTableHide(rountingTableWr)
    }
    createReverseRoutingTable(parent) {
        let rountingTableWr = document.createElement("div")
        rountingTableWr.classList.add("routing-table-wrapper")
        rountingTableWr.innerHTML = `
        <div class="table-trigger no-select">reverse routing table</div>
        <table class="reverse-routing-table">
            <thead class="reverse-routing-table-head">
                <tr><th>destination</th><th>source</th><th>req id</th><th>metric</th><th>prev hop</th></tr>
            </thead>
            <tbody class="reverse-routing-table-body">
            </tbody>
        </table>
        `
        parent.appendChild(rountingTableWr)
        this.reverseRountingTableBody = rountingTableWr.getElementsByClassName("reverse-routing-table-body")[0]
        this.addTableHide(rountingTableWr)
    }

    addTableHide(wrapper) {
        let button = wrapper.getElementsByClassName("table-trigger")[0]
        button.addEventListener("click", () => {
            if (button.nextElementSibling.className.includes("hide")) button.nextElementSibling.classList.remove("hide")
            else button.nextElementSibling.classList.add("hide")
        })
    }
    createFunctions() {
        let settings = document.createElement("div")
        settings.classList.add("chat-functions", "flex-row")

        let clear = document.createElement("div")
        clear.textContent = "clear chat"
        clear.classList.add("button", "clear-button", "ui-button")
        clear.addEventListener("click", () => {
            settings.parentNode.getElementsByClassName("chat-messages-in")[0].innerHTML = ''
        })
        settings.appendChild(clear)
        return settings
    }
    createSettings() {
        let settings = document.createElement("div")
        settings.classList.add("chat-settings", "flex-row")

        let resetWr = document.createElement("div")
        resetWr.classList.add("flex-row", "reset-wrapper")
        let baudtext = document.createElement("div")

        baudtext.classList.add("input-label")
        baudtext.textContent = "baudrate"
        let baud = document.createElement("input")
        baud.type = "number"
        baud.value = this.baud
        baud.classList.add("baud")
        resetWr.appendChild(baudtext)
        resetWr.appendChild(baud)

        let portText = document.createElement("div")
        portText.textContent = "port"

        portText.classList.add("input-label")

        let port = document.createElement("input")
        port.value = this.port
        port.classList.add("port")

        resetWr.appendChild(portText)
        resetWr.appendChild(port)




        let resetButton = document.createElement("div")
        resetButton.textContent = "reset"
        resetButton.classList.add("button", "reset-button", "ui-button")
        resetButton.addEventListener("click", () => {
            this.resetModule(baud.value, port.value)
        })

        resetWr.appendChild(resetButton)


        let configWr = document.createElement("div")
        configWr.classList.add("flex-row", "config-wrapper")

        let configTxt = document.createElement("div")
        configTxt.textContent = "config"


        configTxt.classList.add("input-label")
        let config = document.createElement("input")
        config.classList.add("config")
        config.value = "433000000,5,6,12,4,1,0,0,0,0,3000,8,8"

        let addrText = document.createElement("div")

        addrText.classList.add("input-label")
        addrText.textContent = "address"
        let address = document.createElement("input")
        address.value = this.moduleAddress
        address.classList.add("port")

        configWr.appendChild(addrText)
        configWr.appendChild(address)
        configWr.appendChild(configTxt)
        configWr.appendChild(config)
        let configButton = document.createElement("div")
        configButton.textContent = "set config"
        configButton.classList.add("button", "config-button", "ui-button")
        configButton.addEventListener("click", () => {
            console.log("click config button")
            this.setConfig(config.value, address.value)
        })

        configWr.appendChild(configButton)

        settings.appendChild(resetWr)
        settings.appendChild(configWr)
        settings.addEventListener("reset", () => {
            console.log("event reset module")
            resetButton.click()
        })
        settings.addEventListener("config", () => {
            console.log("event config module")
            configButton.click()
        })
        this.functionbar = settings
        return settings
    }
    renderRoutingTableRows(data) {
        console.log("rows:", data);
        this.rountingTableBody.innerHTML = ""
        for (let i = 0; i < data.length; i++) {
            this.renderRoutingTableRow(this.rountingTableBody, data[i])
        }
    }
    renderRoutingTableRow(parent, data) {
        let row = document.createElement("tr")
        row.innerHTML = `
        <td class="dest-trigger pointer">${data.destination}</td>
        <td>${data.nextHop}</td>
        <td>${data.precursors}</td>
        <td>${data.metric}</td>
        <td>${data.sequenceNumber}</td>
        <td>${data.isValid}</td>
        `
        let trigger = row.getElementsByClassName("dest-trigger")[0]
        trigger.addEventListener("click", () => {
            this.targetInput.value = trigger.textContent
        })

        parent.appendChild(row)
    }
    renderReverseRoutingTableRows(data) {
        this.reverseRountingTableBody.innerHTML = ""
        for (let i = 0; i < data.length; i++) {
            this.renderReverseRoutingTableRow(this.reverseRountingTableBody, data[i])
        }
    }
    renderReverseRoutingTableRow(parent, data) {
        let row = document.createElement("tr")
        row.innerHTML = `
        <td>${data.destination}</td>
        <td>${data.source}</td>
        <td>${data.precursors}</td>
        <td>${data.rreqId}</td>
        <td>${data.metric}</td>
        <td>${data.previousHop}</td>
        `
        parent.appendChild(row)
    }

    setConfig(config, address) {
        let req = {
            name: "set-config",
            config: config,
            address: address
        }

        console.log("set config", req)
        this.api.send(JSON.stringify(req))
    }
    resetModule(baud, port, address) {
        let req = {
            name: "reset-module",
            baud: parseInt(baud),
            port: port
        }
        this.api.send(JSON.stringify(req))
    }
    renderMessage(_msg, _type, suffix) {
        if (_msg == "") return false;
        let box = document.createElement("div")
        box.classList.add("message-wrapper", "flex-colmn")

        let tsW = document.createElement("div")
        tsW.classList.add("message-timestamp-wrapper", "flex-row")

        let ts = document.createElement("div")
        ts.classList.add("message-timestamp")


        let message = document.createElement("div")
        let mText = document.createElement("div")
        switch (_type) {
            case "in":
                message.classList.add("chat-message", "chat-message-in")
                mText.classList.add("message-text", "message-text-in")
                break
            case "system":
                message.classList.add("chat-message", "chat-message-system")
                mText.classList.add("message-text", "message-text-system")
                break
            case "out":
                message.classList.add("chat-message", "chat-message-out")
                mText.classList.add("message-text", "message-text-out")
                break
            default:
                message.classList.add("chat-message")
                mText.classList.add("message-text")
                break
        }
        box.appendChild(tsW)
        tsW.appendChild(ts)

        box.appendChild(message)
        message.appendChild(mText)
        mText.textContent = _msg
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        if (suffix != null)
            ts.innerHTML = new Date().toLocaleDateString("de-DE", options) + " " + new Date().toLocaleTimeString("de-DE") + suffix
        else ts.innerHTML = new Date().toLocaleDateString("de-DE", options) + " " + new Date().toLocaleTimeString("de-DE")
        this.messagesIn.appendChild(box)
        this.scrollDown(this.messagesIn)
        // messagebox(timestamp, message, type(in|out))
    }
    scrollDown(target) {
        target.scrollTop = target.scrollHeight
    }
    sendOut(_msg, target) {
        console.log("msg ->", _msg);

        if (target.className.includes("error") || _msg == "") {
            console.log("request not valid");
            return false
        } else {
            let message = {
                "name": "client-message",
                "message": _msg,
                "destination": target.value
            }
            console.log("# send ->", message);
            this.api.send(JSON.stringify(message))
            return true
        }

    }
}