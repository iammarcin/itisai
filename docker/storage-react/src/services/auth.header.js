export default function authHeader() {
  const user = 1; // JSON.parse(localStorage.getItem('user'));
  if (user) { // && user.value.accessToken) {
    // for Node.js Express back-end
    //return { 'x-access-token': user.value.accessToken };
    // for fastapi
    // get token
    const authToken = JSON.parse(localStorage.getItem('authToken'));

    return { Authorization: authToken && authToken.token ? 'Bearer ' + authToken.token : '' };
  } else {
    return {};
  }
}
