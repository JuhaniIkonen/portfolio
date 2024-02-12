host = "lintutietokantabe.dy.fi"
port = "443"

function createFooter() {
    const page = document.getElementById('page');
    const footer = document.createElement('footer');
    const listItem2 = document.createElement('li');
    listItem2.textContent = 'Sivustoon liittyvissä ongelmatapauksissa ota yhteyttä sivuston tekijään'
    const listItem = document.createElement('li');
    listItem.textContent = '© Juhani Ikonen 2023';


    footer.appendChild(listItem2)
    footer.appendChild(listItem);
    page.appendChild(footer); // Append the footer to the 'page' element
}

function init(){
    createFooter();
    const loggedInUser = document.getElementById('loggedInUser');
        const userName = localStorage.getItem('userName');
      
        if (userName) {
          loggedInUser.textContent += userName;
        }
        
    const logoutButton = document.getElementById('logoutButton');
    logoutButton.addEventListener('click', () => {
      localStorage.removeItem('userName');
      localStorage.removeItem('userId');
      window.location.href = 'index.html';
    });
}

function logged(){
  
document.addEventListener('DOMContentLoaded', () => {
  const userName = localStorage.getItem('userName');
  console.log('logged ladattu ' + userName) 
  if (!userName) {
    window.location.href = 'index.html';
  } else {
    const loggedInUserElement = document.getElementById('loggedInUser');
    if (loggedInUserElement) {
      loggedInUserElement.textContent = `Kirjautuneena: ${userName}`;
    }
  }
  
});
}
async function fetchObservations() {
  try {
    const response = await fetch(`https://${host}:${port}/Lintutietokanta/havainnot`);
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const observations = await response.json();
    return observations;
  } catch (error) {
    console.error('There was a problem fetching observations:', error);
    return [];
  }
}

async function fetchPosts() {
  try {
    const response = await fetch(`https://${host}:${port}/Lintutietokanta/Forum`);
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const observations = await response.json();
    console.log(observations)
    return observations;
  } catch (error) {
    console.error('There was a problem fetching observations:', error);
    return [];
  }
}




// Call the init function when the DOM content is loaded
document.addEventListener('DOMContentLoaded', init);
