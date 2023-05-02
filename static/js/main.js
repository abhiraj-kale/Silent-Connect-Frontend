let header_join_btn = document.getElementById("header_join_btn")
let join_meeting_input = document.getElementById("join_meeting_input");
let meet_join_btn = document.getElementById("meet_join_btn");

header_join_btn.addEventListener("click", function(e) {
    join_meeting_input.focus();
})
meet_join_btn.addEventListener("click", function(e){
    window.location.href = header_join_btn.value;
})
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

let create_meet_btn = document.getElementById("create_meet_btn");
create_meet_btn.addEventListener("click", function(e){
    let uuid = uuidv4();
    window.location.href = "/room/"+uuid;
})