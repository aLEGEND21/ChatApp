function toggleRoomCode () {
    select_room_type = document.getElementById("select_room_type");
    room_code_input = document.getElementById("room_code_input");
    if (select_room_type.checked) {
        room_code_input.setAttribute("type", "text");
    } else {
        room_code_input.setAttribute("type", "hidden");
    }
}