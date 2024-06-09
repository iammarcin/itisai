export default function authHeader() {
  const user = 1; // JSON.parse(localStorage.getItem('user'));
  if (user) { // && user.value.accessToken) {
    // for Node.js Express back-end
    //return { 'x-access-token': user.value.accessToken };
    // for fastapi
    console.log("process.env.MY_AUTH_TOKEN")
    console.log(process.env.MY_AUTH_TOKEN)
    return { Authorization: 'Bearer ' + process.env.MY_AUTH_TOKEN };
  } else {
    return {};
  }
}
