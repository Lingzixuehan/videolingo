const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.VIDEO_SERVER_PORT || 3421;

// Basic CORS middleware for all responses (allows fetch from dev origin)
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  // preflight
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

function contentTypeFor(file) {
  const ext = path.extname(file).toLowerCase();
  if (ext === '.mp4') return 'video/mp4';
  if (ext === '.webm') return 'video/webm';
  if (ext === '.ogg' || ext === '.ogv') return 'video/ogg';
  if (ext === '.mp3') return 'audio/mpeg';
  if (ext === '.mkv') return 'video/x-matroska';
  return 'application/octet-stream';
}

// Helper that serves a file path with Range support
function streamFile(filePath, req, res) {
  fs.stat(filePath, (err, stat) => {
    if (err || !stat.isFile()) {
      res.status(404).send('Not found');
      return;
    }

    const fileSize = stat.size;
    const range = req.headers.range;
    const contentType = contentTypeFor(filePath);

    if (range) {
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      if (isNaN(start) || isNaN(end) || start > end) {
        res.status(416).send('Requested Range Not Satisfiable');
        return;
      }
      const chunksize = end - start + 1;
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': contentType,
      });
      const stream = fs.createReadStream(filePath, { start, end });
      stream.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': fileSize,
        'Content-Type': contentType,
        'Accept-Ranges': 'bytes',
      });
      fs.createReadStream(filePath).pipe(res);
    }
  });
}

// Serve files under front/public/videos at /videos/<name>
// Use express.static so we get proper content-type and Range support
app.use('/videos', express.static(path.join(__dirname, 'public', 'videos')));

// Expose the examples directory so demo video files can be fetched
app.use('/examples', express.static(path.join(__dirname, 'src', 'common', 'whisper', 'examples')));

// Serve arbitrary path via query param (useful for absolute paths)
app.get('/video', (req, res) => {
  const p = req.query.path;
  if (!p) return res.status(400).send('missing path');
  // if it's a relative path (starts with /), resolve to front/public
  let filePath = p;
  if (!path.isAbsolute(p)) {
    filePath = path.join(__dirname, p.replace(/^\//, ''));
  }
  // ensure CORS header present on streamed responses as well
  res.setHeader('Access-Control-Allow-Origin', '*');
  streamFile(filePath, req, res);
});

app.listen(PORT, () => {
  console.log(`video-server listening on http://127.0.0.1:${PORT}`);
});
