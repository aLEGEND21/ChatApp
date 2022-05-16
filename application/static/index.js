async function getUser () {
    return await fetch("/api/get_user")
        .then(async function (resp) {
            return await resp.json();
        });
}

async function getRoomCode () {
    return await fetch("/api/get_room_code")
        .then(async function (resp) {
            return await resp.json();
        })
        .then(function (data) {
            return data["room_code"]
        });
}

async function getMessageById (msgId) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/api/get_message_by_id/" + msgId, false ); // false for synchronous request
    xmlHttp.send( null );
    return JSON.parse(xmlHttp.responseText);
    /*return await fetch("/api/get_message_by_id/" + msgId)
        .then(async function (resp) {
            return await resp.json();
        });*/ // Messages do not scroll into view
}

async function addMessage (m, loadingMessages) {
    let messageContainer = document.getElementById("message-container");
    let messageDiv = document.createElement("div");
    messageContainer.appendChild(messageDiv);
    // Make the message border yellow if the user is being mentioned in it
    mentionCls = ""
    mentionStyle = "border-width: 4px !important; border-color: transparent !important;"
    if (m.content.toLowerCase().includes("@" + userData.username.toLowerCase()) || m.content.toLowerCase().includes("@everyone")) {
        mentionCls = "border-left";
        mentionStyle = "border-width: 4px !important; border-color: var(--blue-green) !important;";
    }
    // Display the buttons for message authors and superusers
    buttons = `
        <button type="button" class="btn btn-outline-secondary btn-sm" style="padding: 1px 1px 0px 1px;" onclick="replyButtonListener(this)">
            <span class="material-symbols-outlined">reply</span>
        </button>
    `
    if (userData.username == m.author_username || userData.user_type == 1) {
        buttons = buttons + `
            <button type="button" class="btn btn-outline-secondary btn-sm" style="padding: 1px 1px 0px 1px;" onclick="editButtonListener(this)">
                <span class="material-symbols-outlined">edit</span>
            </button>
            <button type="button" class="btn btn-outline-danger btn-sm" style="padding: 1px 1px 0px 1px;" onclick="deleteButtonListener(this)">
                <span class="material-symbols-outlined">delete</span>
            </button>
        `
    }
    // Add the message being replied to if the user is replying to a message
    reply = ""
    if (m.replying_to != 0) {
        replyTargetMsg = await getMessageById(m.replying_to);
        if (replyTargetMsg.content != undefined) {
            reply = `
                <div class="text-secondary text-truncate mt--1 ml--3 mb-1 mr-5 pl-5">
                    <span><strong>${replyTargetMsg.author_username}</strong></span>
                    <span class="font-weight-light text-truncate">${replyTargetMsg.content}</span>
                </div>
            `
        }
    }
    // Change the color of the message depending on who sent it
    if (m.author_username == userData.username) {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5 bg-grey ${mentionCls}" style="${mentionStyle}" id="msg-${m.msg_id}">
                            ${reply}
                            <div class="d-inline-flex">
                                <span class="h6"><strong>You</strong></span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <div class="d-inline float-right mr--2" id="icons">
                                ${buttons}
                            </div>
                            <p class="text-secondary text-break" id="content">${m.content}</p>
                        </div>`;
    } else {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5 ${mentionCls}" style="${mentionStyle}" id="msg-${m.msg_id}">
                            ${reply}
                            <div class="d-inline-flex pr-1">
                                <span class="h6">${m.author_username}</span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <div class="d-inline float-right mr--2" id="icons">
                                ${buttons}
                            </div>
                            <p class="text-secondary text-break" id="content">${m.content}</p>
                        </div>`;
    }
    messageDiv.innerHTML = content;
    // Display a notification to the user if they are not on the site when a message is sent
    if (document.hidden && loadingMessages == false && notified == false) {
        if (Notification.permission != 'granted') {
            Notification.requestPermission();
        } else {
            var notification = new Notification(`New Message From ${m.author_username}`, {
                body: m.content
            });
            notified = true;
        }
    } else if (!(document.hidden)) {
        notified = false; // Reset notified back to false
    }
    messageDiv.scrollIntoView();
    // Scroll down to the lowest message unless the user is trying to scroll up
    //let scrollPercent = (messageContainer.scrollTop / (messageContainer.scrollHeight - messageContainer.clientHeight)) * 100;
    /*let scrollPercent = (messageContainer.scrollTop + messageContainer.clientHeight) / messageContainer.scrollHeight * 100;
    if (scrollPercent > 90) {
        messageDiv.scrollIntoView(); // Make sure the message is viewable
    }
    console.log(scrollPercent);*/
    // TODO: ^ Make this display the number of messages unread while a user is reading other messages
    // This should be done by using a global var and then showing/hiding a floating element while updating it with the number of missed messages
    // Toggle whether the unread-messages should be seen: https://stackoverflow.com/questions/18568736/how-to-hide-element-using-twitter-bootstrap-and-show-it-using-jquery
    // Update the number of unread messages every time a message is sent
    // Figure out why the thing that shows unread messages prevents scrolling
    // Figure out why the proportion is different on the live site
    // Percentages are different when site is reloaded
}

