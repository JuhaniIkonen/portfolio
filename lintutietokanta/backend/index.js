const fs = require('fs')
const express = require('express') 
const session = require('express-session')
const MemoryStore = require('memorystore')(session);
const cors = require('cors')

const app = express()
const port = 3000

// cors - allow connection from different domains and ports
app.use(cors())

// Use express-session middleware
app.use(session({
  secret: 'yourSecretKey',
  resave: false,
  saveUninitialized: false,
  store: new MemoryStore({
    checkPeriod: 86400000 // Pruning interval in milliseconds (optional)
  })
}));


// convert json string to json object (from request)
app.use(express.json())

const mongoose = require('mongoose')
const { timeStamp } = require('console')
const mongoDB = 'Tässä on linkki ja kirjautuminen mun MongoDB:hen'
mongoose.connect(mongoDB)

const db = mongoose.connection
db.on('error', console.error.bind(console, 'connection error:'))
db.once('open', function() {
  console.log("Database Lintutietokanta connected")
})

// Schemas
const users = new mongoose.Schema({
    name: String,
    email: String
  })

const havainnot = new mongoose.Schema({
    laji: { type: String, require: true},
    lkm: {type: Number},
    havaintotyyppi: {type: String},
    havaitsija: { type: String, require: true},
    havaintopaikka: { type: String},
    lisätieto: {type: String},
    havaintoaika: {type: String},
    havaintomaa: {type: String}
  })

const forum = new mongoose.Schema({
  poster: {type: String},
  text: {type: String},
  timestamp: {type: String}
})

// Model
const Havainto = mongoose.model('Havainto', havainnot, 'havainnot')
const User = mongoose.model('User', users, 'users')
const Forum = mongoose.model('ForumPost', forum, 'Forum')

// Functions
function getDate(){
    const timestamp = Date.now(); // Get current timestamp in milliseconds
    const date = new Date(timestamp); // Create a Date object from the timestamp

    const day = date.getDate().toString().padStart(2, '0'); // Get the day and format it with leading zero if needed
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Get the month and format it
    const year = date.getFullYear(); // Get the full year

    const hours = date.getHours().toString().padStart(2, '0'); // Get the hours and format it
    const minutes = date.getMinutes().toString().padStart(2, '0'); // Get the minutes and format it
    const seconds = date.getSeconds().toString().padStart(2, '0'); // Get the seconds and format it

    const formattedDateTime = `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`; // Combine date and time in the desired format
return formattedDateTime
}

// Routes /Lintutietokanta/users LOGIN
app.post('/Lintutietokanta/users', async (req, res) => {
  const { name, password } = req.body;
  console.log(name);
  console.log(password);
  
  const user = await User.findOne({ userID: name, salasana: password});

  if (user) {
  
    req.session.isLoggedIn = true;
    req.session.userId = user._id;
    req.session.userName = user.get('nimi');

    // Sending user data as a response to the frontend upon successful login
    res.status(200).json({
      userId: user._id,
      userName: user.get('nimi'),
  
      message: 'Login successful' // You can add any other relevant data or message
    });
  } else {
    console.log('Kirjautuminen epäonnistui');
    res.status(401).json({ message: 'Login failed' });
  }
});

app.get('/logout', (req, res) => {
  req.session.destroy(err => {
    if (err) {
      console.error('Error destroying session:', err);
      res.status(500).send('Error logging out');
    } else {
      res.clearCookie('connect.sid'); // Clear session cookie (if using express-session)

      // Redirect to a different page or send a success response
      res.status(200).send('Logged out successfully');
    }
  });
});



// Routes /Lintutietokanta/havainnot/
app.get('/Lintutietokanta/havainnot', async (request, response) => {
    const havainnot = await Havainto.find({})
    response.json(havainnot)
  })

app.post('/Lintutietokanta/havainnot/', async (request, response) => {
    const { laji } = request.body
    const { lkm } = request.body
    const { havaintotyyppi } = request.body
    const { havaitsija } = request.body
    const { lisätieto } = request.body
    const { havaintopaikka } = request.body
    const { havaintomaa } = request.body
    const havaintoaika = getDate()

    const havainto = new Havainto({
      laji: laji,
      lkm: lkm,
      havaintotyyppi: havaintotyyppi,
      havaitsija: havaitsija,
      lisätieto: lisätieto,
      havaintopaikka: havaintopaikka,
      havaintoaika: havaintoaika,
      havaintomaa: havaintomaa
    })
    const savedHavainto = await havainto.save()
    response.json(savedHavainto)  
  })

  // Routes /Lintutietokanta/forum
  app.get('/Lintutietokanta/forum', async (request, response) => {
    const posts = await Forum.find({})
    response.json(posts)
  })
  
  app.post('/Lintutietokanta/forum', async (request, response) => {
    const { poster } = request.body;
    const { text } = request.body;
    const aikaleima = getDate();
    console.log(poster)
    
  
    const post = new Forum({
      poster: poster,
      text: text,
      timestamp: aikaleima
    });
    console.log(post)
  
    try {
      const savedPost = await post.save();
      response.json(savedPost);
    } catch (error) {
      response.status(500).json({ error: 'Error saving the post' });
    }
  });

// Kaikki käyttäjät
app.get('/Lintutietokanta/users', async (request, response) => {
    const users = await User.find({})
    response.json(users)
  })
// Tietty käyttäjä
app.get('/Lintutietokanta/users/:id', async (request, response) => {
    let ID = request.params.id;
    ID = ID.substring(1); // Update ID to remove the first character
    console.log(ID);

    try {
        const user = await User.findOne({ userID: ID});
        console.log(user)
        if (!user) {
            return response.status(404).json({ message: 'User not found' });
        }

        response.json(user);
    } catch (error) {
        response.status(500).json({ error: error.message });
    }
});

// app listen port 3000
app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })