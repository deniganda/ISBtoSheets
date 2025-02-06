const axios = require('axios');
const { google } = require('googleapis');

// Parse the JSON key from the environment variable
const keyJson = JSON.parse(process.env.GOOGLE_SHEET_KEY_JSON);

// Google Sheets API authentication setup
const auth = new google.auth.GoogleAuth({
    credentials: keyJson, // Use the parsed JSON directly
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});
const sheets = google.sheets({ version: 'v4', auth });

// URL to fetch data from
const url = process.env.API_URL_PEN; // Use environment variable for URL

// Define the spreadsheet ID and range
const spreadsheetId = process.env.SPREADSHEET_ID; // Use environment variable for Spreadsheet ID
const clearRange = 'Penyedia2025!A:ZZ'; // Range to clear
const updateRange = 'Penyedia2025!A1'; // Range to update

async function fetchData() {
    try {
        // Fetch data from the URL
        const response = await axios.get(url);
        const data = response.data;

        // Check if data is in expected format
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Data format is not as expected');
        }

        // Convert JSON data to a 2D array for Sheets
        const headers = Object.keys(data[0] || {});
        const rows = data.map(item => headers.map(header => item[header]));

        // Add headers as the first row
        rows.unshift(headers);

        // Clear existing data in the specified range
        await sheets.spreadsheets.values.clear({
            spreadsheetId,
            range: clearRange,
        });

        // Prepare the data to be written to the spreadsheet
        const resource = {
            values: rows,
        };

        // Write data to Google Sheets
        const result = await sheets.spreadsheets.values.update({
            spreadsheetId,
            range: updateRange,
            valueInputOption: 'RAW',
            resource,
        });

        console.log('Data successfully written to Google Sheets', result.data);
    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
    }
}

fetchData();