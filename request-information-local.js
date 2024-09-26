const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Create a form and append multiple files
const form = new FormData();
// form.append('files', fs.createReadStream('./copel.jpg'));
form.append('files', fs.createReadStream('./docs/preprocessed.jpg'));

// Make the POST request
axios.post(' http://127.0.0.1:5000/process', form, {
  headers: {
    ...form.getHeaders(),
    'Authorization': 'Bearer FURgFU3nT3BlbkFJc',
  },
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error('Error:', error.response ? error.response.data : error.message);
});