// Add a room code to the list of public room codes on the screen
function addPublicRoomCode (code) {
    let publicRoomsContainer = document.getElementById("public-rooms-container");
    // Check whether the room code is already displayed. If it is, then do not add another copy of it to the screen.
    if (!(document.getElementById(`room-code-${code}`) == null)) {
        return;
    }
    // Create the element containing the room code and set its attributes
    let roomCodeContainer = document.createElement("a");
    roomCodeContainer.setAttribute("href", `/?room_code=${code}`);
    roomCodeContainer.setAttribute("class", "list-group-item list-group-item-action");
    roomCodeContainer.setAttribute("id", `room-code-${code}`);
    roomCodeContainer.innerText = code;
    publicRoomsContainer.append(roomCodeContainer);
}

// Handles the sending of the socket event when the nsg edit is confirmed
function editConfirmed (msgContainer) {
    // Get all the data related to the message being edited
    let msgEditInput = msgContainer.querySelector("#edit-msg-input");
    let msgId = msgContainer.getAttribute("id").split("-")[1];
    let oldContent = msgContainer.children["content"].innerText;
    let newContent = msgEditInput.value;
    // Remove the message editing UI and show the hidden old content
    msgEditInput.remove();
    $(msgContainer.children["content"]).removeClass("d-none");
    /*let msgContent = document.createElement("p"); // TODO See why this doesn't show the edit
    $(msgContent).attr({
        class: "text-secondary text-break",
        id: "content"
    });
    $(msgContent).val(newContent);
    console.log(newContent);
    msgContainer.appendChild(msgContent);*/
    // Emit the socket event
    socket.emit("on message edit", {
        msg_id: msgId,
        old_content: oldContent,
        new_content: newContent
    });
}


// Create socket object
var socket = io.connect(document.domain + ":" + location.port);
var userData;
var roomCode;
var notified = false; // Shows whether the user has been already been notified about a new message
var replyingTo = 0; // 0 is used if the user is not replying to a message while the message id is used if the user is replying to a message

// Create global roomStatus html object
var roomStatus = document.createElement("button");
roomStatus.setAttribute("class", "align-self-center btn badge badge-pill");
roomStatus.setAttribute("style", "background-color: var(--blue-green)");
roomStatus.setAttribute("onclick", "roomStatusToggleListener(this)");

// Fetch username on connection and send "client connected" event to the server
socket.on("connect", async function () {
    userData = await getUser();
    roomCode = await getRoomCode();
    document.getElementById("username-display").innerText = `Sending messages as ${userData.username}:`;
    let roomCodeDisplay = document.getElementById("room-code-display");
    if (roomCode == "GLOBAL") {
        roomCodeDisplay.innerText = `Chatting in Global Chat `;
    } else {
        roomCodeDisplay.innerText = `Room Code: ${roomCode} `;
    }
    roomCodeDisplay.appendChild(roomStatus);
    socket.emit("client connected");
})

// Load all messages to the screen after connecting
socket.on("after connection", async function (data) {
    // Add all the messages to the screen and scroll to the bottom
    let messages = data.messages;
    messages.forEach(async (m) => {
        if (m.room_code == roomCode) {
            await addMessage(m, true);
        }
    });
    let messageContainer = document.getElementById("message-container");
    messageContainer.scrollTop = messageContainer.scrollHeight; // Needed because auto-scroll doesn't work when loading messages
    // Update the public room display
    let publicRoomCodes = data.public_rooms;
    publicRoomCodes.forEach(c => addPublicRoomCode(c));
    // Update the room status display 
    if (publicRoomCodes.includes(roomCode) || roomCode == "GLOBAL") {
        roomStatus.innerText = "Public";
    } else {
        roomStatus.innerText = "Private";
    }
})

// Display new message onto the screen when the server sends the message data
socket.on("new message", async function (message) {
    if (message.room_code == roomCode) {
        await addMessage(message, false);
    }
})

socket.on("room status changed", async function (data) {
    // Update the status button if the room being updated is the room the client is in
    if (data.room_code == roomCode) {
        roomStatus.innerText = data.action;
    }
    // Display the room code on the list of public room codes if the room was changed to public
    if (data.action == "Public") {
        addPublicRoomCode(data.room_code);
    }
    // Remove the room code from the list of public room codes if ti was changed to private
    else if (data.action == "Private") {
        document.getElementById(`room-code-${data.room_code}`).remove();
    }
})

