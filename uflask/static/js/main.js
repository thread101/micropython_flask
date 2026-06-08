const BASE = document.location.origin;

async function action(act) {
  let url = BASE + "/?" + act;
  console.log(url);
  // const resp = await fetch(url);
  // const data = await resp.json();
  // console.log(data);
}