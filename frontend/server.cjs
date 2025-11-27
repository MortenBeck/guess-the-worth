/* eslint-env node */
const express = require("express");
const path = require("path");

const app = express();
const port = process.env.PORT || 8080;

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, "dist")));

// Handle client-side routing - always return index.html for unknown routes
// Use middleware instead of route to catch all unmatched routes
app.use((_req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

// Bind to 0.0.0.0 for Docker containers to accept external connections
app.listen(port, "0.0.0.0", () => {
  console.log(`Frontend server running on port ${port}`);
});
