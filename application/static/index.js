// ---NEW---
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
    // Change the color of the message depending on who sent it
    if (m.author_username == userData.username) {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5 bg-grey">
                            <div class="d-flex">
                                <span class="h6"><strong>You</strong></span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <p class="text-secondary text-break">${m.content}</p>
                        </div>`;
    } else {
        var content =  `<div class="pt-4 pb-2 pl-5 pr-5">
                            <div class="d-flex">
                                <span class="h6">${m.author_username}</span>
                                <span class="h6 font-weight-light pl-3">${m.timestamp}</span>
                            </div>
                            <p class="text-secondary text-break">${m.content}</p>
                        </div>`;
    }
    messageDiv.innerHTML = content;
    messageDiv.scrollIntoView(); // Make sure the message is viewable
}


// Create socket object
var socket = io.connect(document.domain + ":" + location.port);
var userData;
var roomCode;

// Fetch username on connection and send "client connected" event to the server
socket.on("connect", async function () {
    userData = await getUser();
    roomCode = await getRoomCode();
    document.getElementById("username-display").innerText = `Sending messages as ${userData.username}:`;
    if (roomCode == "GLOBAL") {
        document.getElementById("room-code-display").innerText = `Chatting in Global Chat`;
    } else {
        document.getElementById("room-code-display").innerText = `Room Code: ${roomCode}`;
    }
    socket.emit("client connected");
})

// Load all messages to the screen after connecting
socket.on("after connection", async function (data) {
    let messages = data.data;
    messages.forEach(m => {
        if (m.room_code == roomCode) {
            addMessage(m);
        }
    });
})

// Display new message onto the screen when the server sends the message data
socket.on("new message", async function (message) {
    if (message.room_code == roomCode) {
        addMessage(message);
    }
})

// Send a message every time the user clicks the enter key
document.addEventListener("keypress", function (event) {
    if (event.key == "Enter") {
        sendBox = document.getElementById("send-box");
        if (sendBox.value != "") {
            socket.emit("send message", {
                "content": sendBox.value,
                "author_id": userData.user_id,
                "author_username": userData.username,
                "room_code": roomCode
            });
            sendBox.value = "";
        }
    }
});