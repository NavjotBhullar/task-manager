let user = localStorage.getItem("username");

if (!user) {
  window.location.href = "/";
}

document.getElementById("loggedUser").innerText = user;
document.getElementById("avatar").innerText = user.charAt(0).toUpperCase();

let socket = new WebSocket(`ws://127.0.0.1:8000/ws/${user}`);

let selectedUser = null;
let selectedGroup = null;
let currentGroupMembers = [];
let groupAdmin = null;

socket.onmessage = function (event) {
  let data = JSON.parse(event.data);

  if (selectedUser) {
    if (data.sender === selectedUser || data.receiver === selectedUser) {
      addMessage(data.sender, data.content);
    }
  }

  if (selectedGroup) {
    if (data.group === selectedGroup) {
      addMessage(data.sender, data.content);
    }
  }
};

function logout() {
  localStorage.removeItem("username");
  window.location.href = "/";
}

async function loadUsers() {
  let res = await fetch("/users");
  let users = await res.json();

  let container = document.getElementById("users");
  container.innerHTML = "";

  users.forEach((u) => {
    if (u.username === user) return;

    let div = document.createElement("div");
    div.className = "user";
    div.innerText = u.username;

    div.onclick = async () => {
      selectedUser = u.username;
      selectedGroup = null;

      document.getElementById("group-actions").classList.add("hidden");

      document.getElementById("chat-header").innerText =
        "Chat with " + selectedUser;

      document.getElementById("messages").innerHTML = "";

      document
        .querySelectorAll(".user, .group")
        .forEach((el) => el.classList.remove("active"));

      div.classList.add("active");

      let res = await fetch(
        `/messages/history?user1=${user}&user2=${selectedUser}`,
      );

      let chats = await res.json();

      chats.forEach((msg) => {
        addMessage(msg.sender, msg.content);
      });
    };

    container.appendChild(div);
  });
}

async function loadGroups() {
  let res = await fetch("/groups");
  let groups = await res.json();

  let container = document.getElementById("groups");
  container.innerHTML = "";

  groups.forEach((g) => {
    if (!g.members.includes(user)) return;

    let div = document.createElement("div");
    div.className = "group";
    div.innerText = "👥 " + g.name;

    div.onclick = async () => {
      selectedGroup = g.name;
      selectedUser = null;
      currentGroupMembers = [...g.members];
      groupAdmin = g.admin || g.members[0];

      document.getElementById("chat-header").innerText =
        "Group: " + selectedGroup;

      document.getElementById("messages").innerHTML = "";

      document
        .querySelectorAll(".user, .group")
        .forEach((el) => el.classList.remove("active"));

      div.classList.add("active");

      document.getElementById("group-actions").classList.remove("hidden");
      document.getElementById("group-name").innerText = selectedGroup;

      let res = await fetch(`/messages/group/${selectedGroup}`);
      let chats = await res.json();

      chats.forEach((msg) => {
        addMessage(msg.sender, msg.content);
      });
    };

    container.appendChild(div);
  });
}

function toggleMembersDropdown() {
  const dropdown = document.getElementById("membersDropdown");

  dropdown.classList.toggle("hidden");

  if (!dropdown.classList.contains("hidden")) {
    renderMembersDropdown();
  }
}

function renderMembersDropdown() {
  const dropdown = document.getElementById("membersDropdown");
  dropdown.innerHTML = "";

  currentGroupMembers.forEach((member) => {
    const div = document.createElement("div");
    div.className = "member-row";

    let isAdmin = member === groupAdmin;

    div.innerHTML = `
      <span class="member-name">
        ${member} ${isAdmin ? '<span class="admin-badge">Admin</span>' : ""}
      </span>

      ${
        !isAdmin
          ? `<button class="remove-btn" onclick="removeMember('${member}')">×</button>`
          : ""
      }
    `;

    dropdown.appendChild(div);
  });
}

async function addMember() {
  const newMember = document.getElementById("newMember").value.trim();
  if (!newMember) return;

  await fetch("/groups/add-member", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group: selectedGroup,
      member: newMember,
    }),
  });

  currentGroupMembers.push(newMember);

  renderMembersDropdown();

  document.getElementById("newMember").value = "";
}

async function removeMember(member) {
  await fetch("/groups/remove-member", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group: selectedGroup,
      member: member,
    }),
  });

  currentGroupMembers = currentGroupMembers.filter((m) => m !== member);

  renderMembersDropdown();
}

function addMessage(sender, msg) {
  let div = document.createElement("div");
  div.className = "message " + (sender === user ? "sent" : "received");
  div.innerText = sender + ": " + msg;

  let messagesDiv = document.getElementById("messages");
  messagesDiv.appendChild(div);

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
  let input = document.getElementById("messageInput");
  let msg = input.value;

  if (!msg.trim()) return;

  if (selectedUser) {
    socket.send(
      JSON.stringify({
        sender: user,
        receiver: selectedUser,
        content: msg,
      }),
    );

    await fetch(`/messages/?sender=${user}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        receiver: selectedUser,
        content: msg,
      }),
    });
  } else if (selectedGroup) {
    socket.send(
      JSON.stringify({
        sender: user,
        group: selectedGroup,
        content: msg,
      }),
    );

    await fetch(`/messages/group?sender=${user}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        group: selectedGroup,
        content: msg,
      }),
    });
  }

  addMessage(user, msg);
  input.value = "";
}

loadUsers();
loadGroups();
