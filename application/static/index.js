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

function addMessage (m) {
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
    // Display a delete button for message authors and superusers
    deleteButton = ""
    if (userData.username == m.author_username || userData.user_type == 1) {
        deleteButton = `<button type="button" class="btn btn-outline-danger btn-sm" style="padding: 2px 2px 1px 2px;" onclick="deleteButtonListener(this)">
                            <span class="material-symbols-outlined">delete</span>
                        </button>`
    }
    // Change the color of the message depending on who sent it
    if (m.author_username == userData.username) {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5 bg-grey ${mentionCls}" style="${mentionStyle}" id="msg-${m.msg_id}">
                            <div class="d-inline-flex">
                                <span class="h6"><strong>You</strong></span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <div class="d-inline float-right mt--1 mr--2" id="icons">
                                ${deleteButton}
                            </div>
                            <p class="text-secondary text-break">${m.content}</p>
                        </div>`;
    } else {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5 ${mentionCls}" style="${mentionStyle}" id="msg-${m.msg_id}">
                            <div class="d-inline-flex">
                                <span class="h6">${m.author_username}</span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <div class="d-inline float-right mt--1 mr--2" id="icons">
                                ${deleteButton}
                            </div>
                            <p class="text-secondary text-break">${m.content}</p>
                        </div>`;
    }
    messageDiv.innerHTML = content;
    messageDiv.scrollIntoView(); // Make sure the message is viewable
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


// Create socket object
var socket = io.connect(document.domain + ":" + location.port);
var userData;
var roomCode;

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
    let messages = data.messages;
    messages.forEach(m => {
        if (m.room_code == roomCode) {
            addMessage(m);
        }
    });
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
        addMessage(message);
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
    try {
        msgContainer.querySelector("#icons").remove(); // Remove all icons attached to the message
    } catch (error) {
    }
    msgText = msgContainer.querySelector("p");
    msgText.innerHTML = "<strong>Message Deleted</strong>";
});

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
                "room_code": roomCode
            });
            msgSendBox.value = "";
        }
        
        // Navigate to a new room if the user presses enter while the room code input is active
        else if (roomCodeInput == document.activeElement && roomCodeInput.value != "") {
            this.location.href = "?room_code=" + roomCodeInput.value;
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