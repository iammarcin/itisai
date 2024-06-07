export default function authHeader() {
  const user = 1; // JSON.parse(localStorage.getItem('user'));
  if (user && user.value.accessToken) {
    // for Node.js Express back-end
    return { 'x-access-token': user.value.accessToken };
    // for fastapi
    //return { Authorization: 'Bearer ' + user.accessToken };
  } else {
    return {};
  }
}
