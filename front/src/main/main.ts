import { app, BrowserWindow, dialog, ipcMain, net, protocol, session } from 'electron';
import * as fsSync from 'fs';
import { createReadStream } from 'fs';
import fs from 'fs/promises';
import path from 'path';
import { Readable } from 'stream';
import { pathToFileURL } from 'url';

const isDev = !app.isPackaged;
let win: BrowserWindow | null = null;

// Video storage folder inside userData
const VIDEO_STORE_DIR = path.join(app.getPath('userData'), 'videos');
const VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.m4v'];

// Register privileged custom scheme before app ready so it behaves like a standard scheme
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'app',
    privileges: {
      standard: true,
      secure: true,
      supportFetchAPI: true,
      stream: true,
      bypassCSP: true,
    },
  },
]);

function getConfigPath() {
  const dir = path.join(app.getPath('userData'), 'videolingo');
  return { dir, file: path.join(dir, 'config.json') };
}

async function ensureDir(p: string) {
  await fs.mkdir(p, { recursive: true }).catch(() => {});
}

function createWindow() {
  win = new BrowserWindow({
    width: 1100,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  win.on('closed', () => (win = null));
}

app.whenReady().then(async () => {
  await ensureDir(getConfigPath().dir);
  await ensureDir(VIDEO_STORE_DIR);
  console.log('VIDEO_STORE_DIR =', VIDEO_STORE_DIR);
  // Handle custom video://local/<encodedPath> requests and stream local files
  try {
    // Helper: convert Node ReadStream to Web ReadableStream (more robust than Readable.toWeb)
    const nodeStreamToWeb = (resultStream: fsSync.ReadStream) => {
      resultStream.pause();
      let closed = false;
      return new ReadableStream({
        start(controller) {
            resultStream.on('data', (chunk) => {
            if (closed) return;
            if (Buffer.isBuffer(chunk)) controller.enqueue(new Uint8Array(chunk));
            else controller.enqueue(chunk);
            if (controller.desiredSize != null && controller.desiredSize <= 0) resultStream.pause();
          });
          resultStream.on('error', (err) => {
            controller.error(err);
          });
          resultStream.on('end', () => {
            if (!closed) {
              closed = true;
              controller.close();
            }
          });
        },
        pull() {
          if (!closed) resultStream.resume();
        },
        cancel() {
          if (!closed) {
            closed = true;
            try { resultStream.close(); } catch (e) {}
          }
        }
      }, { highWaterMark: resultStream.readableHighWaterMark });
    };

    const handleRangeRequest = async (request: Request, targetPath: string) => {
      const rangeHeader = request.headers.get('range') || request.headers.get('Range');
      if (!rangeHeader) return null;
      // support formats like bytes=START-END
      const stat = await fs.stat(targetPath);
      const size = stat.size;
      const m = rangeHeader.match(/bytes=(\d*)-(\d*)/);
      let start = 0;
      let end = size - 1;
      if (m) {
        if (m[1]) start = parseInt(m[1], 10);
        if (m[2]) end = parseInt(m[2], 10);
      }
      if (isNaN(start) || isNaN(end) || start > end || start >= size) {
        return new Response('Requested Range Not Satisfiable', { status: 416 });
      }
      const chunkSize = end - start + 1;
      const fileStream = createReadStream(targetPath, { start, end });
      const mime = (() => {
        const ext = path.extname(targetPath).toLowerCase();
        if (ext === '.mp4') return 'video/mp4';
        if (ext === '.webm') return 'video/webm';
        if (ext === '.ogg' || ext === '.ogv') return 'video/ogg';
        if (ext === '.mp3') return 'audio/mpeg';
        return 'application/octet-stream';
      })();
      const headers = new Headers();
      headers.set('Accept-Ranges', 'bytes');
      headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
      headers.set('Content-Length', String(chunkSize));
      headers.set('Content-Type', mime);
      // Return a web-compatible ReadableStream
      return new Response(nodeStreamToWeb(fileStream as unknown as fsSync.ReadStream), { status: 206, headers });
    };

    protocol.handle('app', async (request) => {
      try {
        // Expect URLs like: app://video/<encoded-filename>
        const urlObj = new URL(request.url);
        const host = urlObj.host;
        const pathname = decodeURIComponent(urlObj.pathname || '').replace(/^\//, '');

        if (host !== 'video') {
          return new Response('Not Found', { status: 404, headers: { 'content-type': 'text/plain' } });
        }

        // Serve from the app userData videos directory
        let rel = pathname.replace(/^\//, '');
        const safeName = path.basename(rel); // sanitize
        let targetPath = path.join(VIDEO_STORE_DIR, safeName);

        const rangeResp = await handleRangeRequest(request, targetPath);
        if (rangeResp) return rangeResp;

        const asFileUrl = pathToFileURL(targetPath).toString();
        return net.fetch(asFileUrl);
      } catch (err) {
        console.error('app protocol handler error', err);
        throw err;
      }
    });
    console.log('app:// protocol handler registered on default session (fetch handler)');

    // Also register a stream protocol on the default session to ensure media elements recognize the scheme
    try {
      const ses = session.defaultSession;
      ses.protocol.registerStreamProtocol('app', (request, callback) => {
        (async () => {
          try {
            const urlObj = new URL(request.url);
            const host = urlObj.host;
            let targetPath = decodeURIComponent(urlObj.pathname || '').replace(/^\//, '');
            // if host === 'video' then targetPath is filename under public
            if (host === 'video') {
              // Serve from the app userData videos directory
              const safeName = path.basename(targetPath.replace(/^\//, ''));
              targetPath = path.join(VIDEO_STORE_DIR, safeName);
            } else {
              // Fallback to public for other app paths
              if (!path.isAbsolute(targetPath)) {
                const rel = targetPath.replace(/^\//, '');
                targetPath = path.join(__dirname, '..', 'public', rel);
              }
            }

            // Ensure file exists
            const stat = await fs.stat(targetPath).catch(() => null);
            if (!stat || !stat.isFile()) {
              console.warn('video stream protocol: file not found', targetPath);
              callback({ statusCode: 404, data: Readable.from(['Not found']) });
              return;
            }

            const fileSize = stat.size;
            const range = (request.headers && (request.headers as any)['range']) || '';
            const contentType = (() => {
              const ext = path.extname(targetPath).toLowerCase();
              if (ext === '.mp4') return 'video/mp4';
              if (ext === '.webm') return 'video/webm';
              if (ext === '.ogg' || ext === '.ogv') return 'video/ogg';
              if (ext === '.mp3') return 'audio/mpeg';
              if (ext === '.mkv') return 'video/x-matroska';
              return 'application/octet-stream';
            })();

            if (range) {
              const parts = range.replace(/bytes=/, '').split('-');
              const start = parseInt(parts[0], 10);
              const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
              if (isNaN(start) || isNaN(end) || start > end) {
                callback({ statusCode: 416, data: Readable.from(['Requested Range Not Satisfiable']) });
                return;
              }
              const chunksize = end - start + 1;
              const stream = fsSync.createReadStream(targetPath, { start, end });
              callback({
                statusCode: 206,
                headers: {
                  'Content-Range': `bytes ${start}-${end}/${fileSize}`,
                  'Accept-Ranges': 'bytes',
                  'Content-Length': String(chunksize),
                  'Content-Type': contentType,
                },
                data: stream,
              });
              return;
            }

            // No range: stream whole file
            const streamAll = fsSync.createReadStream(targetPath);
            callback({
              statusCode: 200,
              headers: {
                'Content-Length': String(fileSize),
                'Content-Type': contentType,
                'Accept-Ranges': 'bytes',
              },
              data: streamAll,
            });
          } catch (err) {
            console.error('video stream protocol handler error', err);
            callback({ statusCode: 500, data: Readable.from(['internal error']) });
          }
        })();
      });
      console.log('app:// stream protocol registered on default session');
    } catch (err) {
      console.warn('failed to register stream protocol on default session', err);
    }
  } catch (err) {
    console.warn('failed to register video protocol handler', err);
  }

  createWindow();

  ipcMain.handle('ping', () => 'pong');

  // Return list of imported videos from VIDEO_STORE_DIR
  ipcMain.handle('get-video-files', async () => {
    try {
      const names = await fs.readdir(VIDEO_STORE_DIR);
      const list: Array<{ name: string; size: number; url: string }> = [];
      for (const n of names) {
        const ext = path.extname(n).toLowerCase();
        if (!VIDEO_EXTENSIONS.includes(ext)) continue;
        const p = path.join(VIDEO_STORE_DIR, n);
        try {
          const s = await fs.stat(p);
          if (!s.isFile() || s.size === 0) continue;
          list.push({ name: n, size: s.size, url: `app://video/${encodeURIComponent(n)}` });
        } catch (e) {
          // ignore
        }
      }
      return list;
    } catch (err) {
      console.error('get-video-files error', err);
      return [];
    }
  });

  // Import a chosen video into the app videos directory (copies file)
  ipcMain.handle('import-video', async (_e, srcPath: string) => {
    try {
      const base = path.basename(srcPath);
      const safe = base.replace(/[^a-zA-Z0-9._-]/g, '_');
      let dest = path.join(VIDEO_STORE_DIR, safe);
      // avoid overwrite: if exists, append suffix
      let idx = 1;
      while (true) {
        try {
          const st = await fs.stat(dest);
          // if exists, add suffix
          const nameOnly = path.basename(safe, path.extname(safe));
          const ext = path.extname(safe);
          dest = path.join(VIDEO_STORE_DIR, `${nameOnly}_${idx}${ext}`);
          idx++;
        } catch (e) {
          break; // not exists
        }
      }

      // copy file
      await fs.copyFile(srcPath, dest);
      const st = await fs.stat(dest);
      const name = path.basename(dest);
      return { name, size: st.size, url: `app://video/${encodeURIComponent(name)}` };
    } catch (err) {
      console.error('import-video error', err);
      throw err;
    }
  });

  ipcMain.handle('dialog:openVideo', async () => {
    const res = await dialog.showOpenDialog(win!, {
      title: '选择视频文件',
      properties: ['openFile'],
      filters: [
        { name: 'Video', extensions: ['mp4', 'mkv', 'mov', 'webm', 'avi'] },
        { name: 'All Files', extensions: ['*'] },
      ],
    });
    return { canceled: res.canceled, filePaths: res.filePaths };
  });

  ipcMain.handle('dialog:openDirectory', async () => {
    const res = await dialog.showOpenDialog(win!, {
      title: '选择目录',
      properties: ['openDirectory', 'createDirectory'],
    });
    return { canceled: res.canceled, filePaths: res.filePaths };
  });

  ipcMain.handle('config:read', async () => {
    const { dir, file } = getConfigPath();
    await ensureDir(dir);
    try {
      const buf = await fs.readFile(file, 'utf-8');
      return JSON.parse(buf);
    } catch {
      return null;
    }
  });

  ipcMain.handle('config:write', async (_e, data: Record<string, any>) => {
    const { dir, file } = getConfigPath();
    await ensureDir(dir);
    try {
      await fs.writeFile(file, JSON.stringify(data ?? {}, null, 2), 'utf-8');
      return true;
    } catch {
      return false;
    }
  });

  ipcMain.handle('file:getInfo', async (_e, filePath: string) => {
    try {
      const stat = await fs.stat(filePath);
      return { size: stat.size };
    } catch {
      return { size: 0 };
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});