socket.on("message deleted", async function (data) {
    // Edit the message to say that the message was deleted
    msgContainer = document.getElementById(`msg-${data.msg_id}`);
    // Remove all icons attached to the message
    try {
        msgContainer.querySelector("#icons").remove();
    } catch (error) {
    }
    // If the user is in the edit message UI, remove the edit UI and make the message content visible again
    try {
        msgContainer.querySelector("#edit-msg-input").remove();
        $(msgContainer.querySelector("#content")).removeClass("d-none");
    } catch (error) {
    }
    msgText = msgContainer.querySelector("p");
    msgText.innerHTML = "<strong>Message Deleted</strong>";
});

socket.on("message edited", async function (data) {
    // Edit the existing msgContent element to have the new message content
    msgContainer = document.getElementById(`msg-${data.msg_id}`);
    msgContent = msgContainer.children["content"];
    msgContent.innerHTML = data.new_content;
})

// Add a listener to perform an event every time the user presses the enter key
document.addEventListener("keypress", function (event) {
    if (event.key == "Enter") {
        msgSendBox = document.getElementById("message-send-box");
        roomCodeInput = document.getElementById("room-code-input");

        // Send a message if the user presses enter while the message send box is active
        if (msgSendBox == document.activeElement && msgSendBox.value != "") {
            socket.emit("send message", {
                "content": msgSendBox.value,
                "author_id": userData.user_id,
                "author_username": userData.username,
                "room_code": roomCode,
                "replying_to": replyingTo
            });
            msgSendBox.value = "";
            replyingTo = 0;
        }
        
        // Navigate to a new room if the user presses enter while the room code input is active
        else if (roomCodeInput == document.activeElement && roomCodeInput.value != "") {
            this.location.href = "?room_code=" + roomCodeInput.value;
        }

        // Run the edit confimed function if enter is clicked with a message edit box active
        else if (document.activeElement.getAttribute("id") == "edit-msg-input") {
            editConfirmed(document.activeElement.parentElement);
        }
    }
});

// Listen to the user clicking on the room status button and tell the server the updated status
function roomStatusToggleListener (statusDisplay) {
    if (userData.user_type == 1 && !(roomCode == "GLOBAL")) {
        data = {
            room_code: roomCode
        }
        // Update the data based on whether the room is being changed from public to private or vice versa
        if (statusDisplay.innerText == "Public") {
            data.action = "Private";
        }
        else if (statusDisplay.innerText == "Private") {
            data.action = "Public";
        }
        socket.emit("room status update", data);
    }
}

// Listen to when the reply button is pressed and show the reply UI
function replyButtonListener (btn) {
    let targetMsgContainer = btn.parentElement.parentElement;
    let targetMsgId = targetMsgContainer.getAttribute("id").split("-")[1];
    replyingTo = targetMsgId;
    document.getElementById("message-send-box").focus(); // All the user to start replying immediately
    // TODO: Show the message editing UI
    // Also, when a message is edited, make the messages that are replying to it have their quote from the edited message edited
    // This means that there needs to be some class that replying messages have
}

// Listen to when the edit button is clicked on a message and edit the UI so that the user can edit the message
function editButtonListener (btn) {
    /*let msgContainer = btn.parentElement.parentElement;
    let msgId = msgContainer.getAttribute("id").split("-")[1];
    let oldContent = msgContainer.children["content"].innerText;*/
    // TODO: ^ Move this to an enter button listener where this data is retrieved when the user confirms the edit
    // Hide the message content
    let msgContainer = btn.parentElement.parentElement;
    // Do not allow the user to edit the message if the edit UI is already being displayed
    if (msgContainer.children["edit-msg-input"] != undefined) {
        return;
    }
    $(msgContainer.children["content"]).addClass("d-none");
    // Add an input element to the message body which the user can type in
    editInput = document.createElement("input");
    $(editInput).attr({
        type: "text",
        class: "form-control",
        id: "edit-msg-input",
        autocomplete: "off",
        style: "background-color: rgba(240,240,240,10); width: 95%;"
    });
    $(editInput).val(msgContainer.children["content"].innerText.replace(" (edited)", "")); // Remove "(edited)" message from string
    msgContainer.appendChild(editInput);
    editInput.focus();
    // Add an edit confimed button
    /*editConfirmButton = document.createElement("button");
    $(editConfirmButton).attr({
        class: "btn bg-blue-green",
        onclick: "editConfirmed(this.parentElement)",
    });
    editConfirmButton.innerText = "Edit";
    msgContainer.appendChild(editConfirmButton);*/
}

// Listen to when the delete button is clicked on a message and emit an "on message delete" event
function deleteButtonListener (btn) {
    // Retrive the msg id from the id of the parent of the parent of the button
    let msgContainer = btn.parentElement.parentElement;
    let msgId = msgContainer.getAttribute("id").split("-")[1];
    // Emit the event to the server that the message was deleted
    socket.emit("on message delete", {
        msg_id: msgId
    });
}